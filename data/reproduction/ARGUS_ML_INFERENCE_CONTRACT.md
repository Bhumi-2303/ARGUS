# ARGUS ML Inference Contract
This document defines the strict boundary between the ML pipelines and the multi-agent orchestration. The agents must NOT execute standalone training scripts. Instead, they must interface through a defined API.

## 1. Input Contract
The incoming payload from `data_intelligence` must be pre-transformed into the Canonical Feature Space:
```json
{
  "features": {
    "total_pkts": <int>,
    "total_bytes": <int>,
    "protocol": <str>
  },
  "metadata": {
    "source_ip": <str>,
    "dest_ip": <str>,
    "timestamp": <float>
  }
}
```
**Important**: Metadata must NOT be passed to the ML models to prevent target identification leakage.

## 2. Adaptation Inference
The ML module will apply frozen `StandardScaler` and `OneHotEncoder` parameters (fitted exclusively on source training data). For domain adaptation (e.g. DANN), the feature extractor will project the scaled vector. Target-domain labels are strictly prohibited at inference.

## 3. Output Contract
The ML module will output a prediction object to `threat_analysis`:
```json
{
  "prediction": {
    "attack_probability": <float>,
    "predicted_class": <int>,
    "is_anomaly": <bool>
  },
  "explainability": {
    "confidence": <float>,
    "domain_shift_detected": <bool>
  }
}
```
