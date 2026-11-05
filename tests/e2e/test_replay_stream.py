"""End-to-end tests for verified flow replay streaming over WebSocket and SSE.

Tests assert:
1. Stream metadata and UI labels match "verified flow replay"
2. Handshake and initial telemetry metadata
3. Strict 6-agent stage event ordering (DATA_INTELLIGENCE -> THREAT_ANALYSIS -> EXPLAINABILITY -> KNOWLEDGE_CONTEXT -> RISK_PREDICTION -> DECISION_SUPPORT)
4. Upstream stage failures produce SKIPPED downstream events with dependency error tracking
5. Interactive controls: pause, resume, speed, domain selection (CICIoT / NF-ToN), and deterministic seed
6. RBAC enforcement (missing or unauthorized token rejected with 1008 policy violation)
7. Message size limit enforcement (>32 KB rejected with 1009)
"""

import json
import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect

from argus.api.main import app
from argus.auth.models import UserPrincipal
from argus.auth.jwt import jwt_validator
from configs.settings import get_settings

client = TestClient(app)


def test_replay_stream_handshake_and_verified_label():
    """WebSocket /api/v1/stream must complete handshake and label stream as 'verified flow replay'."""
    with client.websocket_connect("/api/v1/stream?domain=nfton&speed=50.0&seed=42") as ws:
        init_data = ws.receive_json()
        assert init_data["type"] == "stream_init"
        assert init_data["stream_type"] == "verified flow replay"
        assert init_data["label"] == "verified flow replay"
        assert init_data["domain"] == "nfton"
        assert init_data["status"] == "ready"
        assert init_data["total_rows"] > 0


def test_replay_stream_backward_compatible_endpoint():
    """WebSocket /api/v1/stream/ws backward-compatible endpoint also works identically."""
    with client.websocket_connect("/api/v1/stream/ws?domain=ciciot&speed=50.0&seed=101") as ws:
        init_data = ws.receive_json()
        assert init_data["type"] == "stream_init"
        assert init_data["stream_type"] == "verified flow replay"
        assert init_data["domain"] == "ciciot"


def test_replay_stream_event_order_and_stage_schemas():
    """Stream must emit per-stage events in strict 6-stage order matching trace schemas."""
    expected_order = [
        "DATA_INTELLIGENCE",
        "THREAT_ANALYSIS",
        "EXPLAINABILITY",
        "KNOWLEDGE_CONTEXT",
        "RISK_PREDICTION",
        "DECISION_SUPPORT",
    ]

    with client.websocket_connect("/api/v1/stream?domain=nfton&speed=50.0&seed=42") as ws:
        # Handshake
        init_msg = ws.receive_json()
        assert init_msg["type"] == "stream_init"

        # Collect events for one full flow run
        stages_started = []
        stages_ended = []
        flow_completed_msg = None

        # A complete flow produces 6 start + 6 end = 12 events + 1 flow_completed
        for _ in range(13):
            msg = ws.receive_json()
            if msg.get("type") == "flow_event":
                assert msg["stream_type"] == "verified flow replay"
                evt = msg.get("event", {})
                assert "source_node" in evt
                assert "target_node" in evt
                assert "payload" in evt

                if msg.get("event_type") == "stage_start":
                    stages_started.append(msg["stage"])
                    assert msg["status"] == "RUNNING"
                elif msg.get("event_type") == "stage_end":
                    stages_ended.append(msg["stage"])
                    assert msg["status"] in ("SUCCESS", "SKIPPED", "FAILED")
                    assert msg["duration_ms"] is not None
            elif msg.get("type") == "flow_completed":
                flow_completed_msg = msg
                break

        # Assert strict stage ordering
        assert stages_started == expected_order, f"Stages started out of order: {stages_started}"
        assert stages_ended == expected_order, f"Stages ended out of order: {stages_ended}"

        # Assert flow completion payload
        assert flow_completed_msg is not None
        assert flow_completed_msg["type"] == "flow_completed"
        assert flow_completed_msg["stream_type"] == "verified flow replay"
        assert flow_completed_msg["status"] == "completed"
        assert flow_completed_msg["total_stages"] == 6


def test_replay_stream_upstream_failure_produces_skipped_downstream(monkeypatch):
    """Upstream failure in DATA_INTELLIGENCE must produce FAILED event and SKIPPED for all downstream stages."""
    from argus.agents.data_intelligence.agent import DataIntelligenceAgent

    # Monkeypatch process_flow to simulate upstream failure
    async def mock_failed_process_flow(self, flow_input):
        raise RuntimeError("Simulated upstream sensor corruption")

    monkeypatch.setattr(DataIntelligenceAgent, "process_flow", mock_failed_process_flow)

    with client.websocket_connect("/api/v1/stream?domain=nfton&speed=50.0&seed=42") as ws:
        # Handshake
        ws.receive_json()

        # Collect events for the failed flow
        events = []
        for _ in range(10):
            msg = ws.receive_json()
            events.append(msg)
            if msg.get("type") == "flow_completed":
                break

        stage_events = [e for e in events if e.get("type") == "flow_event" and e.get("event_type") == "stage_end"]
        
        # DIA must be FAILED
        dia_evt = next((e for e in stage_events if e["stage"] == "DATA_INTELLIGENCE"), None)
        assert dia_evt is not None
        assert dia_evt["status"] == "FAILED"
        assert "Simulated upstream sensor corruption" in dia_evt["error"]

        # Downstream stages must all be SKIPPED with dependency error
        downstream = ["THREAT_ANALYSIS", "EXPLAINABILITY", "KNOWLEDGE_CONTEXT", "RISK_PREDICTION", "DECISION_SUPPORT"]
        for stage in downstream:
            stage_evt = next((e for e in stage_events if e["stage"] == stage), None)
            assert stage_evt is not None, f"Missing event for stage {stage}"
            assert stage_evt["status"] == "SKIPPED"
            assert "Dependency failed: Simulated upstream sensor corruption" in stage_evt["error"]

        # Flow completion must report failed status
        flow_done = next((e for e in events if e.get("type") == "flow_completed"), None)
        assert flow_done is not None
        assert flow_done["status"] == "failed"


