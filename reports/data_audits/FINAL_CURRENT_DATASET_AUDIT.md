# FINAL CURRENT DATASET AUDIT

## 1. TOTAL DATASETS CURRENTLY PRESENT
4 (CICIoT2023, NF-ToN-IoT, TON_IoT, HAI)

## 2. TOTAL DATASET DIRECTORIES
4 core directories within `data/`

## 3. TOTAL APPROXIMATE STORAGE USED
572 MB total physical disk usage

## 4. COMPLETE DATASETS
- **NF-ToN-IoT**: VERIFIED COMPLETE (9.5MB, 1.15M rows)

## 5. PARTIAL DATASETS
- **TON_IoT**: PARTIAL (IoT Telemetry intact ~168MB; Network is head-only 1MB; Ground Truth missing)
- **HAI**: PARTIAL (`train1.csv` only, ~53MB)

## 6. SAMPLE/HEAD-ONLY DATASETS
- **CICIoT2023**: SAMPLE (only part 0 out of 169 is downloaded, ~70MB)

## 7. METADATA-ONLY DATASETS
None strictly metadata-only. All 4 have at least a sample or partial physical data slice.

## 8. MOST USEFUL DATA CURRENTLY AVAILABLE
- **NF-ToN-IoT**: Provides complete cross-domain network flow representations.
- **TON_IoT (Telemetry)**: Provides robust IoT telemetry signals.
- **HAI**: Provides rich, timestamped industrial OT measurements.

## 9. EXPERIMENTS CURRENTLY POSSIBLE
- **In-domain classification**: READY (all 4 datasets have enough rows for minimal train/test).
- **Temporal correlation**: READY (TON_IoT Telemetry and HAI both contain intact absolute timestamps).
- **Cross-domain detection**: PARTIAL (possible between CICIoT2023/NF-ToN-IoT with feature alignment).

## 10. EXPERIMENTS CURRENTLY BLOCKED
- **Multimodal fusion**: BLOCKED (TON_IoT `SecurityEvents_GroundTruth_datasets` is physically missing from the mirror, making authoritative alignment of network and telemetry attacks scientifically invalid).

## 11. CRITICAL MISSING COMPONENTS
- **TON_IoT SecurityEvents_GroundTruth**: Prevents true multi-modal integration.
- **CICIoT2023 Remaining Splits (1-168)**: Prevents large-scale generalization testing due to lack of diverse conditions.

## 12. WHETHER DATASET ACQUISITION SHOULD STOP OR CONTINUE
STOP. Bulk API mirrors have repeatedly stalled out at the infrastructure level (MTU / rate-limits). What is acquired is sufficient for bounded prototype development. Continuing automated large-file downloads will only result in further hangs.

## 13. EXACT NEXT RESEARCH STEP
Move from data acquisition into **Environment Setup / Pipeline Engineering**. Begin coding the data loaders and agent testbed utilizing the physically acquired samples and the complete NF-ToN-IoT parquet file.

---

### PREVIOUS STATE VS CURRENT STATE

| Dataset | Previous Claims | Current Filesystem Reality | Change / Status |
|---------|-----------------|----------------------------|-----------------|
| CICIoT2023 | Partial (1/169) | `processed/part-00000...csv` exists (70MB, 238k rows). | Unchanged. |
| NF-ToN-IoT | Verified Complete | `processed/NF-ToN-IoT.parquet` exists (9.5MB, 1.15M rows). | Unchanged. |
| TON_IoT | Partial | Network is a 1MB chunk. Telemetry is intact. No ground truth. | Unchanged. |
| HAI | Partial | `train1.csv` exists (53MB, 93k rows). `train2.csv.zip` incomplete. | Unchanged. |

### DATASET-BY-DATASET ANALYSIS

#### 1. CICIoT2023
- **What exists:** `processed/part-00000...csv`
- **What does NOT exist:** Parts 1-168.
- **Completeness:** SAMPLE / HEAD CHUNK
- **Data modalities:** Network Flow
- **Labels:** `label` (Multi-class attacks)
- **Timestamps:** NO (inter-arrival times only)
- **Experimental usefulness:** BASELINE ONLY

#### 2. NF-ToN-IoT
- **What exists:** `processed/NF-ToN-IoT.parquet`
- **What does NOT exist:** Nothing (It is structurally complete).
- **Completeness:** COMPLETE
- **Data modalities:** Network Flow
- **Labels:** `Label` (Binary), `Attack` (Multi-class)
- **Timestamps:** NO (duration only)
- **Experimental usefulness:** PRIMARY EXPERIMENT DATA (Network base)

#### 3. TON_IoT
- **What exists:** `processed/Processed_IoT_dataset/*.csv` (Telemetry), `network_timestamped/Network_dataset_1.csv` (1MB), train/test splits.
- **What does NOT exist:** `SecurityEvents_GroundTruth`, network chunks 2-23.
- **Completeness:** PARTIAL
- **Data modalities:** Network + IoT Telemetry
- **Labels:** `label`, `type`
- **Timestamps:** YES (`ts`, `date`/`time`)
- **Experimental usefulness:** IoT TELEMETRY EXPERIMENTS

#### 4. HAI
- **What exists:** `processed/train1.csv`, raw Git checkout.
- **What does NOT exist:** Remaining train/test files.
- **Completeness:** PARTIAL
- **Data modalities:** OT/ICS Industrial Control
- **Labels:** `Attack`
- **Timestamps:** YES (`timestamp`)
- **Experimental usefulness:** INDUSTRIAL VALIDATION

---

### CROSS-DOMAIN EXPERIMENT MATRIX (Train → Test)

| Train \ Test | CICIoT2023 | NF-ToN-IoT | TON_IoT (Network) | HAI |
|--------------|------------|------------|-------------------|-----|
| **CICIoT2023** | FEASIBLE | FEASIBLE W/ ALIGNMENT | FEASIBLE W/ ALIGNMENT | NOT COMPARABLE |
| **NF-ToN-IoT** | FEASIBLE W/ ALIGNMENT | FEASIBLE | FEASIBLE W/ ALIGNMENT | NOT COMPARABLE |
| **TON_IoT** | FEASIBLE W/ ALIGNMENT | FEASIBLE W/ ALIGNMENT | FEASIBLE | NOT COMPARABLE |
| **HAI** | NOT COMPARABLE | NOT COMPARABLE | NOT COMPARABLE | FEASIBLE |

### ARGUS EXPERIMENT READINESS

| Experiment | CICIoT2023 | NF-ToN-IoT | TON_IoT | HAI | Overall Status |
|------------|-------------|-------------|---------|-----|----------------|
| In-domain detection | READY | READY | READY | READY | READY |
| Cross-domain detection | PARTIAL | READY | PARTIAL | N/A | PARTIAL |
| Domain generalization | BLOCKED | READY | BLOCKED | BLOCKED | BLOCKED (needs full variance) |
| Network detection | READY | READY | PARTIAL | N/A | READY |
| Telemetry detection | N/A | N/A | READY | N/A | READY |
| OT/ICS detection | N/A | N/A | N/A | READY | READY |
| Multimodal fusion | N/A | N/A | BLOCKED | N/A | BLOCKED |
| Temporal correlation | N/A | N/A | READY | READY | READY |
