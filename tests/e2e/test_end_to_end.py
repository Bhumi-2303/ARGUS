import pytest
from tests.fixtures.events import FIXTURES
from argus.schemas.incident import Incident, IncidentStatus
from argus.services.incident_service import incident_service

def test_e2e_security_event_to_incident():
    # 1. Security Event
    event = FIXTURES["high_criticality_attack"]()
    
    # 2. ARGUS Processing (Mocked for E2E)
    # The event is processed by detector, risk, knowledge, explainability, policy, decision
    # ...
    
    # 3. Final Decision -> Incident Creation
    incident_data = Incident(
        event_id=event.event_id,
        severity=event.risk.severity if event.risk else "low",
        asset=event.asset,
        asset_criticality=event.asset_criticality,
        risk_score=event.risk.risk_score if event.risk else 0.0,
        detector_summary="Anomaly detected with high confidence",
        knowledge_summary="Matched MITRE T0889",
    )
    
    created = incident_service.create_incident(incident_data)
    
    assert created.incident_id is not None
    assert created.status == IncidentStatus.DETECTED
    assert created.severity == "critical"
    assert created.asset == "SCADA-MTU-01"
    
    # 4. Status Transition
    incident_service.update_status(created.incident_id, IncidentStatus.TRIAGED, "test_operator")
    updated = incident_service.update_status(created.incident_id, IncidentStatus.INVESTIGATING, "test_operator")
    assert updated.status == IncidentStatus.INVESTIGATING
    assert len(updated.timeline) == 3 # 1 for creation, 2 for updates
