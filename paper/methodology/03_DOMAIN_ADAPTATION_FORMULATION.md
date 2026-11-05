# Methodology Module 03: Domain Adaptation & Alignment Formulations

**Document Status**: Official Research Methodology Specification  
**Associated Manuscript**: Section III (Methodology & Mathematical Formulation)

---

## 1. Covariance Alignment (CORAL)

### 1.1 Global CORAL Formulation
Global Correlation Alignment (Sun & Saenko, 2016) seeks a linear transformation matrix $A \in \mathbb{R}^{d \times d}$ that aligns the second-order statistics (covariance) of source features $X_s \in \mathbb{R}^{n_s \times d}$ with target features $X_t \in \mathbb{R}^{n_t \times d}$.

Let the sample covariance matrices be:
$$C_s = \frac{1}{n_s - 1} (X_s - \mu_s)^T (X_s - \mu_s) + \lambda I$$
$$C_t = \frac{1}{n_t - 1} (X_t - \mu_t)^T (X_t - \mu_t) + \lambda I$$
where $\lambda = 10^{-5}$ is a Tikhonov regularization parameter ensuring positive definiteness.

The optimal whitening and re-coloring transformation matrix is:
$$A = C_s^{-1/2} C_t^{1/2}$$
where matrix square roots and inverses are computed via Singular Value Decomposition (SVD):
$$C = U \Sigma U^T \implies C^{1/2} = U \Sigma^{1/2} U^T, \quad C^{-1/2} = U \Sigma^{-1/2} U^T$$

The transformed source features are:
$$X_s^* = X_s A$$

### 1.2 Failure Mode: Specificity Collapse Under Class Imbalance
In network security datasets, class priors are severely imbalanced (e.g., D2 has $72.58\%$ attack flows). Global covariance is given by:
$$C_t = P_t(y=0) C_{t,0} + P_t(y=1) C_{t,1} + \sum_{c=0}^1 P_t(y=c) (\mu_{t,c} - \mu_t)(\mu_{t,c} - \mu_t)^T$$
Because $P_t(y=1) \gg P_t(y=0)$, the global covariance is heavily dominated by the attack manifold. Aligning marginal covariance minimizes overall distribution distance, but shears benign flows into the attack decision region, producing **specificity collapse** (Table IV: Specificity $= 2.44\%$, $\text{MCC} = -0.161$).

---

## 2. Class-Aware CORAL (Supervised Target Adaptation)

To overcome specificity collapse, ARGUS introduces **Class-Aware CORAL**, which aligns covariance structures conditioned on class labels $c \in \{0, 1\}$.

### Formulation
For each class $c$:
$$C_{s, c} = \frac{1}{n_{s, c} - 1} \sum_{i: y_{s, i} = c} (x_{s, i} - \mu_{s, c})(x_{s, i} - \mu_{s, c})^T + \lambda I$$
$$C_{t, c} = \frac{1}{n_{t, c} - 1} \sum_{j: y_{t, j} = c} (x_{t, j} - \mu_{t, c})(x_{t, j} - \mu_{t, c})^T + \lambda I$$

The class-conditional alignment operators are:
$$A_c = C_{s, c}^{-1/2} C_{t, c}^{1/2}$$

During training, class-specific transformations are applied to source partitions:
$$x_{s, i}^* = (x_{s, i} - \mu_{s, c}) A_c + \mu_{t, c}$$

### Leakage Controls
- **Diagnostic Variant**: Estimates $C_{t, c}$ using labels from the target test set. Reported *strictly as an explanatory diagnostic* to isolate the mechanism; excluded from all validity claims.
- **Clean Variant**: Estimates $C_{t, c}$ strictly on an independent target adaptation split ($\mathcal{D}_{\text{adapt}}$) without touching the frozen test set.

---

## 3. Bayesian Prior Shift Likelihood Ratio Correction

Transfer across network domains violates the covariate shift assumption ($P_s(y) \ne P_t(y)$). When source prior $P_s(y=1) = 0.9764$ is transferred to target prior $P_t(y=1) = 0.7258$ (or SCADA $0.2246$), unadjusted posterior probabilities are systematically biased toward attack.

Given a model outputting posterior estimate $\hat{P}_s(y=1|x)$, the Bayes-optimal target posterior $P_t(y=1|x)$ is recovered by likelihood ratio re-weighting:

$$P_t(y=1|x) = \frac{\hat{P}_s(y=1|x) \cdot \frac{P_t(y=1)}{P_s(y=1)}}{\hat{P}_s(y=1|x) \cdot \frac{P_t(y=1)}{P_s(y=1)} + (1 - \hat{P}_s(y=1|x)) \cdot \frac{P_t(y=0)}{P_s(y=0)}}$$

Target priors $P_t(y)$ are estimated on the calibration split ($\mathcal{D}_{\text{calib}}$) and applied at inference time.

---

## 4. Domain-Adversarial Neural Networks (DANN)

DANN (Ganin & Lempitsky, 2015) uses a minimax game between a feature extractor $G_f(\cdot; \theta_f)$, a label classifier $G_y(\cdot; \theta_y)$, and a domain discriminator $G_d(\cdot; \theta_d)$ coupled via a Gradient Reversal Layer (GRL):

$$\mathcal{R}(x) = x, \quad \frac{d\mathcal{R}}{dx} = -\alpha I$$

The joint optimization objective is:
$$\min_{\theta_f, \theta_y} \max_{\theta_d} \mathcal{L}_y(G_y(G_f(X_s)), Y_s) - \alpha \mathcal{L}_d(G_d(G_f([X_s, X_t])), D)$$

### DANN Empirical Behavior in ARGUS
Under severe tabular class imbalance, the domain discriminator forces $G_f$ to erase features that correlate with domain differences. Because attack and benign flows across D1 and D2 have distinct volumetric distributions, adversarial alignment inadvertently strips out class-discriminative signal, resulting in majority-class collapse ($\text{ROC-AUC} = 0.332$, $\text{MCC} = +0.013$).
