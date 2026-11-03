# ARGUS Experimental Research Audit & Experiment Gap Analysis

**Audit Date**: November 1, 2026  
**Auditor Role**: Senior Research Engineer & ML Research Auditor  
**Working Directory**: `/home/bhumi/GitHub/ARGUS`  
**Evaluation Standard**: Evidence-based audit against empirical artifacts, code implementations, logs, and verifiable outputs.

---

## 1. Master Experimental Inventory

The following master inventory accounts for every experiment found across `results/verified/`, `experiments/execution/`, `paper/experiments/journal_completion/`, `data/raw/legacy_package/`, and `data/reproduction/`:

| Experiment ID | Experiment Name | Research Objective | Dataset | Source Domain | Target Domain | Model Architecture | Method | Actual Reported Metrics | Result Location | Execution Evidence | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **EXP-D1D2-01** | Source-Only Cross-Domain Baseline | Measure out-of-domain degradation under common representation | CICIoT2023 & NF-ToN-IoT-v2 | D1 (CICIoT) | D2 (NF-ToN) | XGBoost (`n_est=100, lr=0.1`) | Zero-Shot Transfer (No adaptation, $\tau=0.50$) | Acc: 0.7207, Prec: 0.7247, Rec: 0.9919, F1: 0.8375, BalAcc: 0.4972, Spec: 0.0025, MCC: -0.0311, ROC-AUC: 0.3230 | `results/verified/five_model_complete_comparison.csv` | `generate_d1_d2_baselines.py`, raw test predictions ($N=2.63\text{M}$) | **VERIFIED** |
| **EXP-D1D2-02** | Global CORAL Alignment | Test unsupervised second-order statistical alignment | CICIoT2023 & NF-ToN-IoT-v2 | D1 (CICIoT) | D2 (NF-ToN) | XGBoost on aligned features | Global CORAL ($A=C_s^{-1/2}C_t^{1/2}, \tau=0.50$) | Acc: 0.6347, Prec: 0.7013, Rec: 0.8652, F1: 0.7747, BalAcc: 0.4448, Spec: 0.0244, MCC: -0.1610, ROC-AUC: 0.2852 | `results/verified/five_model_complete_comparison.csv` | Covariance matrix in `coral_parameters.npz` | **VERIFIED** |
| **EXP-D1D2-03** | Diagnostic Class-Aware CORAL | Upper-bound diagnostic test using target test labels | CICIoT2023 & NF-ToN-IoT-v2 | D1 (CICIoT) | D2 (NF-ToN) | XGBoost on class-aligned features | Diagnostic Class-Aware CORAL (Leaked test labels, $\tau=0.50$) | Acc: 0.5506, Prec: 0.7262, Rec: 0.6113, F1: 0.6638, BalAcc: 0.5006, Spec: 0.3899, MCC: +0.0011, ROC-AUC: 0.6361 | `results/verified/five_model_complete_comparison.csv` | Code in `data/raw/legacy_package/argus_coral_data/` | **VERIFIED (DIAGNOSTIC ONLY)** |
| **EXP-D1D2-04** | Clean Class-Aware CORAL | Leakage-controlled class-conditional covariance adaptation | CICIoT2023 & NF-ToN-IoT-v2 | D1 (CICIoT) | D2 (NF-ToN) | XGBoost on adaptation-aligned features | Supervised Adaptation (Adaptation split $N=8.41\text{M}$, Calib $\tau^*=0.99$) | Acc: 0.6191, Prec: 0.9400, Rec: 0.5076, F1: 0.6592, BalAcc: 0.7109, Spec: 0.9143, MCC: +0.3855, ROC-AUC: 0.5970 | `results/verified/five_model_complete_comparison.csv` | Pre-aligned CSV `ciciot_train_clean_class_aware_coral.csv` | **VERIFIED** |
| **EXP-D1D2-05** | DANN Adversarial Adaptation | Test unsupervised adversarial domain invariance | CICIoT2023 & NF-ToN-IoT-v2 | D1 (CICIoT) | D2 (NF-ToN) | PyTorch MLP + GRL | Adversarial UDA (Unlabeled target adaptation, Calib $\tau^*=0.60$) | Acc: 0.7259, Prec: 0.7259, Rec: 0.9998, F1: 0.8412, BalAcc: 0.5002, Spec: 0.0006, MCC: +0.0129, ROC-AUC: 0.3321 | `results/verified/dann_final_test_metrics.csv` | `dann_best_model.pt`, raw test predictions ($N=2,627,177$) | **VERIFIED** |
| **EXP-D3-01** | SCADA D1->D3 Transfer Baseline | Test transfer of compact 4-features into industrial SCADA | CICIoT2023 & IEC-104 SCADA | D1 (CICIoT) | D3 (IEC-104) | LightGBM | Calibrated Zero-Shot Transfer | Acc: 0.2487, Prec: 0.2292, Rec: 0.9923, F1: 0.3724, FPR: 0.9668, MCC: 0.0650, ROC-AUC: 0.5442 | `experiments/execution/tables/Table2_Primary_Benchmark.csv` | Scripts in `experiments/execution/` | **VERIFIED** |
| **EXP-D3-02** | SCADA D2->D3 Transfer Baseline | Test transfer of smart home IoT into SCADA | NF-ToN-IoT-v2 & IEC-104 SCADA | D2 (NF-ToN) | D3 (IEC-104) | LightGBM | Calibrated Zero-Shot Transfer | Acc: 0.2344, Prec: 0.2251, Rec: 0.9860, F1: 0.3666, FPR: 0.9833, MCC: 0.0087, ROC-AUC: 0.4381 | `experiments/execution/tables/Table2_Primary_Benchmark.csv` | Scripts in `experiments/execution/` | **VERIFIED** |
| **EXP-D3-03** | SCADA Native Ceiling Benchmark | Establish discriminative ceiling under domain-native features | IEC-104 SCADA ($N=3.57\text{M}$) | D3 (IEC-104) | D3 (IEC-104) | LightGBM (Native 70 transport features) | In-Domain Supervised | Acc: 0.4335, Prec: 0.2802, Rec: 0.9700, F1: 0.4348, FPR: 0.7220, MCC: 0.2489, ROC-AUC: 0.6739 | `experiments/execution/tables/Table4_Feature_Resolution_Scaling.csv` | `artifacts/models/model_d3_native.txt`, test predictions ($N=714\text{K}$) | **VERIFIED** |
| **EXP-D3-04** | Protocol-Aware Grouped SCADA Model | Evaluate application-layer ASDU features under 0% file overlap | IEC-104 SCADA Protocol ($N=47.3\text{K}$) | D3 (IEC-104) | D3 (IEC-104) | LightGBM (44 Protocol ASDU features) | In-Domain Grouped Split (`GroupShuffleSplit`, 24 held-out files) | Acc: 0.9999, Prec: 0.9998, Rec: 1.0000, F1: 0.9999, FPR: 0.0002, MCC: 0.9998, ROC-AUC: 1.0000 | `verification/leakage_audit_report.md` | `model_d3_protocol_aware_grouped.txt` | **VERIFIED (CONFOUNDED BY VOLUME)** |
| **EXP-D3-05** | Volume-Matched Protocol Ratio Model | Evaluate pure protocol ratio features with volume confound removed | IEC-104 SCADA Protocol ($N=3,766$) | D3 (IEC-104) | D3 (IEC-104) | LightGBM (Protocol ratio features only: `i_msg_ratio`, `APDU length mean`) | In-Domain Volume-Matched Subsample (0% file overlap) | Acc: 0.9967, Prec: 1.0000, Rec: 0.9935, F1: 0.9967, FPR: 0.0000, MCC: 0.9950, ROC-AUC: 0.999965 | `verification/duration_confound_report.md` | `verification/i_msg_ratio_leakage_check.md` | **VERIFIED** |
| **EXP-REP-01** | Representation Resolution Scaling Sweep | Test performance as feature dimensionality increases (4 vs 6 vs 8 vs 70) | IEC-104 SCADA ($N=714\text{K}$ test) | D1/D2 Source | D3 (IEC-104) | LightGBM & FT-Transformer | Multi-Feature Representation Comparison | ARGUS-4: ROC-AUC 0.6262; ARGUS-6: ROC-AUC 0.6534; ARGUS-8: ROC-AUC 0.6536; Native-73: ROC-AUC 0.6739 | `experiments/execution/tables/Table4_Feature_Resolution_Scaling.csv` | Scripts & plots in `paper/ARGUS_Paper_Data/2_REP01_Deliverables/` | **VERIFIED** |
| **EXP-JC-01** | Forensic Feature & Split Leakage Audit | Verify lack of overlap and class priors across train/calib/test | CICIoT, NF-ToN, IEC-104 | D1, D2 | D1, D2 | Data Auditor | Anti-join verification across splits | All splits verify 0 row overlap. Duplication rates: D1=78.3%, D2=87.7%. Status: PASS. | `paper/experiments/journal_completion/tables/exp01_dataset_leakage_summary.csv` | `.venv/bin/python paper/experiments/journal_completion/scripts/run_exp01_leakage_audit.py` | **VERIFIED** |
| **EXP-JC-02** | Grouped vs Chronological Split Audit | Test impact of session burst autocorrelation | NF-ToN-IoT-v2 | D2 | D2 | LightGBM | Split Strategy Comparison (Random vs Chronological vs Grouped) | Random: F1 0.9525, ROC-AUC 0.9651; Chronological: F1 0.9523, ROC-AUC 0.9666; Group-Disjoint: F1 0.9528, ROC-AUC 0.9662 | `paper/experiments/journal_completion/tables/exp02_split_comparison.csv` | `run_exp02_group_split_audit.py` | **VERIFIED** |
| **EXP-JC-03** | Multi-Seed Evaluation & Bootstrap CIs | Measure statistical uncertainty across 5 seeds | CICIoT & NF-ToN | D1 | D2 | LightGBM (Source vs Clean CORAL) | 5-Seed Bootstrap Resampling ($B=1,000$) | Clean CORAL 95% CIs: ROC-AUC [0.7331, 0.7409], MCC [0.3844, 0.3968], Specificity [0.9159, 0.9248] | `paper/experiments/journal_completion/tables/exp03_bootstrap_ci.csv` | `run_exp03_multiseed_uncertainty.py` | **VERIFIED** |
| **EXP-JC-04** | Operational Constrained FPR Sweep | Evaluate attack recall under SOC false alarm budgets | NF-ToN ($N=2.63\text{M}$) & IEC-104 ($N=714\text{K}$) | D1, D2 | D2, D3 | 5 Models | Threshold Search ($\text{FPR} \le 0.01\%, 0.10\%, 1.0\%, 5.0\%$) | At FPR $\le 0.01\%$: Clean CORAL Recall = 2.13% (FPR=0.13%); Native SCADA Recall = 7.12% (FPR=0.01%) | `paper/experiments/journal_completion/tables/exp04_operational_threshold_table.csv` | `run_exp04_calibration_roc_pr.py` | **VERIFIED** |
| **EXP-JC-05** | Domain Shift Quantification (KS & Covariance) | Measure KS distance and covariance divergence across domains | D1, D2, D3 | D1, D2 | D2, D3 | Distributional Statistics | KS Test, PSI, Wasserstein Distance | Unwritten script listed in registry | `paper/experiments/journal_completion/scripts/run_exp05_domain_shift_coral.py` (Script missing) | None (Script not yet written) | **MISSING** |
| **EXP-JC-06** | Cross-Domain Benchmark Multi-Model Suite | Re-execute all models under unified multi-seed framework | D1, D2, D3 | D1, D2 | D2, D3 | LightGBM, XGBoost, CatBoost, DANN | Unified Benchmark Re-run | Unwritten script listed in registry | `paper/experiments/journal_completion/scripts/run_exp06_benchmark_comparison.py` (Script missing) | None | **MISSING** |
| **EXP-JC-07** | Leave-One-Component-Out Pipeline Ablation | Isolate contributions of CORAL vs Prior Correction vs Threshold Calibration | D1, D2 | D1 | D2 | XGBoost | Component Ablation | Unwritten script listed in registry | `paper/experiments/journal_completion/scripts/run_exp07_pipeline_ablation.py` (Script missing) | Partial in `experiments/ablations/phase4_execute.py` | **PARTIAL** |
| **EXP-JC-08** | Hyperparameter Sensitivity (Weights & Regularization) | Sensitivity to CORAL reg $\lambda \in [10^{-6}, 10^{-1}]$ | D1, D2 | D1 | D2 | XGBoost + CORAL | Grid Sweep on Calibration Split | Unwritten script listed in registry | `paper/experiments/journal_completion/scripts/run_exp08_sensitivity_analysis.py` (Script missing) | Partial in `experiments/domain_adaptation/dann/stage2_pilot_lambda_sweep.py` | **PARTIAL** |
| **EXP-JC-09** | Robustness Under Noise & Feature Missingness | Adversarial feature perturbation and zero-replacement | NF-ToN-IoT-v2 | D1 | D2 | Trained Models | Perturbation Sweeps ($N=250\text{K}$) | Unwritten script listed in registry | `paper/experiments/journal_completion/scripts/run_exp09_robustness_stress_test.py` (Script missing) | None | **MISSING** |
| **EXP-JC-10** | Attack-Family Granular Breakdown | Per-attack class recall across DoS, DDoS, Scan, Backdoor, Injection | NF-ToN-IoT-v2 | D1 | D2 | Clean CORAL | Per-Class Confusion Matrices | Unwritten script listed in registry | `paper/experiments/journal_completion/scripts/run_exp10_attack_family_breakdown.py` (Script missing) | Partial in `results/verified/dann_final_test_classification_report.csv` | **PARTIAL** |
| **EXP-JC-11** | SHAP Stability & False-Alarm Error Analysis | Check if SHAP attributions remain stable across seeds and noise | D1, D2 | D1 | D2 | LightGBM / XGBoost | TreeSHAP Attribution Variance | Unwritten script listed in registry | `paper/experiments/journal_completion/scripts/run_exp11_shap_error_analysis.py` (Script missing) | Single sample SHAP only | **MISSING** |
| **EXP-JC-12** | Computational Profiling & Latency Benchmarks | Measure training throughput and per-flow inference latency | Telemetry Streams | D1, D2 | D2 | All Models | Benchmarked sample of 100k flows | Unwritten script listed in registry | `paper/experiments/journal_completion/scripts/run_exp12_computational_profiling.py` (Script missing) | Partial in `scripts/test_stream_performance.py` | **PARTIAL** |

