"""Incident service implementation with database persistence, state transitions, and HITL approvals."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import structlog
from sqlalchemy import select, update, desc

from argus.schemas.incident import Incident, IncidentStatus, ApprovalStatus, TimelineEvent
from argus.database.engine import get_session
from argus.database.models import IncidentModel, IncidentTimelineModel, DecisionApprovalTokenModel

logger = structlog.get_logger("argus.services.incidents")


class InvalidTransitionError(Exception):
    """Raised when an incident status transition violates the state machine."""

    pass


class IncidentService:
    """Manages incident lifecycle, state transitions, and HITL approvals."""

    def __init__(self, db_url: Optional[str] = None):
        self._db_url = db_url
        self._cache: Dict[str, Incident] = {}

    def _save_to_db(self, incident: Incident) -> None:
        """Persist or update an incident in the database."""
        session = get_session(self._db_url)
        try:
            record = session.execute(
                select(IncidentModel).where(IncidentModel.incident_id == incident.incident_id)
            ).scalar_one_or_none()

            actions_json = json.dumps(incident.decision, default=str) if incident.decision else None

            if record is None:
                record = IncidentModel(
                    incident_id=incident.incident_id,
                    title=f"Incident {incident.incident_id} [{incident.severity.upper()}]",
                    description=incident.detector_summary or incident.knowledge_summary or "",
                    severity=incident.severity.lower() if incident.severity else "medium",
                    status=incident.status.value,
                    source="argus_pipeline",
                    source_event_id=incident.event_id,
                    confidence=None,
                    threat_level=incident.severity.lower() if incident.severity else None,
                    risk_score=incident.risk_score,
                    approval_required=incident.approval_required,
                    approval_status=incident.approval_status.value.lower(),
                    approved_by=incident.approved_by,
                    approved_at=incident.approved_at,
                    approval_reason=incident.approval_reason,
                    approval_token=incident.approval_token,
                    approval_token_expires_at=incident.approval_token_expires_at,
                    recommended_actions_json=actions_json,
                    created_at=incident.created_at,
                    updated_at=incident.updated_at,
                )
                session.add(record)
            else:
                record.status = incident.status.value
                record.severity = incident.severity.lower() if incident.severity else "medium"
                record.risk_score = incident.risk_score
                record.approval_required = incident.approval_required
                record.approval_status = incident.approval_status.value.lower()
                record.approved_by = incident.approved_by
                record.approved_at = incident.approved_at
                record.approval_reason = incident.approval_reason
                record.updated_at = incident.updated_at

            # Add latest timeline event to database
            if incident.timeline:
                latest_event = incident.timeline[-1]
                tl_record = IncidentTimelineModel(
                    incident_id=incident.incident_id,
                    event_type=latest_event.action,
                    description=latest_event.details,
                    actor=latest_event.actor,
                    timestamp=latest_event.timestamp,
                )
                session.add(tl_record)

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                "incident_db_persist_failed", incident_id=incident.incident_id, error=str(e)
            )
        finally:
            session.close()

    def create_incident(self, incident: Incident) -> Incident:
        """Create a new incident, recording creation event and persisting to DB."""
        if incident.incident_id in self._cache:
            raise ValueError(f"Incident {incident.incident_id} already exists")

        incident.add_timeline_event("incident_created", "Incident created from detection event.")
        self._cache[incident.incident_id] = incident
        self._save_to_db(incident)
        logger.info(
            "incident_created", incident_id=incident.incident_id, severity=incident.severity
        )
        return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Fetch incident from in-memory cache or query from the database."""
        if incident_id in self._cache:
            return self._cache[incident_id]

        session = get_session(self._db_url)
        try:
            record = session.execute(
                select(IncidentModel).where(IncidentModel.incident_id == incident_id)
            ).scalar_one_or_none()

            if not record:
                return None

            timeline_records = (
                session.execute(
                    select(IncidentTimelineModel)
                    .where(IncidentTimelineModel.incident_id == incident_id)
                    .order_by(IncidentTimelineModel.timestamp.asc())
                )
                .scalars()
                .all()
            )

            timeline = [
                TimelineEvent(
                    event_id=str(tl.id),
                    timestamp=tl.timestamp,
                    action=tl.event_type,
                    actor=tl.actor,
                    details=tl.description,
                )
                for tl in timeline_records
            ]

            status_enum = (
                IncidentStatus(record.status.upper())
                if hasattr(IncidentStatus, record.status.upper())
                else IncidentStatus.DETECTED
            )
            approval_enum = (
                ApprovalStatus(record.approval_status.upper())
                if hasattr(ApprovalStatus, record.approval_status.upper())
                else ApprovalStatus.NOT_REQUIRED
            )

            decision_dict = None
            if record.recommended_actions_json:
                try:
                    decision_dict = json.loads(record.recommended_actions_json)
                except Exception:
                    pass

            incident = Incident(
                incident_id=record.incident_id,
                event_id=record.source_event_id or "evt-unknown",
                created_at=record.created_at,
                updated_at=record.updated_at,
                status=status_enum,
                severity=record.severity.upper() if record.severity else "MEDIUM",
                asset="SCADA_GRID_NODE_1",
                risk_score=record.risk_score,
                decision=decision_dict,
                approval_required=record.approval_required,
                approval_status=approval_enum,
                approval_token=record.approval_token,
                approval_token_expires_at=record.approval_token_expires_at,
                approved_by=record.approved_by,
                approved_at=record.approved_at,
                approval_reason=record.approval_reason,
                timeline=timeline,
            )
            self._cache[incident.incident_id] = incident
            return incident
        except Exception as e:
            logger.error("get_incident_db_failed", incident_id=incident_id, error=str(e))
            return None
        finally:
            session.close()

    def list_incidents(self, status: Optional[IncidentStatus] = None) -> List[Incident]:
        """List all incidents, merging in-memory records and database store."""
        session = get_session(self._db_url)
        try:
            query = select(IncidentModel.incident_id).order_by(desc(IncidentModel.created_at))
            if status:
                query = query.where(IncidentModel.status == status.value)
            ids = session.execute(query).scalars().all()

            for inc_id in ids:
                if inc_id not in self._cache:
                    self.get_incident(inc_id)
        except Exception as e:
            logger.error("list_incidents_db_failed", error=str(e))
        finally:
            session.close()

        results = list(self._cache.values())
        if status:
            results = [inc for inc in results if inc.status == status]
        return results

    def update_status(
        self, incident_id: str, new_status: IncidentStatus, actor: str = "system"
    ) -> Incident:
        """Transition incident status according to authoritative state machine."""
        incident = self.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        current = incident.status

        # Valid explicit transitions
        valid_transitions = {
            IncidentStatus.DETECTED: [IncidentStatus.TRIAGED, IncidentStatus.CLOSED],
            IncidentStatus.TRIAGED: [
                IncidentStatus.INVESTIGATING,
                IncidentStatus.ESCALATED,
                IncidentStatus.CLOSED,
            ],
            IncidentStatus.INVESTIGATING: [
                IncidentStatus.CONTAINED,
                IncidentStatus.RESOLVED,
                IncidentStatus.ESCALATED,
            ],
            IncidentStatus.ESCALATED: [
                IncidentStatus.INVESTIGATING,
                IncidentStatus.CONTAINED,
                IncidentStatus.CLOSED,
            ],
            IncidentStatus.CONTAINED: [IncidentStatus.RESOLVED],
            IncidentStatus.RESOLVED: [IncidentStatus.CLOSED],
            IncidentStatus.CLOSED: [],
        }

        if new_status not in valid_transitions.get(current, []):
            raise InvalidTransitionError(f"Cannot transition from {current} to {new_status}")

        incident.status = new_status
        incident.add_timeline_event(
            "status_changed",
            f"Status changed from {current.value} to {new_status.value}",
            actor=actor,
        )
        self._save_to_db(incident)
        return incident

    def approve_incident(
        self, incident_id: str, approver: str, reason: str, token: Optional[str] = None
    ) -> Incident:
        """Grant human approval for an incident response mitigation."""
        incident = self.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if not incident.approval_required:
            raise ValueError("Incident does not require approval")

        if token and incident.approval_token and incident.approval_token != token:
            raise ValueError("Invalid approval token for this incident")

        now = datetime.now(timezone.utc)
        incident.approval_status = ApprovalStatus.APPROVED
        incident.approved_by = approver
        incident.approved_at = now
        incident.approval_reason = reason

        incident.add_timeline_event(
            "approval_granted", f"Action approved by {approver}: {reason}", actor=approver
        )
        self._save_to_db(incident)

        # Update DecisionApprovalTokenModel in DB if present
        session = get_session(self._db_url)
        try:
            session.execute(
                update(DecisionApprovalTokenModel)
                .where(DecisionApprovalTokenModel.incident_id == incident_id)
                .values(
                    status="APPROVED",
                    resolved_at=now,
                    resolved_by=approver,
                    resolution_reason=reason,
                )
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("update_token_approved_failed", error=str(e))
        finally:
            session.close()

        logger.info("incident_approval_granted", incident_id=incident_id, approver=approver)
        return incident

    def reject_incident(
        self, incident_id: str, rejecter: str, reason: str, token: Optional[str] = None
    ) -> Incident:
        """Reject human approval for an incident response mitigation."""
        incident = self.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if not incident.approval_required:
            raise ValueError("Incident does not require approval")

        if token and incident.approval_token and incident.approval_token != token:
            raise ValueError("Invalid approval token for this incident")

        now = datetime.now(timezone.utc)
        incident.approval_status = ApprovalStatus.REJECTED
        incident.approved_by = rejecter
        incident.approved_at = now
        incident.approval_reason = f"REJECTED: {reason}"

        # Transition to CLOSED or CONTAINED upon rejection
        try:
            self.update_status(incident_id, IncidentStatus.CLOSED, actor=rejecter)
        except InvalidTransitionError:
            pass  # Keep current status if direct close is not allowed by state machine

        incident.add_timeline_event(
            "approval_rejected", f"Action rejected by {rejecter}: {reason}", actor=rejecter
        )
        self._save_to_db(incident)

        # Update DecisionApprovalTokenModel in DB if present
        session = get_session(self._db_url)
        try:
            session.execute(
                update(DecisionApprovalTokenModel)
                .where(DecisionApprovalTokenModel.incident_id == incident_id)
                .values(
                    status="REJECTED",
                    resolved_at=now,
                    resolved_by=rejecter,
                    resolution_reason=reason,
                )
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("update_token_rejected_failed", error=str(e))
        finally:
            session.close()

        logger.info("incident_approval_rejected", incident_id=incident_id, rejecter=rejecter)
        return incident

    def resolve_decision_token(
        self, token: str, action: str, actor: str, reason: str
    ) -> Dict[str, Any]:
        """Resolve a decision approval token by token string ('approve' or 'reject')."""
        session = get_session(self._db_url)
        try:
            record = session.execute(
                select(DecisionApprovalTokenModel).where(DecisionApprovalTokenModel.token == token)
            ).scalar_one_or_none()

            if not record:
                raise ValueError(f"Approval token '{token}' not found.")

            now = datetime.now(timezone.utc)
            exp = record.expires_at
            if exp:
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                if exp < now:
                    record.status = "EXPIRED"
                    session.commit()
                    raise ValueError("Approval token has expired.")

            if record.status != "PENDING":
                raise ValueError(f"Approval token already resolved with status '{record.status}'.")

            action_lower = action.lower()
            if action_lower not in ("approve", "reject"):
                raise ValueError(
                    f"Invalid approval action '{action}'. Must be 'approve' or 'reject'."
                )

            new_status = "APPROVED" if action_lower == "approve" else "REJECTED"
            record.status = new_status
            record.resolved_at = now
            record.resolved_by = actor
            record.resolution_reason = reason
            session.commit()

            # If token was linked to an incident, sync incident state
            if record.incident_id:
                if action_lower == "approve":
                    self.approve_incident(
                        record.incident_id, approver=actor, reason=reason, token=token
                    )
                else:
                    self.reject_incident(
                        record.incident_id, rejecter=actor, reason=reason, token=token
                    )

            return {
                "token": token,
                "status": new_status,
                "incident_id": record.incident_id,
                "correlation_id": record.correlation_id,
                "resolved_by": actor,
                "resolved_at": now.isoformat(),
                "reason": reason,
            }
        finally:
            session.close()

    def get_pending_approvals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve list of all pending HITL decision approval tokens."""
        session = get_session(self._db_url)
        try:
            now = datetime.now(timezone.utc)
            records = (
                session.execute(
                    select(DecisionApprovalTokenModel)
                    .where(DecisionApprovalTokenModel.status == "PENDING")
                    .order_by(desc(DecisionApprovalTokenModel.created_at))
                    .limit(limit)
                )
                .scalars()
                .all()
            )

            results = []
            for r in records:
                exp = r.expires_at
                if exp:
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    if exp < now:
                        continue
                results.append(
                    {
                        "token": r.token,
                        "incident_id": r.incident_id,
                        "event_id": r.event_id,
                        "correlation_id": r.correlation_id,
                        "action_summary": r.action_summary,
                        "approver_role": r.approver_role,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                        "expires_at": r.expires_at.isoformat() if r.expires_at else None,
                    }
                )
            return results
        finally:
            session.close()


# Global singleton for production runtime
incident_service = IncidentService()
