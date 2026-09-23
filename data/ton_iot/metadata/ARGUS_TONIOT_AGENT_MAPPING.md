# ARGUS × TON_IoT Agent Mapping

----------------------------------------
DATA INTELLIGENCE
----------------------------------------
**What TON_IoT data can this agent consume?**
- Network flows (`train_test_network.csv`)
- IoT telemetry (`IoT_*.csv` files)
- Host logs (`Train_Test_Linux_*.csv`, `Train_Test_Windows_*.csv`)

**What preprocessing/feature extraction would logically belong here?**
- Type casting (e.g., parsing timestamps from IoT telemetry).
- One-hot encoding of categorical features (e.g., `proto`, `service` from network data).
- Imputation of missing values (though current analysis shows 0 missing values).
- Dropping identifier columns (e.g., `src_ip`, `dst_ip`, `PID`) before inference to prevent leakage.

**What information should it output to downstream agents?**
- Cleaned, normalized numerical feature vectors ready for model inference.

----------------------------------------
THREAT ANALYSIS
----------------------------------------
**Which TON_IoT modalities can support threat analysis?**
- Network, IoT Telemetry, Linux Host, and Windows Host.

**What evidence can be provided?**
- Normalized feature vectors from Data Intelligence.

**What attack labels can potentially be predicted?**
- Binary classification: `label` (Normal vs. Attack).
- Multiclass classification: `type` (e.g., backdoor, ddos, injection, password, ransomware, xss, etc.).

----------------------------------------
RISK PREDICTION
----------------------------------------
**What TON_IoT information can support risk estimation?**
- Threat probabilities (from Threat Analysis).
- IoT device type (inferred from the dataset name, e.g., Fridge, Garage Door, Weather sensor) can inform asset criticality.

**What information is currently unavailable?**
- True business impact or organizational criticality scores for the specific simulated devices.
- Network topology to assess lateral movement risk.

----------------------------------------
KNOWLEDGE CONTEXT
----------------------------------------
**What contextual information exists?**
- Attack types (`type` column) can be mapped to known MITRE ATT&CK techniques.
- Device types (from IoT dataset names) provide environmental context.

**What contextual information is missing?**
- The **SecurityEvents_GroundTruth_datasets** is MISSING. 
- As a result, cross-modality temporal correlation (mapping a network flow to a simultaneous host process) is effectively blocked, since the network dataset lacks timestamp data, and the ground-truth timeline is absent.

**Can security-event correlation currently be performed?**
- **NO.** Without the ground truth and consistent timestamps across all modalities (specifically missing in `train_test_network.csv`), temporal correlation cannot be performed.

----------------------------------------
DECISION SUPPORT
----------------------------------------
**What outputs can it consume?**
- Threat classification and Risk scores.
- Device context (e.g., knowing the attack targets a Modbus vs. a Fridge).

**What decisions can currently be supported?**
- Rule-based isolation policies (e.g., block source IP from the network dataset).
- Process termination (using PID from the Linux/Windows datasets).

----------------------------------------
EXPLAINABILITY
----------------------------------------
**What evidence can currently be exposed to explain predictions?**
- Feature importance vectors (e.g., SHAP values) on the specific TON_IoT features (like `http_request_body_len` or `Processor_pct_ Idle_Time`).
- Highlighted anomalous metrics compared to normal baselines for the specific simulated devices.
