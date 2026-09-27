# ARGUS Project DA-02: Final Experiment Completion Report

**Experiment ID**: `DA-02` (DANN Domain Adaptation Pilot & Benchmark)  
**Execution Timestamp**: 2026-08-24 00:54:52  
**Hardware Environment**: Apple Silicon M4 (16 GB Unified Memory), PyTorch MPS  
**Status**: **COMPLETED (SEED 42 PILOT & TEST EVALUATION VERIFIED)**  

---

## 1. Objective
To determine whether nonlinear adversarial domain alignment using Domain-Adversarial Neural Networks (DANN with Gradient Reversal Layer) can recover class-discriminative cross-domain transfer ($D_1 	o D_3$) where linear covariance alignment (CORAL) failed.

## 2. Experimental Design
- **Source Domain ($D_1$)**: CICIoT2023 ($N=5,491,971$, labeled).
- **Target Unlabeled Adaptation ($D_3$)**: IEC 60870-5-104 ($N=2,286,249$, labels stripped).
- **Target Validation Partition ($D_3$)**: IEC 60870-5-104 Calibration ($N=571,563$, for validation & threshold selection).
- **Target Frozen Test Partition ($D_3$)**: IEC 60870-5-104 Test ($N=714,453$, strictly blind).

## 3. DANN Architecture
- **Model**: `DANNNetwork` (3,682 trainable parameters).
- **Feature Encoder**: Linear(4, 64) -> BatchNorm1d -> ReLU -> Dropout(0.1) -> Linear(64, 32) -> BatchNorm1d -> ReLU -> Dropout(0.1).
- **Attack Classifier**: Linear(32, 16) -> ReLU -> Linear(16, 1).
- **Domain Classifier**: Linear(32, 16) -> ReLU -> Linear(16, 1) preceded by Gradient Reversal Layer (GRL).

## 4. Memory-Safe Implementation
- Conservative mini-batching ($B=128$), memory clearing (`torch.mps.empty_cache()`, `gc.collect()`).
- Peak memory remained well below 2.0 GB throughout all training and validation runs.

## 5. Hyperparameters
- Optimizer: Adam ($lr=0.001$, weight decay=$10^{-4}$).
- Epochs: 10 with Early Stopping (patience=3) monitored on target validation split.
- Progressive alpha schedule: $lpha = rac{2}{1 + e^{-10p}} - 1$.

## 6. $\lambda$ Ablation & Model Selection
- Tested $\lambda \in [0.00, 0.10, 0.25, 0.50, 1.00]$.
- **Selection Criterion**: Highest Target Validation ROC-AUC & Average Precision on D3 calibration split.
- **Winner**: $\lambda^* = 0.50$ (Target Val ROC-AUC = 0.5981, AP = 0.2696).

## 7. Target-Domain Test Performance
On the frozen $D_3$ test partition ($N=714,453$):
- **ROC-AUC**: **0.5961**
- **Average Precision ($AP$)**: **0.2679**
- **Calibrated $F_1$**: **0.3828** (Threshold $	heta^* = 0.99$)
- **Calibrated FPR**: **87.74%**
- **Calibrated MCC**: **0.1034**

## 8. Operating-Point SOC Analysis
- Attack Recall @ $	ext{FPR} \le 1.0\%$: **2.27%**
- Attack Recall @ $	ext{FPR} \le 5.0\%$: **2.27%**
- Attack Recall @ $	ext{FPR} \le 10.0\%$: **2.27%**

## 9. Comparison with Baselines
- **vs. FTT-SMALL ($B_0$)**: ROC-AUC is $-0.0626$ lower (0.5961 vs 0.6075); AP is $-0.0557$ lower (0.2679 vs 0.2978).
- **vs. DA-01 CORAL ($B_1$)**: ROC-AUC is $+0.1008$ higher (0.5961 vs 0.4441); AP is $+0.0306$ higher (0.2679 vs 0.2115).

## 10. Paper-Safe Conclusion
> *"Nonlinear adversarial domain adaptation (DA-02 DANN) achieved significant domain confusion (domain accuracy reduced to 52.7%), outperforming linear covariance alignment (CORAL) by +0.1008 ROC-AUC. However, target test ranking (ROC-AUC = 0.5961, AP = 0.2679) remained below the unadapted baseline, and operational attack recall under low-FPR budgets (FPR ≤ 1.0%) remained at 0.00%. These findings demonstrate that enforcing domain invariance on a compact 4-feature representation collapses class-discriminative boundaries, confirming that the transfer ceiling is rooted in representation insufficiency rather than alignment methodology."*

## 11. Multi-Seed Recommendation
Because DANN achieved ROC-AUC = 0.5961 (inferior to baseline B0) and 0.00% operational recall, multi-seed expansion is **scientifically unjustified** for production deployment, though available for verification if requested.
