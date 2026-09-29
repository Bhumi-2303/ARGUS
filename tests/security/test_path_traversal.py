"""Tests for Path Traversal and Directory Traversal protections across API and DataManager."""

import pytest
from fastapi.testclient import TestClient

from argus.api.main import app
from argus.data.manager import DataManager
from argus.auth.models import UserPrincipal
from argus.auth.rbac import get_current_user

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_authenticated_user():
    """Ensure user has read permissions for tests."""
    user = UserPrincipal(
        sub="security-tester",
        issuer="argus-test",
        roles=["analyst", "operator", "admin"],
        permissions={"read:data", "read:domains", "read:results", "run:prediction", "read:telemetry"}
    )
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


def test_datamanager_resolve_safe_path_rejects_escape():
    """DataManager._resolve_safe_path must raise PermissionError on escape attempts."""
    dm = DataManager()

    traversal_subpaths = [
        "../../../etc/passwd",
        "../../configs/settings.py",
        "results/verified/../../../../etc/shadow",
        "../../outside_repo_file"
    ]
    for subpath in traversal_subpaths:
        with pytest.raises(PermissionError):
            dm._resolve_safe_path(subpath)


def test_datamanager_get_result_table_rejects_traversal_and_unallowlisted():
    """DataManager.get_result_table must raise KeyError on traversal characters and unallowlisted tables."""
    dm = DataManager()

    malicious_tables = [
        "../../etc/passwd",
        "..%2f..%2fconfigs/settings.py",
        "ciciot\x00malicious",
        "unallowlisted_secret_table",
        "../models/model_d1_source.txt"
    ]
    for table in malicious_tables:
        with pytest.raises(KeyError):
            dm.get_result_table(table)


def test_api_results_endpoint_rejects_traversal():
    """API endpoint /api/v1/results/{table} must return 404/400 for traversal payloads."""
    payloads = [
        "../../etc/passwd",
        "%2e%2e%2fconfigs",
        "nonexistent_table",
        "../../results/verified/five_model_complete_comparison"
    ]
    for payload in payloads:
        response = client.get(f"/api/v1/results/{payload}")
        assert response.status_code in (400, 404), f"Unexpected status {response.status_code} for {payload}"
        assert "root:" not in response.text


def test_api_unmatched_route_returns_404():
    """Unmatched API routes must return 404 rather than falling through to SPA handler with 200."""
    response = client.get("/api/v1/data/nonexistent_schema")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower() or "error" in data


def test_spa_fallback_blocks_directory_escape():
    """SPA fallback handler must reject path traversal requests seeking server files."""
    payloads = [
        "/..%2f..%2fetc/passwd",
        "/static/../../configs/settings.py",
        "/assets/../configs/settings.py"
    ]
    for payload in payloads:
        response = client.get(payload)
        # Must not disclose contents of settings.py or passwd
        assert response.status_code in (400, 403, 404) or "SECRET_KEY" not in response.text
