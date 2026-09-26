"""Test that diagnostic results can never be returned without diagnostic_only: true."""

import pytest
from fastapi.testclient import TestClient

from argus.api.main import app
from argus.data.manager import data_manager

client = TestClient(app)


def test_diagnostic_table_endpoint_carries_flag():
    """Verify that GET /api/v1/results/diagnostic_class_aware_coral includes diagnostic_only: true."""
    response = client.get("/api/v1/results/diagnostic_class_aware_coral")
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["diagnostic_only"] is True, "Diagnostic results MUST carry diagnostic_only: true"
    assert "diagnostic" in payload["protocol_status"].lower() or payload["protocol_status"] == "diagnostic_only"


def test_data_manager_enforces_diagnostic_flag():
    """Verify DataManager directly enforces diagnostic_only=True for any diagnostic table."""
    table_res = data_manager.get_result_table("diagnostic_class_aware_coral")
    assert table_res.diagnostic_only is True, "DataManager must enforce diagnostic_only=True for diagnostic tables"


def test_diagnostic_flag_cannot_be_false_for_diagnostic_table():
    """Verify that any table containing diagnostic protocols cannot have diagnostic_only=False."""
    table_res = data_manager.get_result_table("diagnostic_class_aware_coral")
    
    # Asserting invariant: if protocol_status or table_name contains 'diagnostic', diagnostic_only MUST be True
    if "diagnostic" in table_res.table_name.lower() or "diagnostic" in table_res.protocol_status.lower():
        assert table_res.diagnostic_only is True
