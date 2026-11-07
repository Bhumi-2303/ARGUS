"""Durable asyncio pub/sub message bus with SQLite outbox, back-pressure and DLQ."""

import asyncio
import inspect
from datetime import datetime, timezone
import fnmatch
from typing import Any, Callable, Dict, List, Optional
import structlog

from argus.bus.events import BusEvent
from argus.bus.outbox import SqliteOutbox

logger = structlog.get_logger("argus.bus")


class BackpressureError(Exception):
    """Raised when subscriber queue reaches capacity under excessive load."""

    pass


class SubscriberRegistration:
    """Manages queue buffer and worker task for a single subscriber handler."""

    def __init__(self, topic_pattern: str, handler: Callable, max_queue_size: int = 500):
        self.topic_pattern = topic_pattern
        self.handler = handler
        self.max_queue_size = max_queue_size
        self._queue: Optional[asyncio.Queue[BusEvent]] = None
        self.worker_task: Optional[asyncio.Task] = None
        self.is_running: bool = False

    @property
    def queue(self) -> asyncio.Queue[BusEvent]:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        if self._queue is None or (
            current_loop and getattr(self._queue, "_loop", None) not in (None, current_loop)
        ):
            self._queue = asyncio.Queue(maxsize=self.max_queue_size)
        return self._queue

    def matches(self, topic: str) -> bool:
        """Check if topic matches the subscriber pattern."""
        if self.topic_pattern == "*" or self.topic_pattern == topic:
            return True
        return fnmatch.fnmatch(topic, self.topic_pattern)


