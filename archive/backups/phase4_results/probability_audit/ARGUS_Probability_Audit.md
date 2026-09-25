# ARGUS Probability Audit Report

## A. Probability integrity: PASS
The stored Full ARGUS probability outputs are valid 64-bit floating-point arrays with values strictly bounded in $[0.008578, 0.959224]$. No NaN, inf, or out-of-bounds probability values exist.

## B. Fusion integrity: PASS
Multi-source probability fusion is executed on continuous probabilities ($P_{\text{fused}} = w_1 P_{D1} + w_2 P_{D2}$ with $w_1=0.9, w_2=0.1$). It operates on un-thresholded floating-point prior-corrected outputs.

## C. Prior correction integrity: PASS
Bayesian prior correction ($P_T(Y|X) \propto P_S(Y|X) \frac{P_T(Y)}{P_S(Y)}$) is implemented using continuous floating-point operations. Probability normalization is exact ($P_T(Y=1|X) + P_T(Y=0|X) = 1.0$).

## D. Calibration integrity: PASS
Calibration is performed via empirical target threshold optimization on the calibration distribution ($N=571,563$). Probability distributions remain continuous floating-point values throughout.

## E. Pre-thresholding detected: NO
Comprehensive code-path inspection confirmed zero instances of `round()`, `astype(int)`, `argmax()`, or boolean mask pre-thresholding prior to metric calculation.

## F. Probability concentration
The probability output is **highly quantized in practice** due to the low cardinality of the 4-tuple network packet feature set (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`). In the 571,563-sample calibration set, there are only **1,574 unique feature combinations**, resulting in **185 unique fused probability values**.

## G. Threshold discontinuity
In the transition region $[0.4900, 0.5100]$, there are only three distinct probability values:
1. $p_1 = 0.49766751$
2. $p_2 = 0.50128340$
3. $p_3 = 0.50413849$

Because no probability predictions fall between $0.497668$ and $0.501283$, **all thresholds in the range $\theta \in [0.4977, 0.5012]$ produce identical predictions**. Crossing $\theta = 0.5013$ jumps across a massive cluster of $484,775$ samples (84.8% of the dataset), causing the sharp drop in recall from $96.17\%$ to $11.37\%$.

## H. Corrected Full ARGUS result
No pipeline bug was found. The original Phase 4 Full ARGUS result remains mathematically and empirically valid:
- **F1**: $0.3869$
- **MCC**: $0.1205$
- **Recall**: $96.08\%$
- **Precision**: $24.23\%$
- **FPR**: $87.08\%$
- **FNR**: $3.92\%$