---

## 2. Evaluation Across the 17 Research Areas

### 1. In-Domain Baseline Evaluation
- **Status**: **PARTIALLY COMPLETED**
- **Evidence**: In-domain baselines exist for D1 (CICIoT2023, F1 = 0.949–0.986) and D3 native (IEC-104, ROC-AUC = 0.6739).
- **Critical Gap**: An in-domain supervised model trained on the **target domain (NF-ToN-IoT-v2)** using its 8.41M training/adaptation split is **completely absent** from Table II / `five_model_complete_comparison.csv`. Because Clean Class-Aware CORAL accesses 8.41M labeled target samples, the failure to report an in-domain target baseline obscures how much information is lost compared to training directly on target.

### 2. Cross-Domain Generalization Evaluation
- **Status**: **VERIFIED COMPLETED**
- **Evidence**: D1 -> D2 transfer evaluated on 2,627,177 samples; D1 -> D3 evaluated on 714,453 samples; D2 -> D3 evaluated on 714,453 samples. Extreme performance collapse is thoroughly documented.

### 3. Zero-Shot Generalization
- **Status**: **VERIFIED COMPLETED**
- **Evidence**: Source-Only XGBoost and Source-Only LightGBM evaluated with zero target information. Results show complete collapse (Balanced Acc = 0.4972 on D2, Specificity = 0.0025; ROC-AUC = 0.5442 on D3).

