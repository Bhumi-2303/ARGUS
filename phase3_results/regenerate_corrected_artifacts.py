#!/usr/bin/env python3
"""
ARGUS Phase 3 — Regenerate Corrected Report, Excel, and ZIP.

Reads the validated metrics from the validation report JSON and regenerates:
- ARGUS_Phase3_Final_Report.md (corrected)
- ARGUS_Phase3_Results.xlsx (corrected Log Loss values)
- ARGUS_Phase3_Artifacts.zip (updated archive)

Does NOT retrain any models. Preserves all model artifacts.
"""

import json
import os
import zipfile
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

PROJECT_ROOT = Path("/Users/tirthkosambia/Documents/ARGUS")
RESULTS_DIR = PROJECT_ROOT / "phase3_results"

EXPERIMENT_IDS = [
    "D1_D3_BASELINE", "D2_D3_BASELINE",
    "D1_D3_CORAL", "D2_D3_CORAL",
    "D1_D3_DANN", "D2_D3_DANN"
]

EXPERIMENT_META = {
    "D1_D3_BASELINE": {"Source_Domain": "D1 (CICIoT2023)", "Model_Architecture": "LightGBM", "Adaptation_Method": "None (Source Baseline)"},
    "D2_D3_BASELINE": {"Source_Domain": "D2 (NF-ToN-IoT-v2)", "Model_Architecture": "LightGBM", "Adaptation_Method": "None (Source Baseline)"},
    "D1_D3_CORAL": {"Source_Domain": "D1 (CICIoT2023)", "Model_Architecture": "CORAL + LightGBM", "Adaptation_Method": "CORAL (Covariance Alignment)"},
    "D2_D3_CORAL": {"Source_Domain": "D2 (NF-ToN-IoT-v2)", "Model_Architecture": "CORAL + LightGBM", "Adaptation_Method": "CORAL (Covariance Alignment)"},
    "D1_D3_DANN": {"Source_Domain": "D1 (CICIoT2023)", "Model_Architecture": "DANN (Neural Net)", "Adaptation_Method": "DANN (Adversarial Domain Invariance)"},
    "D2_D3_DANN": {"Source_Domain": "D2 (NF-ToN-IoT-v2)", "Model_Architecture": "DANN (Neural Net)", "Adaptation_Method": "DANN (Adversarial Domain Invariance)"},
}


