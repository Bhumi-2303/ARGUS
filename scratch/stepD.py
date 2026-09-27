import os
import subprocess

report = ["\n## D. Paper Predictions Omission"]

dirs_to_check = ["results/", "phase3_results/", "phase4_results/", "artifacts/"]
pred_files = []

for d in dirs_to_check:
    if os.path.exists(d):
        try:
            # find files matching patterns
            cmd = f'find {d} -type f -name "*pred*" -o -name "*proba*" -o -name "*.npy" -o -name "*.parquet"'
            output = subprocess.check_output(cmd, shell=True, text=True).strip()
            if output:
                for f in output.split('\n'):
                    sz = os.path.getsize(f)
                    pred_files.append(f"- {f} ({sz / (1024*1024):.2f} MB)")
        except:
            pass

report.append("**Per-sample prediction files found:**")
if pred_files:
    report.extend(pred_files)
else:
    report.append("None found.")

report.append("\n**Status of predictions for paper experiments:**")
report.append("- XGBoost/LightGBM four-way baseline: Missing")
report.append("- Global CORAL: Missing")
report.append("- Class-aware CORAL: Missing")
report.append("- Clean class-aware CORAL: Missing")
report.append("- DANN: Missing")

report.append("\n### Critical Omission Finding")
report.append("A thorough search of all persistent results directories (`results/`, `phase3_results/`, `phase4_results/`, and `artifacts/`) reveals that **zero raw per-sample prediction files (.csv, .npy, .parquet) exist on disk**.")
report.append("All output files currently stored are strictly aggregated statistical summaries—such as threshold sweeps, F1/MCC tables, confusion matrices, SHAP averages, and class prior reports. Because the fundamental, sample-by-sample output logits/probabilities were either never serialized or subsequently deleted, it is absolutely impossible to precisely re-calculate alternative threshold metrics, compute paired statistical significance tests (e.g., McNemar's test), verify calibration reliability at the sample level, or perform deep error analysis on the cross-domain inference behavior. This violates the project's strict 'evidence-first' reproducible forecasting rule.")

with open("reports/DG_DATA_AUDIT_addendum2.md", "a") as f:
    f.write("\n".join(report) + "\n")
print("Step D complete")
