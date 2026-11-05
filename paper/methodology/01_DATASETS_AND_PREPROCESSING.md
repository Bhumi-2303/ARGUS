# Methodology Module 01: Datasets, Environments & Preprocessing

**Document Status**: Official Research Methodology Specification  
**Associated Manuscript**: Section IV (Experimental Setup & Protocol)

---

## 1. Domain Environments & Topologies

ARGUS evaluates cross-domain generalization across three fundamentally distinct operational network domains:

```text
┌─────────────────────────────────┐       ┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│        Domain 1 (D1)            │       │        Domain 2 (D2)            │       │        Domain 3 (D3)            │
│       CICIoT2023                │       │      NF-ToN-IoT-v2              │       │      IEC 60870-5-104            │
│  Enterprise IoT Topology        │──────>│   Smart Home NetFlow IoT        │──────>│  Industrial SCADA Substation    │
│  46 Raw Features                │       │   43 Standardized Features      │       │  70 Native SCADA Telemetry      │
│  97.64% Attack Prevalence       │       │   72.58% Attack Prevalence      │       │  22.46% Attack Prevalence       │
└─────────────────────────────────┘       └─────────────────────────────────┘       └─────────────────────────────────┘
```

### Domain 1: CICIoT2023 (D1)
- **Environment**: Enterprise Internet of Things (IoT) testbed comprising 33 physical smart devices (cameras, sensors, smart plugs, microcontrollers) connected across 16 distinct network topologies.
- **Attack Composition**: High-volume Distributed Denial of Service (DDoS UDP/TCP flood), Denial of Service (DoS), brute force credential attacks, and port scanning.
- **Total Ingestion**: 6,668,822 network flows.
- **Class Distribution**: 157,247 Benign flows (2.36%), 6,511,575 Attack flows (97.64%).
- **Role**: Primary source domain ($\mathcal{D}_s$) for supervised baseline training and feature representation extraction.

### Domain 2: NF-ToN-IoT-v2 (D2)
- **Environment**: Smart Home and Industrial IoT hybrid testbed captured using Cisco NetFlow-v9 standardized fields (Sarhan et al., 2022).
- **Attack Composition**: Web application attacks, scanning, password cracking, backdoors, ransomware, and volumetric DoS.
- **Total Ingestion**: 13,135,881 network flows.
- **Class Distribution**: 3,601,776 Benign flows (27.42%), 9,534,105 Attack flows (72.58%).
- **Role**: Primary cross-domain adaptation and transfer evaluation target ($\mathcal{D}_t$).

### Domain 3: IEC 60870-5-104 SCADA Power Grid (D3)
- **Environment**: Critical infrastructure telemetry monitoring electric power distribution substations over the IEC 60870-5-104 supervisory control and data acquisition protocol.
- **Attack Composition**: SCADA interrogation floods, unauthorized command injection, Application Service Data Unit (ASDU) spoofing, and protocol sabotage.
- **Total Ingestion**: 3,572,265 network flows.
- **Class Distribution**: 2,769,902 Benign flows (77.54%), 802,363 Attack flows (22.46%).
- **Role**: Second target domain evaluating zero-shot transfer generalization into critical operational technology (OT).

---

## 2. Partition Schemes & Frozen-Test Protocol

To prevent catastrophic evaluation leakage, target domains are strictly divided into three disjoint functional splits:

1. **Unlabeled Adaptation Split ($\mathcal{D}_{\text{adapt}}$)**:
   - Used exclusively for estimating target second-order statistics ($C_t$) in CORAL or domain discrimination in DANN.
   - Ground truth class labels are strictly masked during adaptation.
2. **Calibration Split ($\mathcal{D}_{\text{calib}}$)**:
   - Used exclusively for post-adaptation threshold selection ($\tau^* = \arg\max \text{MCC}$) and empirical prior probability estimation.
   - Disjoint from both training and test data.
3. **Frozen Test Split ($\mathcal{D}_{\text{test}}$)**:
   - Evaluated blind exactly once per model after all pipeline components and thresholds are frozen.
   - Zero gradient feedback, covariance updates, or threshold re-tuning are permitted on this split.

| Domain | Partition | Sample Count | Benign Flows | Attack Flows | Attack % | Evaluation Role |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **D1 (CICIoT)** | Train | 5,491,971 | 129,538 | 5,362,433 | 97.64% | Supervised Source Training |
| **D1 (CICIoT)** | Test | 1,176,851 | 27,709 | 1,149,142 | 97.64% | Source In-Domain Baseline |
| **D2 (NF-ToN)** | Train / Adapt | 10,508,704 | 2,881,519 | 7,627,185 | 72.58% | Unlabeled Adaptation & Calibration |
| **D2 (NF-ToN)** | Frozen Test | 2,627,177 | 720,257 | 1,906,920 | 72.58% | Blind Cross-Domain Benchmark |
| **D3 (SCADA)** | Train / Calib | 2,857,812 | 2,215,958 | 641,854 | 22.46% | D3 Native Training & Threshold Calib |
| **D3 (SCADA)** | Frozen Test | 714,453 | 553,944 | 160,509 | 22.46% | Coordinate-Disjoint Independent Test |

---

## 3. Preprocessing & Normalization Pipeline

1. **Missing & Infinite Value Handling**:
   - Zero flows containing `NaN`, `Inf`, or unparsable fields were imputed. Erroneous negative duration timestamps are strictly pruned.
2. **Feature Log-Transformation**:
   - Skewed volumetric features (e.g., total bytes, packet sizes, flow duration) are transformed via $x \mapsto \ln(1 + \max(0, x))$ to stabilize variance across orders of magnitude.
3. **Standardization**:
   - Zero-mean, unit-variance standardization ($z = \frac{x - \mu_s}{\sigma_s}$) computed on the source training set is applied symmetrically across target domains. Target statistics are never used to normalize test sets.
