# ARGUS Scientific Research Overview (`docs/RESEARCH_OVERVIEW.md`)

This document summarizes the academic research foundations, experimental methodology, and empirical findings presented in the ARGUS research paper: **"Cross-Domain Generalization Failure in IoT/SCADA Intrusion Detection: Representation Resolution and Class-Aware Adaptation"**.

---

## 1. Research Motivation & Core Problem

Intrusion Detection Systems (IDS) for the Internet of Things (IoT) and Industrial Control Systems (ICS/SCADA) are commonly trained and benchmarked within a single collection domain. However, smart grid and industrial networks exhibit severe distribution shifts compared to academic testbeds:
- Differing traffic protocol semantics (e.g., Modbus, DNP3, IEC 60870-5-104 vs. standard HTTP/MQTT).
- Extreme class imbalance and label prior shifts (e.g., attack-heavy IoT testbeds vs. benign-dominated SCADA utility networks).
- Information loss when harmonizing heterogeneous network telemetry into unified feature spaces.

When models trained on one network domain are evaluated on an unseen target network under a shared, compact representation, **they suffer catastrophic generalization failure**. ARGUS investigates the root causes of this failure and establishes rigorous zero-leakage adaptation protocols.

---

## 2. Research Questions (RQ1 – RQ6)

| Research Question | Scientific Focus | Validated Finding in ARGUS |
| :--- | :--- | :--- |
| **RQ1: Degradation Severity** | How severely do supervised models degrade when transferred cross-domain under a compact representation? | Supervised models (XGBoost, LightGBM) achieving $>97\%$ in-domain F1 collapse to near-chance or majority-class prediction ($\text{ROC-AUC} \le 0.323\text{--}0.692$, $\text{MCC} \le -0.031$). |
| **RQ2: Root Cause Analysis** | Is degradation caused by classifier capacity limitations or information loss in the representation? | Kolmogorov-Smirnov statistics ($0.37\text{--}0.74$) reveal the shift is primarily class-conditional and state-space collapse destroys class separability. |
| **RQ3: Domain Adaptation** | Can unsupervised or class-aware domain adaptation recover discriminability under domain shift? | Standard global covariance alignment (Global CORAL) and adversarial alignment (DANN) fail. However, **Clean Class-Aware CORAL** with calibration ($\tau^* = 0.99$) successfully recovers performance ($\text{MCC} = +0.3855$, Balanced Accuracy $= 71.09\%$). |
| **RQ4: Representation Scaling** | Does increasing the resolution (feature count) of the common representation monotonically improve transfer? | **No. Representation scaling is non-monotonic.** An 8-feature representation collapses to $\text{ROC-AUC} = 0.445$, performing worse than 4- and 6-feature variants. |
| **RQ5: Operational Viability** | Does cross-domain IDS remain viable under realistic Security Operations Center (SOC) false alarm budgets? | Under strict false-positive budgets ($\text{FPR} \le 0.1\%$), attack recall drops below $1\%$; at $\text{FPR} \le 1.0\%$, recall remains below $21\%$, revealing a massive gap between aggregate academic metrics and operational triage reality. |
| **RQ6: Domain-Native Representation** | Can rich, domain-native representations recover discriminability that generic flow representations lose? | Only abandoning cross-domain harmonization in favor of D3's native 73-feature representation restores discrimination ($\text{ROC-AUC} = 0.674$, $\text{MCC} = +0.249$). |

---

## 3. Evaluated Domains & Dataset Accounting

ARGUS conducts evaluations across three distinct network environments:

| Domain ID | Dataset | Environment | Protocol Mix | Attack Prevalence | Role in Study |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **D1** | **CICIoT2023** | Enterprise / Lab IoT | 802.11, TCP/UDP, DoS, Brute Force | $97.64\%$ Attack | Source Domain |
| **D2** | **NF-ToN-IoT-v2** | Smart Home IoT | NetFlow v9, Mixed IoT protocols | $72.58\%$ Attack | Target Domain |
| **D3** | **IEC 60870-5-104** | Industrial SCADA Substation | Telecontrol SCADA flows | $22.46\%$ Attack | Target Industrial Domain |

