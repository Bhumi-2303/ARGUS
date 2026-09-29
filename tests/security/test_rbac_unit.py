"""Tests for fine-grained Role-Based Access Control (RBAC) and incident approval auditing."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends, Request

from argus.api.main import app
from argus.auth.models import UserPrincipal
from argus.auth.rbac import get_current_user, require_permission
from argus.services.incident_service import incident_service
from argus.schemas.incident import Incident, ApprovalStatus

client = TestClient(app)


def test_rbac_rejects_unauthorized_user(monkeypatch):
    """User without 'run:prediction' permission is rejected with 403 Forbidden."""
    # Principal lacking 'run:prediction'
    viewer_user = UserPrincipal(
        sub="viewer-001",
        issuer="argus-test",
        roles=["viewer"],
        permissions={"read:models", "read:domains"}
    )
    app.dependency_overrides[get_current_user] = lambda: viewer_user

    try:
        payload = {
            "features": {
                "pkt_mean_to_max": 0.5,
                "tcp_flag_density": 1.0,
                "log_pkt_mean": 4.0,
                "log_pkt_max": 4.5
            },
            "model_name": "model_d2_coral"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 403
        assert "Missing required permission 'run:prediction'" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_rbac_allows_authorized_user(monkeypatch):
    """User with 'run:prediction' permission succeeds."""
    operator_user = UserPrincipal(
        sub="operator-001",
        issuer="argus-test",
        roles=["operator"],
        permissions={"run:prediction"}
    )
    app.dependency_overrides[get_current_user] = lambda: operator_user

    try:
        payload = {
            "features": {
                "pkt_mean_to_max": 0.5,
                "tcp_flag_density": 1.0,
                "log_pkt_mean": 4.0,
                "log_pkt_max": 4.5
            },
            "model_name": "model_d2_coral"
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200
        assert "probability" in response.json()
    finally:
        app.dependency_overrides.clear()


def test_incident_approval_requires_explicit_permission():
    """Incident approval requires 'approve:response' and rejects unauthorized roles."""
    analyst_user = UserPrincipal(
        sub="analyst-001",
        issuer="argus-test",
        roles=["analyst"],
        permissions={"read:incidents", "write:incidents"}  # Lacks approve:response
    )
    app.dependency_overrides[get_current_user] = lambda: analyst_user

    try:
        # Create test incident
        inc = incident_service.create_incident(Incident(
            title="SCADA Grid Overcurrent",
            description="High risk anomaly",
            severity="critical",
            affected_assets=["Substation-4"],
            event_id="EV-999",
            asset="Breaker-A",
            approval_required=True,
            approval_status=ApprovalStatus.PENDING
        ))

        # Attempt approval
        response = client.post(
            f"/api/v1/incidents/{inc.incident_id}/approve",
            json={"reason": "Approved mitigation by security lead"}
        )
        assert response.status_code == 403
        assert "Missing required permission 'approve:response'" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_incident_approval_succeeds_with_verified_principal():
    """Authorized approval succeeds and records caller's actual identity."""
    security_lead = UserPrincipal(
        sub="lead-engineer-42",
        issuer="argus-test",
        roles=["operator"],
        permissions={"read:incidents", "approve:response"}
    )
    app.dependency_overrides[get_current_user] = lambda: security_lead

    try:
        inc = incident_service.create_incident(Incident(
            title="SCADA Grid Overcurrent",
            description="High risk anomaly",
            severity="critical",
            affected_assets=["Substation-4"],
            event_id="EV-1000",
            asset="Breaker-B",
            approval_required=True,
            approval_status=ApprovalStatus.PENDING
        ))

        response = client.post(
            f"/api/v1/incidents/{inc.incident_id}/approve",
            json={"reason": "Verified benign substation switching sequence."}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["approval_status"] == "APPROVED"
        assert data["approved_by"] == "lead-engineer-42"
        assert data["approval_reason"] == "Verified benign substation switching sequence."
    finally:
        app.dependency_overrides.clear()
