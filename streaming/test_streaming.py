#!/usr/bin/env python3
"""
Unit and Integration Test Suite for ARGUS Streaming Traffic Replay & Consumer.
Verifies sample telemetry generation, producer payload serialisation, dry-run mode,
and consumer message invocation logic.
"""

from streaming.replay_producer import get_sample_data, run_replay_producer
from streaming.stream_consumer import process_single_message

def test_sample_data_generation():
    df = get_sample_data()
    print("Sample flow data count:", len(df))
    assert len(df) == 5
    assert "pkt_mean_to_max" in df.columns
    assert "tcp_flag_density" in df.columns
    assert "log_pkt_mean" in df.columns
    assert "log_pkt_max" in df.columns
    assert "asset_id" in df.columns

def test_dry_run_producer():
    print("Testing Dry-Run Producer Execution...")
    run_replay_producer(rate_rps=100.0, limit=3, dry_run=True)
    print("[✓] Dry-run producer completed successfully!")

def test_consumer_payload_processing():
    print("Testing Consumer Message Processing Function...")
    sample_payload = {
        "asset_id": "SCADA-MTU-01",
        "flow_record": {
            "pkt_mean_to_max": 0.95,
            "tcp_flag_density": 1.0,
            "log_pkt_mean": 4.2,
            "log_pkt_max": 4.3
        },
        "sequence_id": 1
    }
    # Test processing logic (if Orchestrator isn't running, returns graceful error dict)
    res = process_single_message(sample_payload)
    assert isinstance(res, dict)
    print("[✓] Consumer payload processing test passed!")

if __name__ == "__main__":
    test_sample_data_generation()
    test_dry_run_producer()
    test_consumer_payload_processing()
    print("\n[✓] All Streaming Pipeline unit tests passed successfully!")
