"""Tests for global error masking, preventing information disclosure in exception responses."""

import pytest
import httpx
from fastapi.testclient import TestClient

from argus.api.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_internal_server_error_masks_implementation_details(monkeypatch):
    """500 Internal Server Errors must never disclose stack traces, paths, or variables to clients."""
    from argus.data.manager import data_manager

    def broken_get_domains():
        raise RuntimeError("CRITICAL_INTERNAL_DB_FAILURE: password='super_secret_db_pass' at /var/data/private.db")

    monkeypatch.setattr(data_manager, "get_domains", broken_get_domains)

    from argus.auth.models import UserPrincipal
    from argus.auth.rbac import get_current_user

    # Provide authorized user so it passes RBAC and hits the bug
    test_user = UserPrincipal(
        sub="test-user",
        issuer="argus-test",
        roles=["analyst"],
        permissions={"read:domains"}
    )
    app.dependency_overrides[get_current_user] = lambda: test_user

    try:
        # Use ASGITransport with raise_app_exceptions=False to simulate external client receiving HTTP 500
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
            response = await async_client.get("/api/v1/domains")
            assert response.status_code == 500

            data = response.json()
            assert data.get("error") == "internal_server_error"
            assert "unexpected error" in data.get("message", "").lower()
            assert "request_id" in data

            # CRITICAL ASSERTIONS: Sensitive details must NEVER appear in client body
            response_text = response.text
            assert "Traceback" not in response_text
            assert "super_secret_db_pass" not in response_text
            assert "CRITICAL_INTERNAL_DB_FAILURE" not in response_text
            assert "/var/data" not in response_text
    finally:
        app.dependency_overrides.clear()


def test_404_error_envelope_structure():
    """404 responses must use clean error envelope without stack traces."""
    response = client.get("/api/v1/nonexistent_route_xyz")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data or "detail" in data
    assert "Traceback" not in response.text


def test_validation_error_masks_python_internals():
    """422 Validation errors must disclose validation fields without internal Python object dumps."""
    response = client.post(
        "/api/v1/predict",
        json={"invalid_json_shape": True}
    )
    assert response.status_code == 422
    data = response.json()
    assert data.get("error") in ("ValidationError", "validation_error")
    assert "Traceback" not in response.text
    assert "File \"" not in response.text
