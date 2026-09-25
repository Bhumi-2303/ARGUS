# Global Experiment Validation & Integrity Report

## 1. Metric Integrity Audit
- [x] All metric values strictly bounded within $[0, 1]$ (or $[-1, 1]$ for MCC).
- [x] Zero string function objects (`<function...>`) in exported CSVs.
- [x] Log Loss bounded and clipped to prevent infinite/NaN values.
- [x] Confusion matrix sums ($TN + FP + FN + TP = 714,453$) strictly match test set size.

## 2. Dataset Isolation Audit
- [x] D3 Test Set ($N=714,453$) completely isolated; zero test samples used in training or scaling.
- [x] D3 Calibration Set ($N=571,563$) used *strictly* for threshold parameter searches.
- [x] D3 Adaptation Set ($N=2,286,249$) used *strictly* without labels for CORAL covariance estimation.

## 3. Terminology & Prohibited Claims Check
- [x] Prohibited term "Domain Generalization" replaced with "Unsupervised Domain Adaptation with Target Calibration".
- [x] Prohibited claim "Autonomous Multi-Agent Defense" removed from empirical benchmark scope.
- [x] High FPR ($87.08\%$) explicitly reported and analyzed under operational constraints.