def main():
    print("=" * 80)
    print("ARGUS PHASE 3 — REGENERATING CORRECTED ARTIFACTS")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 80)

    # Load validation results
    with open(RESULTS_DIR / "metrics_validation_report.json", "r") as f:
        validation = json.load(f)

    vr = validation["validation_results"]
    corrected_tables = validation["corrected_tables"]

    # ── Build Corrected Master CSV ───────────────────────────────────────────
    print("\n[1/5] Building corrected master CSV...")
    master_rows = []

    for exp_id in EXPERIMENT_IDS:
        if exp_id not in vr:
            continue
        meta = EXPERIMENT_META[exp_id]
        m_u = vr[exp_id]["uncalibrated"]["metrics"]
        m_c = vr[exp_id]["calibrated"]["metrics"]
        th = vr[exp_id]["calibrated"]["metrics"]["Threshold"]

        # Uncalibrated row
        master_rows.append({
            "Experiment_ID": exp_id,
            "Source_Domain": meta["Source_Domain"],
            "Target_Domain": "D3 (IEC 60870-5-104)",
            "Model_Architecture": meta["Model_Architecture"],
            "Adaptation_Method": meta["Adaptation_Method"],
            "Calibration_Status": "Uncalibrated (θ=0.50)",
            "Decision_Threshold": 0.50,
            "Accuracy": m_u["Accuracy"], "Precision": m_u["Precision"],
            "Recall": m_u["Recall"], "F1": m_u["F1"],
            "Specificity": m_u["Specificity"],
            "Balanced_Accuracy": m_u["Balanced_Accuracy"],
            "Cohen_Kappa": m_u["Cohen_Kappa"], "MCC": m_u["MCC"],
            "TP": m_u["TP"], "TN": m_u["TN"], "FP": m_u["FP"], "FN": m_u["FN"],
            "False_Positive_Rate": m_u["FPR"],
            "False_Negative_Rate": m_u["FNR"],
            "ROC_AUC": m_u["ROC_AUC"], "PR_AUC": m_u["PR_AUC"],
            "Log_Loss": m_u["Log_Loss"], "Brier_Score": m_u["Brier_Score"],
            "ECE": m_u["ECE"]
        })

        # Calibrated row
        master_rows.append({
            "Experiment_ID": exp_id + "_CALIBRATED",
            "Source_Domain": meta["Source_Domain"],
            "Target_Domain": "D3 (IEC 60870-5-104)",
            "Model_Architecture": meta["Model_Architecture"],
            "Adaptation_Method": meta["Adaptation_Method"],
            "Calibration_Status": f"Calibrated (θ*={th:.2f})",
            "Decision_Threshold": th,
            "Accuracy": m_c["Accuracy"], "Precision": m_c["Precision"],
            "Recall": m_c["Recall"], "F1": m_c["F1"],
            "Specificity": m_c["Specificity"],
            "Balanced_Accuracy": m_c["Balanced_Accuracy"],
            "Cohen_Kappa": m_c["Cohen_Kappa"], "MCC": m_c["MCC"],
            "TP": m_c["TP"], "TN": m_c["TN"], "FP": m_c["FP"], "FN": m_c["FN"],
            "False_Positive_Rate": m_c["FPR"],
            "False_Negative_Rate": m_c["FNR"],
            "ROC_AUC": m_c["ROC_AUC"], "PR_AUC": m_c["PR_AUC"],
            "Log_Loss": m_c["Log_Loss"], "Brier_Score": m_c["Brier_Score"],
            "ECE": m_c["ECE"]
        })

    df_master = pd.DataFrame(master_rows)
    df_master.to_csv(RESULTS_DIR / "metrics/final_comparison_master.csv", index=False)
    print(f"  Corrected master CSV saved ({len(df_master)} rows)")

    # ── Update Individual Experiment metrics.json ────────────────────────────
    print("\n[2/5] Updating individual experiment metrics.json files...")
    for exp_id in EXPERIMENT_IDS:
        if exp_id not in vr:
            continue
        metrics_path = RESULTS_DIR / f"experiments/{exp_id}/metrics.json"
        m_u = vr[exp_id]["uncalibrated"]["metrics"]
        m_c = vr[exp_id]["calibrated"]["metrics"]
        th = vr[exp_id]["calibrated"]["metrics"]["Threshold"]

        # Remove internal keys not in original format
        def clean_metrics(m):
            out = {}
            key_map = {
                "Accuracy": "Accuracy", "Precision": "Precision", "Recall": "Recall",
                "F1": "F1", "Specificity": "Specificity",
                "Balanced_Accuracy": "Balanced_Accuracy",
                "Cohen_Kappa": "Cohen_Kappa", "MCC": "MCC",
                "TP": "TP", "TN": "TN", "FP": "FP", "FN": "FN",
                "FPR": "False_Positive_Rate", "FNR": "False_Negative_Rate",
                "ROC_AUC": "ROC_AUC", "PR_AUC": "PR_AUC",
                "Log_Loss": "Log_Loss", "Brier_Score": "Brier_Score",
                "ECE": "ECE"
            }
            for src, dst in key_map.items():
                if src in m:
                    out[dst] = m[src]
            return out

        updated = {
            "Experiment_ID": exp_id,
            "Uncalibrated": clean_metrics(m_u),
            "Calibrated": clean_metrics(m_c),
            "Optimal_Threshold": th
        }
        with open(metrics_path, "w") as f:
            json.dump(updated, f, indent=2)
        print(f"  Updated: {exp_id}/metrics.json")

    # ── Regenerate Excel ─────────────────────────────────────────────────────
    print("\n[3/5] Regenerating Excel workbook...")
    excel_path = RESULTS_DIR / "ARGUS_Phase3_Results.xlsx"

    # Load supplementary data
    df_ablation = pd.read_csv(RESULTS_DIR / "metrics/ablation_study_results.csv")
    df_class_priors = pd.read_csv(RESULTS_DIR / "domain_shift/class_prior_summary.csv")
    df_domain_shift = pd.read_csv(RESULTS_DIR / "domain_shift/domain_shift_statistics.csv")
    df_shap = pd.read_csv(RESULTS_DIR / "shap/shap_feature_importance.csv")

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Sheet 1: Summary
        df_master[["Experiment_ID", "Source_Domain", "Target_Domain", "Model_Architecture",
                    "Adaptation_Method", "Calibration_Status", "F1", "Balanced_Accuracy",
                    "MCC", "Accuracy", "ROC_AUC", "PR_AUC", "Log_Loss"]].to_excel(
            writer, sheet_name="Experiment_Summary", index=False)

        # Sheet 2: Full Metrics
        df_master.to_excel(writer, sheet_name="Final_Metrics", index=False)

        # Sheet 3: Confusion Matrices
        cm_rows = []
        for _, row in df_master.iterrows():
            cm_rows.append({
                "Model": row["Experiment_ID"],
                "TN": int(row["TN"]), "FP": int(row["FP"]),
                "FN": int(row["FN"]), "TP": int(row["TP"]),
                "Total": int(row["TP"] + row["TN"] + row["FP"] + row["FN"]),
                "TPR_Recall": row["Recall"],
                "TNR_Specificity": row["Specificity"],
                "FPR": row["False_Positive_Rate"]
            })
        pd.DataFrame(cm_rows).to_excel(writer, sheet_name="Confusion_Matrices", index=False)

        # Sheet 4: Class Distribution
        df_class_priors.to_excel(writer, sheet_name="Class_Distribution", index=False)

        # Sheet 5: Domain Shift
        df_domain_shift.to_excel(writer, sheet_name="Domain_Shift", index=False)

        # Sheet 6: Calibration Deltas
        calib_deltas = []
        for exp_id in EXPERIMENT_IDS:
            m_u_row = df_master[df_master['Experiment_ID'] == exp_id]
            m_c_row = df_master[df_master['Experiment_ID'] == exp_id + "_CALIBRATED"]
            if len(m_u_row) > 0 and len(m_c_row) > 0:
                m_u = m_u_row.iloc[0]
                m_c = m_c_row.iloc[0]
                calib_deltas.append({
                    "Experiment_ID": exp_id,
                    "Uncalibrated_Threshold": 0.50,
                    "Calibrated_Threshold": m_c["Decision_Threshold"],
                    "Uncalibrated_F1": m_u["F1"], "Calibrated_F1": m_c["F1"],
                    "Delta_F1": m_c["F1"] - m_u["F1"],
                    "Uncalibrated_MCC": m_u["MCC"], "Calibrated_MCC": m_c["MCC"],
                    "Delta_MCC": m_c["MCC"] - m_u["MCC"],
                    "Uncalibrated_FPR": m_u["False_Positive_Rate"],
                    "Calibrated_FPR": m_c["False_Positive_Rate"],
                    "Delta_FPR": m_c["False_Positive_Rate"] - m_u["False_Positive_Rate"]
                })
        pd.DataFrame(calib_deltas).to_excel(writer, sheet_name="Calibration", index=False)

        # Sheet 7: Ablation
        df_ablation.to_excel(writer, sheet_name="Ablation", index=False)

        # Sheet 8: Feature Importance
        df_shap.to_excel(writer, sheet_name="Feature_Importance", index=False)

        # Sheet 9: SHAP Summary
        df_shap[["Feature", "Mean_Abs_SHAP", "Relative_Importance_Pct"]].to_excel(
            writer, sheet_name="SHAP_Summary", index=False)

        # Sheet 10: Runtime (placeholder if not available)
        pd.DataFrame([{"Note": "Runtimes loaded from checkpoints — see logs"}]).to_excel(
            writer, sheet_name="Runtime", index=False)

        # Sheet 11: Hyperparameters
        hyperparams = [
            {"Model": "LightGBM Baseline", "Learning_Rate": 0.05, "Num_Leaves": 31,
             "Max_Depth": 6, "Num_Boost_Rounds": 200, "Objective": "binary:logloss", "Seed": 42},
            {"Model": "CORAL + LightGBM", "Learning_Rate": 0.05, "Num_Leaves": 31,
             "Max_Depth": 6, "Num_Boost_Rounds": 200, "Regularization": 1e-6, "Seed": 42},
            {"Model": "DANN Neural Net", "Architecture": "MLP (4 -> 128 -> 64 -> 32 -> 1)",
             "Optimizer": "Adam", "LR": 0.001, "Epochs": 10, "Batch_Size": 1024,
             "Weight_Decay": 1e-5, "Seed": 42}
        ]
        pd.DataFrame(hyperparams).to_excel(writer, sheet_name="Hyperparameters", index=False)

        # Sheet 12: Reproducibility
        reproducibility = [
            {"Parameter": "Random Seed", "Value": "42 (Deterministic)"},
            {"Parameter": "D1 Source Data", "Value": "CICIoT2023 (5,491,971 train / 1,176,851 test)"},
            {"Parameter": "D2 Source Data", "Value": "NF-ToN-IoT-v2 (10,508,704 train / 2,627,177 test)"},
            {"Parameter": "D3 Target Data", "Value": "IEC 60870-5-104 (2,286,249 adapt / 571,563 calib / 714,453 test)"},
            {"Parameter": "Test Set Leakage Guard", "Value": "Zero leakage - D3 final test untouched during training & threshold selection"},
            {"Parameter": "Features Used", "Value": "4 features: pkt_mean_to_max, tcp_flag_density (Multiplicity), log_pkt_mean, log_pkt_max"},
            {"Parameter": "Metrics Audit", "Value": f"Independent validation completed {datetime.now().isoformat()} — Log Loss corrected from 0.0 to computed values"},
            {"Parameter": "Execution Timestamp", "Value": datetime.now().isoformat()}
        ]
        pd.DataFrame(reproducibility).to_excel(writer, sheet_name="Reproducibility", index=False)

    print(f"  Excel workbook saved: {excel_path}")

    # ── Generate Corrected Final Report ──────────────────────────────────────
    print("\n[4/5] Generating corrected final report...")

    # Build clean markdown table for primary results
    df_table_a = pd.DataFrame(corrected_tables["table_a"])
    df_table_b = pd.DataFrame(corrected_tables["table_b"])
    df_table_c = pd.DataFrame(corrected_tables["table_c"])

    # Get key values for report text
    d1_base_u = vr["D1_D3_BASELINE"]["uncalibrated"]["metrics"]
    d1_base_c = vr["D1_D3_BASELINE"]["calibrated"]["metrics"]
    d2_base_u = vr["D2_D3_BASELINE"]["uncalibrated"]["metrics"]
    d2_base_c = vr["D2_D3_BASELINE"]["calibrated"]["metrics"]
    d2_coral_c = vr["D2_D3_CORAL"]["calibrated"]["metrics"]
    d1_dann_c = vr["D1_D3_DANN"]["calibrated"]["metrics"]

    report_md = f"""# ARGUS Phase 3 — Cross-Domain Adaptation & Evaluation Final Report

## Executive Summary

This report presents the empirical evaluation for **Phase 3 of the ARGUS research project**, extending the IEEE paper *"Cross-Domain IoT-IDS: Exposing the Cross-Domain Generalization Gap in Machine-Learning-Based IoT Intrusion Detection"* to a third, grid-native target domain (**Domain 3: IEC 60870-5-104 SCADA/ICS**).

The frozen four-feature ARGUS representation:

$$\\mathbf{{x}} = [\\text{{pkt\\_mean\\_to\\_max}}, \\, \\text{{tcp\\_flag\\_multiplicity}}, \\, \\text{{log\\_pkt\\_mean}}, \\, \\text{{log\\_pkt\\_max}}]^\\top$$

was evaluated across cross-domain transfer pairs from heterogeneous IoT/network-flow source domains (**D1: CICIoT2023**, **D2: NF-ToN-IoT-v2**) to target SCADA traffic (**D3: IEC 60870-5-104**).

> **Metrics Audit**: All metrics in this report have been independently validated from saved prediction artifacts. Log Loss values were corrected (originally reported as 0.0 due to a numerical exception). All other metrics (ROC-AUC, PR-AUC, Brier, ECE, confusion matrices) have been verified as consistent.

---

## 1. Experimental Setup & Partitioning Integrity

- **D1 (CICIoT2023)**: 5,491,971 Train / 1,176,851 Test ($97.64\\%$ Attack / $2.36\\%$ Benign)
- **D2 (NF-ToN-IoT-v2)**: 10,508,704 Train / 2,627,177 Test / 8,406,962 Adapt / 2,101,742 Calib ($72.58\\%$ Attack / $27.42\\%$ Benign)
- **D3 (IEC 60870-5-104)**: 2,857,812 Train / 714,453 Test / 2,286,249 Adapt / 571,563 Calib ($22.47\\%$ Attack / $77.53\\%$ Benign)

> **Zero-Leakage Guard Enforcement**: The D3 held-out test set ($714,453$ rows) was strictly reserved for final evaluation and was **never used** during model training, CORAL covariance estimation, DANN adversarial learning, or threshold calibration. Threshold calibration was performed exclusively on the D3 calibration partition ($571,563$ rows) using $\\text{{argmax}}\\,F_1(\\text{{calibration set}})$ over $\\theta \\in [0.01, 0.99]$ with step $0.01$.

---

## 2. Empirical Performance Summary

### Table A — Primary Transfer & Adaptation Metrics on IEC 60870-5-104 Test Set (N = 714,453)

{df_master.to_markdown(index=False)}

---

## 3. Key Research Findings & Answer to Research Question

> **Research Question**: *Can a lightweight four-feature cybersecurity detector maintain useful detection performance when transferred from heterogeneous IoT/network-flow source domains to an IEC 60870-5-104 SCADA target domain, and can domain adaptation and calibration improve the transfer performance?*

### Scientific Findings

1. **Cross-Domain Generalization Gap Verified**: Uncalibrated zero-shot baseline detectors ($\\theta=0.50$) experience severe degradation when transferred directly to SCADA traffic.
   - **D1 $\\to$ D3 Baseline**: Uncalibrated F1 = {d1_base_u['F1']:.4f}, MCC = {d1_base_u['MCC']:.4f}. The D1-trained model classifies nearly all samples as attack (FPR = {d1_base_u['FPR']:.4f}), resulting in **extreme false-positive inflation**. This is consistent with D1's attack-saturated prior ($97.64\\%$ attack) encountering D3's benign-majority traffic ($77.53\\%$ benign).
   - **D2 $\\to$ D3 Baseline**: Uncalibrated F1 = {d2_base_u['F1']:.4f}, MCC = {d2_base_u['MCC']:.4f}. The D2-trained model classifies most samples as benign (FNR = {d2_base_u['FNR']:.4f}), resulting in **extreme false-negative inflation**. This is a qualitatively different failure mode from D1.

2. **Crucial Role of Threshold Calibration under Class-Prior Shift**: Because SCADA traffic is benign-majority ($77.53\\%$ benign) compared to attack-heavy IoT training sets, standard default decision thresholds ($\\theta=0.50$) produce different failure modes depending on source domain:
   - **D1 $\\to$ D3**: $\\theta=0.50$ produces massive false positives (FPR ≈ 0.98). Calibration to $\\theta^*=0.63$ marginally improves F1 from {d1_base_u['F1']:.4f} to {d1_base_c['F1']:.4f} ($\\Delta F_1 = {d1_base_c['F1']-d1_base_u['F1']:+.4f}$).
   - **D2 $\\to$ D3**: $\\theta=0.50$ produces massive false negatives (FNR ≈ 0.94). Calibration to $\\theta^*=0.01$ dramatically improves F1 from {d2_base_u['F1']:.4f} to {d2_base_c['F1']:.4f} ($\\Delta F_1 = {d2_base_c['F1']-d2_base_u['F1']:+.4f}$).

3. **Domain Adaptation Performance**:
   - **CORAL Covariance Alignment**: Combined with threshold calibration ($\\theta^*=0.68$), **D2 $\\to$ D3 CORAL** achieves the highest adapted performance among all evaluated configurations with **F1 = {d2_coral_c['F1']:.4f}** and **MCC = {d2_coral_c['MCC']:.4f}**.
   - **DANN Adversarial Alignment**: DANN achieves adversarial domain invariance across feature representations. D1 $\\to$ D3 DANN yields the highest ROC-AUC ({vr['D1_D3_DANN']['uncalibrated']['metrics']['ROC_AUC']:.4f}) among all experiments, but calibrated F1 ({d1_dann_c['F1']:.4f}) is comparable to the calibrated baselines.

---

## 4. Calibration Improvement Summary

### Table B — Impact of Threshold Calibration

{df_table_b.to_markdown(index=False)}

### Calibration Protocol

| Parameter | Value |
|-----------|-------|
| Calibration dataset | D3 calibration partition (571,563 samples) |
| Optimization metric | $\\text{{argmax}}\\,F_1(\\text{{calibration set}})$ |
| Search range | $\\theta \\in [0.01, 0.99]$, step = 0.01 |
| Test set involvement | **None** (zero leakage verified) |

### Selected Thresholds

| Experiment | Threshold (θ*) |
|------------|:--------------:|
| D1 Baseline | 0.63 |
| D2 Baseline | 0.01 |
| D1 CORAL | 0.92 |
| D2 CORAL | 0.68 |
| D1 DANN | 0.92 |
| D2 DANN | 0.42 |

---

## 5. Feature Ablation Study Results

### Table C — Ablation Study (D1 → D3, separate LightGBM models, 150 boost rounds)

{df_table_c.to_markdown(index=False)}

> **Note**: The ablation study trains separate LightGBM models (num_boost_round=150) for each feature subset. These are distinct from the primary experiment models (num_boost_round=200). Metrics should be compared only within the ablation study, not against the primary results table.

### Ablation Interpretation

Individual feature removal produces only small changes in F1 and MCC under the evaluated D1→D3 setting, indicating that the compact representation is relatively robust to removal of individual features. The `pkt_mean_to_max` removal variant slightly improves F1 ($\\Delta F_1 = +0.0004$) and MCC ($\\Delta \\text{{MCC}} = +0.0028$), suggesting that this feature is not independently essential for this particular transfer configuration. All changes are within $\\sim$0.003 F1 and $\\sim$0.003 MCC, indicating minimal practical significance.

Notably, `log_pkt_max` removal causes the largest PR-AUC drop (from 0.567 to 0.158), and `log_pkt_mean` removal drops PR-AUC from 0.567 to 0.423, suggesting these features influence probability ranking even when threshold-dependent metrics remain stable.

---

## 6. SHAP Feature Explainability Ranking

{pd.read_csv(RESULTS_DIR / 'shap/shap_feature_importance.csv').to_markdown(index=False)}

---

## 7. Probability Diagnostics

| Experiment | Min | Max | Mean | Median | Exact 0s | Exact 1s | NaN | Inf |
|------------|----:|----:|-----:|-------:|---------:|---------:|----:|----:|
"""

    prob_diag = validation["probability_diagnostics"]
    for exp_id in EXPERIMENT_IDS:
        d = prob_diag[exp_id]
        report_md += f"| {exp_id} | {d['min']:.6f} | {d['max']:.6f} | {d['mean']:.6f} | {d['median']:.6f} | {d['n_exact_zero']} | {d['n_exact_one']} | {d['n_nan']} | {d['n_inf']} |\n"

    report_md += f"""
---

## 8. Metrics Audit Summary

| Check | Status | Detail |
|-------|--------|--------|
| Log Loss | **FIXED** | All values were 0.0 due to numerical exception; recomputed with clipping |
| PR-AUC | **DOCUMENTED** | Primary vs ablation discrepancy explained by different models |
| ROC-AUC | **PASS** | Computed from raw probabilities, verified |
| Brier Score | **PASS** | Computed from raw probabilities, verified |
| ECE | **PASS** | 10 uniform bins, proportional weighting, verified |
| Calibration leakage | **NONE** | Threshold selection uses only D3 calibration set |
| Ablation interpretation | **FIXED** | "Synergistic contribution" claim removed (unsupported) |
| Test-set integrity | **PASS** | N = 714,453 verified for all experiments |
| Models requiring retraining | **NONE** | All saved predictions are valid |

---

## 9. Scientific Verdict

### Q1: Is the cross-domain generalization gap supported?
**YES.** All uncalibrated cross-domain transfers show F1 < 0.37 and MCC < 0.08, confirming severe performance degradation when transferring from IoT/network-flow domains to SCADA traffic.

### Q2: Does calibration materially improve target-domain performance?
**YES, for D2→D3 transfers.** D2→D3 baseline calibration improves F1 from 0.109 to 0.365 (ΔF1 = +0.256). D2→D3 DANN calibration improves F1 from 0.131 to 0.376 (ΔF1 = +0.245). For D1→D3, improvement is marginal (ΔF1 ≈ +0.003) since uncalibrated F1 is already near the calibrated ceiling.

### Q3: Does CORAL materially improve transfer?
**MARGINAL.** D2→D3 CORAL + calibration achieves the highest F1 (0.377) and MCC (0.079), but the improvement over the calibrated D2→D3 baseline is +0.012 F1 and +0.076 MCC. The improvement over calibrated DANN is +0.001 F1 and +0.003 MCC.

### Q4: Does DANN materially improve transfer?
**MIXED.** D1→D3 DANN shows the highest ROC-AUC (0.564) among all experiments, indicating better probability ranking. However, calibrated F1 and MCC are comparable to baselines. D2→D3 DANN + calibration achieves F1 = 0.376, comparable to CORAL.

### Q5: Which method performs best under the predefined primary metric?
**D2→D3 CORAL + calibration** achieves the highest F1 = 0.377 and highest MCC = 0.079 among all evaluated configurations.

### Q6: Does the four-feature representation require all four features?
**NOT for threshold-dependent metrics.** All 3-feature ablation variants achieve F1 and MCC at least as high as the full 4-feature model. However, `log_pkt_max` and `log_pkt_mean` significantly affect PR-AUC, indicating they contribute to probability ranking quality.

### Q7: Are the final metrics internally consistent and reproducible?
**YES.** After correcting Log Loss (from 0.0 to computed values), all metrics are internally consistent. Sample counts verify N=714,453 across all experiments. Confusion matrix sums are correct. ROC-AUC, PR-AUC, Brier, and ECE are all computed from raw probabilities.

---

## 10. Verification Checklist

- [x] D1, D2, D3 partitions frozen & untouched
- [x] Four-feature representation strictly enforced
- [x] Zero leakage into D3 final test set
- [x] Resumable checkpointing & JSON logging complete
- [x] Master Excel workbook generated (12 sheets)
- [x] Independent metrics validation completed
- [x] Log Loss corrected from 0.0 to computed values
- [x] Ablation interpretation corrected (synergy claim removed)
- [x] D1→D3 vs D2→D3 failure modes correctly distinguished
- [x] Final ZIP artifact archive created

---

*Report generated by ARGUS Phase 3 Corrected Report Generator on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.*
*Metrics independently validated by `validate_metrics.py`.*
"""

    report_path = RESULTS_DIR / "ARGUS_Phase3_Final_Report.md"
    with open(report_path, "w") as f:
        f.write(report_md)
    print(f"  Corrected report saved: {report_path}")

    # ── Regenerate ZIP ───────────────────────────────────────────────────────
    print("\n[5/5] Regenerating ZIP archive...")
    zip_path = RESULTS_DIR / "ARGUS_Phase3_Artifacts.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(RESULTS_DIR):
            for file in files:
                if file != "ARGUS_Phase3_Artifacts.zip":
                    full_p = Path(root) / file
                    rel_p = full_p.relative_to(RESULTS_DIR)
                    zipf.write(full_p, arcname=str(rel_p))

    zip_size = zip_path.stat().st_size / (1024 * 1024)
    print(f"  ZIP archive saved: {zip_path} ({zip_size:.2f} MB)")

    print(f"\n{'=' * 80}")
    print("ALL CORRECTED ARTIFACTS REGENERATED SUCCESSFULLY")
    print(f"{'=' * 80}")
    print(f"  Final Excel:  {excel_path}")
    print(f"  Final Report: {report_path}")
    print(f"  Final ZIP:    {zip_path}")
    print(f"  Validation:   {RESULTS_DIR / 'metrics_validation_report.json'}")
    print(f"  Validation:   {RESULTS_DIR / 'metrics_validation_report.md'}")


if __name__ == "__main__":
    main()
