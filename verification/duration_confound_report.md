# ARGUS Dataset Confound & Duration Audit Report

**Target Domain**: IEC 60870-5-104 SCADA Telemetry (Domain 3 / D3)  
**Dataset Analyzed**: $N = 47,364$ Protocol Layer Flows (118 custom layer CSV files)  
**Audit Purpose**: Test whether benign/attack classification performance is confounded by capture duration, packet volume, or flow length artifacts.  
**Audit Date**: August 21, 2026  

---

## 1. Executive Summary & Confound Declaration

> [!WARNING]
> **Dataset Confound Declaration**: The 47,364-flow IEC 60870-5-104 protocol-layer dataset contains a **severe structural capture volume / packet-count confound**. A trivial classifier trained on ONLY 3 non-protocol features (`flow duration`, `total flow packets`, `flow packets APDU total length`) achieves **$\text{ROC-AUC} = 1.000000$** on a strictly held-out file test set ($0\%$ file overlap). Benign sessions in this dataset consist of long background polling runs, while attack captures consist of short injection bursts. This capture artifact must be disclosed as a dataset limitation in any publication.

> [!NOTE]
> **Pure Protocol Semantic Recovery (Matched Subsample)**: When cumulative volume/packet counts are stripped and the model is evaluated using **ONLY pure protocol ratio features** (`i_msg_ratio`, `cmd_to_mon_ratio`, `cot=7`, `APDU length mean`) on a **volume-matched subsample**, the protocol-aware model still achieves **$\text{ROC-AUC} = 0.999965$** ($99.35\%$ Recall, $100.00\%$ Precision, $0.00\%$ FPR). This proves that genuine application-layer threat semantics (`i_msg_ratio`, COT activation confirm, APDU length) exist independent of the volume confound.

---

## 2. Trivial Non-Protocol Baseline Experiment

To test for dataset volume confounding, a LightGBM model was trained using **ONLY 3 non-protocol-semantic features**:
1. `flow duration` (flow time span)
2. `total flow packets` (total packet count)
3. `flow packets APDU total length` (total byte volume)

### 2.1 Performance Under Strict Grouped Split ($0\%$ File Overlap)

| Model / Feature Set | Features Used | ROC-AUC (Test) | Precision | Recall | FPR | $F_1$ Score | MCC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Trivial Baseline (Volume Only)** | **3** | **$1.000000$** | **$99.98\%$** | **$100.00\%$** | **$0.02\%$** | **$0.9999$** | **$0.9998$** |
| **Protocol-Aware Full** | 44 | $1.000000$ | $99.98\%$ | $100.00\%$ | $0.02\%$ | $0.9999$ | $0.9998$ |

### 2.2 Trivial Baseline Confusion Matrix (Held-Out Test Set, $N = 10,484$)
```
                Predicted Benign    Predicted Attack
True Benign          4,745                 1         (FPR: 0.02%, Precision: 99.98%)
True Attack              0             5,738         (Recall: 100.00%)
```

### 2.3 Feature Importance (Trivial Baseline)
- `total flow packets` (**Gain: $467,050.70$**) — Primary decision boundary.
- `flow packets APDU total length` (Gain: $23,236.10$).
- `flow duration` (Gain: $1,026.73$).

---

## 3. Feature Cross-Tabulation & Purity Analysis

### 3.1 `flow total IEC104_S_Message packets`

| S-Message Packet Count ($S$) | Benign Flows (NORMAL, $y=0$) | Attack Flows ($y=1$) | Total Flows | % Attack Purity |
| :--- | ---: | ---: | ---: | ---: |
| $S \le 1.0$ | 52 | 28,274 | 28,326 | **$99.82\%$ Attack** |
| $1.0 < S \le 2.0$ | 1,176 | 0 | 1,176 | **$100.0\%$ Benign** |
| $2.0 < S \le 5.0$ | 12,036 | 0 | 12,036 | **$100.0\%$ Benign** |
| $S > 5.0$ | 4,552 | 1,274 | 5,826 | **$78.14\%$ Benign** |

**Explanation**: S-frames acknowledge received I-frames. Attack flows in this dataset consist of short 1-packet injection bursts that terminate before multi-packet S-frame acknowledgements are generated ($S \le 1$), whereas benign background polling flows run continuously and exchange multiple S-frames ($S \ge 2$).

