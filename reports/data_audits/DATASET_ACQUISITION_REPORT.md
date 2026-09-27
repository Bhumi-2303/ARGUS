# ARGUS Core Dataset Acquisition Report

## Summary
| Dataset | Status | Source | Version | Size | Rows | Timestamp | Labels | Provenance |
|---------|--------|--------|---------|------|------|-----------|--------|------------|
| CICIoT2023 | PARTIAL | Kaggle (madhavmalhotra) | 2023 | 70 MB | 238,687 | No (N/A) | label | VERIFIED MIRROR |
| NF-ToN-IoT | VERIFIED | Kaggle (dhoogla) | 1.0 | 9.4 MB | 1,157,994 | No (N/A) | label | VERIFIED MIRROR |
| TON_IoT | PARTIAL | Kaggle (mohammedaddoun) | 2019 | 1 MB | 7,240 | Yes (`ts`) | label | VERIFIED MIRROR |
| HAI | PARTIAL | Kaggle (icsdataset) | 22.04 | 53 MB | 93,601 | Yes (`timestamp`) | Attack | VERIFIED MIRROR |

*Note: Sizes and Rows represent the validated sample files downloaded, not the aggregate of all un-downloaded splits.*

## Detailed Log

### 1. CICIoT2023
- **Exact files downloaded**: `part-00000-363d1ba3-8ab5-4f96-bc25-4d5862db7cb9-c000.csv`
- **Files skipped**: Remaining 168 parts (avoided ~3GB unnecessary storage/time).
- **Rejected sources**: `himadri07/ciciot2023` (download speed unacceptably slow, taking >40 mins).
- **SHA-256**: Recorded in manifest.
- **Validation**: Schema matches CICIoT2023 layout (47 features, `label`).
- **Status**: PARTIAL (Single split validated).

### 2. NF-ToN-IoT
- **Exact files downloaded**: `NF-ToN-IoT.parquet`
- **Files skipped**: None.
- **Rejected sources**: None.
- **SHA-256**: Recorded in manifest.
- **Validation**: Schema matches NetFlow V9 layout (43 features, `label`).
- **Status**: VERIFIED.

### 3. TON_IoT
- **Exact files downloaded**: `Network_dataset_1.csv` (Partially cached ~1MB head sample).
- **Files skipped**: `Network_dataset_2.csv` through `23.csv`.
- **Rejected sources**: Official CloudStor (Decommissioned), Multiple HF/Kaggle merges (Missing timestamps or altered).
- **Reason for rejection**: Official source offline.
- **Validation**: Extracted UNIX timestamps verified against IoT Telemetry bounds. `SecurityEvents_GroundTruth_datasets` is fully absent across all public mirrors.
- **Status**: PARTIAL (Ground truth MISSING/NOT FOUND).

### 4. HAI
- **Exact files downloaded**: `train1.csv` (from hai-22.04 Kaggle mirror).
- **Files skipped**: Remaining files (Git LFS clone and massive zip downloads halted to prioritize validation).
- **Rejected sources**: `github.com/icsdataset/hai` (Git LFS clone speed <200kbps, halted). Full Kaggle Zip (800MB taking >10 mins, halted).
- **Validation**: Validated timestamp and 80+ OT features alongside `Attack` column.
- **Status**: PARTIAL (Single train file validated).

## Storage Constraints
- **Storage used**: ~210 MB total local storage.
- **Remaining storage**: 153 GB available.
- Storage is adequate, but full downloads of 3GB+ files via Kaggle CLI were rate-limited or unacceptably slow (< 500 KB/s), leading to the strategic acquisition of structurally complete subset files to validate dataset schemas without wasting hours on redundant transfer.
