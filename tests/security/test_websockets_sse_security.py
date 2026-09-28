"""Tests for WebSockets and SSE streaming security controls."""

import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect

from argus.api.main import app
from argus.auth.models import UserPrincipal
from argus.auth.rbac import get_current_user
from configs.settings import get_settings

client = TestClient(app)


def test_sse_stream_rejects_unauthorized_user():
    """SSE endpoint /api/v1/stream must reject requests without 'read:telemetry' permission."""
    guest_user = UserPrincipal(
        sub="guest-user",
        issuer="argus-test",
        roles=["guest"],
        permissions={"read:models"}
    )
    app.dependency_overrides[get_current_user] = lambda: guest_user

    try:
        response = client.get("/api/v1/stream?domain=nfton")
        assert response.status_code == 403
        assert "Missing required permission 'read:telemetry'" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_sse_stream_validates_domain_parameter():
    """SSE endpoint must reject unallowlisted domain parameters with 400."""
    authorized_user = UserPrincipal(
        sub="analyst-user",
        issuer="argus-test",
        roles=["analyst"],
        permissions={"read:telemetry"}
    )
    app.dependency_overrides[get_current_user] = lambda: authorized_user

    try:
        response = client.get("/api/v1/stream?domain=malicious_injection")
        assert response.status_code == 400
        assert "Invalid domain" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_sse_stream_validates_model_parameters():
    """SSE endpoint must reject unallowlisted or unregistered models with 400."""
    authorized_user = UserPrincipal(
        sub="analyst-user",
        issuer="argus-test",
        roles=["analyst"],
        permissions={"read:telemetry"}
    )
    app.dependency_overrides[get_current_user] = lambda: authorized_user

    try:
        response = client.get("/api/v1/stream?domain=nfton&models=unknown_evil_model")
        assert response.status_code == 400
        assert "Invalid model" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_websocket_stream_rejects_invalid_token(monkeypatch):
    """WebSocket /api/v1/stream/ws must reject connections with invalid token."""
    # Attempt connecting with invalid token
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/stream/ws?token=invalid.jwt.token") as ws:
            pass


def test_websocket_agents_stream_rejects_unauthenticated():
    """WebSocket /api/v1/agents/stream must reject connections without credentials when auth enabled."""
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/agents/stream?token=invalid-jwt") as ws:
            pass
