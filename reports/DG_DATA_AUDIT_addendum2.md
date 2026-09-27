# DG DATA AUDIT - ADDENDUM 2

## A. Feasibility Matrix
Matrix constructed purely from column headers (no row scanning).

| Dataset | duration | src_pkts | dst_pkts | src_bytes | dst_bytes | total_pkts | total_bytes | protocol | tcp_flags | max_pkt_len | pkt_mean_to_max | tcp_flag_density | log_pkt_mean | log_pkt_max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **CICIoT2023** | absent (only IAT available) | absent | absent | absent | absent | present (`Number`) | present (`Tot size`) | present (`Protocol Type`) | derivable (via specific flag columns) | present (`Max`) | derivable (`AVG`/`Max`) | derivable (flag cols) | derivable (`AVG`) | derivable (`Max`) |
| **NF-ToN-IoT** | present (`FLOW_DURATION_MILLISECONDS`) | present (`IN_PKTS`) | present (`OUT_PKTS`) | present (`IN_BYTES`) | present (`OUT_BYTES`) | derivable (`IN_PKTS`+`OUT_PKTS`) | derivable (`IN_BYTES`+`OUT_BYTES`) | present (`PROTOCOL`) | present (`TCP_FLAGS`) | absent | absent | derivable (`TCP_FLAGS`/pkts) | derivable | absent |
| **TON_IoT** | present (`duration`) | present (`src_pkts`) | present (`dst_pkts`) | present (`src_bytes`) | present (`dst_bytes`) | derivable (`src_pkts`+`dst_pkts`) | derivable (`src_bytes`+`dst_bytes`) | present (`proto`) | absent | absent | absent | absent | derivable | absent |
| **BoT-IoT** | present (`dur`) | present (`spkts`) | present (`dpkts`) | present (`sbytes`) | present (`dbytes`) | derivable (`pkts`) | derivable (`bytes`) | present (`proto`) | present (`flgs`) | present (`max`) | derivable (`mean`/`max`) | derivable (`flgs`/pkts) | derivable (`mean`) | derivable (`max`) |

## B. TON_IoT (211,043 rows)
**Benign Count (0):** 50,000
**Attack Count (1):** 161,043

**Attack-type distribution:**
- normal: 50,000
- backdoor: 20,000
- ddos: 20,000
- dos: 20,000
- injection: 20,000
- password: 20,000
- ransomware: 20,000
- scanning: 20,000
- xss: 20,000
- mitm: 1,043

## C. BoT-IoT Distribution
**Files Processed:** 11 / 11

**Attack-Category Distribution:**
- DoS: 6,999,687
- Normal: 462
- DDoS: 3,999,851

**Protocol Mix (All Rows):**
- udp: 7,823,129
- arp: 324
- tcp: 3,176,429
- icmp: 118

**Protocol Mix (Benign Rows):**
- tcp: 232
- udp: 213
- arp: 17

## D. Paper Predictions Omission
**Per-sample prediction files found:**
- phase4_results/audit_probability_output.py (0.01 MB)
- phase4_results/feature_resolution/fig2_unique_probabilities.png (0.03 MB)
- phase4_results/feature_resolution/fig3_probability_distributions.png (0.04 MB)
- phase4_results/probability_audit (0.00 MB)
- phase4_results/probability_audit/stage_probability_stats.csv (0.00 MB)

**Status of predictions for paper experiments:**
- XGBoost/LightGBM four-way baseline: Missing
- Global CORAL: Missing
- Class-aware CORAL: Missing
- Clean class-aware CORAL: Missing
- DANN: Missing

### Critical Omission Finding
A thorough search of all persistent results directories (`results/`, `phase3_results/`, `phase4_results/`, and `artifacts/`) reveals that **zero raw per-sample prediction files (.csv, .npy, .parquet) exist on disk**.
All output files currently stored are strictly aggregated statistical summaries—such as threshold sweeps, F1/MCC tables, confusion matrices, SHAP averages, and class prior reports. Because the fundamental, sample-by-sample output logits/probabilities were either never serialized or subsequently deleted, it is absolutely impossible to precisely re-calculate alternative threshold metrics, compute paired statistical significance tests (e.g., McNemar's test), verify calibration reliability at the sample level, or perform deep error analysis on the cross-domain inference behavior. This violates the project's strict 'evidence-first' reproducible forecasting rule.

## E. Dedup History for CICIoT2023
Based on exhaustive repository scans (grepping for `drop_duplicates`, `dedup`, or `hash` across all scripts):
We investigated the legacy scripts responsible for generating the specific CICIoT2023 splits (the 5,491,971 Train / 1,176,851 Test / 1,176,851 Adapt blocks).

**Findings:**
- No script that loads or splits the CICIoT2023 data employs deduplication logic prior to dividing the dataset.
- **None found.** The only occurrences of `drop_duplicates` in the entire codebase were located in `experiments/analysis/feature_resolution_study.py:345` (which operates exclusively on the IEC104 target domain calibration set) and in `src/argus/agents/data_intelligence/tools/data_cleaner.py:35` (an LLM agent utility).

**Implication:**
Because no deduplication (hashing, `.drop_duplicates()`, or manual filtering) was applied to CICIoT2023 prior to `train_test_split()`, and we proved in Step 3 that the raw CICIoT2023 chunks contain a **51.04% duplicate rate**, the resulting splits are profoundly compromised. Massive numbers of identical feature vectors almost certainly span across the Training, Adaptation, Calibration, and Test splits, resulting in severe data leakage and artificially inflated accuracy metrics for any model trained on this pipeline.
