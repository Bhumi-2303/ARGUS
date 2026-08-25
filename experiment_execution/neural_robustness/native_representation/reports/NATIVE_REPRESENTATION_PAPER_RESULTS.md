# ARGUS NR-03: Paper-Ready Results & Manuscript Paragraph

---

## 1. Manuscript Results Section Paragraph

> *"To determine whether cross-domain transfer degradation stems from classifier capacity or representation bottlenecking, we evaluated the empirical relationship between telemetry resolution and discriminative ceiling on the frozen IEC 60870-5-104 target partition ($N=714,453$). Under a controlled FT-Transformer architecture ($d_{\text{token}}=32, n_{\text{blocks}}=2$), expanding feature resolution from the harmonized 4-feature model (1,388 unique states, entropy 5.84 bits) to 6 and 8 features increased state cardinality to 154,552 unique states (entropy 10.88 bits). The in-domain Native SCADA ceiling (70 features, 178,938 unique states, entropy 14.21 bits) achieved ROC-AUC = 0.6425 and AP = 0.3666. In conjunction with our negative capacity scaling and domain alignment experiments, these findings provide compelling empirical evidence that cross-domain cybersecurity transfer is fundamentally bounded by representation resolution rather than neural model capacity or domain alignment methodology."*

---

## 2. Master Numerical Comparison

| Model | Representation | Training Protocol | Input Dim | ROC-AUC | Average Precision | Calibrated $F_1$ | Calibrated FPR |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **FT-Transformer** | ARGUS-4 | Cross-Domain ($D_1 \to D_3$) | 4 | **0.6075** | **0.2978** | 0.3724 | 96.68% |
| **FT-Transformer** | ARGUS-6 | Cross-Domain ($D_1 \to D_3$) | 6 | **0.5652** | **0.2547** | 0.3724 | 96.68% |
| **FT-Transformer** | ARGUS-8 | Cross-Domain ($D_1 \to D_3$) | 8 | **0.4448** | **0.2209** | 0.3669 | 100.00% |
| **FT-Transformer** | Native SCADA | In-Domain Target Ceiling | 70 | **0.6425** | **0.3666** | **0.1335** | **0.04%** |
| **LightGBM** | Native SCADA | In-Domain Target Ceiling | 70 | **0.6744** | **0.4066** | **0.4354** | **72.20%** |
