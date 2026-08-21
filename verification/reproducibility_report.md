# ARGUS End-to-End Live Pipeline Reproducibility Verification Report

**Target Domain**: IEC 60870-5-104 SCADA Telemetry (Domain 3)  
**Test Dataset Slice**: $N = 1,000$ Labeled SCADA Test Telemetry Records (`iec104_test_features.csv`)  
**Model Artifact**: `phase3_results/models/model_d2_coral.txt`  
**Audit Date**: August 21, 2026  
**Verification Verdict**: **EXACT MATCH ($0 / 1,000$ Divergent Predictions)**  

---

## 1. Executive Summary

This report performs an end-to-end empirical verification to prove that the live ARGUS deployment pipeline (Streaming Replay Producer $\to$ Kafka $\to$ Consumer $\to$ Orchestrator $\to$ Detector API) reproduces the original research metrics reported in Phase 3 and Phase 4.

### **Conclusion**: **EXACT MATCH**
- **Divergent Predictions**: **$0$ out of $1,000$ records diverged**.
- **Confusion Matrix**: The live pipeline returned a confusion matrix ($TN=60, FP=718, FN=14, TP=208$) that is **$100\%$ identical** to the original verified research artifacts.
- **Metric Fidelity**: Accuracy ($26.80\%$), Attack Recall ($93.69\%$), Precision ($22.46\%$), and $F_1$ Score ($0.3624$) match to 4 decimal places.

---

## 2. Test Slice & Artifact Identification

- **Ground Truth & Baseline Reference**: `phase3_results/experiments/D2_D3_CORAL/predictions.csv` (First $1,000$ rows).
- **Raw Telemetry Input Feature Slice**: `ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv` (First $1,000$ rows).
- **Ground Truth Distribution**:
  - **Benign Telemetry ($Y = 0$)**: $778$ records ($77.80\%$)
  - **Attack Telemetry ($Y = 1$)**: $222$ records ($22.20\%$)
- **Decision Threshold**: $\theta = 0.50$ (Matching verified operating point).

---

## 3. Side-by-Side Confusion Matrix Comparison

| Confusion Matrix Cell | Original Verified Research Artifact | Live Deployed Pipeline Output | Absolute Difference |
| :--- | :--- | :--- | :--- |
| **True Negatives (TN)** | **$60$** | **$60$** | **$0$** |
| **False Positives (FP)** | **$718$** | **$718$** | **$0$** |
| **False Negatives (FN)** | **$14$** | **$14$** | **$0$** |
| **True Positives (TP)** | **$208$** | **$208$** | **$0$** |

---

## 4. Performance Metrics Comparison Table

| Performance Metric | Mathematical Formula | Original Research Metric | Live Pipeline Metric | Difference | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Accuracy** | $\frac{TP + TN}{N}$ | **$0.2680$** ($26.80\%$) | **$0.2680$** ($26.80\%$) | $0.0000$ | **EXACT MATCH** |
| **Attack Recall (TPR)** | $\frac{TP}{TP + FN}$ | **$0.9369$** ($93.69\%$) | **$0.9369$** ($93.69\%$) | $0.0000$ | **EXACT MATCH** |
| **Precision** | $\frac{TP}{TP + FP}$ | **$0.2246$** ($22.46\%$) | **$0.2246$** ($22.46\%$) | $0.0000$ | **EXACT MATCH** |
| **$F_1$ Score** | $\frac{2 \cdot P \cdot R}{P + R}$ | **$0.3624$** ($0.3624$) | **$0.3624$** ($0.3624$) | $0.0000$ | **EXACT MATCH** |

---

## 5. Automated Anti-Regression Integration

The end-to-end verification is automated in `streaming/test_end_to_end_reproducibility.py`:
```bash
$ PYTHONPATH=. .venv/bin/python streaming/test_end_to_end_reproducibility.py
```
This test asserts zero prediction divergence (`divergences == 0`), guaranteeing that future code changes or container deployments will not cause scientific regression.

---

## 6. Paper Methodology Statement

To cite this empirical end-to-end validation in your paper's experimental section:

> *"To verify that the deployed streaming architecture (`replay_producer` $\to$ Kafka $\to$ `stream_consumer` $\to$ Orchestrator $\to$ Detector API) preserves offline scientific fidelity, a labeled SCADA test slice ($N = 1,000$ samples) was streamed through the live pipeline. The live system constructed a confusion matrix ($TN=60, FP=718, FN=14, TP=208$) exhibiting 0 prediction divergences from the verified offline research artifacts, confirming exact end-to-end reproducibility."*
