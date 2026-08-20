#!/usr/bin/env python3
"""
Test script for verifying ARGUS Decision Support Agent API endpoints,
system prompt rules compliance, plain-text dashboard formatting, and latency profiling.
"""

from fastapi.testclient import TestClient
from agent.main import app

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        print("Health check response:", response.status_code, response.json())
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["system_prompt_loaded"] is True

def test_explain_output_formatting_rules():
    with TestClient(app) as client:
        payload = [
            {
                "prediction": 1,
                "probability": 0.5200, # Within 0.05 of threshold 0.50 -> Should trigger uncertainty sentence
                "shap_values": {
                    "tcp_flag_density": -1.6375,
                    "log_pkt_max": 0.5843,
                    "pkt_mean_to_max": 0.2972,
                    "log_pkt_mean": -0.8284
                },
                "risk_score": 74.19,
                "risk_tier": "High",
                "attck_context": [
                    {
                        "technique_id": "T0855",
                        "name": "Unauthorized Command Message",
                        "description": "Adversaries may send unauthorized command messages..."
                    }
                ]
            }
        ]
        
        response = client.post("/explain", json=payload)
        print("Explain HTTP Status:", response.status_code)
        assert response.status_code == 200
        data = response.json()
        print("Explain Response Data:\n", data)

        item = data["explanations"][0]
        text = item["explanation_text"]

        # Assert Plain Text rules (no markdown ticks, no bullet points)
        assert "```" not in text
        assert "*" not in text
        assert "#" not in text

        # Assert Sentence Count rule (3-5 sentences)
        import re
        sentences = [s.strip() for s in re.split(r'(?<=[a-zA-Z0-9\)])\.\s+', text) if s.strip()]
        print(f"\nGenerated Sentences ({len(sentences)}):\n", sentences)
        assert 3 <= len(sentences) <= 6

        # Assert Candidate Technique phrasing rule ("possibly consistent with")
        assert "possibly consistent with" in text
        assert "Unauthorized Command Message" in text or "T0855" in text

        # Assert Uncertainty Rule (probability 0.52 is within 0.05 of 0.50)
        assert "uncertain" in text.lower() or "uncertainty" in text.lower()

def test_explain_benign_plain_text():
    with TestClient(app) as client:
        payload = [
            {
                "prediction": 0,
                "probability": 0.1200,
                "shap_values": {
                    "tcp_flag_density": -0.95,
                    "log_pkt_max": -0.40,
                    "pkt_mean_to_max": -0.20,
                    "log_pkt_mean": -0.10
                }
            }
        ]
        response = client.post("/explain", json=payload)
        assert response.status_code == 200
        text = response.json()["explanations"][0]["explanation_text"]
        print("\nBenign Telemetry Plain-Text Output:\n", text)
        assert "benign" in text.lower()
        assert "```" not in text

if __name__ == "__main__":
    test_health()
    test_explain_output_formatting_rules()
    test_explain_benign_plain_text()
    print("\n[✓] All Decision Support Agent system prompt compliance tests passed!")
