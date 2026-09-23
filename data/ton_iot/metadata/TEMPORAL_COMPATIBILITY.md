# Temporal Compatibility Analysis

| Dataset | Timestamp column | Time range | Precision | Overlap | Synchronizable |
|---------|------------------|------------|-----------|---------|----------------|
| Processed IoT Telemetry | `date`, `time` | Mar 31 2019 - Apr 2 2019+ | Seconds | YES (with Network) | YES |
| Network (Timestamped) | `ts` | Apr 2 2019+ | Seconds | YES (with IoT) | YES |
| SecurityEvents_GroundTruth | MISSING | MISSING | MISSING | UNKNOWN | NO |

## Compatibility Assessment
The **Network** and **IoT Telemetry** modalities share overlapping time ranges and precision (down to the second). They can technically be synchronized.
However, because the `SecurityEvents_GroundTruth_datasets` remains **MISSING**, it is impossible to validate which specific timestamps correspond to actual attack injection windows versus normal baseline operations across the entire network.

Multi-modal fusion remains blocked until the authoritative timeline of events is recovered.
