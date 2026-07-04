"""In-process async pub/sub message bus."""
import asyncio
from typing import Any, Callable, Dict, List, Set
import structlog
from datetime import datetime, timezone


class MessageBus:
    """Async in-process pub/sub message bus."""

    def __init__(self):
        self._subscribers: Dict[str, Set[Callable]] = {}
        self._dlq: asyncio.Queue = asyncio.Queue()
        self._running: bool = False
        self._logger = structlog.get_logger("argus.bus")
        
        # Metrics
        self.messages_sent = 0
        self.messages_delivered = 0
        self.messages_failed = 0

    async def start(self) -> None:
        """Start the message bus."""
        self._running = True
        self._logger.info("message_bus_started")

    async def stop(self) -> None:
        """Stop the message bus."""
        self._running = False
        self._logger.info("message_bus_stopped")

    async def subscribe(self, topic: str, handler: Callable) -> None:
        """Subscribe a handler to a topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = set()
        self._subscribers[topic].add(handler)
        self._logger.debug("handler_subscribed", topic=topic)

    async def unsubscribe(self, topic: str, handler: Callable) -> None:
        """Unsubscribe a handler from a topic."""
        if topic in self._subscribers and handler in self._subscribers[topic]:
            self._subscribers[topic].remove(handler)
            self._logger.debug("handler_unsubscribed", topic=topic)

    async def publish(self, topic: str, message: Any) -> None:
        """Publish a message to a topic."""
        if not self._running:
            self._logger.warning("publish_when_stopped", topic=topic)
            return

        self.messages_sent += 1
        handlers = self._subscribers.get(topic, set()).copy()
        
        if not handlers:
            self._logger.debug("no_subscribers", topic=topic)
            return

        for handler in handlers:
            asyncio.create_task(self._deliver(handler, topic, message))

    async def _deliver(self, handler: Callable, topic: str, message: Any) -> None:
        """Deliver a message to a specific handler."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)
            self.messages_delivered += 1
        except Exception as e:
            self.messages_failed += 1
            self._logger.error("message_delivery_failed", topic=topic, error=str(e))
            await self._dlq.put({
                "topic": topic,
                "message": message,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