class MessageBus:
    """Async in-process pub/sub message bus with SQLite-backed outbox and DLQ."""

    def __init__(
        self,
        db_url: Optional[str] = None,
        max_queue_size: int = 500,
        max_retries: int = 3,
        backpressure_timeout: float = 1.0,
    ):
        self._db_url = db_url
        self._max_queue_size = max_queue_size
        self._max_retries = max_retries
        self._backpressure_timeout = backpressure_timeout

        self._outbox: Optional[SqliteOutbox] = None
        self._subscribers: List[SubscriberRegistration] = []
        self._dlq_obj: Optional[asyncio.Queue] = None
        self._running: bool = False
        self._lock_obj: Optional[asyncio.Lock] = None

        # Metrics
        self.messages_sent: int = 0
        self.messages_delivered: int = 0
        self.messages_failed: int = 0
        self.messages_recovered: int = 0

    @property
    def _lock(self) -> asyncio.Lock:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        if self._lock_obj is None or (
            current_loop and getattr(self._lock_obj, "_loop", None) not in (None, current_loop)
        ):
            self._lock_obj = asyncio.Lock()
        return self._lock_obj

    @property
    def _dlq(self) -> asyncio.Queue:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        if self._dlq_obj is None or (
            current_loop and getattr(self._dlq_obj, "_loop", None) not in (None, current_loop)
        ):
            self._dlq_obj = asyncio.Queue()
        return self._dlq_obj

    @property
    def outbox(self) -> SqliteOutbox:
        """Lazy-loaded SQLite outbox instance."""
        if self._outbox is None:
            self._outbox = SqliteOutbox(self._db_url)
        return self._outbox

    async def start(self) -> None:
        """Start the message bus and recover pending events from outbox."""
        async with self._lock:
            if self._running:
                return
            self._running = True

            # Start subscriber background queue workers
            for sub in self._subscribers:
                self._start_subscriber_worker(sub)

            logger.info("message_bus_started", max_queue_size=self._max_queue_size)

        # Recover un-delivered outbox events from prior runs (survive restarts)
        await self._recover_pending_events()

    async def stop(self) -> None:
        """Gracefully stop the message bus and flush subscriber queues."""
        async with self._lock:
            self._running = False
            for sub in self._subscribers:
                sub.is_running = False
                if sub.worker_task and not sub.worker_task.done():
                    sub.worker_task.cancel()
                    try:
                        await sub.worker_task
                    except (asyncio.CancelledError, Exception):
                        pass
                sub.worker_task = None
                sub._queue = None

            logger.info("message_bus_stopped")

    async def subscribe(
        self,
        topic: str,
        handler: Callable,
        max_queue_size: Optional[int] = None,
    ) -> None:
        """Subscribe a handler to a topic or wildcard pattern (e.g. 'agent.*')."""
        async with self._lock:
            # Check for existing duplicate subscription
            for sub in self._subscribers:
                if sub.topic_pattern == topic and sub.handler == handler:
                    return

            queue_size = max_queue_size or self._max_queue_size
            sub = SubscriberRegistration(topic, handler, max_queue_size=queue_size)
            self._subscribers.append(sub)

            if self._running:
                self._start_subscriber_worker(sub)

            logger.debug("handler_subscribed", topic=topic)

    async def unsubscribe(self, topic: str, handler: Callable) -> None:
        """Unsubscribe a handler from a topic."""
        async with self._lock:
            remaining = []
            for sub in self._subscribers:
                if sub.topic_pattern == topic and sub.handler == handler:
                    sub.is_running = False
                    if sub.worker_task and not sub.worker_task.done():
                        sub.worker_task.cancel()
                else:
                    remaining.append(sub)
            self._subscribers = remaining
            logger.debug("handler_unsubscribed", topic=topic)

    async def publish(self, topic: str, message: Any) -> BusEvent:
        """Publish an event to a topic.

        Normalizes input into typed BusEvent, persists to SQLite outbox,
        and enqueues with back-pressure handling.
        """
        event = BusEvent.from_message(topic, message)

        # 1. Persist to SQLite Outbox (ensures events survive process termination)
        try:
            self.outbox.save_event(event)
        except Exception as e:
            logger.error("outbox_persistence_failed", event_id=event.event_id, error=str(e))

        if not self._running:
            logger.warning("publish_when_stopped", topic=topic, event_id=event.event_id)
            return event

        self.messages_sent += 1

        # 2. Find matching subscribers
        matching = [s for s in self._subscribers if s.matches(topic)]
        if not matching:
            logger.debug("no_subscribers_for_topic", topic=topic)
            self.outbox.mark_delivered(event.event_id)
            return event

        # 3. Route to subscriber queues with back-pressure check
        for sub in matching:
            try:
                # Bounded queue back-pressure: wait up to timeout
                await asyncio.wait_for(
                    sub.queue.put(event),
                    timeout=self._backpressure_timeout,
                )
            except (asyncio.TimeoutError, asyncio.QueueFull):
                logger.error(
                    "subscriber_backpressure_overflow",
                    topic=topic,
                    event_id=event.event_id,
                    queue_size=sub.queue.qsize(),
                )
                await self._send_to_dlq(
                    event=event,
                    error=f"Backpressure overflow: subscriber queue reached capacity ({sub.queue.maxsize})",
                )

        return event

    def _start_subscriber_worker(self, sub: SubscriberRegistration) -> None:
        """Launch background worker processing a subscriber's bounded queue."""
        if sub.worker_task is None or sub.worker_task.done():
            sub.is_running = True
            sub.worker_task = asyncio.create_task(self._process_subscriber_queue(sub))

    async def _process_subscriber_queue(self, sub: SubscriberRegistration) -> None:
        """Worker loop processing messages for a single subscriber with retries."""
        while sub.is_running and self._running:
            try:
                event = await sub.queue.get()
            except asyncio.CancelledError:
                break
            except Exception:
                continue

            delivered = False
            last_err = None

            for attempt in range(1, self._max_retries + 1):
                try:
                    if inspect.iscoroutinefunction(sub.handler):
                        await sub.handler(event)
                    else:
                        sub.handler(event)
                    delivered = True
                    self.messages_delivered += 1
                    break
                except Exception as e:
                    last_err = str(e)
                    logger.warning(
                        "message_delivery_attempt_failed",
                        topic=event.topic,
                        event_id=event.event_id,
                        attempt=attempt,
                        error=last_err,
                    )
                    if attempt < self._max_retries:
                        await asyncio.sleep(0.05 * attempt)

            if delivered:
                self.outbox.mark_delivered(event.event_id)
            else:
                self.messages_failed += 1
                await self._send_to_dlq(event, error=last_err or "Unknown handler failure")

            sub.queue.task_done()

    async def _send_to_dlq(self, event: BusEvent, error: str) -> None:
        """Route failed event to dead-letter queue (in-memory + database)."""
        dlq_entry = {
            "event_id": event.event_id,
            "topic": event.topic,
            "payload": event.payload,
            "error": error,
            "failed_at": datetime.now(timezone.utc).isoformat(),
        }
        await self._dlq.put(dlq_entry)
        self.outbox.record_failure(event.event_id, error=error, force_dlq=True)

    async def _recover_pending_events(self) -> None:
        """Recover un-delivered outbox events from disk after restart."""
        try:
            pending = self.outbox.get_pending_events(limit=500)
            if not pending:
                return

            logger.info("recovering_outbox_events", count=len(pending))
            for event in pending:
                matching = [s for s in self._subscribers if s.matches(event.topic)]
                if matching:
                    for sub in matching:
                        try:
                            sub.queue.put_nowait(event)
                            self.messages_recovered += 1
                        except asyncio.QueueFull:
                            await self._send_to_dlq(event, "Queue full during restart recovery")
                else:
                    self.outbox.mark_delivered(event.event_id)

            logger.info("outbox_recovery_complete", recovered=len(pending))
        except Exception as e:
            logger.error("outbox_recovery_failed", error=str(e))

    def get_dlq_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent events from the Dead-Letter Queue."""
        return self.outbox.get_dlq_events(limit=limit)

    def purge_dlq(self) -> int:
        """Clear all records from DLQ."""
        return self.outbox.purge_dlq()

    def requeue_dlq(self, limit: Optional[int] = None) -> int:
        """Requeue dead-letter events for retry."""
        return self.outbox.requeue_dlq(limit=limit)
