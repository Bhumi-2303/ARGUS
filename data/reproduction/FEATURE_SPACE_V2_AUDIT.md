# FEATURE-SPACE AND DOMAIN-ADAPTATION AUDIT (V2)

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
