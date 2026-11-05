# ARGUS EXPERIMENT REGISTRY & REPRODUCIBILITY AUDIT

## Overview
The paper claims extensive multi-model Domain Generalization and Domain Adaptation using XGBoost, CORAL, DANN, etc.

## Experiment Status
1. **Source-Only XGBoost**: IMPLEMENTED BUT UNREPRODUCIBLE (Scripts like `generate_d1_d2_baselines.py` exist but postdate the results by >1 month, use different parameters, and don't match the README numbers).
2. **Global CORAL (XGBoost)**: NOT TRACEABLE (No script exists that trains XGBoost on CORAL-aligned data to produce the reported metrics).
3. **Clean Class-Aware CORAL (XGBoost)**: NOT TRACEABLE (Fabricated thresholding. The reported 0.99 threshold maximizes F1 only if probabilities are inverted. Normal optimization yields 0.01 threshold).
4. **DANN**: BROKEN / FABRICATED (The true checkpoint yields 0.3321 ROC-AUC, but the README reports 0.5226. The true metric was recorded 2 minutes before the README was authored).

## Verdict on Domain Generalization
**INVALID**. 
The repository exhibits catastrophic target-domain leakage (85-98% identical feature vectors). The target domains were used for calibration, threshold selection, and feature alignment. This violates the fundamental premise of Domain Generalization (unseen target).

## Verdict on Multi-Agent Integration
**NOT IMPLEMENTED**.
The ML experiments were executed as standalone python scripts. The agents were never experimentally validated as an integrated system processing these predictions.
