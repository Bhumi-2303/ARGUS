# Cross-Dataset Feature Compatibility

## 1. Local Dataset Inventory

An audit of the local ARGUS project directory reveals the following data files currently present:
- `TON_IoT` datasets (newly acquired).
- `tests/data/1_percent_sample.parquet` (synthetic dataset with features `f1`, `f2`, `f3`, `f4`).
- Result/Metrics files (e.g., `run1.csv`, `REP01_MULTI_SEED_RESULTS.csv` which contain experimental metrics, not raw network traffic).

**Result:** There are currently **no other raw or processed network traffic datasets** (such as CICIoT2023 or NF-ToN-IoT) physically present in the local ARGUS workspace.

## 2. Feature Compatibility Analysis

Because no other network datasets exist locally, we cannot establish feature compatibility with external datasets at this time. 

If external datasets like `CICIoT2023` or `NF-ToN-IoT` are introduced in the future:
- We must map their Flow features (e.g., `Flow Duration`, `Tot Fwd Pkts`) against TON_IoT's Zeek-derived features (e.g., `duration`, `src_pkts`, `src_bytes`).
- TON_IoT network data is extracted using Bro/Zeek and includes application-layer metadata (`http_method`, `dns_query`), which is typically absent in generic flow datasets (like CIC-FlowMeter outputs), meaning cross-dataset evaluations will require significant feature intersection and mapping.

**Conclusion:** Cross-dataset evaluation is **BLOCKED** until another dataset is actually downloaded and mapped to the Zeek format provided by TON_IoT.
