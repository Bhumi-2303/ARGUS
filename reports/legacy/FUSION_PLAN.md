# ARGUS Day 4 Fusion Plan (Pre-Registration)

## Selection Metric
The primary metric for selecting the optimal strategy is **MCC (Matthews Correlation Coefficient) on the calibration split only**.

## Candidates
The following candidates will be evaluated on the calibration set:

*   **A: Source-only @ calibration threshold**: Predictions from the original source model, evaluated at the optimal threshold chosen on the calibration set.
*   **B: Clean Class-aware CORAL alone (Day 1)**: Predictions from the CORAL-adapted model alone.
*   **C: Drift-gated**: A dynamic strategy that uses the adapted model if the drift flag is triggered, otherwise falls back to the source model.
*   **D: Score average**: A weighted ensemble `w * p_source + (1 - w) * p_adapted`. The optimal weight `w` will be selected via grid search on the calibration set.
*   **E: Baselines**:
    *   **Always-predict-attack**: A naïve baseline always predicting the positive (attack) class.
    *   **Prevalence-matched random**: A baseline making random predictions according to the base rate (prior probability) of the attack class.

**Constraint:** The best candidate according to the calibration MCC will be selected for final evaluation. This plan is finalized prior to any test data access.
