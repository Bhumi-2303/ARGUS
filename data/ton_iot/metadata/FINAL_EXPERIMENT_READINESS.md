# TON_IoT Final Experiment Readiness

## 1. Timestamped Network Data Finalization
**Dataset Location**: `data/ton_iot/network_timestamped/Network_dataset_1.csv`
- **Partial/Head sample?** Yes. The file is a 1 MB partial download of what is natively a ~140 MB file (which itself is split 1 of 23 of the original network dataset). The complete dataset size is approximately 3.2 GB.
- **Original Source**: UNSW TON_IoT. The verified mirror is Kaggle (`mohammedaddoun/ton-iot`), which retains the original filename split format (`Network_dataset_X.csv`).
- **Timestamp**: The `ts` column contains UNIX Epoch seconds (e.g., 1554198358).
- **Labels**: `label` (binary 0/1) and `type` (multiclass, e.g., 'normal', 'ddos').
- **Feature Count**: 47
- **Row Count**: 7,240 (in this partial download).
- **Missing Value Rate**: ~0.47% (34 missing values across 7,240 rows).
- **Duplicate Rate**: 0%
- **Class Distribution**: 7,239 Normal, 0 Attack (the partial sample only captured baseline traffic before attacks began).
- **Time Range**: `2019-04-02 09:45:58` to `2019-04-02 12:57:32`
- **Timestamp Integrity**: Timestamps are preserved for all rows.

## 2. Temporal Compatibility Verification
- **Network Time Range**: Starts at `2019-04-02 09:45:58`.
- **IoT Telemetry Time Range**: `2019-03-31 12:36:52` to `2019-04-29 23:59:58`.
- **Overlap Interval**: Complete overlap. The network timeline falls entirely within the broader IoT telemetry baseline timeline.
- **Timestamp Format**: Network uses UNIX Epoch (seconds); IoT uses DD-MMM-YY and HH:MM:SS strings.
- **Timestamp Precision**: Both modalities have 1-second precision.
- **Normalization**: Both can be trivially converted to pandas `datetime64[ns]` without inventing or interpolating information.

## 3. Scientific Possibility Assessment

This assessment strictly defines what is scientifically robust using the **partial TON_IoT collection** currently downloaded.

### A. In-domain network detection
**Status**: **READY**
*Evidence*: We possess the network flows and their corresponding labels (`train_test_network.csv` or `Network_dataset_1.csv`). Standard single-modality intrusion detection is perfectly viable.

### B. In-domain IoT telemetry detection
**Status**: **READY**
*Evidence*: We possess the IoT sensor logs (e.g., `IoT_Fridge.csv`) with full feature sets and corresponding local attack labels.

### C. Cross-modal temporal alignment
**Status**: **READY WITH CAVEAT**
*Evidence*: Both the `Network_dataset_1.csv` and the IoT telemetry feature precise, normalizable timestamps (1-second precision) with overlapping chronological windows (e.g., April 2, 2019). The caveat is that we only possess a partial download of the network timeline.

### D. Authoritative cross-modal attack-event correlation
**Status**: **BLOCKED**
*Evidence*: The `SecurityEvents_GroundTruth_datasets` remains entirely absent from all public mirrors (Cloudstor is decommissioned). Without this ground-truth timeline, we cannot authoritatively state whether a concurrent anomaly in the network and IoT data represents the *same* cyber attack sequence, distinct simultaneous attacks, or normal variance.

### E. Multi-modal fusion
**Status**: **BLOCKED**
*Evidence*: To train a multi-modal fusion model, we must have labels for the *fused* state (e.g., Network flow + IoT state = True Positive Attack). Since we lack the `SecurityEvents_GroundTruth`, synthesizing multi-modal labels by simply assuming overlapping individual labels are the same event constitutes a fundamental data integrity violation (dataset fabrication).
