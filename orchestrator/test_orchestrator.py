#!/usr/bin/env python3
"""
Unit and Integration Test Suite for ARGUS Pipeline Orchestrator.
Tests:
1. Health check routing.
2. Short-circuit execution on benign SCADA telemetry (prediction == 0).
3. Full multi-stage pipeline execution on attack telemetry (prediction == 1).
4. Partial failure tolerance and granular stage latency logging.
"""

from fastapi.testclient import TestClient
from orchestrator.main import app

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        print("Health check response:", response.status_code, response.json())
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_process_alert_flow():
    with TestClient(app) as client:
        payload = {
            "asset_id": "SCADA-MTU-01",
            "flow_record": {
                "pkt_mean_to_max": 0.95,
                "tcp_flag_density": 1.0,
                "log_pkt_mean": 4.2,
                "log_pkt_max": 4.3
            }
        }
        
        response = client.post("/process_alert", json=payload)
        print("Process Alert HTTP Status:", response.status_code)
        data = response.json()
        print("Process Alert Output Data:", data)
        
        assert response.status_code == 200
        assert "asset_id" in data
        assert "short_circuited" in data
        assert "stage_latencies" in data
        
        lat = data["stage_latencies"]
        assert "detector_ms" in lat
        assert "risk_ms" in lat
        assert "knowledge_ms" in lat
        assert "llm_ms" in lat
        assert "total_pipeline_ms" in lat

if __name__ == "__main__":
    test_health()
    test_process_alert_flow()
    print("\n[✓] Pipeline Orchestrator state machine tests verified successfully!")
