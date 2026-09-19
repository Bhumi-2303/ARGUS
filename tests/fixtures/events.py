from datetime import datetime, timezone
import uuid
from argus.schemas.event import ArgusEvent, DetectorContract, RiskContract, KnowledgeContract, ExplainabilityContract, PolicyContract

def get_base_event() -> ArgusEvent:
    return ArgusEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        source="SCADA-MTU-01",
        domain="OT",
        asset="SCADA-MTU-01",
        asset_criticality=5
    )

def fixture_low_criticality_benign() -> ArgusEvent:
    event = get_base_event()
    event.asset_criticality = 1
    event.detector = DetectorContract(is_anomaly=False, confidence=0.99, scores={"raw": 0.01})
    return event

def fixture_low_criticality_false_positive() -> ArgusEvent:
    event = get_base_event()
    event.asset_criticality = 1
    event.detector = DetectorContract(is_anomaly=True, confidence=0.55, threat_category="uncertain", scores={"raw": 0.6})
    event.risk = RiskContract(risk_score=20.0, severity="low", asset_priority=1, impact_estimation="Minimal impact")
    return event

def fixture_high_criticality_attack() -> ArgusEvent:
    event = get_base_event()
    event.asset_criticality = 5
    event.detector = DetectorContract(is_anomaly=True, confidence=0.98, threat_category="injection", scores={"raw": 0.99})
    event.risk = RiskContract(risk_score=95.0, severity="critical", asset_priority=5, impact_estimation="System compromise")
    event.knowledge = KnowledgeContract(mitre_techniques=["T0889"], confidence=0.9)
    event.explanation = ExplainabilityContract(human_readable_explanation="High confidence attack")
    return event

def fixture_high_criticality_uncertain() -> ArgusEvent:
    event = get_base_event()
    event.asset_criticality = 5
    event.detector = DetectorContract(is_anomaly=True, confidence=0.51, threat_category="unknown", scores={"raw": 0.51})
    return event

def fixture_llm_unavailable() -> ArgusEvent:
    event = get_base_event()
    event.asset_criticality = 3
    event.detector = DetectorContract(is_anomaly=True, confidence=0.85, scores={"raw": 0.85})
    # LLM failures affect explanation and knowledge synthesis
    return event

def fixture_knowledge_unavailable() -> ArgusEvent:
    event = get_base_event()
    event.asset_criticality = 4
    event.detector = DetectorContract(is_anomaly=True, confidence=0.9, scores={"raw": 0.9})
    # Knowledge contract explicitly omitted/fails
    return event

def fixture_policy_failure() -> ArgusEvent:
    event = get_base_event()
    event.asset_criticality = 5
    event.detector = DetectorContract(is_anomaly=True, confidence=0.95, scores={"raw": 0.95})
    event.policy = PolicyContract(policy_id="P-001", action_allowed=False, violations=["Action violates safety constraint"])
    return event

FIXTURES = {
    "low_criticality_benign": fixture_low_criticality_benign,
    "low_criticality_false_positive": fixture_low_criticality_false_positive,
    "high_criticality_attack": fixture_high_criticality_attack,
    "high_criticality_uncertain": fixture_high_criticality_uncertain,
    "llm_unavailable": fixture_llm_unavailable,
    "knowledge_unavailable": fixture_knowledge_unavailable,
    "policy_failure": fixture_policy_failure
}