### 4. Domain Adaptation Comparisons
- **Status**: **VERIFIED COMPLETED**
- **Evidence**: Direct comparison between Source-Only, Global CORAL, Diagnostic Class-Aware CORAL, Clean Class-Aware CORAL, and DANN on the exact same frozen 2.63M test set.

### 5. CORAL Effectiveness
- **Status**: **VERIFIED COMPLETED**
- **Evidence**: Empirical proof that unsupervised Global CORAL collapses (Balanced Acc = 0.4448, worse than source-only), whereas Class-Aware CORAL recovers performance (Balanced Acc = 0.7109).

### 6. Ablation Studies
- **Status**: **PARTIALLY COMPLETED**
- **Evidence**: Feature ablation completed for D3 protocol features (removing U-messages and `i_msg_ratio` in `verification/`). However, a unified component-wise ablation table for D1->D2 (stripping CORAL covariance, prior correction, and threshold calibration independently) exists only in `experiments/ablations/phase4_execute.py` and lacks multi-seed confidence intervals.

### 7. Feature Importance & Feature Reduction Studies
- **Status**: **VERIFIED COMPLETED**
- **Evidence**: REP-01 feature scaling study completed (ARGUS-4 vs ARGUS-6 vs ARGUS-8 vs Native-70). Proves non-monotonic scaling where 8 features collapses to near-chance under earlier splits.

