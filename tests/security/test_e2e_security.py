import pytest
from fastapi.testclient import TestClient
from argus.api.main import app
from argus.security.auth import create_access_token
from argus.schemas.incident import Incident
from unittest.mock import patch

client = TestClient(app)

def test_end_to_end_security_scenario():
    # 1. User authenticates (mocked via JWT creation)
    # 2. JWT is validated via get_current_user
    # 3. Identity established: responder1, INCIDENT_RESPONDER
    token_responder = create_access_token("responder1", "INCIDENT_RESPONDER")
    
    # Unauthorized identity: viewer1
    token_viewer = create_access_token("viewer1", "VIEWER")

    # 4. We simulate detection event and risk -> These are internal pipeline steps
    # Usually handled by the orchestrator. For this test, we skip straight to approval
    # where the backend requires INCIDENT_RESPONDER.

    # 10. Unauthorized user receives 403
    response_viewer = client.post(
        "/api/v1/incidents/INC-1234/approve",
        headers={"Authorization": f"Bearer {token_viewer}"},
        json={"reason": "Approve this"}
    )
    assert response_viewer.status_code == 403

    # 11. Authorized responder approves
    with patch("argus.security.sink.AuditSink.dispatch") as mock_dispatch:
        # Note: the incident service requires a real incident in the database to approve.
        # Since we're in e2e without a real DB setup, it might return 404.
        # But the 403 authorization boundary is what we care about!
        # Let's mock incident_service.approve_incident so we can see the 200 OK.
        with patch("argus.api.routers.incidents.incident_service.approve_incident") as mock_approve:
            mock_approve.return_value = Incident(
                title="test", description="desc", severity="low", affected_assets=[], 
                event_id="E1", asset="A1", incident_id="INC-1234"
            )
            
            response_responder = client.post(
                "/api/v1/incidents/INC-1234/approve",
                headers={"Authorization": f"Bearer {token_responder}"},
                json={"reason": "Approve this"}
            )
            
            assert response_responder.status_code == 200
            
            # 12. RESPONSE_APPROVED audit event is generated
            assert mock_dispatch.call_count > 0
            audit_events = [call.args[0] for call in mock_dispatch.call_args_list]
            approved_event = next((e for e in audit_events if e.action == "RESPONSE_APPROVED"), None)
            assert approved_event is not None
            assert approved_event.actor_id == "responder1"
            assert approved_event.resource_id == "INC-1234"
