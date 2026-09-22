# ARGUS — Autonomous Risk-aware Grid Understanding & Security

## Setup
1. Clone the repository and initialize a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. For the frontend dashboard, ensure Streamlit is installed:
   ```bash
   pip install streamlit
   ```

## How to Rebuild from Raw Data
To reproduce the entire pipeline (training models, fitting fusion parameters, and running final evaluation), run:
```bash
make reproduce
```
*(Ensure raw data is placed in the expected `DATA_DIR` before running).*

## How to Run Tests and the Demo
**Tests:**
Run the end-to-end and unit test suites via Pytest:
```bash
pytest tests/
```

**Demo:**
1. Start the FastAPI backend:
   ```bash
   uvicorn argus.api.main:app --reload
   ```
2. In a separate terminal, launch the Streamlit dashboard:
   ```bash
   streamlit run frontend/app.py
   ```

## Artifact Hashes (SHA-256)
- **xgb_source.json**: `3f8211df751beedd68531aaaac2c08bce594cf95e56b1b953d089b51183340e7`
- **xgb_adapted.json**: `ab786fd599a7bc09986e75df8c0d72705fa22f44cec14b14bc382b0e4b9b717f`
- **fusion.json**: `d368e68cc8b00420e0d2f41ab3e5b4f0e7cc022bad7f3a9af688e91781c0125a`

## Limitations
- A single static model is not sufficient to maintain high MCC across all domains simultaneously without adaptation or drift-gated switching.
- In some scenarios, a simple baseline (e.g., source only) remains strong in-domain, but falls short on the target domain.
- There is no calibrated risk score implemented.
- Evaluated strictly using 1 Source & 1 Target Dataset.
- System is designed for Batch Replay only (no real-time streaming constraints).
