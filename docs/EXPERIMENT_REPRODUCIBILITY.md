# ARGUS Scientific Experiment Reproducibility Guide (`docs/EXPERIMENT_REPRODUCIBILITY.md`)

This guide provides researchers, reviewers, and reproducibility auditors with complete instructions to independently verify, execute, and reproduce the empirical benchmarks presented in the ARGUS academic manuscript.

---

## 1. Master Research Workbook Forensic Baseline

All experimental data, metrics, confusion matrices, and distribution statistics are anchored by the master research spreadsheet:

- **Path**: [`results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`](file:///home/bhumi/GitHub/ARGUS/results/ARGUS_ALL_RESEARCH_RESULTS.xlsx)
- **Worksheet Count**: Exactly 17 authoritative worksheets.
- **File Size**: $75,463$ bytes.
- **SHA-256 Fingerprint**: `f4ddc451a0c0d97f1eeea0a57668562b1bf9bb13437e2f30c5ac95d8bdb678f1`.

### Verification Command
```bash
python -c "
import hashlib
path = 'results/ARGUS_ALL_RESEARCH_RESULTS.xlsx'
with open(path, 'rb') as f:
    digest = hashlib.sha256(f.read()).hexdigest()
expected = 'f4ddc451a0c0d97f1eeea0a57668562b1bf9bb13437e2f30c5ac95d8bdb678f1'
assert digest == expected, f'Workbook hash mismatch: {digest}'
print(f'Master research workbook verified: {digest}')
"
```

---

## 2. Reproduction of Core Publication Tables

Every table in `paper/tables/` is backed by raw prediction files, frozen test sets, and deterministic evaluation scripts.

### Table I & II: Dataset Profiles & Partition Balance
- **Underlying Artifacts**: `results/verified/domain_statistics.json`, `paper/tables/Table_I_Domains_And_Profiles.csv`, `Table_II_Partition_Sizes_And_Balance.csv`.
- **Target Observations**:
  - D1 (CICIoT2023): $1,180,683$ samples.
  - D2 (NF-ToN-IoT-v2): $13,135,881$ total pool ($8,406,962$ adapt + $2,101,742$ calib + $2,627,177$ frozen test).
  - D3 (IEC-104 SCADA): $714,453$ frozen test observations.

### Table III: Bidirectional D1 $\leftrightarrow$ D2 Cross-Domain Transfer
- **Underlying Artifacts**: `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx` Sheet `Verified_Primary_Benchmark`.
- **Finding**: In-domain models achieve $\text{MCC} \ge +0.647$ to $+0.831$, but collapse to $\text{MCC} \le -0.031$ when transferred cross-domain without adaptation.

### Table IV: D1 $\to$ D2 Domain Adaptation Benchmark ($N=2,627,177$)
- **Canonical CSV**: [`paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv)
- **Execution Script**: `scripts/p2_1_same_test_comparison.py`
- **Command to Reproduce**:
  ```bash
  python scripts/p2_1_same_test_comparison.py
  ```
- **Validation**: Compares 5 models on the identical frozen test partition ($N=2,627,177$):
  1. *Clean Class-Aware CORAL + XGBoost* ($\tau^* = 0.99$): $\text{MCC} = +0.3855$, $\text{Bal. Acc} = 71.09\%$, $\text{Precision} = 94.00\%$, $\text{Specificity} = 91.43\%$.
  2. *Source-Only XGBoost* ($\tau = 0.50$): $\text{MCC} = -0.0311$, $\text{ROC-AUC} = 0.3230$.
  3. *Global CORAL + XGBoost* ($\tau = 0.50$): $\text{MCC} = -0.1610$, $\text{ROC-AUC} = 0.2852$.
  4. *DANN* ($\tau^* = 0.60$): $\text{MCC} = +0.0129$, $\text{ROC-AUC} = 0.3321$ (Majority-class collapse).
  5. *Diagnostic Class-Aware CORAL* ($\tau = 0.50$): Diagnostic only (used target test labels).
- **Partition Characteristics & DANN Reproducibility**:
  - *Random-Row Coordinate Overlap*: Under random row splitting, 2,592,203 out of 2,627,177 test observations ($98.67\%$) map to identical 4D feature coordinates present in the adaptation training split. The available data does not contain IP addresses or subnets.
  - *DANN Reproducibility Status*: Stored prediction metric recomputation (**Level A**) and checkpoint loading with forward-pass execution (**Level B**) are verified against frozen test metrics ($\text{ROC-AUC} = 0.3321$, $\text{Accuracy} = 0.7259$). Full test-set forward pass is executed (**Level C**). Level D exact tensor equality against stored probabilities is divergent due to PyTorch BatchNorm running statistics. DANN is kept unavailable in the production `ModelRegistry`.

### Table V: Representation Resolution Scaling Sweep (D3 SCADA)
- **Canonical CSV**: [`paper/tables/Table_V_Feature_Resolution_Scaling.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_V_Feature_Resolution_Scaling.csv)
- **Command to Reproduce**:
  ```bash
  python paper/data/2_REP01_Deliverables/scripts/run_rep01_experiments.py
  ```
- **Validation**: Evaluates 3-seed mean performance on D3 SCADA test set ($N=714,453$):
  - 4-feature (`ARGUS-4`): $\text{ROC-AUC} = 0.6083$, $\text{MCC} = +0.0652$
  - 6-feature (`ARGUS-6`): $\text{ROC-AUC} = 0.5654$, $\text{MCC} = +0.0650$
  - 8-feature (`ARGUS-8`): $\text{ROC-AUC} = 0.4452$, $\text{MCC} = 0.0000$ (Representation collapse)
  - 73-feature (`D3 Native`): $\text{ROC-AUC} = 0.6739$, $\text{MCC} = +0.2486$ (SCADA Native ceiling)

### Table VI: Operational Performance at Fixed FPR Budgets
- **Canonical CSV**: [`paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv)
- **Command to Reproduce**:
  ```bash
  python paper/experiments/journal_completion/scripts/run_exp04_calibration_roc_pr.py
  ```
- **Validation**:
  - At $\text{FPR} \le 0.1\%$: Native SCADA LightGBM achieves $0.85\%$ attack recall.
  - At $\text{FPR} \le 1.0\%$: Native SCADA LightGBM achieves $20.73\%$ attack recall.

---

## 3. Publication Figure Generation

To regenerate all 8 camera-ready composite publication panels (`FIG-PUB-01` through `FIG-PUB-08`):
```bash
python scripts/generate_publication_figures.py
```
This script reads the raw predictions from `results/verification/predictions/` and `results/verified/five_model_complete_comparison.csv` and outputs 300 DPI PNG and vector SVG files into:
`paper/figures/experimental_results/10_publication_figures/`

---

## 4. 4D Feature-Coordinate Disjoint Protocol Reproduction (Phase 2.3)

To reproduce the 4D feature-coordinate disjoint benchmarks where no identical four-dimensional feature tuple appears in more than one partition:
```bash
python -c "
import pandas as pd
df = pd.read_csv('results/experiments/p2_3_reconciliation/p2_3_coordinate_disjoint_results.csv')
print(df[['model', 'threshold', 'mcc', 'balanced_accuracy', 'roc_auc']])
"
```
**Protocol Notes & Results**:
- **Separation Definition**: This protocol strictly separates identical four-dimensional feature tuples `(pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max)` in representation space, not IP addresses, subnets, or network sessions (which are not present in the 5-column tabular data).
- Default threshold ($\theta = 0.50$): $\text{MCC} = 0.0504$.
- Calibrated threshold ($\tau^* = 0.99$): $\text{MCC} = 0.0795$.
- Historical audit mention of $0.3896$ was an editorial typo referencing split thresholds.
