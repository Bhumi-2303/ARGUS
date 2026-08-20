#!/usr/bin/env python3
"""
replay_producer.py — ARGUS Streaming Traffic Replay Producer.

Replays pre-captured historical dataset CSV exports (CICIoT2023, NF-ToN-IoT-v2, or IEC 60870-5-104)
and streams each flow record as a JSON payload to Apache Kafka topic 'argus-flows' at a configurable rate.

PAPER LIMITATION NOTICE:
This script replays historical dataset CSV exports through Apache Kafka to simulate real-time
streaming traffic. It is NOT a live physical grid tap.
"""

import os, sys, time, json, argparse
from pathlib import Path
import pandas as pd

try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_TOPIC = os.getenv("KAFKA_TOPIC", "argus-flows")
DEFAULT_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
DEFAULT_RATE = float(os.getenv("REPLAY_RATE_RPS", "5.0"))  # Records per second

FEATURE_COLS = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
DEFAULT_ASSET_IDS = ["SCADA-MTU-01", "SCADA-RTU-04", "PLC-SUB-12", "HMI-WORKSTATION-02", "SENSOR-NODE-88"]

def get_sample_data() -> pd.DataFrame:
    """Generates synthetic sample flow DataFrame if no CSV file path is provided."""
    data = [
        {"pkt_mean_to_max": 0.95, "tcp_flag_density": 1.0, "log_pkt_mean": 4.2, "log_pkt_max": 4.3, "asset_id": "SCADA-MTU-01"},
        {"pkt_mean_to_max": 0.05, "tcp_flag_density": 0.0, "log_pkt_mean": 1.0, "log_pkt_max": 1.2, "asset_id": "SENSOR-NODE-88"},
        {"pkt_mean_to_max": 0.88, "tcp_flag_density": 2.0, "log_pkt_mean": 3.9, "log_pkt_max": 4.1, "asset_id": "SCADA-RTU-04"},
        {"pkt_mean_to_max": 0.12, "tcp_flag_density": 0.0, "log_pkt_mean": 1.5, "log_pkt_max": 1.8, "asset_id": "PLC-SUB-12"},
        {"pkt_mean_to_max": 0.91, "tcp_flag_density": 1.5, "log_pkt_mean": 4.0, "log_pkt_max": 4.2, "asset_id": "HMI-WORKSTATION-02"}
    ]
    return pd.DataFrame(data)

def load_csv(csv_path: str) -> pd.DataFrame:
    """Loads CSV export and maps/verifies feature columns."""
    file_p = Path(csv_path)
    if not file_p.exists():
        print(f"[!] Warning: CSV file '{csv_path}' not found. Using synthetic sample flows.")
        return get_sample_data()

    print(f"[*] Loading historical flow dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Ensure required feature columns exist or map defaults
    for col in FEATURE_COLS:
        if col not in df.columns:
            print(f"[!] Warning: Missing column '{col}' in CSV. Filling default 0.0.")
            df[col] = 0.0

    if "asset_id" not in df.columns:
        # Assign synthetic asset IDs deterministically
        df["asset_id"] = [DEFAULT_ASSET_IDS[i % len(DEFAULT_ASSET_IDS)] for i in range(len(df))]

    return df

def run_replay_producer(
    csv_path: Optional[str] = None,
    bootstrap_servers: str = DEFAULT_BOOTSTRAP,
    topic: str = DEFAULT_TOPIC,
    rate_rps: float = DEFAULT_RATE,
    limit: Optional[int] = None,
    dry_run: bool = False
):
    """
    Main Producer Loop:
    Reads historical telemetry rows and publishes JSON payloads to Kafka topic.
    """
    df = load_csv(csv_path) if csv_path else get_sample_data()
    if limit and limit > 0:
        df = df.iloc[:limit]

    print("=" * 80)
    print("ARGUS STREAMING TRAFFIC REPLAY PRODUCER")
    print(f"Target Kafka Topic  : {topic}")
    print(f"Bootstrap Servers   : {bootstrap_servers}")
    print(f"Replay Rate (RPS)   : {rate_rps} records/sec")
    print(f"Total Flow Records  : {len(df)}")
    print(f"Mode                : {'DRY RUN (No Kafka)' if dry_run else 'Kafka Streaming'}")
    print("=" * 80)

    producer = None
    if not dry_run:
        if not KAFKA_AVAILABLE:
            print("[!] Warning: kafka-python module not available. Falling back to DRY RUN mode.")
            dry_run = True
        else:
            try:
                print(f"[*] Connecting to Kafka Broker at {bootstrap_servers}...")
                producer = KafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    request_timeout_ms=5000
                )
                print("[+] Kafka Producer connected successfully!")
            except Exception as e:
                print(f"[!] Kafka connection failed: {e}. Falling back to DRY RUN mode.")
                dry_run = True

    delay = 1.0 / max(rate_rps, 0.1)
    sent_count = 0

    for idx, row in df.iterrows():
        payload = {
            "asset_id": str(row.get("asset_id", "SCADA-MTU-01")),
            "flow_record": {
                "pkt_mean_to_max": float(row["pkt_mean_to_max"]),
                "tcp_flag_density": float(row["tcp_flag_density"]),
                "log_pkt_mean": float(row["log_pkt_mean"]),
                "log_pkt_max": float(row["log_pkt_max"])
            },
            "replay_timestamp": time.time(),
            "sequence_id": idx + 1
        }

        if not dry_run and producer:
            try:
                producer.send(topic, value=payload)
            except Exception as e:
                print(f"[!] Send error on record #{idx+1}: {e}")

        sent_count += 1
        if sent_count % 10 == 0 or sent_count == len(df):
            print(f"[*] Replayed [{sent_count}/{len(df)}] flows -> Asset: {payload['asset_id']} | pkt_mean_to_max: {payload['flow_record']['pkt_mean_to_max']:.2f}")

        time.sleep(delay)

    if producer:
        producer.flush()
        producer.close()

    print(f"\n[+] Successfully replayed {sent_count} historical flow records!")

def main():
    parser = argparse.ArgumentParser(description="ARGUS Streaming Traffic Replay Producer")
    parser.add_argument("--csv", type=str, default=None, help="Path to historical flow CSV export")
    parser.add_argument("--bootstrap-servers", type=str, default=DEFAULT_BOOTSTRAP, help="Kafka bootstrap servers")
    parser.add_argument("--topic", type=str, default=DEFAULT_TOPIC, help="Kafka topic name")
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE, help="Replay rate in records per second")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records to replay")
    parser.add_argument("--dry-run", action="store_true", help="Run without connecting to Kafka broker")
    args = parser.parse_args()

    run_replay_producer(
        csv_path=args.csv,
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        rate_rps=args.rate,
        limit=args.limit,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()
