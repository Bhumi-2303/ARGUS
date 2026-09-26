# ARGUS System Demonstration Script (4-Minute Walkthrough)

This document provides a click-by-click demonstration script for showcasing the **ARGUS Autonomous Grid & Network Telemetry Adaptation Platform**.

---

## 🚀 Quick Launch Instructions (Single Command)

To verify startup integrity and launch the API + built frontend in one command:

```bash
make demo
```

Or run directly:

```bash
python scripts/start_demo.py
```

* **Frontend & REST API URL**: `http://localhost:8000`
* **Network Status**: Works 100% offline with zero external internet requirements.

---

## ⏱️ 4-Minute Click-by-Click Presentation Script

### Minute 1: Overview & The Four Story Tiles (`/`)
1. **Navigate to**: `http://localhost:8000/`
2. **Action**: Point out the **System Narrative in Four Tiles**:
   * **Tile 1 (In-Domain vs. Cross-Domain Performance)**:
     * *Exact Numbers*: Source Baseline MCC = `0.7203` on unadapted target domain vs. `0.9842` in-domain.
     * *Source File*: [`results/verified/five_model_complete_comparison.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/five_model_complete_comparison.csv)
   * **Tile 2 (Statistical Domain Shift)**:
     * *Exact Numbers*: 4 / 4 harmonized features shifted (KS statistic threshold `0.10`, PSI threshold `0.25`).
     * *Source File*: [`data/samples/nfton.parquet`](file:///c:/Users/acer/Desktop/ARGUS/data/samples/nfton.parquet)
   * **Tile 3 (CORAL Adaptation Gain)**:
     * *Exact Numbers*: Clean Class-Aware CORAL target MCC = `0.9412`, F1 Score = `0.9840`, FPR = `0.0280`.
     * *Source File*: [`results/verified/five_model_complete_comparison.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/five_model_complete_comparison.csv)
   * **Tile 4 (Honest Limitations & Protocol Controls)**:
     * *Exact Numbers*: Single-seed protocol (Seed 42) disclosure; DANN representation collapse MCC = `0.0000`.
     * *Source File*: [`results/verified/dann_final_test_metrics.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/dann_final_test_metrics.csv)
3. **Key Highlight**: Point out that every single metric card displays a clickable `ProvenanceBadge` linking to its underlying source file.

---

### Minute 2: Live Monitor & Deterministic Replay Sequence (`/monitor`)
1. **Navigate to**: Click **Live Monitor** in sidebar or navigate to `http://localhost:8000/monitor`.
2. **Action**:
   * Select Domain: `nfton` (Target Smart Home / NetFlow v2).
   * Select Models: Check `model_d2_coral` and `xgb_source`.
   * Set Speed to `10x` and Seed to `42`.
   * Click **Start Stream**.
3. **Deterministic Replay Sequence**:
   * **Phase 1 (In-Domain Telemetry)**: Observe smooth flow ingestion in table and real-time probability timeline chart. Balanced accuracy remains $>95\%$.
   * **Phase 2 (Domain Switch)**: Switch domain dropdown to `iec104` mid-stream.
   * **Phase 3 (Shift Alert Trigger)**: Point out the animated **⚠️ STATISTICAL DOMAIN SHIFT DETECTED** banner. Note unadapted `xgb_source` accuracy dropping while `model_d2_coral` maintains high specificity ($>97\%$).
4. **Key Highlight**: Fixed 320px scroll container guarantees **zero layout shift** during streaming at up to 200 events/sec.

---

### Minute 3: Model Comparison & SHAP Explainability (`/benchmark`, `/explain`)
1. **Navigate to**: `http://localhost:8000/benchmark`.
2. **Action**:
   * View the sortable **4-Architecture Performance Matrix**:
     * `model_d2_coral` (Clean Class-Aware CORAL): MCC = `0.9412`, F1 = `0.9840`, FPR = `0.0280`, $\tau = 0.52$.
     * `model_d1_coral` (Global CORAL): MCC = `0.8840`, F1 = `0.9610`, FPR = `0.0590`, $\tau = 0.50$.
     * `xgb_source` (Unadapted Source-Only): MCC = `0.7203`, F1 = `0.9120`, FPR = `0.1190`, $\tau = 0.50$.
     * `dann_adapted` (DANN): MCC = `0.0000`, F1 = `0.9640`, Recall = `1.0000`, FPR = `1.0000`, $\tau = 0.50$.
   * Point to the **DANN Degenerate-Risk Warning Alert**: DANN suffers feature representation collapse under 93% attack imbalance, predicting 100% majority class.
   * Click open the collapsed **diagnostic (not a final result)** panel showing `diagnostic_class_aware_coral.csv` metrics tagged with `protocolStatus="diagnostic-only"`.
3. **Navigate to**: `http://localhost:8000/explain`.
4. **Action**:
   * Click **Calculate SHAP Attribution**. Point out `tcp_flag_density` as top contributor ($+0.3850$).
   * Inspect **Source Gain vs. Target Impact Disconnect Table** (referenced to [`results/verified/SHAP_vs_Target_Gain.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/SHAP_vs_Target_Gain.csv)).

---

### Minute 4: Target Network Onboarding & Protocol Integrity (`/onboard`, `/protocol-limits`)
1. **Navigate to**: `http://localhost:8000/onboard`.
2. **Action**:
   * Step through the 5-stage wizard: Adaptation Window ($5,000$ flows) $\rightarrow$ CORAL Covariance Fitting $\rightarrow$ Calibration Sweep $\rightarrow$ Freeze Threshold ($\tau = 0.52$).
   * Click **Execute Onboarding Simulation**. Show the generated holdout test MCC = `0.9412` and FPR = `0.0280`.
   * Note the prominent **`DEMO SCALE`** badge and `protocolStatus="demo-scale"`.
3. **Navigate to**: `http://localhost:8000/protocol-limits`.
4. **Action**:
   * Audit the **Zero-Leakage Dataset Partitioning Protocol**:
     * Target Adaptation Split: *Unsupervised* (0 target labels).
     * Calibration Split: *Threshold sweep only*.
     * Test Split: *Zero-leakage holdout* (frozen).
   * Review Class-Prior Shift Matrix (CICIoT2023 67% attack vs. NF-ToN-IoT-v2 93% attack vs. IEC 104 18% attack).

---

## 📊 Summary of Source Results Files

| Metric / Table | Source CSV Path |
| :--- | :--- |
| **5-Model Comparison** | [`results/verified/five_model_complete_comparison.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/five_model_complete_comparison.csv) |
| **DANN Test Metrics** | [`results/verified/dann_final_test_metrics.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/dann_final_test_metrics.csv) |
| **D3 Native Sweep** | [`results/verified/d3_native_threshold_sweep.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/d3_native_threshold_sweep.csv) |
| **SHAP vs Target Gain** | [`results/verified/SHAP_vs_Target_Gain.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/verified/SHAP_vs_Target_Gain.csv) |
| **Diagnostic CORAL Run** | [`results/diagnostic/diagnostic_class_aware_coral.csv`](file:///c:/Users/acer/Desktop/ARGUS/results/diagnostic/diagnostic_class_aware_coral.csv) |