### 8. Model Architecture Comparisons
- **Status**: **VERIFIED COMPLETED**
- **Evidence**: Comparisons across LightGBM, XGBoost, FT-Transformer (in REP-01), MLP/DANN, and Random Forest. V2 Group-Token Transformer evaluated and rejected at gate.

### 9. Hyperparameter Sensitivity
- **Status**: **PARTIALLY COMPLETED**
- **Evidence**: Threshold sweeps conducted across all models ($0.01 \le \tau \le 0.99$). DANN domain loss weight $\lambda$ swept in `experiments/domain_adaptation/dann/stage2_pilot_lambda_sweep.py`. Sensitivity to CORAL covariance regularization parameter $\lambda_{reg}$ ($10^{-6}$ vs $10^{-5}$ vs $10^{-3}$) has not been systematically charted.

### 10. Class Imbalance Analysis
- **Status**: **VERIFIED COMPLETED**
- **Evidence**: Explicit tracking of class priors (D1: 97.6% attack; D2: 72.6% attack; D3: 22.5% attack). Prior shift decomposed in `experiments/execution/tables/EXP02_prior_shift_decomposition.csv`.

### 11. Robustness & Noise Testing
- **Status**: **MISSING**
- **Evidence**: EXP-09 in `paper/experiments/journal_completion/` was specified but the script was never implemented. No evaluations exist for feature noise perturbations (Gaussian jitter), dropped packets, or missing feature imputations.