### 3.2 `flow packet APDU length mean`

| Mean APDU Length (Bytes) | Benign Flows (NORMAL, $y=0$) | Attack Flows ($y=1$) | Total Flows | % Class Purity |
| :--- | ---: | ---: | ---: | ---: |
| $4.0 \le \text{APDU} \le 6.22$ | 9,464 | 73 | 9,537 | **$99.23\%$ Benign** |
| $6.22 < \text{APDU} \le 6.80$ | 5,318 | 4,102 | 9,420 | $56.45\%$ Benign |
| $6.80 < \text{APDU} \le 7.62$ | 2,758 | 10,890 | 13,648 | **$79.79\%$ Attack** |
| $7.62 < \text{APDU} \le 8.40$ | 274 | 5,150 | 5,424 | **$94.95\%$ Attack** |
| $\text{APDU} > 8.40$ | 2 | 9,333 | 9,335 | **$99.98\%$ Attack** |

**Explanation**: Benign background polling messages (e.g. S-ACKs and cyclic status polls) have small APDU lengths ($4 \dots 6$ bytes). Attack flows (e.g. command injections, setpoint writes, file transfer exploits) contain larger ASDU payload structures ($\text{APDU} > 8.4$ bytes).

---

## 4. Volume-Matched Subsample Experiment

To eliminate the packet volume confound, we constructed a **packet-count matched subsample** ($N = 3,766$ flows, $1,883$ benign / $1,883$ attack) where benign and attack flows have matching packet-count quantile distributions.

We then evaluated **ONLY pure protocol ratio/semantic features** (excluding all cumulative volume/packet counts: `i_msg_ratio`, `s_msg_ratio`, `u_msg_ratio`, `cmd_to_mon_ratio`, `seq_to_single_ioa_ratio`, `APDU length mean/std`, `COT` dummy variables):

### 4.1 Results on Packet-Count Matched Subsample (0% File Overlap)

| Metric | Full Dataset (Confounded Baseline) | Matched Subsample (Protocol Ratios Only) |
| :--- | :---: | :---: |
| **ROC-AUC (Test)** | $1.000000$ | **$0.999965$** |
| **Recall (Sensitivity)** | $100.00\%$ | **$99.35\%$** |
| **Precision** | $99.98\%$ | **$100.00\%$** |
| **False Positive Rate (FPR)** | $0.02\%$ | **$0.00\%$** |
| **$F_1$ Score** | $0.9999$ | **$0.9967$** |
| **MCC** | $0.9998$ | **$0.9950$** |

### 4.2 Matched Subsample Confusion Matrix (Held-Out Files Test Set)
```
                Predicted Benign    Predicted Attack
True Benign            563                 0         (FPR: 0.00%, Precision: 100.00%)
True Attack              2               304         (Recall: 99.35%)
```

### 4.3 Top Protocol Drivers on Matched Subsample (LightGBM Gain)
1. **`i_msg_ratio`** (**Gain: $38,080.21$**) — Ratio of Information ASDUs to total IEC104 frames.
2. **`cot=7`** (**Gain: $696.78$**) — Cause of Transmission = Confirmation of Activation.
3. **`cot=3`** (**Gain: $663.71$**) — Cause of Transmission = Spontaneous.
4. **`flow packet APDU length mean`** (**Gain: $444.90$**).
5. **`cmd_to_mon_ratio`** (**Gain: $372.51$**) — Ratio of control/parameter commands to monitoring frames.

---

## 5. Paper Limitations Disclosure Statement

> *"Disclosure of Dataset Confound: Evaluation on the 47,364-flow IEC 60870-5-104 protocol dataset revealed that benign and attack sessions exhibit distinct packet-volume distributions due to capture duration artifacts (trivial 3-feature flow-volume baseline $\text{ROC-AUC} = 1.000000$). However, when controlling for this volume confound via a packet-count matched subsample and evaluating strictly non-cumulative protocol ratio features (`i_msg_ratio`, `cmd_to_mon_ratio`, Cause of Transmission `COT=7/3`, APDU payload length), protocol-aware classification retains near-perfect discriminative performance ($\text{ROC-AUC} = 0.999965$, $99.35\%$ Recall, $100.00\%$ Precision, $0.00\%$ FPR) under a strict 0% file-overlap grouped split."*
