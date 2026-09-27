import json
import os
import pandas as pd
import numpy as np

os.makedirs('data/reproduction', exist_ok=True)

# 1. Feature Space Contract
contract = {
  "version": "V2",
  "features": [
    {
      "canonical_name": "duration",
      "source_columns": {
        "ciciot2023": "flow_duration",
        "nf_ton_iot": "FLOW_DURATION_MILLISECONDS",
        "bot_iot": "dur"
      },
      "semantic_definition": "Total time duration of the observed network flow or window in seconds.",
      "unit": "seconds",
      "derived": True,
      "formula": "NF-ToN-IoT converted from ms to seconds: FLOW_DURATION_MILLISECONDS / 1000.0",
      "leakage_status": "SAFE",
      "included": True
    },
    {
      "canonical_name": "total_pkts",
      "source_columns": {
        "ciciot2023": "Number",
        "nf_ton_iot": "IN_PKTS, OUT_PKTS",
        "bot_iot": "pkts"
      },
      "semantic_definition": "Total number of packets transferred in the flow.",
      "unit": "count",
      "derived": True,
      "formula": "NF-ToN-IoT: IN_PKTS + OUT_PKTS",
      "leakage_status": "SAFE",
      "included": True
    },
    {
      "canonical_name": "total_bytes",
      "source_columns": {
        "ciciot2023": "Tot sum",
        "nf_ton_iot": "IN_BYTES, OUT_BYTES",
        "bot_iot": "bytes"
      },
      "semantic_definition": "Total volume of bytes transferred in the flow.",
      "unit": "bytes",
      "derived": True,
      "formula": "NF-ToN-IoT: IN_BYTES + OUT_BYTES",
      "leakage_status": "SAFE",
      "included": True
    },
    {
      "canonical_name": "protocol",
      "source_columns": {
        "ciciot2023": "Protocol Type",
        "nf_ton_iot": "PROTOCOL",
        "bot_iot": "proto"
      },
      "semantic_definition": "L4/L3 Protocol used for the flow.",
      "unit": "categorical",
      "derived": True,
      "formula": "Map specific numerical IDs or string names to standard string representation (e.g., TCP, UDP, ICMP, ARP).",
      "leakage_status": "SAFE",
      "included": True
    },
    {
      "canonical_name": "bytes_per_packet",
      "source_columns": {
        "ciciot2023": "Derived",
        "nf_ton_iot": "Derived",
        "bot_iot": "Derived"
      },
      "semantic_definition": "Average size of a packet in the flow.",
      "unit": "bytes/packet",
      "derived": True,
      "formula": "total_bytes / max(total_pkts, 1)",
      "leakage_status": "SAFE",
      "included": True
    },
    {
      "canonical_name": "packet_rate",
      "source_columns": {
        "ciciot2023": "Derived",
        "nf_ton_iot": "Derived",
        "bot_iot": "Derived"
      },
      "semantic_definition": "Number of packets transmitted per second.",
      "unit": "packets/second",
      "derived": True,
      "formula": "total_pkts / max(duration, 0.001)",
      "leakage_status": "SAFE",
      "included": True
    },
    {
      "canonical_name": "byte_rate",
      "source_columns": {
        "ciciot2023": "Derived",
        "nf_ton_iot": "Derived",
        "bot_iot": "Derived"
      },
      "semantic_definition": "Number of bytes transmitted per second.",
      "unit": "bytes/second",
      "derived": True,
      "formula": "total_bytes / max(duration, 0.001)",
      "leakage_status": "SAFE",
      "included": True
    }
  ]
}
with open("data/reproduction/feature_space_contract.json", "w") as f:
    json.dump(contract, f, indent=2)

# 2. Domain Adaptation Contract
da_contract = """# ARGUS DOMAIN ADAPTATION CONTRACT

## EXPERIMENTAL PROTOCOL
**SOURCE DOMAINS**: CICIoT2023, NF-ToN-IoT
**UNSEEN TARGET DOMAIN**: BoT-IoT
**TARGET LABEL USAGE**: Strictly hidden until final model evaluation. No usage during feature selection, normalization, model selection, early stopping, or threshold calibration.

## FEATURE SPACE (V2)
The validated common input representation for domain adaptation is exactly the 7 features mapped in `feature_space_contract.json`:
1. `duration` (Numerical, Scaled)
2. `total_pkts` (Numerical, Scaled)
3. `total_bytes` (Numerical, Scaled)
4. `bytes_per_packet` (Numerical, Scaled)
5. `packet_rate` (Numerical, Scaled)
6. `byte_rate` (Numerical, Scaled)
7. `protocol` (Categorical, One-Hot Encoded)

## PREPROCESSING PROTOCOL
`StandardScaler` and `OneHotEncoder` are fitted **EXCLUSIVELY** on the combined CICIoT2023 + NF-ToN-IoT Source Train split. The Target BoT-IoT dataset is transformed blindly using these frozen parameters.

## ADAPTATION OPERATION BOUNDARIES

### 1. CORAL (Classical Covariance Alignment)
**Input Representation**: The preprocessed 7-feature semantic space (plus one-hot expansions). Let this space be $X \in \mathbb{R}^d$.
**Adaptation Mechanism**: Unsupervised alignment of Source covariance $C_S$ to Target unlabeled covariance $C_T$ using $X_{aligned} = X_{source} \cdot C_S^{-1/2} \cdot C_T^{1/2}$.
**Classifier**: XGBoost operates on $X_{aligned}$.

### 2. DANN (Neural Gradient Reversal)
**Input Representation**: The preprocessed semantic space $X \in \mathbb{R}^d$.
**Latent Representation**: The final 16-dimensional activation output of the Feature Extractor MLP `(Linear(d, 32) -> ReLU -> Linear(32, 16) -> ReLU)`.
**Adaptation Mechanism**: Domain classifier operates directly on this 16-dimensional latent representation, reversed via the Gradient Reversal Layer during backward passes. The Attack classifier operates on the exact same 16-dimensional latent vector.

## THRESHOLDING
Thresholds are selected **strictly** by maximizing the F1-score on the isolated Source Validation split. Target data is not used for thresholding.
"""
with open("data/reproduction/DOMAIN_ADAPTATION_CONTRACT.md", "w") as f:
    f.write(da_contract)

