"""Unit and integration tests for SQLite/SQLAlchemy incident store and pipeline run persistence."""

import os
import tempfile
import pytest
from datetime import datetime, timezone
from pydantic import BaseModel

from argus.database.engine import get_sync_engine, get_session
from argus.database.migrations import create_all_tables_sync
from argus.database.models import (
    IncidentModel,
    PipelineRunModel,
    PipelineStageTraceModel,
    DecisionApprovalTokenModel,
)
from argus.orchestrator.pipeline import PipelineContext, TraceEvent
from argus.orchestrator.store import PipelineRunStore


class MockThreat(BaseModel):
    threat_level: str = "critical"
    confidence: float = 0.98


class MockRisk(BaseModel):
    risk_score: float = 85.0
    criticality: str = "HIGH"


class MockDecision(BaseModel):
    approval_required: bool = True
    reasoning: str = "Automated isolation requested for compromised endpoint"
    execution_plan: str = "Isolate host from control VLAN"


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_url = f"sqlite:///{path}"
    create_all_tables_sync(db_url)
    yield db_url
    if os.path.exists(path):
        os.remove(path)


def test_database_table_creation(temp_db):
    """Verify that all relational models are created properly."""
    engine = get_sync_engine(temp_db)
    table_names = engine.dialect.get_table_names(engine.connect())
    assert "incidents" in table_names
    assert "pipeline_runs" in table_names
    assert "pipeline_stage_traces" in table_names
    assert "decision_approval_tokens" in table_names
    assert "bus_outbox" in table_names
    assert "bus_dead_letter" in table_names


def test_persist_pipeline_run_benign(temp_db):
    """Verify persisting benign pipeline context creates run records without incident."""
    store = PipelineRunStore(db_url=temp_db)

    ctx = PipelineContext(
        correlation_id="corr-benign-01",
        event_id="evt-benign-01",
        flow={"src_ip": "10.0.0.1", "dst_ip": "10.0.0.2"},
        features={"pkt_mean_to_max": 0.5, "tcp_flag_density": 0.1, "log_pkt_mean": 2.0, "log_pkt_max": 3.0},
        model_name="model_d2_coral",
        status="completed",
    )
    ctx.add_trace(TraceEvent(
        agent="data_intelligence",
        status="SUCCESS",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        duration=3.5,
        output_summary="Features normalized",
    ))

    token = store.persist_pipeline_run(ctx)
    assert token is None

    # Retrieve and verify run
    run = store.get_pipeline_run("corr-benign-01")
    assert run is not None
    assert run["correlation_id"] == "corr-benign-01"
    assert run["model_name"] == "model_d2_coral"
    assert run["incident_id"] is None
    assert run["approval_token"] is None
    assert len(run["traces"]) == 1
    assert run["traces"][0]["agent"] == "data_intelligence"


def test_persist_pipeline_run_critical_attack_generates_incident_and_token(temp_db):
    """Verify high criticality attack persists incident and decision approval token."""
    store = PipelineRunStore(db_url=temp_db)

    ctx = PipelineContext(
        correlation_id="corr-attack-01",
        event_id="evt-attack-01",
        flow={"src_ip": "192.168.1.50", "dst_ip": "192.168.1.1"},
        features={"pkt_mean_to_max": 0.9, "tcp_flag_density": 0.95, "log_pkt_mean": 6.0, "log_pkt_max": 7.0},
        model_name="model_d3_native",
        threat=MockThreat(threat_level="critical", confidence=0.98),
        risk=MockRisk(risk_score=92.0, criticality="HIGH"),
        decision=MockDecision(
            approval_required=True,
            reasoning="Critical injection attack detected",
            execution_plan="Isolate subnet",
        ),
        status="completed",
    )
    ctx.add_trace(TraceEvent(
        agent="threat_analysis",
        status="SUCCESS",
        duration=12.5,
        output_summary="Threat classified CRITICAL",
    ))
    ctx.add_trace(TraceEvent(
        agent="decision_support",
        status="SUCCESS",
        duration=8.0,
        output_summary="HITL approval required",
    ))

    token = store.persist_pipeline_run(ctx)
    assert token is not None
    assert token.startswith("appr-")

    # Verify database records
    session = get_session(temp_db)
    try:
        inc = session.query(IncidentModel).filter_by(correlation_id="corr-attack-01").first()
        assert inc is not None
        assert inc.severity == "critical"
        assert inc.status == "detected"
        assert inc.approval_required is True
        assert inc.approval_status == "pending"
        assert inc.approval_token == token

        tok_record = session.query(DecisionApprovalTokenModel).filter_by(token=token).first()
        assert tok_record is not None
        assert tok_record.incident_id == inc.incident_id
        assert tok_record.status == "PENDING"
        assert tok_record.approver_role == "incident_commander"
    finally:
        session.close()

    # Verify retrieval through store
    run = store.get_pipeline_run("corr-attack-01")
    assert run is not None
    assert run["approval_token"] == token
    assert run["incident_id"] == inc.incident_id
    assert len(run["traces"]) == 2


def test_list_recent_pipeline_runs(temp_db):
    """Verify listing recent runs."""
    store = PipelineRunStore(db_url=temp_db)

    for i in range(3):
        ctx = PipelineContext(
            correlation_id=f"corr-batch-{i}",
            event_id=f"evt-batch-{i}",
            flow={"id": i},
            features={"pkt_mean_to_max": 0.5},
            model_name="model_d2_coral",
            status="completed",
        )
        store.persist_pipeline_run(ctx)

    runs = store.list_runs(limit=10)
    assert len(runs) == 3
    corr_ids = [r["correlation_id"] for r in runs]
    assert "corr-batch-0" in corr_ids
    assert "corr-batch-1" in corr_ids
    assert "corr-batch-2" in corr_ids
