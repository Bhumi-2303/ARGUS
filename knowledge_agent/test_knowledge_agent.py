#!/usr/bin/env python3
"""
Unit test script for verifying ARGUS Knowledge & Context Agent.
Tests GET /health and POST /context vector search against Chroma DB.
"""

from fastapi.testclient import TestClient
from knowledge_agent.main import app

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        print("Health check response:", response.status_code, response.json())
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["indexed_techniques_count"] > 0

def test_post_context():
    with TestClient(app) as client:
        payload = {
            "query": "SCADA Modbus command injection or length anomaly",
            "top_k": 3
        }
        response = client.post("/context", json=payload)
        print("Context response status:", response.status_code)
        data = response.json()
        print("Context response data:", data)
        assert response.status_code == 200
        assert "query" in data
        assert "techniques" in data
        assert len(data["techniques"]) == 3
        for item in data["techniques"]:
            assert "technique_id" in item
            assert "name" in item
            assert "description" in item
            assert "mitigations" in item
            assert "distance" in item

if __name__ == "__main__":
    test_health()
    test_post_context()
    print("\n[✓] Knowledge & Context Agent vector search tests passed successfully!")
