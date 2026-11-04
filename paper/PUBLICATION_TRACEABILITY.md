# ARGUS Scientific Publication Traceability Matrix (`paper/PUBLICATION_TRACEABILITY.md`)

This document establishes the end-to-end scientific provenance chain for every publication table and figure presented in the ARGUS research paper: **"Cross-Domain Generalization Failure in IoT/SCADA Intrusion Detection: Representation Resolution and Class-Aware Adaptation"**.

---

## 1. End-to-End Scientific Lineage Model

Every publication exhibit follows a strict 7-link evidence chain:

```text
Publication Exhibit (Figure / Table)
       │
       ▼
Experiment Identifier (e.g., EXP-01, EXP-02, P2.1)
       │
       ▼
Evaluation / Execution Script (`scripts/` or `paper/experiments/`)
       │
       ▼
Configuration Manifest (`configs/`)
       │
       ▼
Frozen Dataset Partition (`data/` or `dataset/`)
       │
       ▼
Raw Prediction / Metric Artifact (`results/verified/` or Parquet)
       │
       ▼
Formal Research Validation Report (`audit/` or `results/experiments/`)
```

---

## 2. Master Table Traceability Matrix

| Manuscript Table | Exhibit File | Experiment ID | Execution Script | Configuration Manifest | Target Dataset & Split | Underlying Result Artifact | Scientific Validation Report |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Table I** (Domain Profiles) | [`paper/tables/Table_I_Domains_And_Profiles.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_I_Domains_And_Profiles.csv) | Pre-Experiment Profiling | `scripts/generate_architecture_audit.py` | `experiments/configs/paths.yaml` | D1, D2, D3 Full Ingestion | `results/verified/domain_statistics.json` | [`audit/historical/AUDIT.md`](file:///home/bhumi/GitHub/ARGUS/audit/historical/AUDIT.md) |
| **Table II** (Partition Balance) | [`paper/tables/Table_II_Partition_Sizes_And_Balance.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_II_Partition_Sizes_And_Balance.csv) | Protocol Setup | `scripts/generate_architecture_audit.py` | `experiments/configs/paths.yaml` | D1/D2/D3 Disjoint Splits | `paper_text.txt` Table II | [`audit/independent/MASTER_AUDIT_REPORT.md`](file:///home/bhumi/GitHub/ARGUS/audit/independent/MASTER_AUDIT_REPORT.md) |
| **Table III** (Bidirectional D1↔D2) | [`paper/tables/Table_III_Bidirectional_D1_D2_Cross_Domain.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_III_Bidirectional_D1_D2_Cross_Domain.csv) | EXP-01 (D1↔D2) | `archive/scripts/root_scripts/generate_d1_d2_baselines.py` | `experiments/training/configs/xgboost.yaml` | D1 (CICIoT, 1.18M), D2 (NF-ToN, 2.63M) | `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx` (Sheet `Verified_Primary_Benchmark`) | [`audit/historical/AUDIT.md`](file:///home/bhumi/GitHub/ARGUS/audit/historical/AUDIT.md) |
| **Table IV** (D1→D2 Random-Row Benchmark) | [`paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv) | EXP-02 (UDA Benchmark) | `scripts/p2_1_same_test_comparison.py` | `experiments/domain_adaptation/coral/config.yaml` | D2 Frozen Test ($N=2,627,177$) | `results/verified/five_model_complete_comparison.csv` | [`results/experiments/p2_1_validation/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_1_validation/) |
| **Table V** (Resolution Scaling) | [`paper/tables/Table_V_Feature_Resolution_Scaling.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_V_Feature_Resolution_Scaling.csv) | EXP-REP-01 (Resolution) | `paper/data/2_REP01_Deliverables/scripts/run_rep01_experiments.py` | `paper/data/2_REP01_Deliverables/configs/config.json` | D3 SCADA Test ($N=714,453$) | `experiments/execution/tables/Table4_Feature_Resolution_Scaling.csv` | [`paper/data/2_REP01_Deliverables/reports/REP01_FINAL_REPORT.md`](file:///home/bhumi/GitHub/ARGUS/paper/data/2_REP01_Deliverables/reports/REP01_FINAL_REPORT.md) |
| **Table VI** (FPR Budgets) | [`paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv) | EXP-04 (Operational FPR) | `paper/experiments/journal_completion/scripts/run_exp04_calibration_roc_pr.py` | `paper/experiments/journal_completion/configs/experiment_registry.json` | D3 SCADA Test ($N=714,453$) | `paper/experiments/journal_completion/tables/exp04_operational_threshold_table.csv` | [`results/experiments/p2_2_robustness/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_2_robustness/) |

---

## 3. Master Figure Traceability Matrix

| Figure ID | Exhibit File | Category | Experiment ID | Execution Script | Target Dataset | Source Data Artifact | Scientific Validation Report |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FIG-ARCH-01** | [`paper/figures/architecture/fig01_argus_system_architecture.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/architecture/fig01_argus_system_architecture.png) | Architecture | System Platform | Conceptual Specification | D1, D2, D3 | `docs/architecture/00_ARGUS_MASTER_SPECIFICATION.md` | [`audit/architecture/TARGET_ARCHITECTURE.md`](file:///home/bhumi/GitHub/ARGUS/audit/architecture/TARGET_ARCHITECTURE.md) |
| **FIG-ARCH-02** | [`paper/figures/architecture/fig02_evaluation_pipeline.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/architecture/fig02_evaluation_pipeline.png) | Protocol | Protocol Verification | Conceptual Protocol | D1, D2, D3 | `paper_text.txt` Section IV-A | [`audit/independent/RESEARCH_PAPER_READINESS.md`](file:///home/bhumi/GitHub/ARGUS/audit/independent/RESEARCH_PAPER_READINESS.md) |
| **FIG-METH-01** | [`paper/figures/methodology/fig01_feature_harmonization.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/methodology/fig01_feature_harmonization.png) | Harmonization | EXP-REP-01 | Feature Schema Engine | D1, D2, D3 | `paper/data/2_REP01_Deliverables/tables/REP01_FEATURE_AUDIT.csv` | [`paper/data/2_REP01_Deliverables/reports/REP01_FINAL_REPORT.md`](file:///home/bhumi/GitHub/ARGUS/paper/data/2_REP01_Deliverables/reports/REP01_FINAL_REPORT.md) |
| **FIG-METH-02** | [`paper/figures/methodology/fig02_coral_alignment_concept.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/methodology/fig02_coral_alignment_concept.png) | Domain Adaptation | EXP-02 | Mathematical Formulation | D1, D2 | `results/verified/five_model_complete_comparison.csv` | [`results/experiments/p2_1_validation/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_1_validation/) |
| **FIG-SYS-01** | [`paper/figures/system_implementation/fig01_live_monitoring_platform.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/system_implementation/fig01_live_monitoring_platform.png) | Implementation | Live Demo Platform | Web Application Console | SCADA Telemetry Stream | `web/src/pages/OverviewPage.tsx` | [`docs/LIVE_DEMO_VALIDATION.md`](file:///home/bhumi/GitHub/ARGUS/docs/LIVE_DEMO_VALIDATION.md) |
| **FIG-PUB-01** | [`paper/figures/experimental_results/10_publication_figures/FIGURE_1_cross_domain_confusion_matrix_grid.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/10_publication_figures/FIGURE_1_cross_domain_confusion_matrix_grid.png) | Confusion Matrices | EXP-01 / EXP-02 | `scripts/generate_publication_figures.py` | D1, D2, D3 Frozen Tests | `results/verification/predictions/*.npz` | [`results/experiments/p2_3_reconciliation/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/) |
| **FIG-PUB-02** | [`paper/figures/experimental_results/10_publication_figures/FIGURE_2_roc_pr_dual_panel.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/10_publication_figures/FIGURE_2_roc_pr_dual_panel.png) | ROC & PR Curves | EXP-02 | `scripts/generate_publication_figures.py` | D2 Frozen Test ($N=2.63\text{M}$) | `results/verified/five_model_complete_comparison.csv` | [`results/experiments/p2_1_validation/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_1_validation/) |
| **FIG-PUB-03** | [`paper/figures/experimental_results/10_publication_figures/FIGURE_3_zero_shot_generalization_and_operational_perf.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/10_publication_figures/FIGURE_3_zero_shot_generalization_and_operational_perf.png) | Zero-Shot Transfer | EXP-03 / EXP-04 | `scripts/generate_publication_figures.py` | D3 SCADA ($N=714\text{K}$) | `experiments/execution/tables/Table3_Harmonized_vs_Native.csv` | [`experiments/execution/reports/EXP03_REPORT.md`](file:///home/bhumi/GitHub/ARGUS/experiments/execution/reports/EXP03_REPORT.md) |
| **FIG-PUB-04** | [`paper/figures/experimental_results/10_publication_figures/FIGURE_4_bidirectional_transfer_heatmap.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/10_publication_figures/FIGURE_4_bidirectional_transfer_heatmap.png) | Transfer Heatmap | EXP-01 | `scripts/generate_publication_figures.py` | D1, D2 | `paper_text.txt` Table III | [`audit/historical/AUDIT.md`](file:///home/bhumi/GitHub/ARGUS/audit/historical/AUDIT.md) |
| **FIG-PUB-05** | [`paper/figures/experimental_results/10_publication_figures/FIGURE_5_shap_feature_importance_and_target_disconnect.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/10_publication_figures/FIGURE_5_shap_feature_importance_and_target_disconnect.png) | Explainability | EXP-05 | `scripts/generate_publication_figures.py` | D1 Source vs D2 Target | `results/verified/SHAP_vs_Target_Gain.csv` | [`experiments/execution/reports/EXP05_REPORT.md`](file:///home/bhumi/GitHub/ARGUS/experiments/execution/reports/EXP05_REPORT.md) |
| **FIG-PUB-06** | [`paper/figures/experimental_results/10_publication_figures/FIGURE_6_coral_alignment_and_latent_projection.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/10_publication_figures/FIGURE_6_coral_alignment_and_latent_projection.png) | Latent Projections | EXP-02 | `scripts/generate_publication_figures.py` | D1 Source -> D2 Target | `results/verification/predictions/` | [`results/experiments/p2_1_validation/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_1_validation/) |
| **FIG-PUB-07** | [`paper/figures/experimental_results/10_publication_figures/FIGURE_7_model_and_representation_ablation_study.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/10_publication_figures/FIGURE_7_model_and_representation_ablation_study.png) | Ablations | EXP-REP-01 / M0-M7 | `scripts/generate_publication_figures.py` | D3 SCADA ($N=714\text{K}$) | `experiments/execution/tables/Table4_Feature_Resolution_Scaling.csv` | [`paper/data/2_REP01_Deliverables/reports/REP01_FINAL_REPORT.md`](file:///home/bhumi/GitHub/ARGUS/paper/data/2_REP01_Deliverables/reports/REP01_FINAL_REPORT.md) |
| **FIG-PUB-08** | [`paper/figures/experimental_results/10_publication_figures/FIGURE_8_dann_training_and_convergence_analysis.png`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/10_publication_figures/FIGURE_8_dann_training_and_convergence_analysis.png) | Training Dynamics | EXP-02 | `scripts/generate_publication_figures.py` | D1 -> D2 Adaptation Split | `results/verified/dann_final_test_metrics.csv` | [`results/experiments/p2_3_reconciliation/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_3_reconciliation/) |

---

## 4. Known Provenance Gaps & Explicit Scientific Disclosures

1. **D1↔D2 Single-Seed Limitation**: Table III and Figure 4 are reconstructed from single-run historical exports. Multi-seed uncertainty bounds (Mean ± SD) and DeLong paired tests are not available for D1↔D2, whereas they are rigorously established for D3.
2. **Tuple Cardinality & Entropy Mechanism**: The hypothesis that state-space tuple collapse directly drives cross-domain error rates remains an exploratory hypothesis rather than an empirically proven mathematical law.
3. **Target Label Availability in Adaptation**: Clean Class-Aware CORAL relies on access to labeled samples in the target adaptation split ($\mathcal{D}_{\text{adapt}}$). In classical unsupervised domain adaptation (UDA), target labels are unavailable; this is disclosed as a Few-Shot Supervised Adaptation protocol.
