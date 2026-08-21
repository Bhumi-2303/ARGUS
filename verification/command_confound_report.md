# ARGUS Legitimate vs. Malicious Command ASDU Audit Report

**Target Domain**: IEC 60870-5-104 SCADA Telemetry (Domain 3 / D3)  
**Dataset Analyzed**: $N = 47,364$ Protocol Layer Flows (and $N = 42,989$ Command-Containing Flows)  
**Audit Purpose**: Verify whether benign flows contain legitimate command-type ASDUs (`C_` types, `COT=6` Activation, `COT=7` Confirmation), and evaluate classification performance when distinguishing **Legitimate Commands vs. Malicious Commands**.  
**Audit Date**: August 21, 2026  

---

## 1. Executive Summary & Core Audit Answers

1. **Existence of Legitimate Commands**:
   - **Confirmed**: The dataset contains **$15,376$ benign-labeled flows ($86.30\%$ of all benign telemetry)** that include command-type ASDUs or activation COT codes (`COT=6` Activation, `COT=7` Activation Confirmation).
   - Legitimate command traffic includes general interrogation commands (`C_IC_NA_1`), single commands (`C_SC_NA_1`), and select/execute sequences (`C_SE_NA_1`) issued by authorized SCADA master stations (`qtester`).

2. **Legitimate vs. Malicious Command Classification Experiment**:
   - When the dataset is restricted to **ONLY flows containing command ASDUs or activation COTs** ($N = 42,989$ flows: $15,376$ legitimate command flows vs. $27,613$ malicious command flows) and evaluated under a strict **0% file-overlap grouped split**:
   - **Test ROC-AUC**: **$1.000000$**
   - **Test Confusion Matrix ($\theta=0.50$, $N = 9,540$ test flows)**: $\text{TN} = 4,094$, $\text{FP} = 0$, $\text{FN} = 0$, $\text{TP} = 5,446$ ($\text{Recall} = 100.00\%$, $\text{Precision} = 100.00\%$, $\text{FPR} = 0.00\%$, $\text{MCC} = 1.0000$).

3. **Conclusion**:
   - Command presence (`cmd_to_mon_ratio`, `cot=7`, `i_msg_ratio`) is **NOT** a trivial binary artifact of attack vs. non-attack sessions.
   - The classifier successfully discriminates **legitimate SCADA control commands** from **malicious command injections and DoS bursts** with zero false alarms under strict file-grouped holdout splits.

---

## 2. Command ASDU and Activation COT Scan Breakdown

Across all $47,364$ protocol layer flows in the dataset:

| Feature / ASDU Category | Benign Flows ($y=0$, $N=17,816$) | Attack Flows ($y=1$, $N=29,548$) | Total Flows |
| :--- | ---: | ---: | ---: |
| **Flows with ANY Command ASDU or COT=6/7** | **$15,376$ ($86.30\%$)** | **$27,613$ ($93.45\%$)** | **$42,989$ ($90.76\%$)** |
| Process Control Commands (`type_id_process_control > 0`) | $4,458$ ($25.02\%$) | $8,818$ ($29.84\%$) | $13,276$ |
| System Control Commands (`type_id_system_control > 0`) | $12,630$ ($70.89\%$) | $19,713$ ($66.72\%$) | $32,343$ |
| Parameter Control Commands | $0$ | $0$ | $0$ |
| File Transfer ASDUs | $0$ | $0$ | $0$ |
| Activation COT (`cot=6 > 0`) | $6,652$ ($37.34\%$) | $27,137$ ($91.84\%$) | $33,789$ |
| Activation Confirmation COT (`cot=7 > 0`) | $15,376$ ($86.30\%$) | $27,613$ ($93.45\%$) | $42,989$ |

---

## 3. Legitimate vs. Malicious Command Performance (0% File Overlap)

Restricting the dataset exclusively to command-containing flows ($N = 42,989$ flows across 118 files):

### 3.1 Test Metrics (Held-Out Files Test Set, 24 Files, $N = 9,540$ Flows)

| Metric | Full Dataset (All Flows) | Command-Only Subset (Legitimate vs. Malicious Commands) |
| :--- | :---: | :---: |
| **Total Test Flows** | $10,484$ | **$9,540$** |
| **ROC-AUC (Test)** | $1.000000$ | **$1.000000$** |
| **Precision** | $99.98\%$ | **$100.00\%$** |
| **Recall (Sensitivity)** | $100.00\%$ | **$100.00\%$** |
| **False Positive Rate (FPR)** | $0.02\%$ | **$0.00\%$** |
| **$F_1$ Score** | $0.9999$ | **$1.0000$** |
| **MCC** | $0.9998$ | **$1.0000$** |

### 3.2 Command-Only Confusion Matrix ($\theta=0.50$)
```
                Predicted Legitimate    Predicted Malicious
Legitimate Cmd         4,094                     0         (FPR: 0.00%, Precision: 100.00%)
Malicious Cmd              0                 5,446         (Recall: 100.00%)
```

---

## 4. Top Protocol Feature Drivers (Legitimate vs. Malicious Commands)

When distinguishing legitimate SCADA commands from malicious commands:

1. **`s_msg_ratio`** (**Gain: $328,400.09$**) — Supervisory ACK ratio. Authorized SCADA command executions maintain standard handshake acknowledgment cycles (S-frames), whereas malicious command floods inject rapid unacknowledged I-frame bursts.
2. **`cot=3`** (**Gain: $74,463.04$**) — Spontaneous COT presence. Legitimate master command operations occur alongside ongoing spontaneous outstation telemetry updates.
3. **`i_msg_ratio`** (**Gain: $32,649.66$**) — Information frame ratio relative to total traffic.
4. **`flow packet APDU length mean`** (**Gain: $1,108.81$**) — Mean APDU payload length.
5. **`cmd_to_mon_ratio`** (**Gain: $575.25$**) — Ratio of control commands to monitoring frames.
6. **`cot=7`** (**Gain: $391.06$**) — Activation Confirmation frequency.

---

## 5. Paper Limitations Wording

> *"Legitimate Command Integrity: To confirm that protocol-aware classification distinguishes malicious control actions from legitimate SCADA operations rather than command presence alone, we evaluated the model on a command-only subset ($N = 42,989$ flows, including $15,376$ benign command flows with process/system control ASDUs and COT=6/7 activation confirmations). Under a strict 0% file-overlap grouped split, protocol-aware classification achieves $\text{ROC-AUC} = 1.000000$ ($100.00\%$ Recall, $100.00\%$ Precision, $0.00\%$ FPR) when separating legitimate control commands from malicious command injections, driven by Supervisory ACK framing ratios (`s_msg_ratio`), Spontaneous COT distribution (`COT=3`), and APDU payload statistics."*
