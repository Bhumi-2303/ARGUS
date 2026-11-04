"""Unit and integration tests for Human-in-the-Loop (HITL) approval/rejection endpoints, RBAC, and auditing."""

import secrets
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from argus.api.main import app
from argus.auth.models import UserPrincipal
from argus.auth.rbac import get_current_user
from argus.database.engine import get_session
from argus.database.models import IncidentModel, DecisionApprovalTokenModel
from argus.schemas.incident import Incident, ApprovalStatus
from argus.services.incident_service import incident_service

client = TestClient(app)


@pytest.fixture
def test_approval_token():
    """Seed an incident with a decision approval token in database."""
    session = get_session()
    now = datetime.now(timezone.utc)
    token_str = f"appr-{secrets.token_urlsafe(16)}"
    incident_id = f"inc-{secrets.token_hex(6)}"

    try:
        inc = IncidentModel(
            incident_id=incident_id,
            title="High Severity Anomaly: Substation Breaker Trip",
            description="Immediate isolation recommended",
            severity="critical",
            status="detected",
            source="argus_pipeline",
            approval_required=True,
            approval_status="pending",
            approval_token=token_str,
            approval_token_expires_at=now + timedelta(hours=24),
            created_at=now,
            updated_at=now,
        )
        session.add(inc)

        token_record = DecisionApprovalTokenModel(
            token=token_str,
            incident_id=incident_id,
            action_summary="Trip feeder breaker and quarantine VLAN 12",
            approver_role="incident_commander",
            status="PENDING",
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )
        session.add(token_record)
        session.commit()
    finally:
        session.close()

    return {"token": token_str, "incident_id": incident_id}


def test_hitl_decision_token_approval_success(test_approval_token):
    """Authorized operator with 'approve:response' successfully approves decision token."""
    commander = UserPrincipal(
        sub="operator-lead-01",
        issuer="argus-test",
        roles=["operator"],
        permissions={"read:incidents", "approve:response"},
    )
    app.dependency_overrides[get_current_user] = lambda: commander

    try:
        resp = client.post(
            "/api/v1/incidents/decision/approve",
            json={
                "token": test_approval_token["token"],
                "reason": "Confirmed emergency trip protocol with transmission dispatch.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["status"] == "APPROVED"
        assert data["token"] == test_approval_token["token"]
        assert data["resolved_by"] == "operator-lead-01"

        # Verify token in database
        session = get_session()
        try:
            tok = session.query(DecisionApprovalTokenModel).filter_by(token=test_approval_token["token"]).first()
            assert tok.status == "APPROVED"
            assert tok.resolved_by == "operator-lead-01"
            assert "Confirmed emergency trip" in tok.resolution_reason

            inc = session.query(IncidentModel).filter_by(incident_id=test_approval_token["incident_id"]).first()
            assert inc.approval_status == "approved"
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_hitl_decision_token_rejection_success(test_approval_token):
    """Authorized operator rejects decision token with logged reason."""
    commander = UserPrincipal(
        sub="operator-lead-02",
        issuer="argus-test",
        roles=["operator"],
        permissions={"read:incidents", "approve:response"},
    )
    app.dependency_overrides[get_current_user] = lambda: commander

    try:
        resp = client.post(
            "/api/v1/incidents/decision/reject",
            json={
                "token": test_approval_token["token"],
                "reason": "Scheduled maintenance outage underway on this feeder; trip not authorized.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["status"] == "REJECTED"
        assert data["token"] == test_approval_token["token"]
        assert data["resolved_by"] == "operator-lead-02"

        # Verify token in database
        session = get_session()
        try:
            tok = session.query(DecisionApprovalTokenModel).filter_by(token=test_approval_token["token"]).first()
            assert tok.status == "REJECTED"
            assert tok.resolved_by == "operator-lead-02"
            assert "Scheduled maintenance" in tok.resolution_reason

            inc = session.query(IncidentModel).filter_by(incident_id=test_approval_token["incident_id"]).first()
            assert inc.approval_status == "rejected"
        finally:
            session.close()
    finally:
        app.dependency_overrides.clear()


def test_hitl_incident_direct_reject_endpoint():
    """Direct incident reject endpoint marks incident closed."""
    operator = UserPrincipal(
        sub="operator-lead-03",
        issuer="argus-test",
        roles=["operator"],
        permissions={"read:incidents", "approve:response"},
    )
    app.dependency_overrides[get_current_user] = lambda: operator

    try:
        inc = incident_service.create_incident(Incident(
            title="Transient Voltage Dip",
            description="Power quality event",
            severity="low",
            affected_assets=["Bus-1"],
            event_id="EV-PQ-01",
            asset="Bus-1",
            approval_required=True,
            approval_status=ApprovalStatus.PENDING,
        ))

        resp = client.post(
            f"/api/v1/incidents/{inc.incident_id}/reject",
            json={"reason": "Transient power factor sag from transformer tap change."},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["approval_status"] == "REJECTED"
        assert data["status"] == "CLOSED"
    finally:
        app.dependency_overrides.clear()


def test_hitl_decision_pending_list_endpoint(test_approval_token):
    """Pending tokens list returns active tokens waiting for human operator review."""
    viewer = UserPrincipal(
        sub="viewer-001",
        issuer="argus-test",
        roles=["viewer"],
        permissions={"read:incidents"},
    )
    app.dependency_overrides[get_current_user] = lambda: viewer

    try:
        resp = client.get("/api/v1/incidents/decision/pending")
        assert resp.status_code == 200
        tokens = resp.json()["data"]
        matching = [t for t in tokens if t["token"] == test_approval_token["token"]]
        assert len(matching) == 1
        assert matching[0]["incident_id"] == test_approval_token["incident_id"]
        assert "Trip feeder breaker" in matching[0]["action_summary"]
    finally:
        app.dependency_overrides.clear()


def test_hitl_decision_rbac_enforcement(test_approval_token):
    """User without 'approve:response' cannot approve or reject decision tokens (403 Forbidden)."""
    unauthorized = UserPrincipal(
        sub="viewer-unauthorized",
        issuer="argus-test",
        roles=["viewer"],
        permissions={"read:incidents"},  # Lacks approve:response
    )
    app.dependency_overrides[get_current_user] = lambda: unauthorized

    try:
        # Attempt approve
        approve_resp = client.post(
            "/api/v1/incidents/decision/approve",
            json={"token": test_approval_token["token"], "reason": "No auth attempt"},
        )
        assert approve_resp.status_code == 403
        assert "approve:response" in approve_resp.json()["detail"]

        # Attempt reject
        reject_resp = client.post(
            "/api/v1/incidents/decision/reject",
            json={"token": test_approval_token["token"], "reason": "No auth attempt"},
        )
        assert reject_resp.status_code == 403
        assert "approve:response" in reject_resp.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_hitl_decision_invalid_token_returns_404():
    """Submitting a non-existent token returns 404 Not Found."""
    operator = UserPrincipal(
        sub="operator-01",
        issuer="argus-test",
        roles=["operator"],
        permissions={"read:incidents", "approve:response"},
    )
    app.dependency_overrides[get_current_user] = lambda: operator

    try:
        resp = client.post(
            "/api/v1/incidents/decision/approve",
            json={"token": "appr-nonexistent-token-123", "reason": "Testing 404"},
        )
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()
