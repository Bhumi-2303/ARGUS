# ARGUS REP-01: Artifact & Feature Audit Report

**Target Domain**: IEC 60870-5-104 SCADA Telemetry ($D_3$)  
**Objective**: Audit available protocol, temporal, flow, and contextual features across raw captures and pre-extracted CSVs.  
**Audit Date**: August 26, 2026  

---

## 1. Inventory of Available Data Sources
1. **Flow Telemetry Files (`*_Flow.csv`)**: 84 column header format generated via CICFlowMeter, containing aggregate bidirectional flow durations, packet length statistics, inter-arrival time moments, and TCP flag summaries.
2. **Protocol Layer Telemetry Files (`*iec104_network_flow_leayer.csv`)**: 119 column format containing application-layer IEC 60870-5-104 APDU and ASDU telemetry, Cause of Transmission (COT) indicators (1–13, 20), Type IDs (Monitor, Control, Parameter, File Transfer), and I/S/U frame structures.
3. **Temporal Markers**: `flow start timestamp` (e.g. `04/26/2020 14:00:27`), Flow IAT moments, Idle/Active duration windows.

---

## 2. Representation Ladder Definitions (R0 to R4)
- **R0 (Compact ARGUS-4)**: 4 harmonized statistical features (`flow_duration`, `total_packets`, `total_bytes`, `byte_rate`). Lowest common denominator across IoT ($D_1$) and SCADA ($D_3$).
- **R1 (Native SCADA Flow-70)**: 70 statistical flow features from CICFlowMeter without non-feature identifiers.
- **R2 (Native + Protocol-Aware-79)**: 70 flow features + ASDU Type ID indicators + COT indicators + IOA counts + normalized APDU frame ratios (`i_msg_ratio`, `s_msg_ratio`, `u_msg_ratio`, `cmd_to_mon_ratio`).
- **R3 (Native + Temporal Context-74)**: 70 flow features + causal rolling packet rate, rolling byte rate, burstiness index, and inter-arrival change ratios.
- **R4 (Full Combined Representation-83)**: Full union of Native Flow (R1), Protocol-Aware (R2), and Temporal Context (R3) features.

---

## 3. Strict Zero-Leakage Protocol
All added features satisfy the causal visibility constraint: features depend only on current and past traffic events; no future lookaheads or target-test distribution statistics are permitted.
