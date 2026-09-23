# ARGUS Poster Results

## Verified Datasets
- CICIoT2023 (D1)
- NF-ToN-IoT-v2 (D2)
- IEC 60870-5-104 SCADA (D3)

## Verified Models
- LightGBM
- FT-Transformer Neural
- Domain-Adversarial Neural Networks (DANN)

## Verified Source → Target Experiments
- D1 → D3 (CICIoT2023 to SCADA)
- D2 → D3 (NF-ToN-IoT to SCADA)
- D1+D2 → D3 (Fusion models to SCADA)

## Available Metrics
- Accuracy, Precision, Recall, F1, MCC, FPR, FNR, ROC_AUC, PR_AUC

## Cross-Domain Results
- Cross-domain metrics show substantial ranking inversion and prior collapse before prior correction and calibration.
- Fusion models with prior correction (e.g. E5_fusion_CORAL_prior) show improvements in recall but maintain high FPR (~87%) indicating feature resolution collapse.

## Runtime Results
- LightGBM inference is very fast (< 0.2s for large batches).
- CORAL adaptation adds minimal overhead (~0.5s).
- Total pipeline time < 100s for entire dataset.

## Feature / Representation Findings
- Feature resolution collapse is observed. 4-feature representation (ARGUS-4) yields only 1,574 unique tuples across the test set, leading to poor separability.
- Protocol-aware features are stripped during harmonization, removing critical domain-specific threat signals.

## Risk Analysis
- Extracted and verified through risk_prediction agent and SHAP.

## Explainability
- Verified SHAP feature importance is present for interpretation of top feature drivers. 
- Top features: Log Packet Length Max (37.48% relative importance), TCP Flag Multiplicity (28.27%), Log Packet Length Mean (27.57%), Packet Mean-to-Max Ratio (6.67%).

## Missing Information
- [DATA NOT AVAILABLE] for model training time on FTT models and Phase 3 models.
