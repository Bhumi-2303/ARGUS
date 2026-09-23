# DAY 1 REPORT: Pipeline Reconstruction

## Completed Tasks
1. **Preflight**: Python 3.14.7 active. Successfully imported `xgboost`, `lightgbm`, `sklearn`, `pandas`, `pyarrow`, and `shap` natively without issues.
2. **Recipe Recovery**: Recovered the frozen feature formulas, data splitting mechanism (80/20 train split stratifying on seed 42), the hyperparameters for XGBoost, and the Max MCC threshold rule. Documented in `RECIPE.md`. 

## BLOCKED: Missing Data (Rule 4)
According to the standing rule: *"If a file you need is missing, stop and report exactly what is missing."*

I cannot proceed to Step 3 (Build) because the raw source datasets were purged from the git repository (via `ARGUS_HISTORY_REMOVE.txt`) and your prompt passed `[PATH]` placeholders.

### What you need to do:
Please download the raw datasets and place them in the correct data directory so the pipeline can process them natively:
1. **CICIoT2023 Raw Data**: Place the CSV files into `training/data/raw/CICIoT2023/`
2. **NF-ToN-IoT-v2 Raw Data**: Place the CSV files into `training/data/raw/NF-ToN-IoT-v2/`

Once they are downloaded and placed there, pass me the explicit paths so I can resume from Step 3!

## Files Produced
- `RECIPE.md` (Contains exact answers for 2a, 2b, 2c, 2d).

## Open Issues
- Waiting for raw dataset downloads.
- `MANIFEST.sha256` not updated yet as no new artifacts have been built.
