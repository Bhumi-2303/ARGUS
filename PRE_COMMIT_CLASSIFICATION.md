# Pre-Commit File Classification

| Path | Type | Size | Track? | Ignore? | Reason |
|------|------|------|--------|---------|--------|
| `ARGUS_HEALTH_CHECK/` | Documentation / Project Tooling | 12K | YES | NO | Contains `REPORT.md` and `requirements.txt` outlining the operational health and dependencies of the ARGUS project; valuable documentation. No secrets detected. |
| `final_eval_output.txt` | Temporary Console Log | 4.0K | NO | YES | Unstructured standard output dump from a temporary script execution. Not reproducible scientific data. No secrets detected. |
| `results/` | Scientific Research Artifacts | 200K | YES | NO | Contains structured, curated findings (`poster_results.csv`, confusion matrices, `POSTER_RESULTS_SUMMARY.md`) representing key deliverables for evaluation. Highly reusable for paper writing/reproducibility. No secrets detected. |
| `run1.csv` | Temporary Execution Output | 8.0K | NO | YES | Appears to be an ad-hoc local metrics dump from a single test run rather than a formalized, organized result set. Can be regenerated. No secrets detected. |
| `scratch/` | Temporary Tooling / Caches | 48K | NO | YES | Contains one-off Python scripts (`download_kaggle.py`, `profile_all.py`), bash wrappers, and partial JSON manifests built purely for immediate local dataset downloading/auditing. Clutters the root repo. No secrets detected. |

**Secret Scan**: Verified that none of the above files contain any hardcoded API keys, JWT tokens, AWS credentials, or other private secrets.
**Reproducibility**: The `results/` directory is the only path containing formalized, structured, and curated data that serves the long-term scientific record of the project.
