# Timestamp Compatibility Matrix

| Dataset | Timestamp Column(s) | Format | Temporal Splitting Possible? | Notes |
|---------|---------------------|--------|------------------------------|-------|
| **CICIoT2023** | None | N/A | **NO** | Dataset only contains `flow_duration`. Absolute times were scrubbed. |
| **NF-ToN-IoT** | `FIRST_SWITCHED`, `LAST_SWITCHED` | Epoch (int) | **YES** | Allows ordering of flows. |
| **BoT-IoT** | `stime`, `ltime` | Epoch (float) | **YES** | Precise float epoch. |
| **TON_IoT** | None (in Zeek CSV) | N/A | **NO** | Raw PCAPs have time, but standard CSVs lack absolute timestamps. |
| **HAI 21.03** | `time` | String (`YYYY-MM-DD HH:MM:SS`) | **YES** | Perfectly chronological telemetry stream. |

### Conclusion
**Temporal splitting (train on past, test on future) is NOT universally possible across the network datasets** because `CICIoT2023` lacks absolute timestamps. Domain Generalization must rely on cross-environment (dataset-to-dataset) splits rather than chronological splits.