### 12. Statistical Significance Testing
- **Status**: **PARTIALLY COMPLETED**
- **Evidence**: 5-seed bootstrap resampling completed for EXP-03 (`exp03_bootstrap_ci.csv`). However, formal pairwise hypothesis tests (DeLong test for ROC-AUC differences, McNemar test for classification discordance) between Clean CORAL and Source-Only have not been computed.

### 13. Computational Complexity
- **Status**: **PARTIALLY COMPLETED**
- **Evidence**: Big-O covariance matrix complexity ($O(n d^2 + d^3)$) and SVD scaling documented in text. Floating-point operation (FLOP) counts for LightGBM vs FT-Transformer were not formally measured.

### 14. Inference Latency
- **Status**: **VERIFIED COMPLETED**
- **Evidence**: Benchmarked in `scripts/test_stream_performance.py` and live orchestrator trace (~0.8ms for DIA, ~500ms for initial model inference, ~1ms for subsequent predictions). Fallback vs Ollama LLM latency audited (3.5ms fallback vs 400–2500ms live Ollama).

### 15. Explainability Evaluation
- **Status**: **PARTIALLY COMPLETED**
- **Evidence**: TreeSHAP feature attributions verified in live inference. Disconnect between source SHAP and target gain verified in `SHAP_vs_Target_Gain.csv`. Missing: quantitative attribution stability across random seeds and adversarial noise.

### 16. Data Leakage Verification
- **Status**: **VERIFIED COMPLETED**
- **Evidence**: 100% source file overlap in random split audited in `verification/leakage_audit_report.md`. Corrected to strict file-level grouping (`GroupShuffleSplit`, 0% file overlap). Zero row overlap verified in EXP-JC-01.

### 17. Reproducibility Across Random Seeds
- **Status**: **PARTIALLY COMPLETED**
- **Evidence**: Multi-seed (5-seed) results available for D3 Native SCADA (`Table4_Feature_Resolution_Scaling.csv`) and EXP-JC-03 bootstrap CIs. However, primary benchmark in Table II of the current paper manuscript is still reported using single seed 42.

---

## 3. Detailed Specifications for Missing & Partial Experiments

