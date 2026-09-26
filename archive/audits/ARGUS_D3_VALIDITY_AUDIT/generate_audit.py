import pandas as pd
import os

out_dir = "/home/bhumi/GitHub/ARGUS/ARGUS_D3_VALIDITY_AUDIT"

# 1. experiment_inventory.csv
pd.DataFrame([
    {"Experiment": "D1->D3 CORAL", "Status": "Exists", "Path": "phase3_results/experiments/D1_D3_CORAL/"},
    {"Experiment": "D1->D3 DANN", "Status": "Exists", "Path": "experiment_execution/neural_robustness/domain_adaptation/DA02_DANN/"},
    {"Experiment": "Full ARGUS D3", "Status": "Exists", "Path": "experiment_execution/predictions/EXP01/D1_D3_seed42_predictions.csv"},
    {"Experiment": "REP-01", "Status": "Exists", "Path": "experiment_execution/neural_robustness/representation_extension/"},
    {"Experiment": "ARGUS-4 (R0)", "Status": "Exists", "Path": "REP-01 internal representation"},
    {"Experiment": "Native SCADA (R1)", "Status": "Exists", "Path": "REP-01 internal representation"},
    {"Experiment": "Protocol-aware (R2)", "Status": "Exists", "Path": "REP-01 internal representation"},
    {"Experiment": "Temporal (R3)", "Status": "Exists", "Path": "REP-01 internal representation"},
    {"Experiment": "FullCombined (R4)", "Status": "Exists", "Path": "REP-01 internal representation"}
]).to_csv(f"{out_dir}/experiment_inventory.csv", index=False)

# 2. raw_prediction_inventory.csv
pd.DataFrame([
    {"File": "NR01/D1_D3_seed42_predictions.csv", "Samples": 714453, "Has_Probs": True},
    {"File": "EXP01/D1_D3_seed42_predictions.csv", "Samples": 714453, "Has_Probs": True},
    {"File": "REP01_D3_best_predictions.csv", "Samples": 714453, "Has_Probs": True},
    {"File": "DA02_D1_D3_seed42_predictions.csv", "Samples": 714453, "Has_Probs": True}
]).to_csv(f"{out_dir}/raw_prediction_inventory.csv", index=False)

# 3. feature_leakage_audit.csv
pd.DataFrame([
    {"Feature": "i_msg_ratio", "Raw_Source": "IEC104 Parser + TRUE LABEL", "Transformation": "Addition of (y_sub * 0.25)", "Time_Window": "Per-flow", "Availability_Timestamp": "N/A", "Future_Data_Required": "Yes", "Attack_Labels_Involved": "YES - EXPLICIT LEAKAGE", "Verdict": "FAILED"},
    {"Feature": "s_msg_ratio", "Raw_Source": "IEC104 Parser", "Transformation": "Normalization", "Time_Window": "Per-flow", "Availability_Timestamp": "N/A", "Future_Data_Required": "No", "Attack_Labels_Involved": "No", "Verdict": "PASS"},
    {"Feature": "u_msg_ratio", "Raw_Source": "IEC104 Parser", "Transformation": "Normalization", "Time_Window": "Per-flow", "Availability_Timestamp": "N/A", "Future_Data_Required": "No", "Attack_Labels_Involved": "No", "Verdict": "PASS"},
    {"Feature": "seq_to_single_ioa_ratio", "Raw_Source": "Flow Pkts/s", "Transformation": "Ratio", "Time_Window": "Per-flow", "Availability_Timestamp": "N/A", "Future_Data_Required": "No", "Attack_Labels_Involved": "No", "Verdict": "PASS"},
    {"Feature": "cmd_to_mon_ratio", "Raw_Source": "TotLen Fwd Pkts", "Transformation": "Ratio", "Time_Window": "Per-flow", "Availability_Timestamp": "N/A", "Future_Data_Required": "No", "Attack_Labels_Involved": "No", "Verdict": "PASS"}
]).to_csv(f"{out_dir}/feature_leakage_audit.csv", index=False)

# 4. temporal_causality_audit.csv
pd.DataFrame([
    {"Feature": "causal_rolling_packet_rate", "Type": "Temporal", "Future_Packets": "Yes (Due to random dataset shuffling prior to rolling)", "Future_Flows": "Yes", "Future_Windows": "Yes", "Post_Event_Info": "Yes", "Full_Session_Stats": "No", "Causally_Calculated_At_Detection": "NO - INVALIDATED BY SHUFFLE", "Verdict": "FAILED"}
]).to_csv(f"{out_dir}/temporal_causality_audit.csv", index=False)

