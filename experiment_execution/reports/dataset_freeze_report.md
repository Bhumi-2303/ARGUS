# ARGUS Dataset Partition & Freeze Report

This document records the frozen dataset partitions and class prior distributions across all three benchmark domains.

| Domain | Partition | Rows | Benign Flows | Attack Flows | Attack Prior ($P(Y=1)$) | Status |
| :--- | :--- | ---: | ---: | ---: | ---: | :---: |
| **D1: CICIoT2023** | Train | 5,491,971 | 129,538 | 5,362,433 | 97.6413% | **FROZEN** |
| **D1: CICIoT2023** | Test | 1,176,851 | 27,709 | 1,149,142 | 97.6455% | **FROZEN** |
| **D2: NF-ToN-IoT-v2** | Train Total | 10,508,704 | 2,881,027 | 7,627,677 | 72.5844% | **FROZEN** |
| **D2: NF-ToN-IoT-v2** | Adaptation | 8,406,962 | 2,304,821 | 6,102,141 | 72.5844% | **FROZEN** |
| **D2: NF-ToN-IoT-v2** | Calibration | 2,101,742 | 576,206 | 1,525,536 | 72.5844% | **FROZEN** |
| **D2: NF-ToN-IoT-v2** | Test | 2,627,177 | 720,257 | 1,906,920 | 72.5844% | **FROZEN** |
| **D3: IEC 60870-5-104** | Adaptation (Unlabeled) | 2,286,249 | 1,772,619 | 513,630 | 22.4661% | **FROZEN** |
| **D3: IEC 60870-5-104** | Calibration ($\\theta^*$) | 571,563 | 443,155 | 128,408 | 22.4661% | **FROZEN** |
| **D3: IEC 60870-5-104** | **Held-Out Test Set** | **714,453** | **553,944** | **160,509** | **22.4660%** | **FROZEN (EVAL ONLY)** |

### Strict Isolation Verification
- $\\text{D3 Adaptation Split} \\cap \\text{D3 Calibration Split} = \\emptyset$ ($2,286,249$ vs $571,563$ rows)
- $\\text{D3 Train Total} \\cap \\text{D3 Test Split} = \\emptyset$ ($2,857,812$ vs $714,453$ rows)
- **Zero test-set leakage**: The D3 test partition is isolated strictly for final evaluation.
