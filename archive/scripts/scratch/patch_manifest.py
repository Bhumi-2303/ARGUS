with open("results/verified/MANIFEST.md", "r") as f:
    lines = f.readlines()

log_idx = 0
for i, l in enumerate(lines):
    if l.startswith("| **DANN ROC-AUC**"):
        log_idx = i
        break

new_row = "| **Source-only XGBoost Metrics** | **Manually appended** | **Missing row from 5-Model Comparison** | **`five_model_complete_comparison.csv` (2026-09-27)** — Discovered that the CSV was missing the Source-only XGBoost baseline entirely due to manual assembly of the CSV file. Restored metrics using `FINAL_D1_D2_AUDIT.md` as provenance (MCC = -0.031074). |\n"
lines.insert(log_idx, new_row)

with open("results/verified/MANIFEST.md", "w") as f:
    f.writelines(lines)
