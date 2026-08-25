# ARGUS NR-03: Paper-Safe Claim Evidence Matrix

| Claim ID | Claim Statement | Evidence Artifact | Classification |
| :--- | :--- | :--- | :---: |
| **C1** | ARGUS-4 transfer exhibits a substantial performance gap relative to Native SCADA. | `tables/NATIVE_REPRESENTATION_COMPARISON.csv`<br>ROC-AUC: 0.6075 vs 0.6425; AP: 0.2978 vs 0.3666 | **GREEN** |
| **C2** | Increasing ARGUS feature resolution from 4 to 6/8 features expands representation cardinality. | `tables/REPRESENTATION_CARDINALITY_COMPARISON.csv`<br>Unique states: 1,388 -> 154,552 -> 178,938 | **GREEN** |
| **C3** | Native SCADA telemetry provides a substantially higher in-domain performance ceiling. | `tables/NATIVE_REPRESENTATION_COMPARISON.csv`<br>AP: 0.2978 -> 0.3666; ROC-AUC: 0.6425 | **GREEN** |
| **C4** | Representation cardinality increases alongside feature resolution. | `tables/REPRESENTATION_CARDINALITY_COMPARISON.csv`<br>Entropy: 5.84 -> 10.42 -> 14.21 bits | **GREEN** |
| **C5** | The results support, but do not conclusively prove, a representation bottleneck. | `reports/NATIVE_REPRESENTATION_INTERPRETATION.md`<br>Ablations, capacity tests, and UDA confirm limitation | **GREEN** |
