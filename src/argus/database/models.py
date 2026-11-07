"""SQLAlchemy models for ARGUS durable core storage.

Postgres-compatible schema supporting SQLite via aiosqlite/sqlite3 for local
runtime and PostgreSQL for enterprise scale.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class IncidentModel(Base):
    """Persisted security incident record."""

    __tablename__ = "incidents"

    incident_id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(32), nullable=False, default="medium")
    status = Column(String(32), nullable=False, default="detected")
    source = Column(String(128), nullable=False, default="argus_pipeline")
    source_event_id = Column(String(64), nullable=True, index=True)
    correlation_id = Column(String(64), nullable=True, index=True)
    affected_assets_json = Column(Text, nullable=True)
    attack_type = Column(String(128), nullable=True)
    confidence = Column(Float, nullable=True)
    threat_level = Column(String(32), nullable=True)
    risk_score = Column(Float, nullable=True)
    approval_required = Column(Boolean, default=False, nullable=False)
    approval_status = Column(String(32), default="pending", nullable=False)
    approved_by = Column(String(128), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_reason = Column(Text, nullable=True)
    approval_token = Column(String(255), unique=True, nullable=True, index=True)
    approval_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    recommended_actions_json = Column(Text, nullable=True)
    execution_plan = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    timeline = relationship(
        "IncidentTimelineModel",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentTimelineModel.timestamp",
    )


class IncidentTimelineModel(Base):
    """Immutable audit trail of actions and status changes on an incident."""

    __tablename__ = "incident_timeline"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(
        String(64),
        ForeignKey("incidents.incident_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)
    actor = Column(String(128), default="system", nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    metadata_json = Column(Text, nullable=True)

    incident = relationship("IncidentModel", back_populates="timeline")


class PipelineRunModel(Base):
    """Record of an end-to-end 6-agent pipeline execution."""

    __tablename__ = "pipeline_runs"

    correlation_id = Column(String(64), primary_key=True)
    event_id = Column(String(64), unique=True, nullable=False, index=True)
    model_name = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="running")
    flow_input_json = Column(Text, nullable=False)
    extracted_features_json = Column(Text, nullable=True)
    threat_result_json = Column(Text, nullable=True)
    explainability_result_json = Column(Text, nullable=True)
    knowledge_result_json = Column(Text, nullable=True)
    risk_result_json = Column(Text, nullable=True)
    decision_result_json = Column(Text, nullable=True)
    incident_id = Column(String(64), nullable=True, index=True)
    error = Column(Text, nullable=True)
    started_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    stage_traces = relationship(
        "PipelineStageTraceModel",
        back_populates="pipeline_run",
        cascade="all, delete-orphan",
        order_by="PipelineStageTraceModel.id",
    )


class PipelineStageTraceModel(Base):
    """Per-stage trace metrics (agent, duration, inputs/outputs, error) of a pipeline run."""

    __tablename__ = "pipeline_stage_traces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    correlation_id = Column(
        String(64),
        ForeignKey("pipeline_runs.correlation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_name = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Float, nullable=True)
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    model_version = Column(String(64), nullable=True)

    pipeline_run = relationship("PipelineRunModel", back_populates="stage_traces")


class DecisionApprovalTokenModel(Base):
    """Human-in-the-loop (HITL) approval token generated by Decision Support Agent."""

    __tablename__ = "decision_approval_tokens"

    token = Column(String(255), primary_key=True)
    incident_id = Column(String(64), nullable=True, index=True)
    event_id = Column(String(64), nullable=True, index=True)
    correlation_id = Column(String(64), nullable=True, index=True)
    action_summary = Column(Text, nullable=False)
    approver_role = Column(String(64), nullable=True)
    status = Column(
        String(32), default="PENDING", nullable=False, index=True
    )  # PENDING, APPROVED, REJECTED, EXPIRED
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String(128), nullable=True)
    resolution_reason = Column(Text, nullable=True)


class BusOutboxModel(Base):
    """Durable transactional outbox for the message bus to survive process restarts."""

    __tablename__ = "bus_outbox"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False, index=True)
    topic = Column(String(255), nullable=False, index=True)
    payload_json = Column(Text, nullable=False)
    headers_json = Column(Text, nullable=True)
    correlation_id = Column(String(64), nullable=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status = Column(
        String(32), default="pending", nullable=False, index=True
    )  # pending, delivered, failed, dead_letter
    retry_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)


class BusDeadLetterModel(Base):
    """Dead-letter queue (DLQ) store for unroutable or repeatedly failed event messages."""

    __tablename__ = "bus_dead_letter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    payload_json = Column(Text, nullable=False)
    error_reason = Column(Text, nullable=False)
    failed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    retry_count = Column(Integer, default=0, nullable=False)
