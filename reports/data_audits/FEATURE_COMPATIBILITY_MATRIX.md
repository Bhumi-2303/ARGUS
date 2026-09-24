# Feature Compatibility Matrix

## Overview
This audit evaluates the semantic alignment of features across five ARGUS datasets: `CICIoT2023`, `NF-ToN-IoT`, `BoT-IoT`, `TON_IoT_Network`, and `HAI_21.03`.

## 1. Network Datasets (CICIoT, NF-ToN-IoT, BoT-IoT)
These three datasets provide NetFlow-style aggregate statistics, making them the primary candidates for a shared network feature space.

| Core Feature Concept | CICIoT2023 | NF-ToN-IoT | BoT-IoT | Compatibility |
|----------------------|------------|------------|---------|---------------|
| Protocol | `ProtocolType` (mixed) | `PROTOCOL` / `L7_PROTO` | `proto` | **B (Transform)** |
| Flow Duration | `flow_duration` | `FLOW_DURATION_MILLISECONDS` | `dur` | **A (Direct)** |
| Total Packets | Derived | `IN_PKTS` + `OUT_PKTS` | `pkts` | **B (Transform)** |
| Source Packets | `Tot Fwd Pkts` | `IN_PKTS` | `spkts` | **A (Direct)** |
| Dest Packets | `Tot Bwd Pkts` | `OUT_PKTS` | `dpkts` | **A (Direct)** |
| Source Bytes | `TotLen Fwd Pkts` | `IN_BYTES` | `sbytes` | **A (Direct)** |
| Dest Bytes | `TotLen Bwd Pkts` | `OUT_BYTES` | `dbytes` | **A (Direct)** |
| TCP Flags | `FIN Flag Cnt`, `SYN`, etc. | `TCP_FLAGS` (bitmask) | `flgs` (string) | **B (Transform)** |

## 2. TON_IoT_Network (Zeek Format)
This dataset provides Application-layer (L7) Zeek metadata rather than pure NetFlow numerics.
*   **Unique Features:** `dns_query`, `ssl_version`, `http_uri`, `conn_state`.
*   **Verdict:** **F (Incompatible)** with the core numerical NetFlow schema without discarding 80% of its columns. Must be modeled separately or merged only on basic `src_bytes`/`dst_bytes`/`duration`.

## 3. HAI (Industrial Telemetry)
*   **Unique Features:** 79 sensor/actuator readings (`P1_B2004`, `P2_AutoGO`, etc.).
*   **Verdict:** **F (Incompatible)** with network data. HAI has zero network features and tracks physical OT variables.

