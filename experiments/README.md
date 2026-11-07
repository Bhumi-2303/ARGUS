# ARGUS Experiments Directory (`experiments/`)

This directory houses the model training code, domain adaptation pipelines, historical experiment execution runs, and ablation studies supporting the scientific publications and benchmarks of ARGUS.

---

## 1. Directory Structure

```text
experiments/
├── training/                       # Production and benchmark training pipelines
│   ├── trainers/                   # Base and specific model trainers (LightGBM, XGBoost, CatBoost, DANN, etc.)
│   ├── configs/                    # YAML model configuration manifests
│   ├── preprocessing/              # Tabular data cleaning and normalizers
│   ├── feature_engineering/        # Cross-domain semantic alignment & feature synthesis
│   ├── feature_selection/          # Feature selector modules
│   ├── tuning/                     # Optuna/grid hyperparameter tuners
│   ├── evaluation/                 # Domain evaluation metrics and scorers
│   ├── scripts/                    # Training execution runners (Phase 2, Phase 3, etc.)
│   ├── archive_leaked_run/         # Historical pre-audit run artifacts (retained for provenance)
│   └── exports/                    # Exported model weights and summaries
├── domain_adaptation/              # Unsupervised Domain Adaptation (UDA) pipelines
│   ├── coral/                      # Class-Aware & Global CORAL alignment (Stages A–F)
│   └── dann/                       # Domain-Adversarial Neural Network (Stages 1–3)
├── execution/                      # Master execution benchmarks (EXP01–EXP07)
│   ├── FINAL_MASTER_RESULTS.csv    # Master CSV summary of benchmark results
│   ├── configs/                    # Manifests and execution configs
│   ├── figures/                    # Benchmark ROC, PR, and calibration curves
│   ├── metrics/                    # Per-experiment CSV metrics
│   ├── neural_robustness/          # Tabular Transformer & neural capacity experiments
│   ├── predictions/                # Raw prediction CSVs for EXP01–EXP05
│   ├── reports/                    # Markdown execution reports for EXP01–EXP07
│   ├── scripts/                    # Generation scripts for figures and tables
│   └── tables/                     # Publication tables Table1–Table5
├── ablations/                      # Phase 4 ablation experiment scripts
├── analysis/                       # Feature resolution and state-space compression studies
└── configs/                        # System-wide path definitions (paths.yaml)
```

---

## 2. Research Phase Execution Runners (`scripts/`)

To guarantee reproducible CLI invocation without path ambiguity across audit reports, the primary research phase runners are maintained in `scripts/`:

| Research Phase | Runner Script | Primary Focus | Output Directory |
| :--- | :--- | :--- | :--- |
| **P1-1 In-Domain** | [`scripts/train_nfton_in_domain_baseline.py`](file:///home/bhumi/GitHub/ARGUS/scripts/train_nfton_in_domain_baseline.py) | Supervised NF-ToN in-domain reference | `results/experiments/p1_1_nfton_in_domain/` |
| **P1-1 Evaluation**| [`scripts/evaluate_nfton_in_domain_baseline.py`](file:///home/bhumi/GitHub/ARGUS/scripts/evaluate_nfton_in_domain_baseline.py) | In-domain metric recomputation | `results/experiments/p1_1_nfton_in_domain/` |
| **P2 Exp A** | [`scripts/p2_experiment_a_seen_unseen.py`](file:///home/bhumi/GitHub/ARGUS/scripts/p2_experiment_a_seen_unseen.py) | Coordinate overlap & leakage diagnosis | `results/experiments/p2_coordinate_generalization/` |
| **P2 Exp B** | [`scripts/p2_experiment_b_ambiguity.py`](file:///home/bhumi/GitHub/ARGUS/scripts/p2_experiment_b_ambiguity.py) | 4-tuple coordinate label ambiguity | `results/experiments/p2_coordinate_generalization/` |
| **P2 Exp C** | [`scripts/p2_experiment_c_disjoint.py`](file:///home/bhumi/GitHub/ARGUS/scripts/p2_experiment_c_disjoint.py) | Coordinate-disjoint grouped splits | `results/experiments/p2_coordinate_generalization/` |
| **P2 Exp D** | [`scripts/p2_experiment_d_historical.py`](file:///home/bhumi/GitHub/ARGUS/scripts/p2_experiment_d_historical.py) | Historical subset evaluation | `results/experiments/p2_coordinate_generalization/` |
| **P2.1 Comparison**| [`scripts/p2_1_same_test_comparison.py`](file:///home/bhumi/GitHub/ARGUS/scripts/p2_1_same_test_comparison.py) | Same-test-set cross-domain evaluation | `results/experiments/p2_1_validation/` |
| **P2.1 Statistical**| [`scripts/p2_1_statistical_validation.py`](file:///home/bhumi/GitHub/ARGUS/scripts/p2_1_statistical_validation.py) | Bootstrap CI & Paired DeLong tests | `results/experiments/p2_1_validation/` |
| **P2.2 Multi-Split**| [`scripts/p2_2_multisplit_evaluation.py`](file:///home/bhumi/GitHub/ARGUS/scripts/p2_2_multisplit_evaluation.py) | 5 independent coordinate-group splits | `results/experiments/p2_2_robustness/` |
| **P2.2 Bootstrap** | [`scripts/p2_2_statistical_audit.py`](file:///home/bhumi/GitHub/ARGUS/scripts/p2_2_statistical_audit.py) | Cluster-bootstrap (1,000 resamples) | `results/experiments/p2_2_robustness/` |
| **P2.3 Audit** | [`scripts/p2_3_reconciliation_audit.py`](file:///home/bhumi/GitHub/ARGUS/scripts/p2_3_reconciliation_audit.py) | Adversarial reconciliation of P2.1 & P2.2 | `results/experiments/p2_3_reconciliation/` |

---

## 3. Scientific Status Classification

Outputs generated from this directory are classified into strict scientific categories:

1. **Verified Historical Results**:
   - `experiments/execution/FINAL_MASTER_RESULTS.csv`: The authoritative master benchmark across EXP01–EXP07.
   - `experiments/execution/tables/Table1_Dataset_Characteristics.csv` through `Table5_Operational_Performance.csv`.
2. **Exploratory & Ablation Results**:
   - `experiments/ablations/phase4_execute.py`: Early hyperparameter and architecture sweeps.
   - `experiments/analysis/feature_resolution_study.py`: State-space compression proofs.
   - `experiments/training/archive_leaked_run/`: Pre-audit exploratory baseline containing known data leakage; retained strictly as negative control evidence.
3. **Not Yet Independently Validated**:
   - Neural robustness capacity tests (`experiments/execution/neural_robustness/capacity_test/`): Require cluster GPU execution for full multi-seed convergence.
