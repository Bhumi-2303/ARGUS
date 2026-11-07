"""Unit tests for argus.memory: WorkingMemory, SharedMemory, and pruned stub verification."""

from pathlib import Path
import pytest

from argus.blackboard.blackboard import Blackboard
from argus.core.enums import BlackboardSection
from argus.memory import WorkingMemory, SharedMemory


@pytest.mark.asyncio
async def test_working_memory_isolated_operations():
    """Verify WorkingMemory storage, retrieval, deletion, and clear."""
    wm = WorkingMemory(agent_id="agent_threat")
    assert wm.agent_id == "agent_threat"

    # Set and get
    await wm.set("threat_score", 0.89)
    await wm.set("anomaly_type", "DOS_SYN")
    assert await wm.get("threat_score") == 0.89
    assert await wm.get("anomaly_type") == "DOS_SYN"
    assert await wm.get("non_existent") is None

    # Get all
    all_data = await wm.get_all()
    assert all_data["threat_score"] == 0.89
    assert all_data["anomaly_type"] == "DOS_SYN"

    # Delete
    assert await wm.delete("anomaly_type") is True
    assert await wm.get("anomaly_type") is None
    assert await wm.delete("non_existent") is False

    # Clear
    await wm.clear()
    assert len(await wm.get_all()) == 0


@pytest.mark.asyncio
async def test_shared_memory_blackboard_integration():
    """Verify SharedMemory reads and writes through Blackboard state."""
    bb = Blackboard()
    sm = SharedMemory(agent_id="pipeline_runner", blackboard=bb)

    await sm.set("protocol", "IEC-60870-5-104")
    await sm.set("packet_rate", 1450)

    assert await sm.get("protocol") == "IEC-60870-5-104"
    assert await sm.get("packet_rate") == 1450

    # Check Blackboard raw read
    bb_val = await bb.read(BlackboardSection.SHARED_CONTEXT, "protocol")
    assert bb_val == "IEC-60870-5-104"

    # Delete from shared memory
    assert await sm.delete("protocol") is True
    assert await sm.get("protocol") is None

    # Clear section
    await sm.set("temp_metric", 99)
    await sm.clear()
    assert await sm.get("temp_metric") is None


def test_pruned_memory_stubs_are_deleted():
    """Verify that unused stubs (cache, persistent_memory, vector_memory) were pruned."""
    memory_dir = Path("src/argus/memory")
    assert (memory_dir / "working_memory.py").exists()
    assert (memory_dir / "shared_memory.py").exists()
    assert (memory_dir / "__init__.py").exists()

    # Deleted stubs MUST NOT exist on filesystem
    assert not (memory_dir / "cache.py").exists()
    assert not (memory_dir / "persistent_memory.py").exists()
    assert not (memory_dir / "vector_memory.py").exists()

    # Attempting to import stubs from argus.memory must fail
    import argus.memory as mem

    assert not hasattr(mem, "Cache")
    assert not hasattr(mem, "PersistentMemory")
    assert not hasattr(mem, "VectorMemory")

    with pytest.raises(ImportError):
        from argus.memory import cache  # noqa: F401  # type: ignore

    with pytest.raises(ImportError):
        from argus.memory import persistent_memory  # noqa: F401  # type: ignore

    with pytest.raises(ImportError):
        from argus.memory import vector_memory  # noqa: F401  # type: ignore
