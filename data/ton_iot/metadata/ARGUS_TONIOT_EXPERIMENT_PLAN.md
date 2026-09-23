# ARGUS × TON_IoT Experiment Plan

## 1. Available evidence

- **Network Modality:** `train_test_network.csv` (No timestamps)
- **IoT/IIoT Telemetry:** 7 sensor datasets (Fridge, Garage Door, GPS Tracker, Modbus, Motion Light, Thermostat, Weather) with timestamps.
- **Linux Host:** Disk, Memory, and Process statistics (No timestamps).
- **Windows Host:** Windows 7 and Windows 10 performance counters (Timestamps derived from performance counters, but distinct format).

## 2. Current ARGUS agents

- **Data Intelligence:** Consumes CSV rows, removes identifiers, encodes categorical variables, and produces feature vectors.
- **Threat Analysis:** Consumes feature vectors to classify events as Normal or Attack, and identifies the attack type.
- **Risk Prediction:** Consumes threat probabilities and asset context (device type) to calculate risk scores.
- **Knowledge Context:** Maps attack types to MITRE ATT&CK; currently cannot correlate temporally due to missing timestamps/ground truth.
- **Decision Support:** Consumes risk metrics to suggest playbooks or actions (e.g., block IP, kill process).
- **Explainability:** Computes SHAP values or feature importances based on Threat Analysis outputs.

## 3. Experiment 1 — In-domain network detection

**Dataset:**
TON_IoT Network (`train_test_network.csv`)

**Input:**
Zeek-extracted network features (43 features, e.g., `src_bytes`, `duration`, `http_method`).

**Output:**
Binary classification (`label`) or multiclass classification (`type`).

**Purpose:**
Evaluate ARGUS Threat Analysis agent's ability to detect network-borne attacks using Zeek connection logs.

## 4. Experiment 2 — IoT/Telemetry detection

**Dataset:**
TON_IoT IoT (`Train_Test_IoT_*.csv` or `IoT_*.csv` in processed)

**Input:**
Sensor-specific telemetry (e.g., temperature, door state, modbus registers).

**Output:**
Binary classification (`label`) or multiclass classification (`type`).

**Purpose:**
Evaluate detection capabilities on device-specific physical and operational metrics independently of the network.

## 5. Experiment 3 — Host-based detection

**Dataset:**
Linux / Windows Host data (`Train_test_linux_*.csv`, `Train_Test_Windows_*.csv`)

**Input:**
System performance metrics (PID, memory usage, disk IO, CPU interrupts).

**Output:**
Binary classification (`label`) or multiclass classification (`type`).

**Purpose:**
Evaluate detection of malware/attacks based solely on host resource consumption and OS-level telemetry.

## 6. Experiment 4 — Multi-modal fusion

**Dataset:**
None (Currently BLOCKED).

**Reason:**
Multi-modal fusion (combining Network + IoT + Host data for a single attack narrative) requires temporal correlation. Because `train_test_network.csv` lacks timestamps and we do not have the `SecurityEvents_GroundTruth_datasets`, we cannot align a network flow with a simultaneous host process or sensor state change.

## 7. Experiment 5 — Cross-domain generalization

**Dataset:**
None (Currently BLOCKED).

**Reason:**
Cross-domain generalization requires either another local dataset (none exist) or overlapping features between modalities (e.g., Network and Host). The feature sets of Network, Host, and IoT are completely orthogonal in this subset, preventing direct cross-domain evaluation.

## 8. Blocked experiments

The following experiments cannot currently be performed:
- **Temporal Event Correlation:** Blocked because `train_test_network.csv` lacks a timestamp column and `SecurityEvents_GroundTruth_datasets` is missing.
- **Multi-modal Fusion:** Blocked for the same reason.
- **Cross-dataset evaluation (e.g., CICIoT2023):** Blocked because no other network datasets are physically present in the workspace.
- **Strict Zero-Leakage Validation:** Blocked because the `train_test` datasets are not temporally partitioned and we lack timestamps to split them accurately without leakage.

## 9. Required additional data

To unblock the critical Multi-modal fusion and temporal correlation experiments, the following specific files must be downloaded:
- `SecurityEvents_GroundTruth_datasets`
- The raw or correctly processed version of the Network dataset that **includes the timestamp (`ts`) column**. 

*Note: Raw PCAP and huge raw telemetry collections are NOT required. We only need the CSV metadata containing timestamps and the ground truth index.*
