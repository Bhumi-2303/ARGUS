#!/usr/bin/env python3
"""
stream_consumer.py — ARGUS Streaming Alert Consumer Worker.

Consumes real-time streaming flow JSON messages from Kafka topic 'argus-flows'
and invokes the ARGUS Pipeline Orchestrator (POST /process_alert) for each record.

PAPER LIMITATION NOTICE:
Processes replayed historical dataset telemetry messages from Kafka broker.
"""

import os, sys, time, json, argparse
from pathlib import Path
import requests

try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

DEFAULT_TOPIC = os.getenv("KAFKA_TOPIC", "argus-flows")
DEFAULT_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_API_URL", "http://localhost:8004/process_alert")
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "argus-consumer-group")

def process_single_message(payload: dict) -> dict:
    """Invokes Pipeline Orchestrator API (POST /process_alert) for a consumed telemetry record."""
    asset_id = payload.get("asset_id", "SCADA-MTU-01")
    flow_record = payload.get("flow_record", {})
    seq = payload.get("sequence_id", 0)

    orch_payload = {
        "asset_id": asset_id,
        "flow_record": flow_record
    }

    t0 = time.time()
    try:
        resp = requests.post(ORCHESTRATOR_URL, json=orch_payload, timeout=15.0)
        if resp.status_code == 200:
            result = resp.json()
            short = result.get("short_circuited", False)
            risk_info = result.get("risk_output", {})
            risk_score = risk_info.get("risk_score", 0.0) if risk_info else 0.0
            risk_tier = risk_info.get("risk_tier", "N/A") if risk_info else "N/A"
            lat = result.get("stage_latencies", {}).get("total_pipeline_ms", 0.0)

            print(
                f"[CONSUMER] Seq #{seq:03d} | Asset: {asset_id:18s} | "
                f"Short-Circuited: {str(short):5s} | Risk: {risk_score:5.2f} [{risk_tier:8s}] | "
                f"Pipeline Latency: {lat:6.2f} ms"
            )
            return result
        else:
            print(f"[!] Orchestrator HTTP error {resp.status_code}: {resp.text}")
            return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        print(f"[!] Failed to call Orchestrator at {ORCHESTRATOR_URL}: {e}")
        return {"error": str(e)}

def run_stream_consumer(
    bootstrap_servers: str = DEFAULT_BOOTSTRAP,
    topic: str = DEFAULT_TOPIC,
    group_id: str = GROUP_ID,
    max_messages: Optional[int] = None
):
    """Main Consumer Loop: listens on Kafka topic and processes messages sequentially."""
    print("=" * 80)
    print("ARGUS STREAMING ALERT CONSUMER WORKER")
    print(f"Subscribed Topic     : {topic}")
    print(f"Bootstrap Servers    : {bootstrap_servers}")
    print(f"Consumer Group ID    : {group_id}")
    print(f"Orchestrator URL     : {ORCHESTRATOR_URL}")
    print("=" * 80)

    if not KAFKA_AVAILABLE:
        print("[!] Error: kafka-python module not installed. Consumer cannot start.")
        return

    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            consumer_timeout_ms=10000  # Stop after 10s idle if max_messages is set
        )
        print("[+] Kafka Consumer connected and polling for streaming messages...")
    except Exception as e:
        print(f"[!] Failed to connect Kafka Consumer: {e}")
        return

    consumed_count = 0
    try:
        for msg in consumer:
            payload = msg.value
            process_single_message(payload)
            consumed_count += 1
            if max_messages and consumed_count >= max_messages:
                print(f"[*] Reached max_messages limit ({max_messages}). Stopping consumer.")
                break
    except KeyboardInterrupt:
        print("\n[*] Stopping consumer worker on user interrupt.")
    finally:
        consumer.close()
        print(f"[+] Consumer finished. Total messages processed: {consumed_count}")

def main():
    parser = argparse.ArgumentParser(description="ARGUS Streaming Alert Consumer Worker")
    parser.add_argument("--bootstrap-servers", type=str, default=DEFAULT_BOOTSTRAP, help="Kafka bootstrap servers")
    parser.add_argument("--topic", type=str, default=DEFAULT_TOPIC, help="Kafka topic name")
    parser.add_argument("--group-id", type=str, default=GROUP_ID, help="Kafka consumer group ID")
    parser.add_argument("--max-messages", type=int, default=None, help="Stop after N messages (for testing)")
    args = parser.parse_args()

    run_stream_consumer(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        group_id=args.group_id,
        max_messages=args.max_messages
    )

if __name__ == "__main__":
    main()
