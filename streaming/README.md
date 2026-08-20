# ARGUS Streaming Traffic Replay & Kafka Integration

Real-time streaming pipeline component for the **ARGUS project**. It uses **Apache Kafka** and **Zookeeper** to stream pre-captured historical dataset flow telemetry into the ARGUS Pipeline Orchestrator (`http://orchestrator:8004/process_alert`).

---

## ⚠️ RESEARCH LIMITATION NOTICE (FOR PAPER METHODOLOGY)

> **IMPORTANT SCIENTIFIC LIMITATION**:
> This streaming framework replays pre-captured historical dataset CSV exports (**CICIoT2023**, **NF-ToN-IoT-v2**, and **IEC 60870-5-104**) through an Apache Kafka message broker at a configurable rate (`--rate` in records/second).
>
> It represents a **simulated streaming telemetry pipeline**, **NOT a live real-time physical SCADA grid tap**. This distinction must be explicitly documented in the limitations section of academic paper submissions to maintain scientific integrity.

---

## 🏗️ Architecture Component Overview

1. **Apache Zookeeper & Apache Kafka**: Local message broker running inside Docker (`kafka:9092`).
2. **`replay_producer.py`**:
   - Reads historical flow records from CSV exports (or synthetic sample data).
   - Extracts feature 4-tuples (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`) and target `asset_id`.
   - Serializes flow records into JSON payloads and publishes to Kafka topic `argus-flows` at a configurable rate.
3. **`stream_consumer.py`**:
   - Continuous worker process subscribed to Kafka topic `argus-flows`.
   - Consumes telemetry JSON messages and submits each record to the ARGUS Pipeline Orchestrator (`POST /process_alert`).
   - Logs real-time processing outputs, risk scores, short-circuit decisions, and stage latencies.

---

## 🐳 Docker Compose Deployment (All Services)

To launch the complete ARGUS microservice stack (Kafka, Zookeeper, Detector API, Risk Agent, Knowledge Agent, Decision Support Agent, Orchestrator, and Stream Consumer):

```bash
# 1. Build and start containers in background
docker-compose up --build -d

# 2. Verify all 8 containers are running cleanly
docker-compose ps

# 3. Stream live logs from the Consumer Worker
docker-compose logs -f stream-consumer
```

---

## 🏃 Running Replay Producer (Local Execution)

```bash
# Replay sample telemetry at 5 records per second (default)
PYTHONPATH=. .venv/bin/python streaming/replay_producer.py --rate 5.0

# Replay historical dataset CSV export at 10 records per second
PYTHONPATH=. .venv/bin/python streaming/replay_producer.py --csv phase4_results/experiments/group_f_full_argus.csv --rate 10.0

# Dry-run test mode (without connecting to Kafka broker)
PYTHONPATH=. .venv/bin/python streaming/replay_producer.py --dry-run
```

---

## 🧪 Unit Test Verification

```bash
PYTHONPATH=. .venv/bin/python streaming/test_streaming.py
```
