# ARGUS REPRODUCTION RESULTS

## 1. Executive Summary
Successfully rebuilt a strictly leakage-controlled, zero-shot domain adaptation pipeline across CICIoT2023, NF-ToN-IoT, and BoT-IoT. Extreme historical feature-space duplication was identified and purged. Models were trained and evaluated without any target-label influence, establishing a true, scientifically valid baseline.

## 2. Dataset Provenance & 3. Leakage Findings
Forensic analysis confirmed that the raw feature spaces contain astronomical internal duplication. Furthermore, explicit cross-domain overlap was identified.
- CICIoT Internal Duplicates: 205809
- NFToN Internal Duplicates: 1128901
- BoTIoT Internal Duplicates: 999918
- Cross-Domain Overlap (CIC/NF vs BoT) removed: 3 vectors.

## 4. Clean Dataset Construction
- A strict anti-join removed all target feature vectors from the source domain.
- **Source Domains**: CICIoT2023 + NF-ToN-IoT.
- **Target Domain**: BoT-IoT (Unseen).
- Canonical features used: `total_pkts`, `total_bytes`, `protocol`.
- Train/Val/Test sizes: 49571 / 12393 / 82.

## 5. Preprocessing Protocol
StandardScaler and OneHotEncoder were fitted **exclusively** on the Source Train dataset. Target data was transformed using these frozen parameters.

## 6. Source-Only Baseline Methodology
- Model: XGBoost (`n_estimators=100`, `max_depth=6`).
- Validation used for early stopping.
- Threshold: 0.5.

## 7. CORAL Methodology
- Classical CORAL: Source covariance aligned to target covariance.
- Classifier: XGBoost trained on aligned source features.
- No target labels utilized.

## 8. DANN Methodology
- PyTorch MLP with Gradient Reversal Layer.
- Optimization: Adam, LR 0.001, 15 Epochs.
- Domain classifier trained to distinguish source vs target unlabeled features.
- Threshold selected solely using Source Validation F1 score (T=0.60).

## 9. Final Metrics (BoT-IoT Target)

| Metric | Source-Only | Classical CORAL | DANN |
| :--- | :--- | :--- | :--- |
| **ROC-AUC** | 0.6486 | 0.5000 | 0.5429 |
| **PR-AUC** | 0.6511 | 0.5732 | 0.5627 |
| **F1 Score** | 0.1091 | 0.0000 | 0.8034 |
| **Balanced Acc** | 0.4605 | 0.5000 | 0.6714 |
| **Precision** | 0.3750 | 0.0000 | 0.6714 |
| **Recall** | 0.0638 | 0.0000 | 1.0000 |

## 10. Reproducibility
**YES.** Every stage from raw datasets to final metrics is captured in deterministic, version-controlled scripts. Output artifacts and manifests are saved in `data/reproduction/`.

## 11. Limitations & Future Work
The BoT-IoT dataset condensed into merely 82 unique feature vectors under the canonical schema. This severely limits statistical significance. Richer canonical features (e.g., inter-arrival times, sequence lengths) must be extracted from the raw PCAPs to increase feature-space entropy.
