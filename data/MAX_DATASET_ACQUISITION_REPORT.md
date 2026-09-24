# ARGUS Maximum Scientific Data Acquisition Pass

## 1. Dataset Inventory & State
- **CICIoT2023**: COMPLETE (63 merged CSV splits acquired from HuggingFace, ~8.66 GB).
- **NF-ToN-IoT**: COMPLETE (Local Parquet verified).
- **TON_IoT**: PARTIAL (SecurityEvents/GroundTruth datasets could not be located; CloudStor host retired).
- **HAI**: COMPLETE (Extracted full `hai-21.03` dataset from provided local `hai-master.zip`. Later versions like 23.05 are unavailable because GitHub's ZIP download strips Git LFS files and replaces them with 130-byte text pointers).
- **BoT-IoT**: COMPLETE (Extracted 11 CSV files totaling 2.1 GB from provided local zip archive).

## 2. Previous State
Previously, CICIoT2023 only contained a single split, TON_IoT lacked the complete network and ground truth, and HAI was missing several train/test splits. BoT-IoT was absent.

## 3. Current State & Newly Acquired Data
- Successfully completed acquiring the complete CICIoT2023 dataset (8.66 GB) via HuggingFace `bencorn/CIC-IoT-2023`.
- Processed the provided `hai-master.zip`. Because it was an archive of a Git LFS repository, the newest large splits (22.04, 23.05) were missing (replaced by 130-byte metadata pointers). Fortunately, the older `21.03` version was bundled as standard `.csv.gz` archives inside the zip. We extracted and decompressed these, successfully retrieving the complete `hai-21.03` dataset (3 train splits, 5 test splits totaling ~690 MB).
- Processed the provided `BoT-IoT` zip archive, extracting 11 raw CSV files comprising 2.1 GB of network traffic data annotated with `attack`, `category`, and `subcategory` labels. 
- Attempted to locate TON_IoT `SecurityEvents_GroundTruth_datasets`, but the primary CloudStor source is offline and Kaggle mirrors lack this specific component.

## 4. Total Disk Usage
Disk usage successfully expanded by ~8.66 GB for CICIoT2023, ~690 MB for the extracted HAI 21.03 dataset, and ~2.1 GB for the extracted BoT-IoT dataset.

## 5. Dataset Completeness & Modalities
| Dataset | Complete? | Size | Modality | Domain | Labels | Timestamp | DG Role |
|---------|-----------|------|----------|--------|--------|-----------|---------|
| CICIoT2023 | YES | 8.66 GB | Network | IoT | Attack Categories | Yes | SOURCE DOMAIN |
| NF-ToN-IoT | YES | 9.1 MB | Network (NetFlow) | IoT | Attack Categories | Yes | SOURCE DOMAIN |
| TON_IoT | PARTIAL | 175 MB (zip) | Multimodal (Net/Host/Telemetry) | IoT/IIoT | Attack Categories | Yes | MULTIMODAL SOURCE |
| HAI | YES | 690 MB | Industrial/OT | OT/ICS | Anomalies | Yes | INDUSTRIAL VALIDATION |
| BoT-IoT | YES | 2.1 GB | Network | IoT | Attack Categories | Yes | UNSEEN TARGET DOMAIN |
| WUSTL-IIOT | NO | ~500 MB | Network/IIoT | SCADA/IIoT | Attack Categories | Yes | UNSEEN TARGET DOMAIN |

## 6. Blocked Sources & Failures
- **TON_IoT CloudStor**: Host could not be resolved; service retired.
- **HAI GitHub LFS Zip Issue**: The user-provided `hai-master.zip` was downloaded via GitHub's UI "Download ZIP" button. GitHub intentionally omits Git LFS files (which store the large `.csv` datasets for versions like 23.05) in zipped source code downloads, replacing them with LFS text pointers. We bypassed this by extracting the `21.03` version which used `.gz` standard files instead of Git LFS.

## 7. Additional Datasets Evaluated
- **WUSTL-IIOT**: High DG usefulness for IIoT/SCADA network traffic.

## 8. Scientific Usefulness & Domain-Generalization (DG)
- **Source Domains**: `CICIoT2023` and `NF-ToN-IoT` are the best candidates for large-scale source domain training due to their size, comprehensive attack coverage, and reliable network modalities.
- **Unseen Target Domains**: `BoT-IoT` and `TON_IoT` serve as rigorous held-out domains for testing domain generalization.
- **Industrial Validation**: `HAI` remains the primary dataset for OT/ICS validation, and we now possess a complete multi-split version (`hai-21.03`).

## 9. Multimodal Data Available
- `TON_IoT` provides the most comprehensive multimodal data, encompassing Network, IoT Telemetry, and Host (Windows/Linux) features.

## 10. Critical Remaining Gaps
- The `SecurityEvents_GroundTruth_datasets` for TON_IoT remains elusive due to link rot on the primary academic host.

### Final Summary
- **TOTAL DATASETS**: 5 Primary
- **TOTAL STORAGE**: ~11.6 GB
- **COMPLETE DATASETS**: 4 (NF-ToN-IoT, CICIoT2023, HAI, BoT-IoT)
- **PARTIAL DATASETS**: 1 (TON_IoT)
- **NEWLY ACQUIRED DATA**: ~11.45 GB (CICIoT2023 8.6GB + HAI 690MB + BoT-IoT 2.1GB)
- **BLOCKED DATA**: TON_IoT Ground Truth (offline).
- **BEST SOURCE DOMAINS**: CICIoT2023, NF-ToN-IoT
- **AVAILABLE UNSEEN TARGET DOMAINS**: BoT-IoT, TON_IoT
- **MULTIMODAL DATA AVAILABLE**: TON_IoT
- **CRITICAL REMAINING GAPS**: TON_IoT Ground Truth labels.
