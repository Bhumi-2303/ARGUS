#!/usr/bin/env python3
"""
Unit tests for ARGUS Risk Prediction & Triage Agent.
Verifies health check, risk score formula calculations, risk tier mapping,
and sensible ranking assertions for batch alert triage.
"""

from fastapi.testclient import TestClient
from risk_agent.main import app, calculate_risk

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        print("Health check response:", response.status_code, response.json())
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["asset_inventory_count"] == 5

def test_risk_formula_calculation():
    # Test High Prob + High Crit -> Critical Tier
    score, tier, exp = calculate_risk(probability=0.85, criticality=5)
    print(f"Prob 0.85, Crit 5 -> Score: {score}, Tier: {tier}")
    assert score == 91.0
    assert tier == "Critical"

    # Test High Prob + Low Crit -> High Tier
    score, tier, exp = calculate_risk(probability=0.85, criticality=1)
    print(f"Prob 0.85, Crit 1 -> Score: {score}, Tier: {tier}")
    assert score == 59.0
    assert tier == "Medium"

    # Test Low Prob + Low Crit -> Low Tier
    score, tier, exp = calculate_risk(probability=0.10, criticality=1)
    print(f"Prob 0.10, Crit 1 -> Score: {score}, Tier: {tier}")
    assert score == 14.0
    assert tier == "Low"

def test_triage_batch_ranking_sensible():
    with TestClient(app) as client:
        # 4 alerts with varying probability and criticality
        batch_payload = [
            {
                "asset_id": "SENSOR-NODE-88", # Crit 1
                "detection_probability": 0.20 # Score = 20.0
            },
            {
                "asset_id": "SCADA-MTU-01",   # Crit 5
                "detection_probability": 0.90 # Score = 94.0
            },
            {
                "asset_id": "SENSOR-NODE-88", # Crit 1
                "detection_probability": 0.90 # Score = 62.0
            },
            {
                "asset_id": "SCADA-MTU-01",   # Crit 5
                "detection_probability": 0.20 # Score = 52.0
            }
        ]
        
        response = client.post("/triage", json=batch_payload)
        assert response.status_code == 200
        data = response.json()
        print("\nTriaged Alerts Batch Output:")
        for idx, alert in enumerate(data["sorted_alerts"]):
            print(f"  Rank #{idx+1}: {alert['asset_id']:18s} | Crit {alert['asset_criticality']} | Prob {alert['detection_probability']:.2f} -> Risk Score: {alert['risk_score']} [{alert['risk_tier']}]")

        scores = [a["risk_score"] for a in data["sorted_alerts"]]
        # Assert strictly sorted descending
        assert scores == sorted(scores, reverse=True)
        # Assert High Prob + High Crit ranks #1
        assert data["sorted_alerts"][0]["asset_id"] == "SCADA-MTU-01"
        assert data["sorted_alerts"][0]["detection_probability"] == 0.90
        # Assert Low Prob + Low Crit ranks last
        assert data["sorted_alerts"][-1]["asset_id"] == "SENSOR-NODE-88"
        assert data["sorted_alerts"][-1]["detection_probability"] == 0.20

if __name__ == "__main__":
    test_health()
    test_risk_formula_calculation()
    test_triage_batch_ranking_sensible()
    print("\n[✓] All Risk Prediction Agent unit tests passed successfully!")
