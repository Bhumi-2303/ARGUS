"""SQLite-backed transactional outbox and Dead-Letter Queue (DLQ) storage."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog
from sqlalchemy import select, update, delete, desc

from argus.database.engine import get_session, get_sync_engine
from argus.database.models import Base, BusOutboxModel, BusDeadLetterModel
from argus.bus.events import BusEvent

logger = structlog.get_logger("argus.bus.outbox")


class SqliteOutbox:
    """Manages transactional outbox and dead-letter queues in SQLite."""

    def __init__(self, db_url: Optional[str] = None):
        self._db_url = db_url
        self._init_tables()

    def _init_tables(self) -> None:
        """Ensure outbox and DLQ tables exist."""
        engine = get_sync_engine(self._db_url)
        Base.metadata.create_all(
            bind=engine,
            tables=[BusOutboxModel.__table__, BusDeadLetterModel.__table__],
        )

    def save_event(self, event: BusEvent) -> None:
        """Store an event into the outbox with status 'pending'."""
        session = get_session(self._db_url)
        try:
            # Check if event already exists
            existing = session.execute(
                select(BusOutboxModel).where(BusOutboxModel.event_id == event.event_id)
            ).scalar_one_or_none()

            if existing is None:
                record = BusOutboxModel(
                    event_id=event.event_id,
                    topic=event.topic,
                    payload_json=json.dumps(event.payload, default=str),
                    headers_json=json.dumps(event.headers, default=str) if event.headers else None,
                    correlation_id=event.correlation_id,
                    created_at=event.timestamp,
                    status="pending",
                    retry_count=0,
                )
                session.add(record)
                session.commit()
                logger.debug("outbox_event_saved", event_id=event.event_id, topic=event.topic)
        except Exception as e:
            session.rollback()
            logger.error("outbox_save_failed", event_id=event.event_id, error=str(e))
            raise
        finally:
            session.close()

    def mark_delivered(self, event_id: str) -> None:
        """Mark an outbox event as delivered."""
        session = get_session(self._db_url)
        try:
            now = datetime.now(timezone.utc)
            session.execute(
                update(BusOutboxModel)
                .where(BusOutboxModel.event_id == event_id)
                .values(status="delivered", delivered_at=now)
            )
            session.commit()
            logger.debug("outbox_event_marked_delivered", event_id=event_id)
        except Exception as e:
            session.rollback()
            logger.error("outbox_mark_delivered_failed", event_id=event_id, error=str(e))
        finally:
            session.close()

    def record_failure(
        self,
        event_id: str,
        error: str,
        max_retries: int = 3,
        force_dlq: bool = False,
    ) -> bool:
        """Record delivery failure.

        If retry_count reaches max_retries or force_dlq is True, mark as 'dead_letter' and write to DLQ table.
        Returns True if moved to DLQ, False if remaining in retry state.
        """
        session = get_session(self._db_url)
        moved_to_dlq = False
        try:
            record = session.execute(
                select(BusOutboxModel).where(BusOutboxModel.event_id == event_id)
            ).scalar_one_or_none()

            if record:
                record.retry_count += 1
                record.last_error = str(error)

                if force_dlq or record.retry_count >= max_retries:
                    record.status = "dead_letter"
                    moved_to_dlq = True

                    # Also insert into dedicated dead-letter table
                    dlq_record = BusDeadLetterModel(
                        event_id=record.event_id,
                        topic=record.topic,
                        payload_json=record.payload_json,
                        error_reason=str(error),
                        failed_at=datetime.now(timezone.utc),
                        retry_count=record.retry_count,
                    )
                    session.add(dlq_record)
                    logger.warning(
                        "event_moved_to_dead_letter",
                        event_id=event_id,
                        retries=record.retry_count,
                        error=error,
                    )
                else:
                    record.status = "pending"

                session.commit()
        except Exception as e:
            session.rollback()
            logger.error("outbox_record_failure_failed", event_id=event_id, error=str(e))
        finally:
            session.close()

        return moved_to_dlq

    def get_pending_events(self, limit: int = 100) -> List[BusEvent]:
        """Fetch un-delivered pending events ordered by timestamp for restart recovery."""
        session = get_session(self._db_url)
        events = []
        try:
            records = session.execute(
                select(BusOutboxModel)
                .where(BusOutboxModel.status == "pending")
                .order_by(BusOutboxModel.created_at.asc())
                .limit(limit)
            ).scalars().all()

            for r in records:
                try:
                    payload = json.loads(r.payload_json) if r.payload_json else {}
                except Exception:
                    payload = {"raw": r.payload_json}

                try:
                    headers = json.loads(r.headers_json) if r.headers_json else {}
                except Exception:
                    headers = {}

                events.append(
                    BusEvent(
                        event_id=r.event_id,
                        topic=r.topic,
                        payload=payload,
                        timestamp=r.created_at,
                        correlation_id=r.correlation_id,
                        headers=headers,
                    )
                )
        except Exception as e:
            logger.error("outbox_fetch_pending_failed", error=str(e))
        finally:
            session.close()

        return events

    def get_dlq_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent events stored in the Dead-Letter Queue."""
        session = get_session(self._db_url)
        dlq_list = []
        try:
            records = session.execute(
                select(BusDeadLetterModel)
                .order_by(desc(BusDeadLetterModel.failed_at))
                .limit(limit)
            ).scalars().all()

            for r in records:
                try:
                    payload = json.loads(r.payload_json) if r.payload_json else {}
                except Exception:
                    payload = {"raw": r.payload_json}

                dlq_list.append({
                    "id": r.id,
                    "event_id": r.event_id,
                    "topic": r.topic,
                    "payload": payload,
                    "error_reason": r.error_reason,
                    "error": r.error_reason,
                    "failed_at": r.failed_at.isoformat() if r.failed_at else None,
                    "retry_count": r.retry_count,
                })
        except Exception as e:
            logger.error("fetch_dlq_events_failed", error=str(e))
        finally:
            session.close()

        return dlq_list

    def purge_dlq(self) -> int:
        """Clear all entries in the Dead-Letter Queue table."""
        session = get_session(self._db_url)
        count = 0
        try:
            result = session.execute(delete(BusDeadLetterModel))
            session.commit()
            count = result.rowcount
            logger.info("dlq_purged", count=count)
        except Exception as e:
            session.rollback()
            logger.error("purge_dlq_failed", error=str(e))
        finally:
            session.close()
        return count

    def requeue_dlq(self, limit: Optional[int] = None) -> int:
        """Move dead-letter events back to pending outbox status for retry."""
        session = get_session(self._db_url)
        requeued = 0
        try:
            query = select(BusDeadLetterModel).order_by(BusDeadLetterModel.failed_at.asc())
            if limit:
                query = query.limit(limit)
            dead_letters = session.execute(query).scalars().all()

            for dl in dead_letters:
                session.execute(
                    update(BusOutboxModel)
                    .where(BusOutboxModel.event_id == dl.event_id)
                    .values(status="pending", retry_count=0)
                )
                session.delete(dl)
                requeued += 1

            session.commit()
            logger.info("dlq_requeued", count=requeued)
        except Exception as e:
            session.rollback()
            logger.error("requeue_dlq_failed", error=str(e))
        finally:
            session.close()

        return requeued
