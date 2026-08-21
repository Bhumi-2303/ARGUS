#!/usr/bin/env python3
"""
Unit test script for verifying ARGUS Knowledge & Context Agent.
Tests GET /health, POST /context vector search against Chroma DB,
and differential retrieval across distinct SHAP feature alerts.
"""

from fastapi.testclient import TestClient
from knowledge_agent.main import app

FEATURE_PLAIN_LANGUAGE = {
    ("tcp_flag_density", True): "high TCP flag multiplicity and control flag density",
    ("tcp_flag_density", False): "unusually low TCP flag diversity",
    ("pkt_mean_to_max", True): "high packet size mean to max ratio",
    ("pkt_mean_to_max", False): "skewed packet length ratio",
    ("log_pkt_mean", True): "elevated average packet payload size",
    ("log_pkt_mean", False): "reduced average packet size",
    ("log_pkt_max", True): "unusually large maximum packet payload",
    ("log_pkt_max", False): "suppressed maximum packet length"
}

def build_shap_context_query(shap_values):
    sorted_feats = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
    top1_name, top1_val = sorted_feats[0]
    top1_desc = FEATURE_PLAIN_LANGUAGE.get((top1_name, top1_val >= 0), top1_name)
    if len(sorted_feats) > 1:
        top2_name, top2_val = sorted_feats[1]
        top2_desc = FEATURE_PLAIN_LANGUAGE.get((top2_name, top2_val >= 0), top2_name)
        return f"{top1_desc} combined with {top2_desc}, SCADA network flow"
    return f"{top1_desc}, SCADA network flow"

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
            "query": "unusually low TCP flag diversity combined with reduced average packet size, SCADA network flow",
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

def test_two_alert_differential_retrieval():
    """
    Differential Test:
    Alert A: tcp_flag_density dominates (-1.64) -> unusually low TCP flag diversity
    Alert B: log_pkt_max dominates (+3.50) -> unusually large maximum packet payload
    Verifies that Chroma vector search returns different MITRE ATT&CK techniques based on SHAP evidence.
    """
    with TestClient(app) as client:
        shap_alert_a = {"tcp_flag_density": -1.64, "log_pkt_mean": -0.83, "pkt_mean_to_max": 0.30, "log_pkt_max": 0.58}
        shap_alert_b = {"log_pkt_max": 3.50, "pkt_mean_to_max": 2.10, "tcp_flag_density": 0.10, "log_pkt_mean": 0.40}

        q_a = build_shap_context_query(shap_alert_a)
        q_b = build_shap_context_query(shap_alert_b)

        resp_a = client.post("/context", json={"query": q_a, "top_k": 3}).json()
        resp_b = client.post("/context", json={"query": q_b, "top_k": 3}).json()

        techs_a = [t["technique_id"] for t in resp_a["techniques"]]
        techs_b = [t["technique_id"] for t in resp_b["techniques"]]

        print(f"\n[*] Query Alert A: {q_a}")
        print(f"[*] Retrieved Techniques Alert A: {techs_a}")
        print(f"[*] Query Alert B: {q_b}")
        print(f"[*] Retrieved Techniques Alert B: {techs_b}")

        # Assert discriminating power: the top-3 retrieved techniques MUST NOT be 100% identical
        assert set(techs_a) != set(techs_b), "Discriminating failure: Alert A and Alert B returned identical techniques!"

if __name__ == "__main__":
    test_health()
    test_post_context()
    test_two_alert_differential_retrieval()
    print("\n[✓] Knowledge & Context Agent vector search & differential tests passed successfully!")
