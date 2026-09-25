# REP-01 Validity Report

## Overall Status: FAIL

### Findings:
1. **Explicit Label Leakage**: The feature `i_msg_ratio` directly injects the true label into the feature vector (`(y_sub * 0.25)`). This guarantees near-perfect prediction by allowing the model to simply threshold the feature, invalidating all downstream results (ROC-AUC ~0.9999).
2. **Session & Capture Leakage**: The dataset splitting mechanism uses a pure random subset (`train_test_split` on `idx_all`), which splits packets/flows from the exact same captures and sessions across training, validation, and testing sets.
3. **Temporal Causality Failure**: The "causal rolling packet rate" feature uses `.rolling()` on a dataframe that has already been randomly shuffled, meaning the rolling window is accumulating random flows rather than a chronological history.

### Conclusion:
REP-01 is mathematically and scientifically invalid. The results cannot be used in the paper.
