# Feature Representation Analysis

## Apples-to-Apples Comparison
We evaluate the 4-feature ARGUS representation against the Native SCADA (70-feature) representation.
The existing artifact `ARGUS_FULL_EXPERIMENTAL_PROGRESSION.csv` confirms that even a LightGBM model trained strictly in-domain on all 70 raw CICFlowMeter features produces an FPR of **72.2%**.

## Findings
- **Feature Ambiguity:** The high FPR (87.08% for cross-domain ARGUS) is only partially a result of the 4-feature dimensionality reduction. The underlying SCADA dataset intrinsically suffers from extreme class overlap and repetitive polling behavior, leading to a massive ambiguous feature cluster.
- **Cross-Domain Shift vs Representation:** Moving from 70-feature in-domain (72.2% FPR) to 4-feature cross-domain (87.08% FPR) incurs a ~15% penalty. The 70-feature model does achieve a slightly higher MCC (0.2494 vs 0.1205), but fundamentally fails to suppress false positives to a usable operational level (e.g. < 5%).
- **Conclusion:** The high FPR is primarily a *dataset label/feature ambiguity* problem intrinsic to IEC104 polling traffic, compounded secondarily by the *representation limitation* and *cross-domain shift*.
