# ARGUS Model Provenance and Monitoring

This document details the lightweight mechanisms for model provenance tracking and batch drift monitoring implemented in ARGUS. These features guarantee that the deployment state of our models remains observable and scientifically valid without requiring heavy streaming infrastructure.

## Model Provenance

Every event processed by the ARGUS system explicitly tracks its provenance using the `Provenance` block in the canonical `ArgusEvent`. This guarantees that any generated decision or incident is traceable back to its originating scientific configuration.

Provenance metadata captured includes:
- `model_id` / `model_version`: Defines exactly which artifact was used.
- `training_dataset` / `training_date`: Traces back to the specific raw data snapshot.
- `feature_schema_version`: Ensures compatibility with the data pipeline.
- `adaptation_method`: Identifies cross-domain strategies applied (e.g., `CORAL`, `NONE`).
- `threshold` / `calibration_version`: Documents decision boundary metrics.
- `seed`: Random seed ensuring determinism.
- `artifact_reference`: URI to the physical model block (e.g., `phase3_results/models/model_d2_coral.txt`).

### Model Registry
We use a lightweight, static artifact registry located at `artifacts/models/registry.yaml`. This registry maps deployed models to their metadata, avoiding the need for heavy external tracking systems while providing a single source of truth for deployments.

## Drift & Domain-Aware Monitoring

Because ARGUS focuses heavily on cross-domain performance (e.g., training on IT/D1, testing on OT/D2), we implemented a domain-aware drift monitor.

Instead of heavy streaming telemetry, ARGUS uses **batch analysis utilities** (`src/argus/monitoring/drift.py`) designed to run over discrete temporal windows (e.g., daily or hourly batches) or directly against testing pipelines.

### Monitored Distributions
For a new batch of events relative to the reference registry, the system computes:
- **Feature Drift:** Calculated via absolute Z-score of mean shift relative to the reference distribution.
- **Prediction Drift:** Shifts in the classification boundary outputs.
- **Confidence Drift:** Distribution mapping of predicted probabilities (histograms).
- **Class-Prior Drift:** Distribution between `anomaly` and `benign` predictions.

### Output States
The drift analyzer computes scores and outputs one of three explicit warning states:
- **NORMAL**: Expected distribution.
- **WARNING**: Drift exceeds configurable warning thresholds. Requires observation.
- **CRITICAL**: Drift significantly exceeds thresholds. Investigation or re-training required.

*Thresholds are fully configurable via the `DriftConfig` class in `drift.py` without requiring scientifically unsupported hardcodes.*

## API and Frontend Exposition

The provenance registry and drift reports are exposed directly to the React frontend through lightweight FastAPI endpoints:
- `GET /api/v1/monitoring/registry`: Returns the fully parsed model registry.
- `GET /api/v1/monitoring/drift/{model_id}`: Computes and returns the `DriftReport` for a given deployed model, enabling the frontend's Analytics/Health views to consume live status warnings.

## Limitations
- Feature drift is currently tracked using mean-shift (Z-score). More robust statistical divergence metrics (e.g., JS-divergence, KS-tests) can be substituted in `drift.py` for deeper offline analysis.
- Currently, batch simulation is used in the `get_drift_status` API wrapper for demonstration. In a true production mode, it should execute SQL aggregations over the recent telemetry window.
