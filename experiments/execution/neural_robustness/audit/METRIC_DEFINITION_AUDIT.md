# ARGUS Metric Definition & Methodological Audit

## 1. Continuous Ranking Metrics vs. Threshold-Dependent Operational Metrics

A fundamental principle of rigorous machine learning evaluation is the mathematical distinction between **ranking metrics** (which assess model discrimination across all decision thresholds) and **threshold-dependent metrics** (which evaluate operational decision performance at a single chosen threshold).

### Continuous Ranking Metrics

1. **ROC-AUC (Area Under the Receiver Operating Characteristic Curve)**:
   $$\text{ROC-AUC} = \int_{0}^{1} \text{TPR}(\text{FPR}) \, d\text{FPR} = P(S_{\text{pos}} > S_{\text{neg}})$$
   Evaluates the probability that a randomly chosen attack sample receives a higher predicted score than a randomly chosen benign sample. Invariant to class imbalance and monotonic score transformations.

2. **Average Precision ($AP$) — The Standard PR-AUC Definition**:
   $$AP = \sum_{n} (R_n - R_{n-1}) P_n$$
   Where $P_n$ and $R_n$ are the precision and recall at the $n$-th threshold. Computes the area under the PR curve using a step-function integral without linear interpolation between unobserved operational points.

3. **Trapezoidal PR-AUC (Linear Integration $\int P \, dR$)**:
   $$\text{PR-AUC}_{\text{trapz}} = \sum_{n} \frac{P_n + P_{n-1}}{2} (R_{n-1} - R_n)$$
   **Methodological Vulnerability**: In precision-recall space, linear interpolation between distant operating points is mathematically invalid because precision does not change linearly with recall (Davis & Goadrich, 2006). When discrete probability distributions cause large recall gaps (as occurred under label smoothing in A1), trapezoidal integration creates massive phantom area over unobserved regions.

### Threshold-Dependent Operational Metrics

For a given operational threshold $\tau$, predictions are binarized: $\hat{y} = \mathbb{I}(p \ge \tau)$.

- **$F_1$ Score**: $F_1 = \frac{2 \cdot \text{TP}}{2 \cdot \text{TP} + \text{FP} + \text{FN}}$
- **Precision**: $\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$
- **Recall (TPR)**: $\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$
- **False Positive Rate (FPR)**: $\text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$
- **False Negative Rate (FNR)**: $\text{FNR} = \frac{\text{FN}}{\text{FN} + \text{TP}}$
- **Matthews Correlation Coefficient (MCC)**:
  $$\text{MCC} = \frac{\text{TP} \times \text{TN} - \text{FP} \times \text{FN}}{\sqrt{(\text{TP}+\text{FP})(\text{TP}+\text{FN})(\text{TN}+\text{FP})(\text{TN}+\text{FN})}}$$
- **Accuracy**: $\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}$

### Generalization Gap
$$\text{Generalization Gap} = \mathcal{L}_{\text{val}}(\theta) - \mathcal{L}_{\text{train}}(\theta)$$
Measures the discrepancy between target calibration loss and source training loss at the selected model checkpoint.
