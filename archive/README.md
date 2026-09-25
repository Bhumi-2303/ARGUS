# ARGUS Repository Archive

This directory contains archived legacy files, unneeded build artifacts, intermediate experiment scripts, backup model files, and the original Streamlit frontend application.

---

## Streamlit Frontend Deprecation & UI Features Inventory

The original Streamlit application (`archive/frontend/app.py`) was removed from active dependencies to transition to a modern FastAPI + React/Web frontend. Below is the complete specification of UI features present in the original Streamlit interface so they can be faithfully rebuilt in the new web frontend:

### Original Streamlit UI Features List
1. **Threat Monitoring Dashboard**:
   - Live security event ingestion log and status feed.
   - Attack severity indicators (Critical, High, Medium, Low) with color-coded risk pills.
   - Interactive timeline of detected network anomalies.
2. **Interactive Model Comparison Viewer**:
   - Side-by-side performance table for Source-Only, CORAL, and DANN models.
   - Dynamic ROC and PR curve visualization overlays.
   - Threshold slider allowing interactive inspection of Precision, Recall, F1, and FPR at arbitrary decision boundaries $\theta$.
3. **SHAP Feature Attribution Visualizer**:
   - Global feature importance bar chart (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`).
   - Per-sample waterfall / force plots showing feature contributions to specific flow predictions.
4. **Knowledge Retrieval Query Interface (RAG Agent)**:
   - Natural language search input box for querying smart-grid security documentation and MITRE ATT&CK techniques.
   - Formatted response display with source document citations.
5. **Risk Assessment Simulator**:
   - Interactive form to input manual network flow parameters (`Pkt Len Mean`, `Pkt Len Max`, `Header_Length`, TCP flags).
   - Real-time feature extraction and risk score output calculation.

---

## Contents of `archive/`

| Directory / File | Description | Reason for Archiving |
| :--- | :--- | :--- |
| `archive/frontend/` | Original Streamlit application files (`app.py`, components, styles) | Removed to decouple frontend UI from backend Python engine. Features inventoried above for new frontend rebuild. |
| `archive/scripts/` | One-off scratch, path-patching, and ad-hoc analysis scripts (`temp_*.py`, `fix_*.py`, `patch_*.py`) | Unused ad-hoc execution scripts superseded by canonical `src/argus/` package. |
| `archive/reports/` | Internal execution logs and daily development reports (`DAY_1_REPORT.md`, `RECIPE.md`, etc.) | Historical progress logs preserved for provenance; superseded by top-level `README.md` and `AUDIT.md`. |
| `archive/audits/` | Internal audit diagnostics (`ARGUS_D1_D2_AUDIT/`, `ARGUS_D3_VALIDITY_AUDIT/`, `ARGUS_PAPER_READINESS_AUDIT/`) | Historical audit workbooks preserved for verification. |
| `archive/zips/` | Standalone ZIP archives (`ARGUS_NR04_NATIVE_DELIVERABLES.zip`, `ARGUS_REP01_DELIVERABLES.zip`) | Redundant ZIP archives containing files extracted elsewhere. |
| `archive/backups/` | Secondary run folders and raw multi-gigabyte backup outputs (`ARGUS_Cross_Domain_Results/`, `phase3_results/`, `phase4_results/`) | Intermediate evaluation outputs preserved for full provenance; primary results consolidated into `results/verified/`. |
