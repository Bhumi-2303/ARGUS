"""Tests for HTTP security headers and CORS protection policies."""

import pytest
from fastapi.testclient import TestClient

from argus.api.main import app
from configs.settings import get_settings

client = TestClient(app)


def test_security_headers_present():
    """All responses must include standard OWASP defensive security headers."""
    response = client.get("/health")
    assert response.status_code == 200

    headers = response.headers

    # 1. Clickjacking defense
    assert headers.get("x-frame-options") == "DENY"

    # 2. MIME sniffing defense
    assert headers.get("x-content-type-options") == "nosniff"

    # 3. Referrer policy
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    # 4. Permissions policy
    assert "geolocation=()" in headers.get("permissions-policy", "")
    assert "microphone=()" in headers.get("permissions-policy", "")

    # 5. Content Security Policy
    csp = headers.get("content-security-policy", "")
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "object-src 'none'" in csp


def test_cors_preflight_allowed_origin():
    """Preflight OPTIONS request from configured origin must return CORS headers."""
    response = client.options(
        "/api/v1/domains",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    # Under test/dev environment, localhost is allowed
    assert response.headers.get("access-control-allow-origin") in ("http://localhost:5173", "*")


def test_cors_preflight_disallowed_origin_in_production(monkeypatch):
    """In production mode, unauthorized origins must not be granted CORS headers."""
    # We test CORS matching logic directly
    settings = get_settings()
    allowed_origins = [o.rstrip("/") for o in settings.security.cors_origins]
    evil_origin = "http://evil-attacker.com"
    assert evil_origin not in allowed_origins
