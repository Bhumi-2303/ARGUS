# Methodology Module 04: Evaluation Protocols, Metrics & Operational Constraints

**Document Status**: Official Research Methodology Specification  
**Associated Manuscript**: Section IV (Setup) & Section V-E (Operational Constraints)

---

## 1. Metrics for Imbalanced Network Defense

Conventional accuracy is deceptive in network intrusion detection due to severe class imbalance. ARGUS enforces three balanced, threshold-independent and threshold-dependent evaluation metrics:

### 1.1 Matthews Correlation Coefficient (MCC)
The definitive single-number metric for binary classification on imbalanced data:
$$\text{MCC} = \frac{\text{TP} \times \text{TN} - \text{FP} \times \text{FN}}{\sqrt{(\text{TP} + \text{FP})(\text{TP} + \text{FN})(\text{TN} + \text{FP})(\text{TN} + \text{FN})}} \in [-1, +1]$$
- $\text{MCC} = +1.0$: Perfect classification.
- $\text{MCC} = 0.0$: No better than random coin tossing.
- $\text{MCC} < 0.0$: Inverse prediction (worse than random chance).

### 1.2 Balanced Accuracy (BAcc)
The arithmetic mean of sensitivity and specificity:
$$\text{BAcc} = \frac{1}{2} \left( \frac{\text{TP}}{\text{TP} + \text{FN}} + \frac{\text{TN}}{\text{TN} + \text{FP}} \right) = \frac{\text{Recall} + \text{Specificity}}{2}$$

### 1.3 Area Under the Precision-Recall Curve (PR-AUC / Average Precision)
More sensitive to minority class performance than ROC-AUC:
$$\text{PR-AUC} = \sum_{k} (R_k - R_{k-1}) P_k$$

---

## 2. Operational False-Positive Rate Budgets ($\text{FPR} \le \alpha$)

In Security Operations Centers (SOCs), analyst triage capacity is strictly limited. A model with $F1 = 0.90$ that incurs a $5\%$ false-positive rate generates thousands of spurious alerts per hour, causing alert fatigue.

ARGUS evaluates **Attack Recall at Fixed False-Positive Rate Budgets**:
$$\text{Recall}@\text{FPR}_{\alpha} = \max_{\tau \in [0, 1]} \left\{ \frac{\text{TP}(\tau)}{\text{TP}(\tau) + \text{FN}(\tau)} \quad \text{subject to} \quad \frac{\text{FP}(\tau)}{\text{FP}(\tau) + \text{TN}(\tau)} \le \alpha \right\}$$
where budgets are evaluated at:
- $\alpha = 0.1\%$ (Strict SOC tier)
- $\alpha = 0.5\%$ (Moderate tier)
- $\alpha = 1.0\%$ (Tolerable tier)
- $\alpha = 5.0\%$ (Permissive tier)

---

## 3. Statistical Significance & Uncertainty Protocols

### 3.1 Multi-Seed Stability
- D3 FT-Transformer experiments are evaluated across 5 independent random initialization seeds ($S \in \{42, 101, 202, 303, 404\}$).
- Metrics are reported as $\text{Mean} \pm \text{Standard Deviation}$ (Table VI).

### 3.2 Cluster-Bootstrap Resampling
Because network flows exhibit temporal autocorrelation and coordinate correlation (identical IP/port pairs), standard random row bootstrapping underestimates variance.
- **Protocol**: Flows are grouped by (Source IP, Destination IP, Port) coordinates. Resampling is performed with replacement across clusters ($B = 1,000$ iterations) to construct 95% empirical confidence intervals:
  $$\text{CI}_{95\%} = [\hat{\theta}_{(0.025)}, \hat{\theta}_{(0.975)}]$$

### 3.3 DeLong Paired ROC Tests
To determine whether ROC-AUC differences between transfer and native models are statistically significant, paired DeLong tests are evaluated on identical test set predictions:
$$Z = \frac{\widehat{\text{AUC}}_1 - \widehat{\text{AUC}}_2}{\sqrt{\mathbb{V}(\widehat{\text{AUC}}_1) + \mathbb{V}(\widehat{\text{AUC}}_2) - 2 \mathbb{C}(\widehat{\text{AUC}}_1, \widehat{\text{AUC}}_2)}}$$

---

## 4. SHAP Feature Attribution Protocol

Model explainability is evaluated using TreeSHAP (Lundberg & Lee, 2017) to compute Shapley attribution values:
$$f(x) = \phi_0 + \sum_{i=1}^M \phi_i(x)$$
- **Global Importance**: Mean absolute SHAP value across samples: $I_j = \frac{1}{N} \sum_{k=1}^N |\phi_j(x_k)|$.
- **Attribution Disconnect Metric**: Measures the rank correlation between source domain SHAP attribution and empirical target domain feature gain:
  $$\rho_{\text{disconnect}} = 1 - r_s(\text{Rank}(\text{SHAP}_{\text{source}}), \text{Rank}(\text{Gain}_{\text{target}}))$$
  A high disconnect ($\rho \approx 1.0$) confirms that features considered crucial by source models fail to provide discriminative utility in target networks.
