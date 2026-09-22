# ARGUS Day 5 Report: Demo and Packaging (Corrected)

## 1. FastAPI Integration
- **Claim:** Extended the existing FastAPI backend to include `POST /analyze` (returns orchestrator JSON) and `GET /health` (returns live uptime, timestamp, and SHA-256 model hashes).
- **Evidence:** 
  ```bash
  $ curl -s http://127.0.0.1:8001/health
  {"status":"healthy","uptime":3.1415,"timestamp":"2026-09-22T14:02:17+00:00","models":{"source":"3f8211df751beedd68531aaaac2c08bce594cf95e56b1b953d089b51183340e7","adapted":"ab786fd599a7bc09986e75df8c0d72705fa22f44cec14b14bc382b0e4b9b717f"}}
  ```
  *(Note: Hardcoded stubs in Day 5 initial attempt were replaced with live `time.time() - APP_START_TIME` and `datetime.now(timezone.utc)`).*

## 2. Dependencies & Project Packaging
- **Claim:** Pinned `pytest-asyncio==0.23.5` and `pydantic-settings==2.3.0` directly in `pyproject.toml`.
- **Evidence:** 
  ```toml
  [project]
  dependencies = [
      ...
      "pydantic-settings==2.3.0",
  ]
  [project.optional-dependencies]
  test = [
      "pytest-asyncio==0.23.5",
  ]
  ```
- **Finding:** The dependencies were never missing from the project specification (they were previously specified as `>=`). They were only missing from the initial `test_clean_clone.sh` run because that bash script bypassed `pyproject.toml` and ran a manual `pip install` list instead of `pip install -e .[test]`.

## 3. Clean-Clone Test & Backup Restoration
- **Claim:** The `test_clean_clone.sh` script was rewritten to execute a fully isolated `git clone`, run a native `pip install -e .[test]`, and restore artifacts via a newly created `make restore-artifacts` command.
- **Finding (Backup Created):** Because no Day 1 backup command was found in the history, a new `Makefile` was created to explicitly `tar` and `sha256sum` the artifacts.
- **Evidence (Test Failure):** 
  Running `bash scripts/test_clean_clone.sh` failed during the pip installation phase. Despite moving the massive `torch` dependency to an optional `[dann]` extra, the core installation still exhausted the system disk quota (`[Errno 122] Disk quota exceeded`) while building the wheel and unpacking other large packages (like `catboost`, `xgboost`, and `llvmlite`). 
  Because this step fails, **Day 5 cannot be marked complete.**

## 4. Model Format Substitution
- **Finding:** The models existing in the repository prior to Day 4 (e.g., `artifacts/models/model_d1_baseline.txt`) were LightGBM models (`tree\nversion=v4`), contradicting the Day 1 recipe that requested XGBoost.
- **Correction:** The Day 4 `scripts/fit_fusion.py` script was built to strictly train native XGBoost models (`xgb_source.json` and `xgb_adapted.json`) from the raw features rather than loading the legacy LightGBM artifacts. Because the Day 4 evaluation and `RESULTS.md` were generated exclusively using these new XGBoost models, there is no difference in the metrics.
