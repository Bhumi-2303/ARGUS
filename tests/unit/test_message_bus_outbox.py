"""Unit and integration tests for durable MessageBus, SQLite outbox, back-pressure, and DLQ."""

import asyncio
import os
import tempfile
import pytest
from datetime import datetime, timezone

from argus.bus.events import BusEvent
from argus.bus.outbox import SqliteOutbox
from argus.bus.message_bus import MessageBus
from argus.database.models import Base
from argus.database.engine import get_sync_engine


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_url = f"sqlite:///{path}"
    engine = get_sync_engine(db_url)
    Base.metadata.create_all(bind=engine)
    yield db_url
    if os.path.exists(path):
        os.remove(path)


@pytest.mark.asyncio
async def test_typed_bus_event_serialization():
    """Verify BusEvent creation, attributes, serialization, and deserialization."""
    event = BusEvent.from_message(
        topic="alerts.ics",
        message={"alert_id": "ALT-001", "severity": "HIGH"},
        correlation_id="corr-123",
        headers={"origin": "sensor-1"},
    )
    assert event.topic == "alerts.ics"
    assert event.correlation_id == "corr-123"
    assert event.payload["alert_id"] == "ALT-001"
    assert event.headers["origin"] == "sensor-1"

    d = event.to_dict()
    assert d["event_id"] == event.event_id
    assert d["topic"] == "alerts.ics"

    # From dict reconstruct
    reconstructed = BusEvent.from_message(topic=d["topic"], message=d["payload"])
    assert reconstructed.topic == event.topic


@pytest.mark.asyncio
async def test_sqlite_outbox_persistence_and_delivery(temp_db):
    """Verify outbox saves pending event and updates to delivered upon processing."""
    outbox = SqliteOutbox(db_url=temp_db)
    event = BusEvent.from_message("system.telemetry", {"temperature": 75.5})

    outbox.save_event(event)
    pending = outbox.get_pending_events()
    assert len(pending) == 1
    assert pending[0].event_id == event.event_id
    assert pending[0].payload["temperature"] == 75.5

    outbox.mark_delivered(event.event_id)
    remaining = outbox.get_pending_events()
    assert len(remaining) == 0


@pytest.mark.asyncio
async def test_message_bus_pub_sub_lifecycle(temp_db):
    """Verify pub/sub delivery with typed events and subscriber worker execution."""
    bus = MessageBus(db_url=temp_db)
    received = []

    async def sample_handler(evt: BusEvent):
        received.append(evt)

    await bus.subscribe("telemetry.flow", sample_handler)
    await bus.start()

    published_evt = await bus.publish("telemetry.flow", {"flow_bytes": 1024})
    assert published_evt.event_id is not None

    # Wait for async subscriber worker loop
    await asyncio.sleep(0.1)

    assert len(received) == 1
    assert received[0].payload["flow_bytes"] == 1024
    assert bus.messages_delivered == 1

    await bus.stop()


@pytest.mark.asyncio
async def test_message_bus_survives_restart_via_outbox_recovery(temp_db):
    """Verify un-delivered events stored in SQLite outbox are recovered on bus restart."""
    outbox = SqliteOutbox(db_url=temp_db)
    unprocessed_event = BusEvent.from_message(
        topic="agent.threat.alert",
        message={"target_ip": "192.168.1.100", "threat": "SYN Flood"},
    )
    # Save directly to outbox to simulate process crash before in-memory dispatch
    outbox.save_event(unprocessed_event)

    recovered_events = []

    async def recovery_handler(evt: BusEvent):
        recovered_events.append(evt)

    # Boot fresh bus instance on same database
    fresh_bus = MessageBus(db_url=temp_db)
    await fresh_bus.subscribe("agent.threat.*", recovery_handler)

    await fresh_bus.start()
    await asyncio.sleep(0.15)

    assert len(recovered_events) >= 1
    assert recovered_events[0].event_id == unprocessed_event.event_id
    assert fresh_bus.messages_recovered >= 1

    # Outbox should now mark it delivered
    assert len(outbox.get_pending_events()) == 0

    await fresh_bus.stop()


@pytest.mark.asyncio
async def test_message_bus_backpressure_and_dlq_overflow(temp_db):
    """Verify back-pressure bounded queue overflow routes to Dead-Letter Queue."""
    # Bus with max_queue_size=1 and tiny backpressure timeout
    bus = MessageBus(db_url=temp_db, max_queue_size=1, backpressure_timeout=0.01)

    # Slow subscriber that blocks queue
    async def blocking_handler(evt: BusEvent):
        await asyncio.sleep(1.0)

    await bus.subscribe("high.volume.topic", blocking_handler, max_queue_size=1)
    await bus.start()

    # Publish 3 events: 1 gets taken by worker, 1 fills queue of size 1, 1 overflows
    await bus.publish("high.volume.topic", {"msg": 1})
    await bus.publish("high.volume.topic", {"msg": 2})
    await bus.publish("high.volume.topic", {"msg": 3})

    await asyncio.sleep(0.05)

    dlq_events = bus.get_dlq_events()
    assert len(dlq_events) >= 1
    assert "Backpressure overflow" in dlq_events[0]["error"]

    # Purge DLQ
    purged_count = bus.purge_dlq()
    assert purged_count >= 1
    assert len(bus.get_dlq_events()) == 0

    await bus.stop()


@pytest.mark.asyncio
async def test_message_bus_dead_letter_queue_on_repeated_failure(temp_db):
    """Verify failing subscriber handler retries and eventually lands in DLQ."""
    bus = MessageBus(db_url=temp_db, max_retries=2)

    attempt_counts = [0]

    async def failing_handler(evt: BusEvent):
        attempt_counts[0] += 1
        raise ValueError("Simulated parsing crash in consumer handler")

    await bus.subscribe("faulty.topic", failing_handler)
    await bus.start()

    await bus.publish("faulty.topic", {"data": "bad_payload"})

    # Wait for retries
    await asyncio.sleep(0.25)

    assert attempt_counts[0] == 2
    assert bus.messages_failed == 1

    dlq_items = bus.get_dlq_events()
    assert len(dlq_items) == 1
    assert "Simulated parsing crash" in dlq_items[0]["error"]
    assert dlq_items[0]["topic"] == "faulty.topic"

    # Test DLQ requeue
    requeued = bus.requeue_dlq()
    assert requeued == 1
    assert len(bus.get_dlq_events()) == 0

    await bus.stop()
