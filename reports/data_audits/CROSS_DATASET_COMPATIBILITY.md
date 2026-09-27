# Cross-Dataset Compatibility Report

This report defines the compatibility boundaries across the four core ARGUS datasets: **CICIoT2023**, **NF-ToN-IoT**, **TON_IoT**, and **HAI**. 
Merging datasets is fundamentally flawed unless identical environments were used. Thus, no datasets are merged.

## Dataset Summaries

### 1. CICIoT2023
- **Domain**: IoT Network Traffic
- **Modality**: Network features
- **Feature Representation**: 47 flow-based features (e.g., flow duration, packet counts).
- **Label Representation**: Multi-class (33 attacks + 1 normal).
- **Timestamp**: Not strictly available/preserved in processed subsets (often dropped or non-sequential).
- **Temporal Coverage**: Simulated captures without strict global temporal alignment to other datasets.

### 2. NF-ToN-IoT
- **Domain**: IoT Network Traffic (NetFlow)
- **Modality**: NetFlow V9 / IPFIX Network features
- **Feature Representation**: 43 NetFlow features.
- **Label Representation**: Binary (Attack/Normal) and Multi-class (Attack types).
- **Timestamp**: Preserved in NetFlow records, though usually abstracted as flow start/end times.
- **Temporal Coverage**: Derived from TON_IoT network captures (2019).

### 3. TON_IoT
- **Domain**: IoT/IIoT Ecosystem
- **Modality**: Network, IoT Telemetry, OS Logs (Multi-modal)
- **Feature Representation**: Modality-specific (Network flow features vs. Sensor telemetry like temperature/pressure).
- **Label Representation**: Binary and Attack types.
- **Timestamp**: Strict UNIX Epoch and `DD-MMM-YY HH:MM:SS` preserved.
- **Temporal Coverage**: Late March to April 2019.

### 4. HAI (HIL-based Augmented ICS)
- **Domain**: Industrial Control Systems (ICS/OT)
- **Modality**: OT Process Variables (Sensors, Actuators)
- **Feature Representation**: Physical sensor readings (e.g., Boiler temperature, Turbine speed) across 50+ to 80+ dimensions.
- **Label Representation**: Binary anomaly indicators (Attack/Normal).
- **Timestamp**: Precise timestamps preserved for sequential time-series anomaly detection.
- **Temporal Coverage**: Multiple testbed runs (e.g., 2020-2022 depending on version).

---

## Compatibility Scenarios

### 1. In-domain detection
- **Supported Datasets**: CICIoT2023, NF-ToN-IoT, TON_IoT (Network & Telemetry), HAI.
- **Status**: **READY**. Each dataset individually supports single-modality machine learning.

### 2. Cross-domain evaluation (Domain Generalization)
- **Supported Datasets**: Network: CICIoT2023 vs. TON_IoT Network vs. NF-ToN-IoT.
- **Status**: **READY WITH CAVEAT**. Models trained on CICIoT2023 can be tested on TON_IoT network data (and vice-versa) provided feature sets are mapped/aligned (e.g., extracting common flow features). Telemetry/OT cross-evaluation (TON_IoT Telemetry vs. HAI) is conceptually blocked due to completely different physical sensor semantics (smart home vs. industrial boiler).

### 3. Temporal analysis
- **Supported Datasets**: TON_IoT (Telemetry), HAI.
- **Status**: **READY**. These datasets maintain strict temporal sequence integrity, allowing for time-series forecasting and sequential anomaly detection models (e.g., LSTMs, Transformers).

### 4. Multi-modal analysis & Cross-modal temporal alignment
- **Supported Datasets**: TON_IoT (Network + Telemetry).
- **Status**: **BLOCKED** for authoritative attack correlation. While timestamps overlap perfectly, the lack of `SecurityEvents_GroundTruth` prevents verified labeling of cross-modal fused events.
