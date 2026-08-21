# ARGUS Protocol-Aware IEC 60870-5-104 Feature Recovery & Detection Report

**Target Domain**: IEC 60870-5-104 SCADA Telemetry (Domain 3 / D3)  
**Model Artifacts**:  
- `phase3_results/models/model_d3_protocol_aware.txt` (`model_d3_protocol_aware` — Protocol ASDU/APDU Features Only)  
- `phase3_results/models/model_d3_protocol_combined.txt` (`model_d3_protocol_combined` — Protocol ASDU/APDU + Transport Flow Features)  
**Dataset**: $N = 47,364$ Protocol Layer Telemetry Flows (118 extracted layer CSVs, $80\% / 20\%$ Stratified Train/Test Split)  
**Audit Date**: August 21, 2026  

---

## 1. Executive Summary

Reintroducing **protocol-aware IEC 60870-5-104 ASDU and APDU features** recovers near-perfect threat detection performance on the SCADA target domain, increasing test ROC-AUC from **$0.4860$** (4-feature harmonized model) and **$0.6744$** (73-feature native flow model) to **$0.999996$** (Protocol-Aware Only) and **$0.999999$** (Combined).

At an optimal threshold of $\theta^* = 0.92$, the protocol-aware classifier achieves **$100\%$ Recall** ($5,910 / 5,910$ attack flows detected) at a **False Positive Rate of $0.08\%$** ($3 / 3,563$ false alarms), yielding an $F_1$ score of **$0.9997$** and MCC of **$0.9993$**.

---

## 2. Data Provenance & Availability

- **PCAP Availability**: Raw `.pcap` / `.pcapng` files are **not present** in the workspace ($N = 0$).
- **Pre-parsed Protocol Data**: The dataset repository contained **118 pre-extracted protocol layer CSV files** (`data/IEC104/extracted_csvs/*_network_flow_leayer.csv`), totaling $47,364$ flows.
- **Data Engineering**: Features were extracted directly from existing pre-parsed layer CSV files without requiring raw PCAP re-parsing. Engineered features include:
  - **ASDU Type ID Categories**: Process/System info in Monitor & Control directions, Parameter, File Transfer.
  - **Cause of Transmission (COT)**: Dummy indicators for COT 1 through 13, and COT 20.
  - **IOA Structure**: Single IOA vs. Sequential IOA packet counts and engineered ratio `seq_to_single_ioa_ratio`.
  - **APDU Frame Types**: Total counts and ratios (`i_msg_ratio`, `s_msg_ratio`, `u_msg_ratio`) for I-format (Information), S-format (Supervisory), and U-format (Unnumbered) frames.
  - **Directional Command Ratios**: `cmd_to_mon_ratio` (ratio of control/parameter frames to monitoring frames).
  - **APDU Payload Lengths**: Min, max, mean, std, and total length statistics for flow APDUs.

---

## 3. Comparative Performance Across Feature Representations

| Representation / Model | Features Used | ROC-AUC (Test) | Precision | Recall | FPR | $F_1$ Score | MCC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Harmonized Model (`model_d2_coral`, $\theta=0.50$)** | 4 | $0.4860$ | $22.88\%$ | $94.55\%$ | $92.23\%$ | $0.368$ | $-0.046$ |
| **E5 Fused Model ($\theta=0.50$)** | 4 | $0.5017$ | $24.23\%$ | $96.17\%$ | $87.15\%$ | $0.387$ | $0.121$ |
| **Native Flow Model (`model_d3_native`, $\theta=0.50$)** | 73 | $0.6744$ | $28.11\%$ | $96.31\%$ | $71.36\%$ | $0.435$ | $0.247$ |
| **Protocol-Aware Only (`model_d3_protocol_aware`, $\theta^*=0.92$)** | **44** | **$0.999996$** | **$99.95\%$** | **$100.00\%$** | **$0.08\%$** | **$0.9997$** | **$0.9993$** |
| **Full Combined Model (`model_d3_protocol_combined`, $\theta^*=0.99$)** | **97** | **$0.999999$** | **$99.98\%$** | **$100.00\%$** | **$0.03\%$** | **$0.9999$** | **$0.9998$** |

---

## 4. Confusion Matrices (Held-Out Test Set, $N = 9,473$)

### 4.1 Protocol-Aware ASDU/APDU Only (`model_d3_protocol_aware`, $\theta^*=0.92$)
```
                Predicted Benign    Predicted Attack
True Benign          3,560                 3         (FPR: 0.08%, Precision: 99.95%)
True Attack              0             5,910         (Recall: 100.00%)
```

### 4.2 Full Combined Protocol + Flow Model (`model_d3_protocol_combined`, $\theta^*=0.99$)
```
                Predicted Benign    Predicted Attack
True Benign          3,562                 1         (FPR: 0.03%, Precision: 99.98%)
True Attack              0             5,910         (Recall: 100.00%)
```

---

## 5. Top Protocol Feature Importance Drivers (LightGBM Gain)

1. `flow total IEC104_U_Message packets` (**Gain: $524,559.85$**) — Unnumbered Control Format (TESTFR/STOPDT/STARTDT) message count. Attack scenarios flood or manipulate U-format control frames.
2. `s_msg_ratio` (**Gain: $1,422.64$**) — Ratio of Supervisory acknowledgement messages to total IEC104 traffic.
3. `flow total IEC104_I_Message_SingleIOA packets` (**Gain: $910.96$**) — Single IOA Information object message count.
4. `flow packet APDU length mean` (**Gain: $907.11$**) — Mean APDU payload length.
5. `bw total IEC104_U_Message packets` (**Gain: $615.63$**) — Backward U-message count.
6. `fw packets APDU total length` (**Gain: $328.29$**) — Forward APDU total length.
7. `cmd_to_mon_ratio` / `flow down/up ratio` (**Gain: $100.44$**) — Command vs. monitoring directional ratio.

---

## 6. Research & Paper Implications

1. **Root Cause Confirmation**: The failure of `model_d2_coral` ($\text{ROC-AUC} = 0.486$) was not due to model underfitting or threshold error, but because **generic packet statistical features (mean packet size, TCP flag density) discard the essential protocol semantics of industrial control protocols**.
2. **Protocol Semantics Are Decisive**: IEC 60870-5-104 attacks operate at the ASDU/APDU layer (spurious commands, sequence desynchronization, STARTDT/STOPDT U-frame manipulation). Capturing these application-layer fields elevates detection capability from **$0.4860$ to $0.999996$**.
3. **Harmonization Trade-off**: Cross-domain feature harmonization across heterogeneous datasets (e.g. CICIoT, NF-ToN, IEC104) forces reduction to lowest-common-denominator statistical features, stripping domain-specific protocol fields that carry the primary threat signal in SCADA networks.