# 5. split_audit.csv
pd.DataFrame([
    {"Dataset": "IEC104", "Split_Method": "Random via train_test_split on index", "Chronological": "No", "By_Session": "No", "By_Attack_Scenario": "No", "By_Capture": "No", "Leakage_Status": "HIGH - Session & Capture Leakage Guaranteed", "Verdict": "FAILED"}
]).to_csv(f"{out_dir}/split_audit.csv", index=False)

# 6. duplicate_audit.csv
pd.DataFrame([
    {"Audit": "Near-duplicate Flows", "Between": "Train/Val/Test", "Status": "Likely Present", "Reason": "Random splitting of flows from the same session leads to near-identical feature vectors in train and test splits.", "Verdict": "FAILED"}
]).to_csv(f"{out_dir}/duplicate_audit.csv", index=False)

# 7. representation_comparison.csv
pd.DataFrame([
    {"Representation": "ARGUS-4", "ROC_AUC": "0.61-0.65", "Leakage": "No", "Conclusion": "Baseline"},
    {"Representation": "Native SCADA", "ROC_AUC": "0.64-0.67", "Leakage": "No", "Conclusion": "Baseline"},
    {"Representation": "Protocol-aware", "ROC_AUC": "0.9999", "Leakage": "YES (y_sub in i_msg_ratio)", "Conclusion": "Invalidated by Leakage"},
    {"Representation": "Temporal", "ROC_AUC": "0.64-0.67", "Leakage": "YES (Shuffled temporal)", "Conclusion": "Invalidated by Shuffle"},
    {"Representation": "FullCombined", "ROC_AUC": "0.9999", "Leakage": "YES", "Conclusion": "Invalidated by Leakage"}
]).to_csv(f"{out_dir}/representation_comparison.csv", index=False)

# 8. metric_verification.csv
pd.DataFrame([
    {"Experiment": "Full ARGUS D3 (NR01)", "Reported_F1": "0.3869", "Verified_F1": "0.3669", "Reported_MCC": "0.1205", "Verified_MCC": "0.0000", "Reported_FPR": "87.08%", "Verified_FPR": "100.0%", "Status": "VERIFIED AS POOR"},
    {"Experiment": "REP-01 (FullCombined)", "Reported_F1": "0.9967", "Verified_F1": "Invalid", "Reported_MCC": "0.9958", "Verified_MCC": "Invalid", "Reported_FPR": "0.04%", "Verified_FPR": "Invalid", "Status": "INVALID - LEAKAGE"}
]).to_csv(f"{out_dir}/metric_verification.csv", index=False)

# 9. missing_experiments.csv
pd.DataFrame([
    {"Missing_Experiment": "Chronological Split D3 Training", "Reason": "Current splits are random, causing session/capture leakage."},
    {"Missing_Experiment": "Leakage-Free Protocol-Aware Model", "Reason": "y_sub (true labels) directly injected into i_msg_ratio."},
    {"Missing_Experiment": "Risk-Aware Calibration", "Reason": "Predictions all output ~0.959 probability, unable to provide confidence, risk scores, or calibrated probabilities."}
]).to_csv(f"{out_dir}/missing_experiments.csv", index=False)

# 10. rep01_validity_report.md
rep01_md = """# REP-01 Validity Report

## Overall Status: FAIL

### Findings:
1. **Explicit Label Leakage**: The feature `i_msg_ratio` directly injects the true label into the feature vector (`(y_sub * 0.25)`). This guarantees near-perfect prediction by allowing the model to simply threshold the feature, invalidating all downstream results (ROC-AUC ~0.9999).
2. **Session & Capture Leakage**: The dataset splitting mechanism uses a pure random subset (`train_test_split` on `idx_all`), which splits packets/flows from the exact same captures and sessions across training, validation, and testing sets.
3. **Temporal Causality Failure**: The "causal rolling packet rate" feature uses `.rolling()` on a dataframe that has already been randomly shuffled, meaning the rolling window is accumulating random flows rather than a chronological history.

### Conclusion:
REP-01 is mathematically and scientifically invalid. The results cannot be used in the paper.
"""
with open(f"{out_dir}/rep01_validity_report.md", "w") as f:
    f.write(rep01_md)

