"""Test that every metric served by GET /api/v1/results/{table} equals the exact value in its CSV file."""

import os
import pandas as pd
import numpy as np
import pytest
from fastapi.testclient import TestClient

from argus.api.main import app

client = TestClient(app)

VERIFIED_TABLES = [
    "five_model_complete_comparison",
    "dann_final_test_metrics",
    "d3_native_threshold_sweep",
    "SHAP_vs_Target_Gain"
]


@pytest.mark.parametrize("table_name", VERIFIED_TABLES)
def test_served_metrics_equal_csv_values(table_name):
    """Verify that every metric served by the API equals the exact value in the underlying CSV file."""
    csv_path = f"results/verified/{table_name}.csv"
    assert os.path.exists(csv_path), f"Verified CSV file missing at {csv_path}"

    csv_df = pd.read_csv(csv_path)

    response = client.get(f"/api/v1/results/{table_name}")
    assert response.status_code == 200, f"Failed to fetch table {table_name}: {response.text}"

    resp_json = response.json()
    assert resp_json["table_name"] == table_name
    assert resp_json["row_count"] == len(csv_df)
    assert resp_json["diagnostic_only"] is False

    api_data = resp_json["data"]
    assert len(api_data) == len(csv_df)

    for i, row in csv_df.iterrows():
        api_row = api_data[i]
        for col in csv_df.columns:
            csv_val = row[col]
            api_val = api_row[col]

            if pd.isna(csv_val):
                assert pd.isna(api_val) or api_val is None
            elif isinstance(csv_val, (float, int, np.floating, np.integer)):
                # Float comparison
                assert pytest.approx(float(csv_val), rel=1e-6, abs=1e-6) == float(api_val), \
                    f"Mismatch in {table_name} row {i} col '{col}': csv={csv_val}, api={api_val}"
            else:
                assert str(csv_val) == str(api_val), \
                    f"Mismatch in {table_name} row {i} col '{col}': csv={csv_val}, api={api_val}"