### Gap 1: Target In-Domain Supervised Baseline (P0 — Essential for Scientific Integrity)
- **What Needs to be Tested**: Train XGBoost and LightGBM directly on `nfton_train_adaptation.csv` ($N = 8,406,962$) and evaluate on `nfton_test_features.csv` ($N = 2,627,177$) under default $\tau = 0.50$ and calibrated $\tau^*$.
- **Scientific Necessity**: Clean Class-Aware CORAL accessed all 8.41M labeled rows of `nfton_train_adaptation.csv` to calculate class-conditional covariances. Reviewers will rightly ask: *"Why adapt source features at all if you have 8.41 million labeled target examples? What is the in-domain supervised ceiling?"* Without this number, the paper cannot claim adaptation is useful compared to standard target training.
- **Required Datasets**: `data/raw/legacy_package/argus_coral_data/nfton_train_adaptation.csv` (Train), `nfton_train_calibration.csv` (Calib), `nfton_test_features.csv` (Test).
- **Configurations**: XGBoost (`n_est=100, max_depth=6, lr=0.1, random_state=42`) and LightGBM.
- **Metrics to Report**: Accuracy, Precision, Recall, F1, Balanced Accuracy, Specificity, MCC, ROC-AUC, PR-AUC.
- **Expected Contribution**: Provides the empirical upper bound ceiling, proving whether cross-domain adaptation retains sufficient transferability or if in-domain supervised learning is superior when target labels are available.
- **Priority**: **P0 (Critical Blocker)**

### Gap 2: Few-Shot Target Label Adaptation Sweep (P1 — Essential Research Experiment)
- **What Needs to be Tested**: Evaluate Clean Class-Aware CORAL when the number of available target labels $k$ is varied: $k \in \{10, 50, 100, 500, 1000, 5000, 10000, 100000\}$.
- **Scientific Necessity**: Class-Aware CORAL is only practically interesting if it works with *few* target labels. Assuming access to 8.41 million target labels is unrealistic for a new deployment domain. A few-shot curve will demonstrate the minimum number of target labels required to escape majority-class collapse.
- **Required Datasets**: Subsampled target adaptation splits from `nfton_train_adaptation.csv` across 5 random seeds.
- **Metrics to Report**: Balanced Accuracy, MCC, ROC-AUC, Attack Recall at 0.1% FPR.
- **Deliverable**: Figure: "Few-Shot Target Label Adaptation Curve ($k$ vs MCC)".
- **Priority**: **P1 (High Priority)**

### Gap 3: Pairwise Statistical Significance Testing (P1 — Essential for Journal Acceptance)
- **What Needs to be Tested**: Execute formal non-parametric hypothesis tests:
  1. **DeLong Test**: For ROC-AUC difference between Clean CORAL and Source-Only ($H_0: \Delta\text{AUC} = 0$).
  2. **McNemar Test**: For paired 2x2 contingency table discordance on binary predictions.
  3. **Multi-Seed Paired t-test**: Across 5 random seeds (42, 123, 456, 789, 1011).
- **Scientific Necessity**: Journal reviewers at IEEE TDSC/TIFS require statistical significance ($p < 0.001$) and confidence intervals to ensure differences are not artifacts of a single random seed.
- **Required Datasets**: Raw per-sample prediction vectors from `predictions_raw/`.
- **Metrics to Report**: $z$-score, $\chi^2$ statistic, $p$-values, 95% Confidence Intervals.
- **Deliverable**: Table: "Statistical Significance Tests for Model Superiority".
- **Priority**: **P1 (High Priority)**

### Gap 4: Implement Missing Journal Completion Scripts EXP-05 to EXP-12 (P1)
- **What Needs to be Tested**: Implement and execute the remaining 8 experiment scripts in `paper/experiments/journal_completion/scripts/`:
  - `run_exp05_domain_shift_coral.py`: Formal KS test statistics and Wasserstein distances.
  - `run_exp07_pipeline_ablation.py`: Strict leave-one-component-out ablation table.
  - `run_exp08_sensitivity_analysis.py`: CORAL covariance regularization $\lambda_{reg} \in [10^{-8}, 1.0]$.
  - `run_exp09_robustness_stress_test.py`: Gaussian noise jitter $\sigma \in [0.01, 0.5]$ and feature dropouts.
  - `run_exp10_attack_family_breakdown.py`: Granular per-attack class recall.
  - `run_exp11_shap_error_analysis.py`: SHAP attribution stability across seeds.
  - `run_exp12_computational_profiling.py`: FLOPs, wall-clock time, and memory scaling.
- **Scientific Necessity**: These 8 scripts transform the repository from an exploratory codebase into a publication-grade experimental testbed.
- **Priority**: **P1 (High Priority)**
