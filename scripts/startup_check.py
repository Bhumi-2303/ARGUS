#!/usr/bin/env python3
"""ARGUS Demo Startup Health Check Script.

Verifies artifacts, sample parquet files, verified result CSVs, and web build.
Prints a clear PASS/FAIL ASCII table.
Exits with 0 on SUCCESS, 1 on FAILURE.
"""

import os
import sys

REQUIRED_ITEMS = [
    # Category, Item Name, Path
    ("Artifacts", "Model D1 Baseline (LightGBM)", "artifacts/models/model_d1_baseline.txt"),
    ("Artifacts", "Model D1 CORAL (LightGBM)", "artifacts/models/model_d1_coral.txt"),
    ("Artifacts", "Model D2 CORAL (LightGBM)", "artifacts/models/model_d2_coral.txt"),
    ("Artifacts", "Model D3 Native (LightGBM)", "artifacts/models/model_d3_native.txt"),
    ("Artifacts", "Model XGBoost Source", "artifacts/models/xgb_source.json"),
    ("Artifacts", "Model XGBoost Adapted", "artifacts/models/xgb_adapted.json"),

    ("Samples", "CICIoT2023 Source Parquet", "data/samples/ciciot.parquet"),
    ("Samples", "NF-ToN-IoT-v2 Target Parquet", "data/samples/nfton.parquet"),

    ("Results", "5-Model Comparison CSV", "results/verified/five_model_complete_comparison.csv"),
    ("Results", "DANN Test Metrics CSV", "results/verified/dann_final_test_metrics.csv"),
    ("Results", "D3 Native Sweep CSV", "results/verified/d3_native_threshold_sweep.csv"),
    ("Results", "SHAP vs Target Gain CSV", "results/verified/SHAP_vs_Target_Gain.csv"),
    ("Results", "Diagnostic CORAL CSV", "results/diagnostic/diagnostic_class_aware_coral.csv"),

    ("Frontend", "Built Web Dist HTML", "web/dist/index.html"),
]


def run_startup_check() -> bool:
    print("\n" + "=" * 80)
    print("                ARGUS RESEARCH STARTUP INTEGRITY VERIFICATION")
    print("=" * 80)
    print(f"{'Category':<12} | {'Asset / Component':<35} | {'File Status':<12} | {'Result':<8}")
    print("-" * 80)

    all_passed = True
    for cat, name, path in REQUIRED_ITEMS:
        exists = os.path.exists(path)
        status_str = "EXISTS" if exists else "MISSING"
        res_str = "[ PASS ]" if exists else "[ FAIL ]"

        if not exists:
            all_passed = False

        print(f"{cat:<12} | {name:<35} | {status_str:<12} | {res_str:<8}")

    # Validate that models actually load
    print("-" * 80)
    print("Validating Model Deserialization & Data Integrity...")
    try:
        import lightgbm as lgb
        import xgboost as xgb
        import pandas as pd

        # LightGBM validation
        m1 = lgb.Booster(model_file="artifacts/models/model_d2_coral.txt")
        print(f"{'Model Loader':<12} | {'LightGBM model_d2_coral.txt':<35} | {'LOADED':<12} | [ PASS ]")
        
        # XGBoost validation
        m2 = xgb.Booster()
        m2.load_model("artifacts/models/xgb_adapted.json")
        print(f"{'Model Loader':<12} | {'XGBoost xgb_adapted.json':<35} | {'LOADED':<12} | [ PASS ]")

        # Sample data validation
        df_ci = pd.read_parquet("data/samples/ciciot.parquet")
        assert len(df_ci) > 0 and "label" in df_ci.columns
        print(f"{'Data Loader':<12} | {f'CICIoT ({len(df_ci)} real rows)':<35} | {'VALID':<12} | [ PASS ]")

        df_nf = pd.read_parquet("data/samples/nfton.parquet")
        assert len(df_nf) > 0 and "label" in df_nf.columns
        print(f"{'Data Loader':<12} | {f'NF-ToN ({len(df_nf)} real rows)':<35} | {'VALID':<12} | [ PASS ]")

    except Exception as e:
        print(f"FAILED model/data validation: {e}")
        all_passed = False

    print("=" * 80)
    if all_passed:
        print("OVERALL VERIFICATION VERDICT: PASS — All required research assets verified.")
        print("=" * 80 + "\n")
        return True
    else:
        print("OVERALL VERIFICATION VERDICT: FAIL — One or more required assets failed validation.")
        print("=" * 80 + "\n")
        return False


if __name__ == "__main__":
    success = run_startup_check()
    if not success:
        sys.exit(1)
    sys.exit(0)
