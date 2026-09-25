# FINAL ARGUS D3 SCADA + REP-01 SCIENTIFIC VALIDITY REPORT

## 1. D3 Overall Status
**RED (Do not use as primary evidence).** The entire D3 evaluation pipeline is compromised by either catastrophic domain shift failure (CORAL/DANN/Full ARGUS) or explicit methodological leakage (REP-01).

## 2. Full ARGUS D3 Status
**VERIFIED (AS NEGATIVE RESULT).** The previously reported poor metrics (F1 ~0.38, MCC ~0.12) have been verified against raw predictions (yielding F1=0.36, MCC=0.00 to 0.04). The D1->D3 domain adaptation completely fails to generalize to SCADA. 

## 3. REP-01 Status
**FAIL.** REP-01's near-perfect results (ROC-AUC ≈ 0.9999) are scientifically invalid.

## 4. Leakage Findings
- **Label Leakage:** `i_msg_ratio` explicitly embeds the target label (`y_sub`).
- **Capture/Session Leakage:** Pure random splitting mixes the same sessions/captures across train and test.

## 5. Temporal Findings
- **Temporal Leakage:** Temporal rolling features (`rolling_pkt_rate_10`, `burstiness_index`) are calculated *after* the dataset is randomly shuffled and concatenated, destroying causality and turning them into random noise or leaky aggregates.

## 6. Split Findings
- **Split Audit:** Splitting occurs randomly (`train_test_split(idx_all, y_all)`). No chronological, per-session, or per-capture splitting was performed.

## 7. Duplicate Findings
- Exact or near duplicates are highly likely to exist between train and test due to the random splitting of flows from the same capture environments.

## 8. Protocol Feature Findings
- `i_msg_ratio` is completely invalid.
- Other protocol features (e.g., `s_msg_ratio`, `cot_indicators`) do not contain explicit `y_sub` injections, but their true predictive power is obscured by the `i_msg_ratio` leakage in the FullCombined representation.

## 9. Representation Findings
- **ARGUS-4 / Native SCADA:** ROC-AUC ~ 0.61 - 0.67.
- **Protocol-aware / FullCombined:** ROC-AUC ~ 0.9999, driven exclusively by label leakage. The conclusion "more features are better" is false; the improvement is an artifact of leakage.

## 10. Five-Seed Status
- REP-01 includes 42, 123, 456, 789, 1011. The statistical significance is meaningless due to the underlying leakage affecting all seeds.

## 11. Raw Prediction Status
- Raw predictions for Full ARGUS (NR01/EXP01) and REP-01 exist. The NR01 model outputs ~0.959 probability for almost all samples, showing total collapse of calibration.

## 12. Risk-Aware Status
- **FAIL.** D3 models do not demonstrate risk score, calibrated probabilities, confidence, or valid FPR-constrained operating points. Probabilities are completely uncalibrated.

## 13. Which D3 results are paper-ready
- **GREEN:** None.
- **YELLOW:** Full ARGUS D3 (only if explicitly presented as a catastrophic negative transfer baseline).

## 14. Which D3 results are unsafe
- **RED:** All REP-01 representation extension results. All claims of ROC-AUC > 0.90 on D3.

## 15. Exact experiments still required
1. **Clean Feature Extraction:** Re-extract protocol features without `y_sub` injections.
2. **Chronological / Scenario Split:** Re-split the IEC104 dataset strictly by chronological boundaries or isolation of specific captures/scenarios.
3. **Causal Temporal Windows:** Re-calculate temporal features *before* any shuffling, strictly causally.
4. **Calibrated Baseline Training:** Re-train a D3 native model with proper early stopping and calibration techniques to restore probability distributions.
