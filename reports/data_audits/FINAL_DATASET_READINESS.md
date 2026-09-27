# FINAL DATASET READINESS

| Dataset | Domain | Modality | Complete? | Labels | Timestamp | Intended Use |
|---------|--------|----------|-----------|--------|-----------|--------------|
| CICIoT2023 | IoT | Network | PARTIAL | Yes | No | In-domain training & testing |
| NF-ToN-IoT | IoT/IIoT | Network Flow | VERIFIED COMPLETE | Yes | Yes | In-domain training & testing |
| TON_IoT | IoT/IIoT | Network/Telemetry | PARTIAL | Yes | Yes | In-domain training & testing |
| HAI | OT/ICS | Process/Industrial | PARTIAL | Yes | Yes | In-domain training & testing |

## Experiment Support Capabilities

Based *only* on the verifiable, un-corrupted files successfully acquired:

**A. In-domain training**
- Supported: YES (for all 4 datasets). 
- *Constraint*: Training size will be artificially small for CICIoT2023, TON_IoT Network, and HAI due to incomplete mirrors causing the acquisition of only partial data splits.

**B. In-domain testing**
- Supported: YES (for all 4 datasets).
- *Constraint*: Testing must be conducted via rigorous cross-validation on the limited available data chunks.

**C. Cross-domain testing**
- Supported: YES (with caveats). 
- Models trained on CICIoT2023 network flow derivations can theoretically evaluate against TON_IoT / NF-ToN-IoT network data. Due to limited splits, the statistical confidence of the generalizability will be constrained.

**D. Domain-generalization experiments**
- Supported: YES.
- *Constraint*: Using the limited splits restricts the diversity of conditions available to learn generalizable features.

**E. Temporal analysis**
- Supported: YES (for TON_IoT Telemetry and HAI).
- Both maintain sequential, high-precision timestamp features allowing chronological modeling of attacks over process variables.

**F. Multi-modal analysis**
- Supported: **BLOCKED**.
- `SecurityEvents_GroundTruth_datasets` for TON_IoT remains **NOT AVAILABLE FROM VERIFIED PUBLIC SOURCE**. Attempting multi-modal fusion of separate sensor/network logs without the ground truth event labels directly compromises scientific integrity. No synthetic or reconstructed ground truth was fabricated.
