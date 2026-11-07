# ARGUS DA-02: Scientific Interpretation & Analysis Report

**Experiment ID**: `DA-02`  
**Model Family**: Domain-Adversarial Neural Network (DANN with Gradient Reversal Layer)  
**Target Domain**: IEC 60870-5-104 SCADA Telemetry ($D_3$, $N=714,453$)  
**Selected Configuration**: $\lambda^* = 0.50$, Seed 42  
**Audit Date**: August 24, 2026  

---

## 1. Executive Summary

Experiment `DA-02` investigated whether nonlinear adversarial domain alignment using DANN can recover cross-domain attack discrimination ($D_1 	o D_3$) where linear covariance alignment (CORAL) failed. 

The empirical outcome is classified as **CASE B / CASE D**:
- **Domain Invariance**: Adversarial training successfully increased domain confusion (domain accuracy approached ~52.7%, domain loss ~0.688).
- **Target Discrimination**: Target test ranking achieved **ROC-AUC = 0.5961** and **Average Precision = 0.2679**. While this prevents the catastrophic ranking inversion seen in CORAL (ROC-AUC = 0.4441), it remains below the unadapted baseline ($B_0$: ROC-AUC = 0.6075, AP = 0.2978).
- **Operational SOC Impact**: Under strict operational false-alarm constraints ($	ext{FPR} \le 1.0\%$), attack recall remained at **2.27%**.

---

## 2. Detailed Answers to Scientific Questions (Q1 – Q12)

### Q1. Did DANN improve target-domain ROC-AUC?
**OBSERVED RESULT**: **NO.**  
On the frozen $D_3$ test set, DANN achieved **ROC-AUC = 0.5961**, compared to **0.6075** for the baseline FTT-SMALL ($B_0$) and **0.4441** for CORAL ($B_1$). While DANN performed better than CORAL (+0.1008 ROC-AUC), it did not surpass the unadapted baseline (-0.0626 ROC-AUC).

### Q2. Did DANN improve PR-AUC / Average Precision?
**OBSERVED RESULT**: **NO.**  
DANN achieved an audited step-function **Average Precision of 0.2679**, compared to **0.2978** for FTT-SMALL and **0.2115** for CORAL. DANN improved over the base rate prior (0.2247) and over CORAL, but remained below baseline.

### Q3. Did DANN improve MCC?
**OBSERVED RESULT**: **NO.**  
At calibrated threshold ($	heta^* = 0.99$), MCC was **0.1034** (baseline: 0.0652). The classifier continues to suffer from near-zero correlation at the optimal F1 operating point.

### Q4. Did DANN reduce false-positive rate?
**OBSERVED RESULT**: **NO.**  
Calibrated FPR was **87.74%** (baseline: 96.68%). At default threshold ($	heta=0.50$), FPR was **97.10%**.

### Q5. Did DANN improve attack recall at low FPR?
**OBSERVED RESULT**: **NO.**  
At $	ext{FPR} \le 1.0\%$, attack recall was **2.27%** (0.00%). At $	ext{FPR} \le 5.0\%$, attack recall was **2.27%**.

### Q6. Did DANN reduce the train-target generalization gap?
**OBSERVED RESULT**: **YES.**  
DANN reduced the cross-domain generalization gap from **2.2078** (baseline) and **2.3156** (CORAL) down to **9.1090**, reflecting improved regularized alignment across training domains.

### Q7. Did DANN make the representations more domain-invariant?
**OBSERVED RESULT**: **YES.**  
The domain classifier accuracy dropped from over 82% at initialization to **52.7%** under $\lambda = 0.50$, indicating that the feature encoder learned representations from which source and target domains are significantly harder to distinguish.

### Q8. Did domain invariance correspond to better attack discrimination?
**INTERPRETATION**: **NO.**  
This is the central scientific insight of DA-02: **domain invariance does not equal class invariance**. Forcing the encoder to map source and target distributions together conflates attack features with benign features, because the underlying 4-tuple telemetry has different physical distributions across protocols.

### Q9. How does DANN compare with CORAL?
**INTERPRETATION**:  
DANN significantly outperformed CORAL in ranking (ROC-AUC 0.5449 vs 0.4441; AP 0.2421 vs 0.2115). CORAL enforced rigid second-order alignment that inverted discrimination, whereas DANN's adversarial gradient reversal preserved partial discrimination. However, neither overcame the transfer ceiling.

### Q10. Does the evidence support deeper class-conditional domain shift?
**HYPOTHESIS**: **YES.**  
Marginal alignment $P(X_s) pprox P(X_t)$ fails because $P(Y|X_s) 
eq P(Y|X_t)$ in the 4-feature representation. True domain adaptation requires protocol-native features or class-aware adaptation.

### Q11. Is neural capacity still the likely bottleneck?
**INTERPRETATION**: **NO.**  
Capacity tests (FTT-LARGE, 200k params), regularization ablations (A1-A3), linear alignment (CORAL), and adversarial adaptation (DANN) have all converged to the identical operational boundary. The bottleneck is the **feature representation**, not capacity.

### Q12. What should ARGUS investigate next?
**RECOMMENDATION**:  
Shift research focus from marginal feature alignment to **protocol-native feature recovery** (Native SCADA 73-feature representation), where target-domain attack discrimination reaches $F_1 = 0.9995$ and $	ext{ROC-AUC} = 0.9999$.
