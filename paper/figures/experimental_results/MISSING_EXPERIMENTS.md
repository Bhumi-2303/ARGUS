# ARGUS Missing Experiments & Future Research Roadmap

This document provides a scientifically rigorous and transparent audit of experimental figures, configurations, and raw artifacts that could **not** be generated or that remain open items in the ARGUS research project.

In strict compliance with the **Mandatory Safety Rules** of this study:
- No values have been simulated, interpolated, or fabricated.
- Where an experiment lacked verified underlying raw data, it is documented here rather than generated from unverified assumptions.

---

## 1. Unverified or Missing Experimental Artifacts

### 1.1 Representation Entropy & Unique Feature Tuples (Paper Section V-B)
- **Status**: **UNVERIFIED HYPOTHESIS**
- **Description**: An early draft circulated a claim that ARGUS-4 harmonization collapses approximately 3.57 million D3 flows to approximately 1,392 unique feature tuples, with Shannon entropy falling from $\approx 17.84$ to $\approx 5.84$ bits.
- **Why It Could Not Be Plotted**: An extensive cryptographic search of the repository confirmed that no tuple-count log, no verified entropy calculation script, and no raw entropy output file exist in the archived artifacts.
- **Action Taken**: Explicitly excluded from publication figures and documented in the paper (Section V-B, Fig. 3) as requiring verification prior to journal resubmission.

### 1.2 REP-01 Representation Extension & Temporal Causality Audit
- **Status**: **OPEN AUDIT ITEM**
- **Description**: An internal experiment designated `REP-01` attempted to scale harmonized features (8-feature and 14-feature sets) on IEC 60870-5-104 SCADA traffic.
- **Why It Could Not Be Plotted**: As documented in the independent project audit (`AUDIT.md` and `paper_text.txt` Section VII), `REP-01` lacked a verified, leakage-audited checkpoint and was flagged for potential temporal causality leakage.
- **Action Taken**: Only the verified non-monotonic resolution probe (ARGUS-4: 0.608, ARGUS-6: 0.565, ARGUS-8: 0.445, Native: 0.674) is plotted. Unverified claims of smooth monotonic scaling were discarded.

### 1.3 Protocol-Aware (Application-Layer Semantic) SCADA Features
- **Status**: **FUTURE WORK ONLY**
- **Description**: Investigating whether deep application-layer protocol fields (APDU, ASDU Type ID, Cause of Transmission [COT], Information Object Address [IOA]) improve detection over standard network flow attributes.
- **Why It Could Not Be Plotted**: No leak-free, reproducible experimental run testing protocol-aware semantic features has been completed in the repository.
- **Action Taken**: Documented as an open research question (RQ6) in Section VI and VII of the manuscript.

### 1.4 Multi-Seed D1 $\to$ D2 Adaptation Runs
- **Status**: **PLANNED EXTENSION**
- **Description**: Evaluating Clean Class-Aware CORAL, Global CORAL, and DANN across multiple random seeds (e.g., 5 seeds: 42, 123, 456, 789, 1011) with DeLong test and bootstrap confidence intervals.
- **Current Available State**: While the D3 native benchmark possesses complete 5-seed statistical verification (`results/experiments/p1_1_nfton_in_domain/` and `paper_text.txt` Table V/VI), the primary D1 $\to$ D2 benchmark currently rests on a single authoritative run ($N = 2,627,177$).
- **Action Taken**: Plotted as single-run authoritative benchmark with exact sample sizes.

### 1.5 Before/After Adaptation TreeSHAP Comparison
- **Status**: **PARTIAL**
- **Description**: An internal planning document requested a rank-correlation comparison between feature attributions of the unadapted Source-only model versus the Clean Class-aware CORAL model across the full test set.
- **Current State**: Global SHAP importance (`results/shap_feature_importance.csv`), target disconnect (`results/verified/SHAP_vs_Target_Gain.csv`), and representative local waterfall predictions (`sample_attack_flow.csv` and `sample_benign_flow.csv`) are verified and plotted. Full 2.62M-sample before/after correlation is omitted pending full checkpoint re-export.

---

## 2. Summary of Additional Experiments Required Prior to Journal Submission

| # | Priority | Experiment Title | Methodology Required | Deliverable Needed |
| :---: | :---: | :--- | :--- | :--- |
| **1** | **P0** | **Tuple Cardinality & Empirical Entropy Script** | Run exact hash-based tuple aggregation and Shannon entropy on frozen D3 native flows vs ARGUS-4 harmonized flows. | `entropy_results.json` + `tuple_cardinality.csv` |
| **2** | **P0** | **Multi-Seed D1 $\to$ D2 Adaptation Validation** | Re-run Clean Class-Aware CORAL and DANN across seeds 123, 456, 789, 1011; compute DeLong test $p$-values and bootstrap 95% CIs. | `multiseed_d1_d2_metrics.csv` |
| **3** | **P1** | **SCADA Protocol-Aware Semantic Benchmark** | Extract IEC-104 ASDU/APDU attributes from raw PCAP without temporal leakage; benchmark against 70-feature flow ceiling. | `scada_protocol_aware_results.csv` |
| **4** | **P1** | **Operational Cost-Benefit Utility Curve** | Define explicit dollar/consequence cost matrix for false alarms vs missed power grid intrusions to evaluate $\tau^* = 0.99$ optimality. | `operational_cost_curve.csv` |