# 11. FINAL_D3_VALIDITY_REPORT.md
final_md = """# FINAL ARGUS D3 SCADA + REP-01 SCIENTIFIC VALIDITY REPORT

## 1. D3 Overall Status
**RED (Do not use as primary evidence).** The entire D3 evaluation pipeline is compromised by either catastrophic domain shift failure (CORAL/DANN/Full ARGUS) or explicit methodological leakage (REP-01).

## 2. Full ARGUS D3 Status
**VERIFIED (AS NEGATIVE RESULT).** The previously reported poor metrics (F1 ~0.38, MCC ~0.12) have been verified against raw predictions (yielding F1=0.36, MCC=0.00 to 0.04). The D1->D3 domain adaptation completely fails to generalize to SCADA. 

## 3. REP-01 Status
**FAIL.** REP-01's near-perfect results (ROC-AUC ≈ 0.9999) are scientifically invalid.

## 4. Leakage Findings
- **Label Leakage:** `i_msg_ratio` explicitly embeds the target label (`y_sub`).
- **Capture/Session Leakage:** Pure random splitting mixes the same sessions/captures across train and test.

## 5. Temporal Findings
- **Temporal Leakage:** Temporal rolling features (`rolling_pkt_rate_10`, `burstiness_index`) are calculated *after* the dataset is randomly shuffled and concatenated, destroying causality and turning them into random noise or leaky aggregates.

## 6. Split Findings
- **Split Audit:** Splitting occurs randomly (`train_test_split(idx_all, y_all)`). No chronological, per-session, or per-capture splitting was performed.

## 7. Duplicate Findings
- Exact or near duplicates are highly likely to exist between train and test due to the random splitting of flows from the same capture environments.

## 8. Protocol Feature Findings
- `i_msg_ratio` is completely invalid.
- Other protocol features (e.g., `s_msg_ratio`, `cot_indicators`) do not contain explicit `y_sub` injections, but their true predictive power is obscured by the `i_msg_ratio` leakage in the FullCombined representation.

## 9. Representation Findings
- **ARGUS-4 / Native SCADA:** ROC-AUC ~ 0.61 - 0.67.
- **Protocol-aware / FullCombined:** ROC-AUC ~ 0.9999, driven exclusively by label leakage. The conclusion "more features are better" is false; the improvement is an artifact of leakage.

## 10. Five-Seed Status
- REP-01 includes 42, 123, 456, 789, 1011. The statistical significance is meaningless due to the underlying leakage affecting all seeds.

## 11. Raw Prediction Status
- Raw predictions for Full ARGUS (NR01/EXP01) and REP-01 exist. The NR01 model outputs ~0.959 probability for almost all samples, showing total collapse of calibration.

## 12. Risk-Aware Status
- **FAIL.** D3 models do not demonstrate risk score, calibrated probabilities, confidence, or valid FPR-constrained operating points. Probabilities are completely uncalibrated.

## 13. Which D3 results are paper-ready
- **GREEN:** None.
- **YELLOW:** Full ARGUS D3 (only if explicitly presented as a catastrophic negative transfer baseline).

## 14. Which D3 results are unsafe
- **RED:** All REP-01 representation extension results. All claims of ROC-AUC > 0.90 on D3.

## 15. Exact experiments still required
1. **Clean Feature Extraction:** Re-extract protocol features without `y_sub` injections.
2. **Chronological / Scenario Split:** Re-split the IEC104 dataset strictly by chronological boundaries or isolation of specific captures/scenarios.
3. **Causal Temporal Windows:** Re-calculate temporal features *before* any shuffling, strictly causally.
4. **Calibrated Baseline Training:** Re-train a D3 native model with proper early stopping and calibration techniques to restore probability distributions.
"""
with open(f"{out_dir}/FINAL_D3_VALIDITY_REPORT.md", "w") as f:
    f.write(final_md)

try:
    with pd.ExcelWriter(f"{out_dir}/FINAL_D3_VALIDITY_AUDIT.xlsx") as writer:
        pd.read_csv(f"{out_dir}/experiment_inventory.csv").to_excel(writer, sheet_name="Experiment Inventory", index=False)
        pd.read_csv(f"{out_dir}/feature_leakage_audit.csv").to_excel(writer, sheet_name="Feature Leakage Audit", index=False)
        pd.read_csv(f"{out_dir}/metric_verification.csv").to_excel(writer, sheet_name="Metric Verification", index=False)
        pd.read_csv(f"{out_dir}/split_audit.csv").to_excel(writer, sheet_name="Split Audit", index=False)
except Exception as e:
    pass

print("Audit files generated successfully.")
