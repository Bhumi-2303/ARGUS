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

    # Explicit assertions for key remediation metrics
    if table_name == "five_model_complete_comparison":
        model_rows = {r["Model"]: r for r in api_data}
        
        # Remediation F-01 & F-02: Clean Class-aware CORAL verified metrics
        assert "Clean Class-aware CORAL + XGBoost" in model_rows
        clean_coral = model_rows["Clean Class-aware CORAL + XGBoost"]
        assert pytest.approx(clean_coral["MCC"], abs=1e-5) == 0.385503
        assert pytest.approx(clean_coral["Precision"], abs=1e-5) == 0.940039
        assert pytest.approx(clean_coral["Specificity"], abs=1e-5) == 0.914278
        assert pytest.approx(clean_coral["Accuracy"], abs=1e-5) == 0.619096
        assert pytest.approx(clean_coral["F1"], abs=1e-5) == 0.659233
        assert pytest.approx(clean_coral["Threshold"], abs=1e-5) == 0.99

        # Remediation F-03 & F-09: DANN collapsed representation metrics
        assert "DANN" in model_rows
        dann = model_rows["DANN"]
        assert pytest.approx(dann["MCC"], abs=1e-5) == 0.012855
        assert pytest.approx(dann["ROC_AUC"], abs=1e-5) == 0.332096
        assert pytest.approx(dann["Specificity"], abs=1e-5) == 0.000646
        assert pytest.approx(dann["Threshold"], abs=1e-5) == 0.60
        assert dann["Protocol_Status"] == "Leakage-controlled DANN"

        # Source-only XGBoost verified metrics from FINAL_five_model_comparison.csv
        assert "Source-only XGBoost" in model_rows
        source_xgb = model_rows["Source-only XGBoost"]
        assert pytest.approx(source_xgb["Accuracy"], abs=1e-5) == 0.720658
        assert pytest.approx(source_xgb["Precision"], abs=1e-5) == 0.724719
        assert pytest.approx(source_xgb["Recall"], abs=1e-5) == 0.991925
        assert pytest.approx(source_xgb["F1"], abs=1e-5) == 0.837526
        assert pytest.approx(source_xgb["Balanced_Accuracy"], abs=1e-5) == 0.497193
        assert pytest.approx(source_xgb["Kappa"], abs=1e-5) == -0.008062
        assert pytest.approx(source_xgb["MCC"], abs=1e-5) == -0.031074
        assert pytest.approx(source_xgb["ROC_AUC"], abs=1e-5) == 0.323041
        assert pytest.approx(source_xgb["PR_AUC"], abs=1e-5) == 0.639234
        assert pytest.approx(source_xgb["Specificity"], abs=1e-5) == 0.002462
        assert pytest.approx(source_xgb["Threshold"], abs=1e-5) == 0.50

    elif table_name == "dann_final_test_metrics":
        metric_rows = {r["Metric"]: float(r["Value"]) for r in api_data}
        assert pytest.approx(metric_rows["ROC-AUC"], abs=1e-5) == 0.33209554
        assert pytest.approx(metric_rows["Matthews Correlation Coefficient"], abs=1e-5) == 0.01285487
        assert pytest.approx(metric_rows["Specificity"], abs=1e-5) == 0.00064560
        assert pytest.approx(metric_rows["Precision"], abs=1e-5) == 0.72594136
        assert pytest.approx(metric_rows["Recall"], abs=1e-5) == 0.99984478


def test_population_badge_metrics():
    """Verify exact precision and specificity badge formatting for all verified models."""
    # Source-only XGBoost (Precision 0.724719, Specificity 0.002462)
    source_prec = 0.724719
    source_spec = 0.002462
    assert f"{source_prec * 100:.2f}%" == "72.47%"
    assert f"{source_spec * 100:.2f}%" == "0.25%"

    # Clean Class-aware CORAL (Precision 0.940039, Specificity 0.914278)
    coral_prec = 0.940039
    coral_spec = 0.914278
    assert f"{coral_prec * 100:.2f}%" == "94.00%"
    assert f"{coral_spec * 100:.2f}%" == "91.43%"

    # Verify that InputAnalysisPage.tsx contains the exact formatted badge strings
    with open("web/src/features/analysis/InputAnalysisPage.tsx") as f:
        page_content = f.read()

    assert "Prec: <strong className=\"text-slate-200\">72.47%</strong>" in page_content
    assert "Spec: <strong className=\"text-rose-400\">0.25%</strong>" in page_content
    assert "Prec: <strong className=\"text-slate-200\">94.00%</strong>" in page_content
    assert "Spec: <strong className=\"text-slate-200\">91.43%</strong>" in page_content
    assert "Clean CORAL XGBoost" in page_content
    assert "Source-Only XGBoost" in page_content