### Observation Pool Accounting (D2 Target Domain)
The target domain (NF-ToN-IoT-v2) partition pool consists of exactly **13,135,881** observations:
- **Adaptation Split ($\mathcal{D}_{\text{adapt}}$)**: $8,406,962$ rows ($64.0\%$) — used for covariance calculation.
- **Calibration Split ($\mathcal{D}_{\text{calib}}$)**: $2,101,742$ rows ($16.0\%$) — used for threshold optimization ($\tau^* = 0.99$).
- **Frozen Test Split ($\mathcal{D}_{\text{test}}$)**: $2,627,177$ rows ($20.0\%$) — strictly held-out for blind final evaluation.

*(Note: The historical count of $11,034,141$ reported in early project notes was an arithmetic line-count artifact that omitted the calibration split and counted file headers).*

---

## 4. Key Empirical Benchmarks

### Benchmark 1: D1 $\to$ D2 Domain Adaptation (Random-Row Held-Out Split, $N=2,627,177$)

Table IV summarizes the definitive benchmark on the frozen random-row target partition:

| Model | Decision $\tau$ | Accuracy | Precision | Recall | F1 | Balanced Acc. | Specificity | MCC | ROC-AUC | Protocol Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Clean Class-Aware CORAL + XGBoost** | **0.99** | **0.6191** | **0.9400** | 0.5076 | 0.6592 | **0.7109** | **0.9143** | **+0.3855** | 0.5970 | **Verified Winner** |
| Source-Only XGBoost | 0.50 | 0.7207 | 0.7247 | 0.9919 | 0.8375 | 0.4972 | 0.0025 | -0.0311 | 0.3230 | Unadapted Source |
| Global CORAL + XGBoost | 0.50 | 0.6347 | 0.7013 | 0.8652 | 0.7747 | 0.4448 | 0.0244 | -0.1610 | 0.2852 | Global Covariance Alignment |
| DANN (Domain Adversarial NN) | 0.60 | 0.7259 | 0.7259 | 0.9998 | 0.8412 | 0.5002 | 0.0006 | +0.0129 | 0.3321 | Majority-Class Collapse |
| *Diagnostic Class-Aware CORAL* | *0.50* | *0.5506* | *0.7262* | *0.6113* | *0.6638* | *0.5006* | *0.3899* | *+0.0011* | *0.6361* | *Diagnostic (Used Test Labels)* |

### Benchmark 2: Coordinate-Disjoint Evaluation (Phase 2.3 Reconciliation)
To test whether spatial network correlation (IP address / subnet sharing) influences performance, a coordinate-disjoint partition ($N=1,970,428$) was evaluated:
- At default threshold ($\theta = 0.50$): CORAL achieves $\text{MCC} = 0.0504$.
- At calibrated threshold ($\tau^* = 0.99$): CORAL achieves $\text{MCC} = 0.0795$.
- *(Scientific Clarification: The metric $\text{MCC} = 0.3896$ referenced in intermediate audit drafts was an editorial transcription error / threshold misattribution; the authoritative random-row result is $+0.3855$ and coordinate-disjoint result is $+0.0795$).*

### Benchmark 3: Representation Resolution Non-Monotonicity (D3 SCADA)
Table V evaluates representation scaling from 4 to 73 features on IEC-104 SCADA traffic ($N=714,453$):
- **ARGUS-4** ($4$ features): $\text{ROC-AUC} = 0.608$, $\text{MCC} = +0.065$
- **ARGUS-6** ($6$ features): $\text{ROC-AUC} = 0.565$, $\text{MCC} = +0.065$
- **ARGUS-8** ($8$ features): $\text{ROC-AUC} = 0.445$, $\text{MCC} = 0.000$ (Representation collapse)
- **D3 Native** ($73$ features): $\text{ROC-AUC} = 0.674$, $\text{MCC} = +0.249$ (Native SCADA ceiling)

---

## 5. Master Research Workbook Provenance

All research results, multi-seed sweeps, confusion matrices, and distribution metrics are permanently archived in the cryptographically verified master research workbook:
- **Location**: [`results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`](file:///home/bhumi/GitHub/ARGUS/results/ARGUS_ALL_RESEARCH_RESULTS.xlsx)
- **Worksheet Count**: Exactly 17 authoritative sheets.
- **File Size**: $75,463$ bytes.
- **SHA-256 Checksum**: `f4ddc451a0c0d97f1eeea0a57668562b1bf9bb13437e2f30c5ac95d8bdb678f1`.
