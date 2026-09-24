# Experimental Schema Recommendation

Based on the rigorous compatibility and leakage audits, the following experimental setups are recommended for ARGUS.

## 1. Shared Network Feature Set (Domain Generalization)
**Participating Datasets:** `CICIoT2023`, `NF-ToN-IoT`, `BoT-IoT`.
**Incompatible:** `TON_IoT_Network` (Too much L7 categorical data), `HAI` (OT telemetry).

### A. Core Shared Features (MUST INCLUDE)
*   **Protocol:** (Transform to standard mappings: TCP, UDP, ICMP, Other)
*   **Flow Duration:** (Milliseconds/Seconds)
*   **Total Packets:** (`IN_PKTS` + `OUT_PKTS`)
*   **Total Bytes:** (`IN_BYTES` + `OUT_BYTES`)
*   **Directional Metrics:** Source Packets, Destination Packets, Source Bytes, Destination Bytes.

### B. Features Excluded from DG (LEAKAGE)
*   IP Addresses (Source/Dest)
*   MAC Addresses
*   Ports (Raw numbers)
*   Sequential IDs

## 2. Industrial Validation Experiment (Domain-Specific)
**Participating Dataset:** `HAI_21.03`
**Rationale:** HAI is strictly numerical OT/ICS telemetry. It shares zero features with the IT network datasets. It must be utilized in a separate validation experiment testing the anomaly-detection agent's ability to monitor physical process state (P1, P2, P3, P4 variables).

## 3. Multimodal Readiness (TON_IoT)
*   **Readiness:** **BLOCKED**
*   **Rationale:** The `SecurityEvents_GroundTruth_datasets` required to perfectly align the telemetry events with the Zeek network events is offline. Multimodal alignment using just timestamps is impossible because the Zeek network CSVs lack absolute timestamps.

---
## Final Summary & Next Steps
*   **Compatible Groups:** (CICIoT2023, NF-ToN-IoT, BoT-IoT) form a perfect triad for cross-dataset Domain Generalization on aggregate NetFlow statistics.
*   **Incompatible Groups:** HAI and TON_IoT Zeek data cannot merge into the NetFlow triad.
*   **Recommended Source Domains:** Train on `CICIoT2023` + `NF-ToN-IoT`.
*   **Recommended Unseen Target Domain:** Evaluate strictly on `BoT-IoT`.
*   **Exact Next Step:** Write a PySpark or Pandas pipeline (e.g., `preprocess_network_dg.py`) that explicitly extracts and normalizes the **Core Shared Features** across the three compatible datasets, dropping all identified leakage columns.