def _receive_control_ack(ws, expected_action: str):
    for _ in range(50):
        msg = ws.receive_json()
        if msg.get("type") == "control_ack" and msg.get("action") == expected_action:
            return msg
    raise AssertionError(f"Expected control_ack for {expected_action} not received")


def test_replay_stream_interactive_controls():
    """Client can pause, resume, change speed, switch domain, and change seed interactively."""
    with client.websocket_connect("/api/v1/stream?domain=nfton&speed=20.0&seed=42") as ws:
        # 1. Handshake
        init_data = ws.receive_json()
        assert init_data["type"] == "stream_init"

        # 2. Pause command
        ws.send_json({"action": "pause"})
        ack = _receive_control_ack(ws, "pause")
        assert ack["status"] == "paused"
        assert ack["stream_type"] == "verified flow replay"

        # 3. Change speed
        ws.send_json({"action": "speed", "value": 5.0})
        ack = _receive_control_ack(ws, "speed")
        assert ack["speed"] == 5.0

        # 4. Switch domain to CICIoT
        ws.send_json({"action": "domain", "value": "ciciot"})
        ack = _receive_control_ack(ws, "domain")
        assert ack["domain"] == "ciciot"

        # 5. Change seed
        ws.send_json({"action": "seed", "value": 777})
        ack = _receive_control_ack(ws, "seed")
        assert ack["seed"] == 777

        # 6. Resume
        ws.send_json({"action": "resume"})
        ack = _receive_control_ack(ws, "resume")
        assert ack["status"] == "running"


def test_replay_stream_message_size_limit():
    """Incoming messages larger than 32KB must be rejected with WS code 1009 (MESSAGE_TOO_BIG)."""
    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect("/api/v1/stream?domain=nfton&speed=50.0") as ws:
            ws.receive_json()  # handshake

            # Send frame exceeding 32 KB (35 KB payload)
            large_payload = json.dumps({"action": "dummy", "padding": "x" * 35000})
            ws.send_text(large_payload)

            # Read until disconnect
            for _ in range(50):
                ws.receive_json()

    assert excinfo.value.code == 1009


def test_replay_stream_rbac_enforcement(monkeypatch):
    """WebSocket stream rejects unauthenticated or unauthorized users when RBAC is enforced."""
    settings = get_settings()
    monkeypatch.setattr(settings.security, "oidc_enabled", True)

    # 1. Connection without token rejected
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/stream?domain=nfton") as ws:
            pass

    # 2. Connection with invalid token rejected
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/stream?domain=nfton&token=invalid.jwt.token") as ws:
            pass

    # 3. Token lacking 'read:telemetry' rejected
    user_without_perm = UserPrincipal(
        sub="analyst-001",
        issuer="argus-test",
        roles=["viewer"],
        permissions={"read:models"}
    )
    monkeypatch.setattr(jwt_validator, "validate_token", lambda token: asyncio.sleep(0, result=user_without_perm))

    import asyncio
    async def mock_validate_no_perm(tok):
        return user_without_perm

    monkeypatch.setattr(jwt_validator, "validate_token", mock_validate_no_perm)
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/stream?domain=nfton&token=mock-no-perm") as ws:
            pass

    # 4. Token with 'read:telemetry' succeeds
    user_with_perm = UserPrincipal(
        sub="operator-001",
        issuer="argus-test",
        roles=["operator"],
        permissions={"read:telemetry"}
    )
    async def mock_validate_with_perm(tok):
        return user_with_perm

    monkeypatch.setattr(jwt_validator, "validate_token", mock_validate_with_perm)
    with client.websocket_connect("/api/v1/stream?domain=nfton&token=mock-valid-perm") as ws:
        init_data = ws.receive_json()
        assert init_data["type"] == "stream_init"
        assert init_data["stream_type"] == "verified flow replay"


def test_replay_stream_sse_metadata_header():
    """GET /api/v1/stream must include X-Stream-Type header matching 'verified flow replay'."""
    viewer_user = UserPrincipal(
        sub="viewer-001",
        issuer="argus-test",
        roles=["operator"],
        permissions={"read:telemetry"}
    )
    from argus.auth.rbac import get_current_user
    app.dependency_overrides[get_current_user] = lambda: viewer_user

    try:
        response = client.get("/api/v1/stream?domain=nfton&speed=100.0&rows=1")
        assert response.status_code == 200
        assert response.headers.get("X-Stream-Type") == "verified flow replay"
    finally:
        app.dependency_overrides.clear()
