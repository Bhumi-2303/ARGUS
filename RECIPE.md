# ARGUS Recipe Recovery (DAY 1)

## a) Exact Formulas of the Four Features
*Found in `verification/train_d3_native.py` (lines 120-141).*
- **`pkt_mean_to_max`**: `np.where(df["Pkt Len Max"] == 0, 0, df["Pkt Len Mean"] / df["Pkt Len Max"])`
- **`log_pkt_mean`**: `np.log1p(df["Pkt Len Mean"].clip(lower=0))`
- **`log_pkt_max`**: `np.log1p(df["Pkt Len Max"].clip(lower=0))`
- **`tcp_flag_density`**: `df[flag_cols].sum(axis=1)` (where `flag_cols` are columns containing the substring "Flag").

## b) NF-ToN-IoT-v2 Split Logic
*Found via `experiment_execution/validation/dataset_partition_validation.json` and matching `train_d3_native.py` split logic.*
- **Total Train Size**: 10,508,704 rows (72.58% attack prior).
- **Adaptation Set**: 80% of Train = 8,406,962 rows (stratified).
- **Calibration Set**: 20% of Train = 2,101,742 rows (stratified).
- **Test Set**: 2,627,177 rows (72.58% attack prior).
- **Split mechanism**: `train_test_split(..., test_size=0.80, random_state=42, stratify=y_train)` applied iteratively.

## c) Clean Class-aware CORAL Labels
*Found in `FINAL_PAPER_READINESS_REPORT.md` (Section 5).*
- **Covariance Estimation**: The codebase **leaked test labels** for covariance estimation on target domains, which contradicts `Target_Labels_Used_For_Training = No`. 
- **Threshold Selection**: Evaluated dynamically to maximize MCC on the **calibration set** only.

## d) XGBoost Hyperparameters and Threshold Rule
*Found in `generate_d1_d2_baselines.py` and `phase4_results/adaptive_operating_point.py`.*
- **Hyperparameters**: `n_estimators=100`, `learning_rate=0.1`, `random_state=42`.
- **Threshold Rule**: Select the threshold (`theta`) that yields the **Maximum MCC** on the strictly held-out Calibration split.
