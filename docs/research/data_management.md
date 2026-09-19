# ARGUS Data and Artifact Management Policy

## 1. Datasets Used
ARGUS utilizes standard cybersecurity and IoT datasets for its multi-model evaluation, primarily:
- **CICIoT2023**
- **ToN_IoT**

## 2. Local Dataset Location
By default, the codebase expects datasets to be placed locally in the following directory structure:
- `training/data/raw/` (for unmodified, downloaded datasets)
- `training/data/processed/` (for cleaned, normalized, or extracted subsets)

## 3. Git Exclusion Rationale
Raw and processed datasets are strictly excluded from version control (via `.gitignore`). 
- **Size Limitations:** Git is not optimized for handling large binary files or massive CSVs, which severely impacts clone times and repository performance.
- **Data Privacy/Licensing:** Some datasets require agreements or have restrictions on redistribution.
- **Separation of Concerns:** The repository serves as the source of truth for the *methodology* and *code*, while data should be managed via dedicated storage solutions (e.g., S3, Zenodo, Hugging Face Hub).

## 4. Local Experiment Outputs
When experiments and model training scripts run, their artifacts are stored locally in designated untracked directories:
- `experiment_execution/**/predictions/` and `checkpoints/`
- `phase3_results/` and `phase4_results/`
- `artifacts/predictions/`
- `ARGUS_Paper_Data/`

## 5. Artifacts Suitable for Git
Only small, high-value assets should be committed to the repository:
- Source code, configurations (`pyproject.toml`, `.env.example`), and Dockerfiles.
- Small unit-test fixtures (`tests/fixtures/`) under 1MB.
- Aggregated metric reports (e.g., `test_results.txt`, `docs/`) and architecture diagrams.

## 6. Artifacts for External Storage
The following artifacts exceed Git limits and should be stored externally:
- Model weights and checkpoints (`.pt`, `.pkl`, `.onnx`, `.cbm`).
- Full prediction sets and probability distributions (large `.csv`, `.npy`).
- High-resolution or bulk explanation data (e.g., raw SHAP values in `5_SHAP_Values/`).
- Extensive log files and large archived `.zip` outputs.

## 7. Obtaining and Preparing Datasets
To replicate ARGUS experiments:
1. Download the CICIoT2023 and ToN_IoT datasets from their official academic sources.
2. Place the downloaded files into `training/data/raw/`.
3. Run the designated preprocessing scripts (e.g., `training/data/csv_loader.py` or equivalent pipelines) to generate the processed splits in `training/data/processed/`.

## 8. Ensuring Reproducibility
ARGUS experiments remain fully reproducible without hosting the data on GitHub because:
- **Versioned Scripts:** All preprocessing, feature engineering, and model training logic is explicitly versioned in Git.
- **Configuration Management:** Hyperparameters, random seeds, and pipeline steps are defined in configuration files or code constants.
- **Deterministic Workflows:** Following the documented data acquisition steps and running the tracked shell scripts (e.g., `run_multiseed_final.sh`) will yield equivalent datasets and identical experimental results.
