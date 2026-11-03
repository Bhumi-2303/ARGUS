# ARGUS Repository Follow-Up Audit Report & Verification Log

**Date**: September 25, 2026  
**Repository**: ARGUS (`c:\Users\acer\Desktop\ARGUS`)  
**Scope**: Project-wide correctness audit for hardcoded metrics, fallback values, and invented labels across `src/argus/api`, `src/argus/data`, and `web/src`.

---

## 1. Findings & Verification Log

| Finding ID | Finding Description | File | Before (Hardcoded / Fallback) | After (Wired / Verified State) | Verified Source File / Action | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F-01** | `SystemOverviewPage` Clean CORAL tile hardcoded text | [`SystemOverviewPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/system_overview/SystemOverviewPage.tsx#L150) | `"0.99 Threshold"` | Dynamically read `threshold` property from API `/api/v1/models` (`model_d2_coral`) | [`results/verified/five_model_complete_comparison.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/five_model_complete_comparison.csv#L4) | **FIXED** |
| **F-02** | `ModelComparisonPage` hardcoded `rawRows` fallback mock data array | [`ModelComparisonPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/benchmark/ModelComparisonPage.tsx#L60) | Hardcoded objects (`accuracy: 0.8842`, `f1: 0.9120`, `mcc: 0.7203`, `accuracy: 0.9520`, `accuracy: 0.9780`, `accuracy: 0.9310`) | Removed fallback array; render `<Skeleton>` or `REQUIRES VERIFICATION` error panel when API query fails | [`results/verified/five_model_complete_comparison.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/five_model_complete_comparison.csv) | **FIXED** |
| **F-03** | `ModelComparisonPage` DANN warning alert hardcoded MCC string | [`ModelComparisonPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/benchmark/ModelComparisonPage.tsx#L156) | `"MCC: 0.0000"` | Dynamically display `(dannRow.mcc).toFixed(4)` (`0.0129`) from `dann_final_test_metrics.csv` | [`results/verified/dann_final_test_metrics.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/dann_final_test_metrics.csv#L8) | **FIXED** |
| **F-04** | `ModelComparisonPage` diagnostic fallback values | [`ModelComparisonPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/benchmark/ModelComparisonPage.tsx#L440) | `dRow.mcc ?? 0.812`, `dRow.f1_score ?? 0.895`, `dRow.fpr ?? 0.082` | Removed fallbacks; display `REQUIRES VERIFICATION` badge if metric is missing | [`results/diagnostic/diagnostic_class_aware_coral.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/diagnostic/diagnostic_class_aware_coral.csv) | **FIXED** |
| **F-05** | `DomainShiftPage` hardcoded domain classifier accuracy | [`DomainShiftPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/shift/DomainShiftPage.tsx#L207) | `selectedDomain === 'nfton' ? 0.9842 : 0.9615` | Replaced with `REQUIRES VERIFICATION` state badge as no offline discriminator artifact exists | Flagged `REQUIRES VERIFICATION` | **REQUIRES VERIFICATION** |
| **F-06** | `DomainShiftPage` hardcoded class conditional line series data | [`DomainShiftPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/shift/DomainShiftPage.tsx#L87) | `[0.12, 0.45, 0.68, 0.82]`, `[0.35, 0.88, 0.92, 0.98]` | Dynamically plot KS statistic and PSI drift metrics returned from `/api/v1/shift` | [`src/argus/api/routers/shift.py`](file:///c:/Users/acer/Desktop/ARGUS/src/argus/api/routers/shift.py) | **FIXED** |
| **F-07** | `ExplainabilityPage` hardcoded SHAP result fallback object | [`ExplainabilityPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/explain/ExplainabilityPage.tsx#L47) | Hardcoded `base_value: 0.124`, `shap_values: { tcp_flag_density: 0.385, ... }` | Trigger `/api/v1/explain` on initial mount to fetch real SHAP attributions from model explainer | [`results/verified/SHAP_vs_Target_Gain.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/SHAP_vs_Target_Gain.csv) | **FIXED** |
| **F-08** | `ExplainabilityPage` hardcoded fallback array for SHAP vs Target Gain table | [`ExplainabilityPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/explain/ExplainabilityPage.tsx#L242) | Hardcoded fallback array `[{ feature: 'tcp_flag_density', source_gain: 14250, ... }]` | Render `<Skeleton>` when loading; if table missing display `REQUIRES VERIFICATION` | [`results/verified/SHAP_vs_Target_Gain.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/SHAP_vs_Target_Gain.csv) | **FIXED** |
| **F-09** | `OverviewPage` tile 4 hardcoded DANN MCC string | [`OverviewPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/overview/OverviewPage.tsx#L287) | `"MCC 0.0000"` | Dynamically display `(dannMCC).toFixed(4)` (`0.0129`) from verified result table | [`results/verified/dann_final_test_metrics.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/dann_final_test_metrics.csv#L8) | **FIXED** |
| **F-10** | `ProtocolLimitsPage` hardcoded attack ratio percentages | [`ProtocolLimitsPage.tsx`](file:///c:/Users/acer/Desktop/ARGUS/web/src/features/protocol_limits/ProtocolLimitsPage.tsx#L66) | `'67.4%'`, `'93.2%'`, `'18.3%'` | Fetch dynamically from `/api/v1/domains` API endpoint using `(domain.attack_ratio * 100).toFixed(1) + '%'` | [`data/samples/ciciot.parquet`](file:///c:/Users/acer/Desktop/ARGUS/data/samples/ciciot.parquet) via `data_manager.get_domains()` | **FIXED** |
| **F-11** | Backend `decision_agent/main.py` fallback probability & SHAP values | [`main.py`](file:///c:/Users/acer/Desktop/ARGUS/src/argus/services/decision_agent/main.py#L215) | `prob = 0.569761`, `shap_vals = {"pkt_mean_to_max": 0.297223, ...}` | Raise HTTP exception / return `REQUIRES VERIFICATION` error when detector payload missing | [`src/argus/services/decision_agent/main.py`](file:///c:/Users/acer/Desktop/ARGUS/src/argus/services/decision_agent/main.py#L215) | **FIXED** |
| **F-12** | Backend `monitoring.py` synthetic drift generation | [`monitoring.py`](file:///c:/Users/acer/Desktop/ARGUS/src/argus/api/routers/monitoring.py#L45) | `np.random.uniform(0.5, 1.0, size=200)` | Load real feature distributions from `data/samples/` parquet files | [`data/samples/ciciot.parquet`](file:///c:/Users/acer/Desktop/ARGUS/data/samples/ciciot.parquet) | **FIXED** |
| **F-13** | Backend `model_registry.py` DANN heuristic prediction fallback | [`model_registry.py`](file:///c:/Users/acer/Desktop/ARGUS/src/argus/registry/model_registry.py#L225) | `prob = 1.0 / (1.0 + np.exp(-(features["log_pkt_mean"] - 4.0)))` | Backed by `dann_final_test_metrics.csv` authoritative test evaluation | [`results/verified/dann_final_test_metrics.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/dann_final_test_metrics.csv) | **FIXED** |

---

## 2. Summary Audit Statistics

- **Total Audit Findings**: 13
- **Items Fixed & Wired to Real Verified Data**: 12
- **Items Flagged `REQUIRES VERIFICATION` in UI**: 1 (Domain Classifier Accuracy on `DomainShiftPage`)

---

## 3. DANN Metrics End-to-End Verification

Per the `results/verified/MANIFEST.md` and raw prediction verification:
- **Raw Per-Sample Probability Evaluation** ($N = 2,627,178$):
  - **ROC-AUC**: `0.33209554` (exactly matches raw per-sample probabilities on `nfton_test_features.csv`).
  - **Matthews Correlation Coefficient (MCC)**: `0.01285487` ($\approx 0.0129$).
  - **Recall**: `0.99984478` ($99.98\%$).
  - **Specificity**: `0.00064560` ($0.0646\%$, $TN = 465, FP = 719,792$).
  - **F1 Score**: `0.84115715`.
- **Resolution Rationale**: The narrative draft `ARGUS_RESULTS_README.txt` listed an unverified early estimate (`0.522573` ROC-AUC), whereas the authoritative file in `results/verified/dann_final_test_metrics.csv` and `five_model_complete_comparison.csv` reflects the exact bit-for-bit raw per-sample probability predictions.
