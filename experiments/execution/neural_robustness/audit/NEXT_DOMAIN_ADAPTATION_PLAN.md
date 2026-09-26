# ARGUS Stage 3: Domain Adaptation Experimental Protocol

**Status**: PREPARED — AWAITING EXPLICIT INVOCATION (DO NOT START TRAINING)
**Plan Generated**: 2026-08-23T08:15:13.728257+00:00

---

## 1. Experimental Rationale

The Metric Integrity Audit established that:
1. Capacity scaling (CAPACITY-01, CAPACITY-01R) fails to resolve transfer degradation.
2. Standard regularization and input noise (A1–A3) degrade target ranking (ROC-AUC $\le 0.5720$, $AP \le 0.2575$).
3. Transfer failure is fundamentally caused by **domain covariate shift and representation collapse**.

Therefore, the next research stage must evaluate explicit **domain adaptation and representation alignment** algorithms within the identical FT-Transformer model family.

## 2. Experimental Condition Matrix (B0–B3)

| Condition | Model Architecture | Adaptation Mechanism | Loss Function / Objective | Target Partition Used for Adaptation |
|---|---|---|---|---|
| **B0 (Baseline)** | FTT-SMALL (17.5k) | Preserved Unadapted Baseline | $\mathcal{L}_{\text{BCE}}(D_1)$ | None |
| **B1 (CORAL Alignment)** | FTT-SMALL (17.5k) | Feature Covariance Alignment (Deep CORAL) | $\mathcal{L}_{\text{BCE}}(D_1) + \lambda_{\text{coral}} \mathcal{L}_{\text{CORAL}}(D_1, D_3^{\text{adapt}})$ | $D_3$ Adaptation Split (Unlabeled) |
| **B2 (UDA / MMD)** | FTT-SMALL (17.5k) | Maximum Mean Discrepancy (MMD) | $\mathcal{L}_{\text{BCE}}(D_1) + \lambda_{\text{mmd}} \mathcal{L}_{\text{MMD}}(D_1, D_3^{\text{adapt}})$ | $D_3$ Adaptation Split (Unlabeled) |
| **B3 (DANN)** | FTT-SMALL (17.5k) | Domain-Adversarial Neural Network (Gradient Reversal) | $\mathcal{L}_{\text{task}} - \lambda_{\text{adv}} \mathcal{L}_{\text{domain}}$ | $D_3$ Adaptation Split (Unlabeled) |

## 3. Strict Scientific & Safety Controls

1. **Controlled Variables**:
   - Fixed model backbone: FT-Transformer ($d_{\text{token}}=32, n_{\text{blocks}}=2, n_{\text{heads}}=4, d_{\text{ff}}=64$).
   - Fixed feature set: ARGUS-4 (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`).
   - Fixed seeds: 42 (primary), followed by multi-seed validation if positive.
2. **Partition Discipline**:
   - Source Training: $D_1$ CICIoT2023 (`ciciot_train_features.csv`).
   - Unsupervised Adaptation: $D_3$ Adaptation (`iec104_train_adaptation.csv`, **LABELS STRIPPED**).
   - Target Calibration: $D_3$ Calibration (`iec104_train_calibration.csv`, for threshold selection).
   - **Target Test ($D_3$ Frozen)**: `iec104_test_features.csv` ($N=714,453$, **STRICTLY BLIND & FROZEN**).
3. **Stop Rule**: Do not train until explicit approval is granted.
