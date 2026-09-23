# DATASET COMPLETION REPORT

## 1. Initial State
- **CICIoT2023**: PARTIAL (1 of 169 split files)
- **NF-ToN-IoT**: VERIFIED COMPLETE
- **TON_IoT**: PARTIAL (~1MB network head, IoT telemetry present, ground truth missing)
- **HAI**: PARTIAL (train1.csv only)

## 2. Acquisition Actions
- Attempted bulk Kaggle API downloads for CICIoT2023 (~3GB), TON_IoT Network (~3.2GB), and HAI (~800MB) via `kaggle datasets download` and Python `kaggle` API.
- **Result**: The official Kaggle API and CLI exhibited severe throttling and persistent hanging (specifically stalling permanently at 1MB or 0% thresholds across all tested environments). 
- Attempted direct Git LFS cloning for HAI official repository.
- **Result**: Speeds degraded to < 100 KB/s making multi-GB LFS downloads inviable within reasonable constraints.

## 3. What Remains Unavailable
Due to explicit constraints against hammering dead servers or substituting fake data for completion:
- **CICIoT2023**: 168 of 169 parts remain unavailable on local disk.
- **TON_IoT**: 22 of 23 network parts + the remaining ~145MB of part 1 remain unavailable on local disk. The `SecurityEvents_GroundTruth_datasets` remains entirely wiped from public mirrors.
- **HAI**: train2, train3, train4, test1, test2 remain unavailable on local disk.

## 4. Exact Sources
- **CICIoT2023**: `https://www.kaggle.com/datasets/madhavmalhotra/unb-cic-iot-dataset`
- **NF-ToN-IoT**: `https://www.kaggle.com/datasets/dhoogla/nftoniot`
- **TON_IoT**: `https://www.kaggle.com/datasets/mohammedaddoun/ton-iot`
- **HAI**: `https://www.kaggle.com/datasets/icsdataset/hai-security-dataset`

## 5. Dataset Metrics
| Dataset | Files | Total Storage | Rows | Features | Label Col | Timestamp Col | SHA-256 | Provenance |
|---------|-------|---------------|------|----------|-----------|---------------|---------|------------|
| CICIoT2023 | 1 | 70 MB | 238,687 | 47 | `label` | N/A | Recorded | VERIFIED MIRROR |
| NF-ToN-IoT | 1 | 9.4 MB | 1,157,994 | 43 | `label` | N/A | Recorded | VERIFIED MIRROR |
| TON_IoT | 1 | 1 MB | 7,240 | 47 | `label` | `ts` | Recorded | VERIFIED MIRROR |
| HAI | 1 | 53 MB | 93,601 | 80+ | `Attack` | `timestamp` | Recorded | VERIFIED MIRROR |

## 6. Limitations and Readiness
- **Limitations**: The failure of large-scale automated mirror downloads has restricted training bounds. Models must rely on these exact splits. We refuse to fabricate the missing ground truth for TON_IoT.
- **Experiment Readiness**: Ready for in-domain baseline modeling, limited cross-domain network evaluation, and time-series profiling (on HAI). Multi-modal fusion remains explicitly BLOCKED.

---

DATASET COMPLETION STATUS

CICIoT2023: PARTIAL
NF-ToN-IoT: VERIFIED COMPLETE
TON_IoT: PARTIAL
HAI: PARTIAL
