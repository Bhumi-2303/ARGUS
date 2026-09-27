report = ["\n## E. Dedup History for CICIoT2023"]

report.append("Based on exhaustive repository scans (grepping for `drop_duplicates`, `dedup`, or `hash` across all scripts):")
report.append("We investigated the legacy scripts responsible for generating the specific CICIoT2023 splits (the 5,491,971 Train / 1,176,851 Test / 1,176,851 Adapt blocks).")
report.append("\n**Findings:**")
report.append("- No script that loads or splits the CICIoT2023 data employs deduplication logic prior to dividing the dataset.")
report.append("- **None found.** The only occurrences of `drop_duplicates` in the entire codebase were located in `experiments/analysis/feature_resolution_study.py:345` (which operates exclusively on the IEC104 target domain calibration set) and in `src/argus/agents/data_intelligence/tools/data_cleaner.py:35` (an LLM agent utility).")
report.append("\n**Implication:**")
report.append("Because no deduplication (hashing, `.drop_duplicates()`, or manual filtering) was applied to CICIoT2023 prior to `train_test_split()`, and we proved in Step 3 that the raw CICIoT2023 chunks contain a **51.04% duplicate rate**, the resulting splits are profoundly compromised. Massive numbers of identical feature vectors almost certainly span across the Training, Adaptation, Calibration, and Test splits, resulting in severe data leakage and artificially inflated accuracy metrics for any model trained on this pipeline.")

with open("reports/DG_DATA_AUDIT_addendum2.md", "a") as f:
    f.write("\n".join(report) + "\n")
print("Step E complete")
