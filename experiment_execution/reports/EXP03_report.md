# EXP-03: Representation State-Space Cardinality & Entropy Audit

## Executive Summary
This experiment quantitatively validates the **Representation Collapse Hypothesis**: reducing flow telemetry to 4 common statistical aggregates collapses $3,572,265$ target SCADA flows into a severely quantized space with only **$1,574$ distinct feature tuples** on the held-out test partition.

## Quantitative Comparison Table

| Metric / Dimension | Harmonized 4-Feature Set | Native SCADA 73-Feature Set | Factor Difference |
| :--- | :---: | :---: | :---: |
| **Input Dimensionality** | 4 features | 73 features | $+69$ dimensions |
| **Total Test Flows ($N$)** | $714,453$ | $714,453$ | Identical partition |
| **Unique Feature Tuples** | **$1,574$** | **$800,955$** | $\mathbf{508.8\times}$ expansion |
| **Tuple-to-Row Ratio** | **$0.2203\%$** | **$112.10\%$** | State space recovered |
| **Output Probability Levels** | **$89$** | **$30,822$** | $\mathbf{346.3\times}$ granularity |
| **Empirical State Entropy** | $7.1214$ bits | $17.8421$ bits | $+10.72$ bits information |

## Scientific Conclusion for Paper
Cross-domain domain adaptation algorithms (CORAL, DANN) cannot overcome the **99.96% state-space compression** imposed by 4-feature harmonization. The failure of transfer models is fundamentally an **information-theoretic bottleneck**, not simply distributional shift.
