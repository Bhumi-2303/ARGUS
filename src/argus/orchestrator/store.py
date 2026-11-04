"""Durable storage for ARGUS pipeline runs, traces, and decision approval states."""

import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import structlog
from sqlalchemy import select, desc

from argus.database.engine import get_session
from argus.database.models import (
    PipelineRunModel,
    PipelineStageTraceModel,
    DecisionApprovalTokenModel,
    IncidentModel,
)
from argus.schemas.incident import Incident, IncidentStatus, ApprovalStatus

logger = structlog.get_logger("argus.orchestrator.store")


class PipelineRunStore:
    """Persists pipeline runs, stage traces, and approval tokens in SQLite/Postgres."""

    def __init__(self, db_url: Optional[str] = None):
        self._db_url = db_url

    def persist_pipeline_run(self, ctx: Any) -> Optional[str]:
        """Persist a completed or failed PipelineContext and its per-stage traces to the database.

        If DecisionSupport requires human-in-the-loop approval, generates a secure
        approval token, links it to an Incident, and returns the token string.
        """
        session = get_session(self._db_url)
        approval_token: Optional[str] = None

        try:
            # 1. Check for Decision Support approval requirement
            decision = getattr(ctx, "decision", None)
            approval_required = False
            approver_role = "incident_commander"
            action_summary = "Autonomous mitigation execution"

            if decision:
                approval_required = getattr(decision, "approval_required", False)
                if hasattr(decision, "reasoning"):
                    action_summary = decision.reasoning
                if hasattr(decision, "execution_plan"):
                    action_summary = f"{action_summary} | Plan: {decision.execution_plan}"

            linked_incident_id: Optional[str] = None

            # 2. If approval is required or high threat detected, ensure an Incident is created
            threat = getattr(ctx, "threat", None)
            threat_level = getattr(threat, "threat_level", None)
            threat_str = threat_level.value if hasattr(threat_level, "value") else str(threat_level or "low")

            if approval_required or threat_str in ("high", "critical"):
                linked_incident_id = f"inc-{ctx.correlation_id}"
                now = datetime.now(timezone.utc)
                token_expiry = now + timedelta(hours=24)

                if approval_required:
                    approval_token = f"appr-{secrets.token_urlsafe(16)}"

                # Check if incident already exists in database
                existing_inc = session.execute(
                    select(IncidentModel).where(IncidentModel.incident_id == linked_incident_id)
                ).scalar_one_or_none()

                if existing_inc is None:
                    incident_record = IncidentModel(
                        incident_id=linked_incident_id,
                        title=f"Security Alert: {threat_str.upper()} Threat Detected ({ctx.model_name})",
                        description=action_summary,
                        severity=threat_str if threat_str in ("low", "medium", "high", "critical") else "high",
                        status="detected",
                        source="argus_pipeline",
                        source_event_id=ctx.event_id,
                        correlation_id=ctx.correlation_id,
                        confidence=getattr(threat, "confidence", None),
                        threat_level=threat_str,
                        risk_score=getattr(getattr(ctx, "risk", None), "risk_score", None),
                        approval_required=approval_required,
                        approval_status="pending" if approval_required else "not_required",
                        approval_token=approval_token,
                        approval_token_expires_at=token_expiry if approval_required else None,
                        created_at=now,
                        updated_at=now,
                    )
                    session.add(incident_record)

                # Persist approval token if required
                if approval_token:
                    token_record = DecisionApprovalTokenModel(
                        token=approval_token,
                        incident_id=linked_incident_id,
                        event_id=ctx.event_id,
                        correlation_id=ctx.correlation_id,
                        action_summary=action_summary,
                        approver_role=approver_role,
                        status="PENDING",
                        created_at=now,
                        expires_at=token_expiry,
                    )
                    session.add(token_record)

            # 3. Serialize stage results
            threat_json = None
            if threat and hasattr(threat, "model_dump"):
                threat_json = json.dumps(threat.model_dump(), default=str)

            explain_json = None
            explain = getattr(ctx, "explanation", None)
            if explain and hasattr(explain, "model_dump"):
                explain_json = json.dumps(explain.model_dump(), default=str)

            knowledge_json = None
            knowledge = getattr(ctx, "knowledge", None)
            if knowledge and hasattr(knowledge, "model_dump"):
                knowledge_json = json.dumps(knowledge.model_dump(), default=str)

            risk_json = None
            risk = getattr(ctx, "risk", None)
            if risk and hasattr(risk, "model_dump"):
                risk_json = json.dumps(risk.model_dump(), default=str)

            decision_json = None
            if decision and hasattr(decision, "model_dump"):
                decision_json = json.dumps(decision.model_dump(), default=str)

            # 4. Upsert PipelineRunModel
            existing_run = session.execute(
                select(PipelineRunModel).where(PipelineRunModel.correlation_id == ctx.correlation_id)
            ).scalar_one_or_none()

            if existing_run is None:
                run_record = PipelineRunModel(
                    correlation_id=ctx.correlation_id,
                    event_id=ctx.event_id,
                    model_name=ctx.model_name,
                    status=getattr(ctx, "status", "completed"),
                    flow_input_json=json.dumps(getattr(ctx, "flow", {}), default=str),
                    extracted_features_json=json.dumps(getattr(ctx, "features", {}), default=str),
                    threat_result_json=threat_json,
                    explainability_result_json=explain_json,
                    knowledge_result_json=knowledge_json,
                    risk_result_json=risk_json,
                    decision_result_json=decision_json,
                    incident_id=linked_incident_id,
                    error=getattr(ctx, "error", None),
                    started_at=getattr(ctx, "started_at", datetime.now(timezone.utc)),
                    completed_at=getattr(ctx, "completed_at", datetime.now(timezone.utc)),
                )
                session.add(run_record)
            else:
                existing_run.status = getattr(ctx, "status", "completed")
                existing_run.extracted_features_json = json.dumps(getattr(ctx, "features", {}), default=str)
                existing_run.threat_result_json = threat_json
                existing_run.explainability_result_json = explain_json
                existing_run.knowledge_result_json = knowledge_json
                existing_run.risk_result_json = risk_json
                existing_run.decision_result_json = decision_json
                existing_run.completed_at = getattr(ctx, "completed_at", datetime.now(timezone.utc))
                existing_run.error = getattr(ctx, "error", None)

            # 5. Persist per-stage traces
            for trace_evt in getattr(ctx, "trace", []):
                trace_record = PipelineStageTraceModel(
                    correlation_id=ctx.correlation_id,
                    agent_name=getattr(trace_evt, "agent", "UNKNOWN"),
                    status=getattr(trace_evt, "status", "SUCCESS"),
                    started_at=getattr(trace_evt, "started_at", None),
                    completed_at=getattr(trace_evt, "completed_at", None),
                    duration_ms=getattr(trace_evt, "duration", None),
                    input_summary=getattr(trace_evt, "input_summary", None),
                    output_summary=getattr(trace_evt, "output_summary", None),
                    error=getattr(trace_evt, "error", None),
                    model_version=getattr(trace_evt, "model_version", None),
                )
                session.add(trace_record)

            session.commit()
            logger.info(
                "pipeline_run_persisted",
                correlation_id=ctx.correlation_id,
                approval_required=approval_required,
                token=approval_token,
            )

        except Exception as e:
            session.rollback()
            logger.error("pipeline_run_persist_failed", correlation_id=ctx.correlation_id, error=str(e))
        finally:
            session.close()

        return approval_token

    def get_pipeline_run(self, correlation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a pipeline run and its detailed stage execution traces."""
        session = get_session(self._db_url)
        try:
            run = session.execute(
                select(PipelineRunModel).where(PipelineRunModel.correlation_id == correlation_id)
            ).scalar_one_or_none()

            if not run:
                return None

            traces = session.execute(
                select(PipelineStageTraceModel)
                .where(PipelineStageTraceModel.correlation_id == correlation_id)
                .order_by(PipelineStageTraceModel.id.asc())
            ).scalars().all()

            token = session.execute(
                select(DecisionApprovalTokenModel)
                .where(DecisionApprovalTokenModel.correlation_id == correlation_id)
            ).scalar_one_or_none()

            return {
                "correlation_id": run.correlation_id,
                "event_id": run.event_id,
                "model_name": run.model_name,
                "status": run.status,
                "error": run.error,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "incident_id": run.incident_id,
                "approval_token": token.token if token else None,
                "approval_status": token.status if token else None,
                "traces": [
                    {
                        "agent": t.agent_name,
                        "status": t.status,
                        "duration_ms": t.duration_ms,
                        "input_summary": t.input_summary,
                        "output_summary": t.output_summary,
                        "error": t.error,
                    }
                    for t in traces
                ],
            }
        finally:
            session.close()

    def list_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent pipeline executions."""
        session = get_session(self._db_url)
        try:
            records = session.execute(
                select(PipelineRunModel)
                .order_by(desc(PipelineRunModel.started_at))
                .limit(limit)
            ).scalars().all()

            return [
                {
                    "correlation_id": r.correlation_id,
                    "event_id": r.event_id,
                    "model_name": r.model_name,
                    "status": r.status,
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                    "incident_id": r.incident_id,
                }
                for r in records
            ]
        finally:
            session.close()


# Global pipeline run store singleton
pipeline_store = PipelineRunStore()
