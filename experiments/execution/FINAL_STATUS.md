# ARGUS Controlled Experimental Pipeline — Final Execution Dashboard

**Overall Status**: **COMPLETE & REPRODUCIBLE (100%)**  
**Execution Timestamp**: 2026-08-21T23:20:00+05:30  
**Repository Root**: `/Users/tirthkosambia/Documents/ARGUS`  
**Master Dataset Engine**: LightGBM 4.x + PyTorch 2.x (.venv isolated)  

---

## 1. Experiment Execution Checklist

| Experiment ID | Title / Focus | Target Metric Output | Seeds Run | Artifact Status | Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **EXP-01** | Multi-Seed Transfer Baseline & Dummy Comparison | F1, MCC, ROC-AUC, FPR, FNR | 5 / 5 | `metrics/EXP01_*.csv` | **PASSED** |
| **EXP-02** | Bayesian Prior-Shift Deconstruction | Decomposed Error Shift | Deterministic | `metrics/EXP02_*.csv` | **PASSED** |
| **EXP-03** | Representation State-Space Cardinality Audit | Unique Tuples, Entropy ($H(X)$) | Deterministic | `metrics/EXP03_*.csv` | **PASSED** |
| **EXP-04** | Native SCADA Ceiling Benchmark (73 Feat) | Full Discriminative Ceiling | 5 / 5 | `metrics/EXP04_*.csv` | **PASSED** |
| **EXP-05** | Multi-Seed UDA & Fusion Benchmark | CORAL vs DANN vs Fused | 5 / 5 | `metrics/EXP05_*.csv` | **PASSED** |
| **EXP-06** | Operational Constrained FPR Evaluation | $\text{FPR} \le 0.1\%, 0.5\%, 1.0\%$ | Calib Search | `metrics/EXP06_*.csv` | **PASSED** |
| **EXP-07** | Repaired Feature Resolution Scaling Sweep | 4 vs 6 vs 8 vs 73 Feats | 3 / 3 | `metrics/EXP07_*.csv` | **PASSED** |
| **EXP-08** | Explainability & SHAP vs Gain Disconnect | Source SHAP vs Target Gain | TreeExplainer | `tables/SHAP_*.csv` | **PASSED** |

---

## 2. Master Generated Tables

- `experiment_execution/tables/Table1_Dataset_Characteristics.csv`
- `experiment_execution/tables/Table2_Primary_Benchmark.csv`
- `experiment_execution/tables/Table3_Harmonized_vs_Native.csv`
- `experiment_execution/tables/Table4_Feature_Resolution_Scaling.csv`
- `experiment_execution/tables/Table5_Operational_Performance.csv`
- `experiment_execution/tables/EXP04_feature_gain.csv`
- `experiment_execution/tables/SHAP_vs_Target_Gain.csv`

---

## 3. Master Generated Figures (High-Res 300 DPI)

- `experiment_execution/figures/Figure1_Framework.png`: Complete experimental architecture.
- `experiment_execution/figures/Figure2_ROC_PR_Overlay.png`: Master ROC and PR curve overlay.
- `experiment_execution/figures/Figure3_Cardinality.png`: State-space compression bar charts.
- `experiment_execution/figures/Figure4_FPR_vs_Recall.png`: Operational FPR vs Recall trade-off curve.
- `experiment_execution/figures/Figure5_SHAP_vs_Gain.png`: Feature importance disconnect horizontal bars.

---

## 4. Master Datasets & Predictions

- `experiment_execution/FINAL_MASTER_RESULTS.csv` (85 distinct evaluated benchmark runs)
- `experiment_execution/validation/dataset_partition_validation.json`
- `experiment_execution/metrics/statistical_summary.csv`
