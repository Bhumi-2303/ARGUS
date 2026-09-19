# Canonical Event Schema

The ARGUS backend utilizes a standardized, versioned event contract (`ArgusEvent`) to guarantee structural integrity as an event passes through various stages of the pipeline.

## Event Structure

The `ArgusEvent` acts as an envelope. It holds core identifiers and optional sub-documents (Contracts) representing the outputs of independent architectural stages. 

```python
class ArgusEvent(BaseModel):
    schema_version: str = "1.0"
    event_id: str
    timestamp: datetime
    source: str
    domain: str
    asset: str
    asset_criticality: Optional[int]
    telemetry_reference: Optional[str]
    provenance: Optional[Provenance]
    
    # Stage Contracts
    detector: Optional[DetectorContract]
    risk: Optional[RiskContract]
    knowledge: Optional[KnowledgeContract]
    explanation: Optional[ExplainabilityContract]
    review: Optional[ReviewContract]
    policy: Optional[PolicyContract]
    decision: Optional[DecisionContract]
    response: Optional[ResponseContract]
    audit: Optional[AuditContract]
```

## Field Definitions

### Core Fields
*   `schema_version` (str): Defines the schema contract version.
*   `event_id` (str): Unique UUID for tracing the event across microservices.
*   `timestamp` (datetime): UTC creation time of the event.
*   `source` (str): The origin of the telemetry (e.g., specific sensor or log aggregator).
*   `domain` (str): Operating domain (e.g., IT, OT, SCADA).
*   `asset` (str): Target asset identifier (e.g., PLC-01).

## Agent Contracts

Agents operate on explicit contracts using Pydantic. A stage is populated dynamically as the event traverses the pipeline.

### 1. Detector Contract
**Output from:** Threat Analysis Agent
*   `is_anomaly` (bool): `True` if detection triggered.
*   `confidence` (float 0.0-1.0): Model confidence.
*   `threat_category` (Optional[str]): Classification label.
*   `scores` (Dict[str, float]): Raw model scores.

### 2. Risk Contract
**Output from:** Risk Prediction Agent
*   `risk_score` (float 0-100): Calculated risk.
*   `severity` (str): Categorical representation.
*   `asset_priority` (int): Tier of the asset.
*   `impact_estimation` (str): Human-readable impact analysis.

### 3. Knowledge Contract
**Output from:** Knowledge Context Agent
*   `mitre_techniques` (List[str]): MITRE mapping.
*   `cve_ids` (List[str]): Associated CVEs.
*   `cisa_advisories` (List[str]): CISA mapping.
*   `recommended_mitigations` (List[str]): Sourced mitigation logic.
*   `confidence` (float 0.0-1.0): Synthesis confidence.

### 4. Explainability Contract
**Output from:** Explainability Engine
*   `shap_values` (Dict[str, float]): Feature attributions.
*   `top_features` (List[str]): High-impact features.
*   `human_readable_explanation` (str): Generated text explanation.

### 5. Policy Contract
**Output from:** Policy Engine
*   `policy_id` (str): Executed policy reference.
*   `action_allowed` (bool): Output rule evaluation.
*   `violations` (List[str]): Rejected rules.

### 6. Decision Contract
**Output from:** Decision Support Agent
*   `recommended_actions` (List[str]): Action set.
*   `priority` (int): SLA response priority.
*   `urgency` (str): Time-sensitivity.
*   `approval_required` (bool): Flag for HITL gate.

### 7. Response Contract
**Output from:** Response Engine
*   `action_taken` (str): Log of action.
*   `success` (bool): Execution success.
*   `execution_details` (str): Stack trace or execution logs.

## Versioning Policy

*   **Minor updates**: Adding new `Optional` fields or new stage contracts will not increment the major version.
*   **Major updates**: Modifying a required field, changing a type signature, or altering validation bounds increments the `schema_version`. Pydantic's `extra="forbid"` ensures older agents reject incompatible schema additions safely.

## Example
```json
{
  "schema_version": "1.0",
  "event_id": "evt-uuid-1234",
  "timestamp": "2025-01-01T12:00:00Z",
  "source": "suricata-sensor-01",
  "domain": "OT",
  "asset": "SCADA-HMI-02",
  "detector": {
    "is_anomaly": true,
    "confidence": 0.94,
    "scores": {"xgb_score": 0.92, "lgbm_score": 0.95}
  },
  "risk": {
    "risk_score": 85.5,
    "severity": "high",
    "asset_priority": 1,
    "impact_estimation": "Loss of view on HMI"
  }
}
```