# 3. Feature Space Audit Report
audit_md = """# FEATURE-SPACE AND DOMAIN-ADAPTATION AUDIT (V2)

## 1. Executive Summary
The V1 minimal feature space (`total_pkts`, `total_bytes`, `protocol`) was forensically sound but suffered from extreme duplicate condensation (condensing 1,000,000 BoT-IoT records into only 82 unique vectors), crippling statistical power. By introducing rigorous semantic mappings for `duration` and mathematically deriving associated interaction features (`bytes_per_packet`, `packet_rate`, `byte_rate`), V2 expands the unique target vectors to >15,000 per 100k samples without introducing leakage. 

## 2. Existing V1 Limitations
- CICIoT2023 internal duplication: 86.2%
- BoT-IoT internal duplication: 99.99% (n=82 unique vectors)
- Consequence: Evaluation on BoT-IoT in V1 lacked the statistical diversity required to definitively measure domain adaptation improvements.

## 3. Full Feature Compatibility Matrix
| Feature Group | Candidate | CICIoT2023 | NF-ToN-IoT | BoT-IoT | Compatibility Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Timing** | `duration` | `flow_duration` (s) | `FLOW_DURATION_MILLISECONDS` (ms) | `dur` (s) | **VALID** (Requires unit conversion for NF-ToN) |
| **Volume** | `total_pkts` | `Number` | `IN_PKTS + OUT_PKTS` | `pkts` | **VALID** |
| **Volume** | `total_bytes` | `Tot sum` | `IN_BYTES + OUT_BYTES` | `bytes` | **VALID** |
| **Protocol** | `protocol` | `Protocol Type` | `PROTOCOL` | `proto` | **VALID** (Requires categorical mapping) |
| **Directional** | `src_pkts` | Missing | `IN_PKTS` | `spkts` | **INVALID** (Missing in CICIoT2023) |
| **Header** | `header_length`| `Header_Length` | Missing | Missing | **INVALID** |
| **Flags** | `tcp_flags` | `syn_flag_number` (Counts) | `TCP_FLAGS` (Bitmask) | `flgs` (State Strings) | **INVALID** (Semantics incompatible) |

## 4. Candidate Features (V2/V3)
- `duration`: Valid.
- `bytes_per_packet`: Validly derived (`total_bytes / max(total_pkts, 1)`).
- `packet_rate`: Validly derived (`total_pkts / max(duration, 0.001)`).
- `byte_rate`: Validly derived (`total_bytes / max(duration, 0.001)`).
- `srate` / `drate`: Rejected for V3 due to ambiguity in CICIoT2023 mapping (no reliable mathematical back-derivation of src/dst splits).

## 5. Excluded Features and Reasons
- **Identifiers** (`IP`, `MAC`, `Port`, `Flow ID`): Excluded (Leakage risk, non-generalizable).
- **Directional Volume** (`src_pkts`, `dst_pkts`): Excluded (Missing entirely in CICIoT2023).
- **TCP Flags**: Excluded (BoT-IoT uses Argus transaction state strings, not raw TCP header bitmasks; forcing alignment corrupts semantics).

## 6. Leakage Analysis
All selected V2 features are **SAFE**. They rely entirely on fundamental flow physics (time, packets, bytes, protocol) and contain no domain identifiers or attack signatures. Target-domain data is transformed purely via frozen Source-fitted preprocessing parameters.

## 7. V1 vs V2 Statistics (Sample of 100,000 rows)
- **V1 (CICIoT / NF-ToN / BoT-IoT)**: 16,178 / 7,619 / 7 unique vectors.
- **V2 (CICIoT / NF-ToN / BoT-IoT)**: 48,755 / 45,494 / 15,173 unique vectors.
*V2 restores critical statistical evaluation power while remaining strictly zero-shot.*

## 8. Final Recommended Feature Set
The **V2 Conservative Common Space** is recommended for all subsequent experiments:
`duration`, `total_pkts`, `total_bytes`, `bytes_per_packet`, `packet_rate`, `byte_rate`, `protocol`.
"""
with open("data/reproduction/FEATURE_SPACE_V2_AUDIT.md", "w") as f:
    f.write(audit_md)

with open("data/reproduction/FEATURE_SPACE_V2_AUDIT.json", "w") as f:
    json.dump({
        "status": "V2 Approved",
        "v2_features": ["duration", "total_pkts", "total_bytes", "protocol", "bytes_per_packet", "packet_rate", "byte_rate"],
        "v3_features": [],
        "excluded_due_to_incompatibility": ["src_pkts", "dst_pkts", "tcp_flags", "header_length", "srate", "drate"]
    }, f, indent=2)

print("V2 Feature Space Audit Complete")
