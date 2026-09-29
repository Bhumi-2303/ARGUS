# ARGUS Datasets Directory

This folder (`dataset/` or `datasets/`) centralizes all datasets used for live demos, model predictions, evaluation, and testing in the ARGUS platform.

---

## 🚀 Live Demo & Prediction CSVs (Drag-and-Drop / Upload in UI)

These CSV files are pre-formatted with the 4 harmonized network features required by the ARGUS ML pipeline (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`). You can directly upload them in the UI at **[http://localhost:8000/input](http://localhost:8000/input)** under the *"Upload Custom Flow CSV"* section:

| File | Description | Expected Classification |
| :--- | :--- | :--- |
| `sample_attack_flow.csv` | Curated attack traffic flows (DoS, brute force, port scan). | **High / Critical Threat** |
| `sample_benign_flow.csv` | Normal, non-malicious operational network flows. | **Low / Safe Threat** |
| `ciciot_sample.csv` | 100 benchmark sample flows from the CICIoT2023 source domain. | Mixed |
| `nfton_sample.csv` | 100 benchmark sample flows from the NF-ToN-IoT-v2 target domain. | Mixed |

---

## 📊 Parquet Datasets (10,000 Verified Rows Each)

*   `ciciot.parquet`: Source domain (CICIoT2023) sampled dataset used by the API endpoints (`/api/v1/data/samples`).
*   `nfton.parquet`: Target domain (NF-ToN-IoT-v2) sampled dataset used for adaptation evaluation and drift monitoring.

---

## 📁 Full Benchmark & Raw Data

*   `ciciot_test_features.csv`: Full test partition for CICIoT2023 (58 MB).
*   `nfton_test_features.csv`: Full test partition for NF-ToN-IoT-v2 (133 MB).
*   `BoT-IoT dataset-20260924T054841Z-1-006.zip`: Full BoT-IoT raw archive (192 MB).
*   `hai-master.zip`: Full HAI (Hardware-in-the-Loop ICS) raw archive (300 MB).

---

## 💻 CLI Quick Prediction Example

```bash
# Test prediction using sample attack flow
curl -X POST "http://localhost:8000/api/v1/agents/trace" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "pkt_mean_to_max": 0.99,
      "tcp_flag_density": 0.95,
      "log_pkt_mean": 8.5,
      "log_pkt_max": 9.1
    },
    "model_name": "xgb_adapted"
  }'
```
