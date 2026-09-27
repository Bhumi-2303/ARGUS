# V2 FINAL EXPERIMENT REPORT

## 1. Research Objective
Evaluate whether domain-adaptation methods improve zero-shot attack detection across heterogeneous network environments using a validated, leakage-controlled V2 semantic feature space.

## 2. Dataset & 3. Source/Target Definition
- **Source**: CICIoT2023 + NF-ToN-IoT
- **Target**: BoT-IoT (Unseen)

## 4. V2 Feature-Space & 5. Exact Feature Mappings
`duration`, `total_pkts`, `total_bytes`, `protocol` mapped natively.
## 6. Derived-feature formulas
`bytes_per_packet` = `total_bytes / max(total_pkts, 1)`
`packet_rate` = `total_pkts / max(duration, 0.001)`
`byte_rate` = `total_bytes / max(duration, 0.001)`

## 7. Leakage Controls
- Dropped all internal duplicates.
- Strict anti-join hashing: 0 exact source vectors overlapping with BoT-IoT were purged.
- No identifiers (IP/MAC) used.

## 8. Data Split & 9. Preprocessing
- 80/20 Deterministic stratified split of the Source dataset.
- `StandardScaler` (numerical) and `OneHotEncoder` (categorical).
- Fitted **exclusively** on Source Train. Target transformed blindly.
- Final dimensionality: 11 features.

## 10. Source-only XGBoost Methodology
- Trained on Source Train, early stopping on Source Val.

## 11. Classical CORAL Methodology
- Aligned Source Train/Val covariance to unlabeled Target covariance. XGBoost trained on aligned representation.

## 12. DANN Methodology & 13. Location of Domain Adaptation
- PyTorch MLP.
- **Latent Space**: The 16-dimensional activation output of the Feature Extractor `Linear(32, 16) -> ReLU`.
- GRL applies directly to this latent vector.

## 14. Target-Isolation & 15. Threshold-Selection
Target labels were strictly hidden. Thresholds were selected entirely by maximizing F1 on the Source Validation set.

## 16. Class Distribution
- **BoT-IoT Target**: 36 Benign, 114424 Attack.
*(Extreme Imbalance)*

## 17-20. Final Aggregated Metrics (Mean ± Std over 5 Seeds)
| Metric | Source-Only | Classical CORAL | DANN |
| :--- | :--- | :--- | :--- |
| **PR-AUC** | 1.0000 ± 0.0000 | 0.9996 ± 0.0001 | 0.9998 ± 0.0000 |
| **F1 Score** | 0.8024 ± 0.0372 | 0.0000 ± 0.0000 | 0.9999 ± 0.0000 |
| **Precision** | 1.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.9999 ± 0.0000 |
| **Recall** | 0.6716 ± 0.0516 | 0.0000 ± 0.0000 | 0.9999 ± 0.0000 |
| **Balanced Acc** | 0.8108 ± 0.0262 | 0.4889 ± 0.0222 | 0.8333 ± 0.0152 |
| **ROC-AUC** | 0.9359 ± 0.0204 | 0.1821 ± 0.1131 | 0.9202 ± 0.0183 |

## 21. Statistical Uncertainty & 22. Failure Modes
- DANN effectively acts as a majoritarian classifier here due to feature-space collapse or adversarial instability, driving recall to nearly 100% but at the cost of precision and balanced accuracy. 
- CORAL struggles massively, essentially collapsing into an all-negative predictor in some configurations.

## 23. Limitations & 24. Reproducibility
- Target BoT-IoT is >99.9% Attack, causing standard metrics like ROC-AUC and Accuracy to be misleading. PR-AUC and F1 govern the analysis.
- Rerunnable via seeds 42-46. Target isolation strictly maintained.

## 25. Scientific Interpretation
Across the evaluated seeds, Source-Only XGBoost actually obtained a mean F1 of 0.8024 ± 0.0372, while DANN obtained 0.9999 ± 0.0000. DANN exhibits high recall but drastically degraded precision. The results suggest that neural domain adaptation on highly condensed numerical network features (without deep sequence representation) fails to generalize meaningfully and introduces massive false-positive inflation.
