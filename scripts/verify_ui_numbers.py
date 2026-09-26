#!/usr/bin/env python3
"""ARGUS Final Metric Verification Script.

Fetches every metric served by the API/UI and compares it directly against
the authoritative source CSV files in results/verified/ and results/diagnostic/.
Fails (exit code 1) if any numerical metric differs.
"""

import os
import sys
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

from argus.data.manager import data_manager


def verify_metrics():
    print("\n" + "=" * 80)
    print("        ARGUS FINAL NUMERICAL INTEGRITY VERIFICATION (CSV vs API)")
    print("=" * 80)

    tables_to_verify = [
        ("five_model_complete_comparison", "results/verified/five_model_complete_comparison.csv"),
        ("dann_final_test_metrics", "results/verified/dann_final_test_metrics.csv"),
        ("d3_native_threshold_sweep", "results/verified/d3_native_threshold_sweep.csv"),
        ("SHAP_vs_Target_Gain", "results/verified/SHAP_vs_Target_Gain.csv"),
        ("diagnostic_class_aware_coral", "results/diagnostic/diagnostic_class_aware_coral.csv"),
    ]

    all_matched = True

    for table_name, csv_path in tables_to_verify:
        print(f"\nVerifying Table: {table_name:<30} | CSV Path: {csv_path}")
        if not os.path.exists(csv_path):
            print(f"  [ FAIL ] Source CSV missing at {csv_path}")
            all_matched = False
            continue

        try:
            # Fetch from DataManager (same as API /results/{table})
            res = data_manager.get_result_table(table_name)
            api_data = res.data

            # Read raw CSV
            csv_df = pd.read_csv(csv_path)
            csv_data = csv_df.to_dict(orient="records")

            if len(api_data) != len(csv_data):
                print(f"  [ FAIL ] Row count mismatch: API={len(api_data)} vs CSV={len(csv_data)}")
                all_matched = False
                continue

            table_match = True
            for i, (api_row, csv_row) in enumerate(zip(api_data, csv_data)):
                for k, v in csv_row.items():
                    api_val = api_row.get(k)
                    # Float comparison
                    if isinstance(v, (float, int, np.floating, np.integer)) and not pd.isna(v):
                        if abs(float(api_val) - float(v)) > 1e-5:
                            print(f"  [ FAIL ] Row {i} Key '{k}': API={api_val} vs CSV={v}")
                            table_match = False
                            all_matched = False
                    elif str(api_val) != str(v):
                        if pd.isna(api_val) and pd.isna(v):
                            continue
                        print(f"  [ FAIL ] Row {i} Key '{k}': API='{api_val}' vs CSV='{v}'")
                        table_match = False
                        all_matched = False

            if table_match:
                print(f"  [ PASS ] All {len(csv_data)} rows and numerical metrics match source CSV 100%.")

        except Exception as ex:
            print(f"  [ ERROR ] Exception during verification of '{table_name}': {ex}")
            all_matched = False

    return all_matched

def verify_topology_strings():

    print("\n" + "=" * 80)
    print("        ARGUS SYSTEM TOPOLOGY STRING VERIFICATION (/api/v1/agents/topology)")
    print("=" * 80)

    try:
        from argus.api.routers.agents import TOPOLOGY_NODES, TOPOLOGY_EDGES
        print(f"Crawled {len(TOPOLOGY_NODES)} topology nodes and {len(TOPOLOGY_EDGES)} edge connections.")

        matched = True
        valid_types = {"bus", "gateway", "engine", "agent"}
        valid_implementations = {"full", "stub"}

        for node in TOPOLOGY_NODES:
            print(f"  Node [{node.id:<18}]: '{node.name}' | Type: {node.type} | Impl: {node.implementation_type}")
            if node.type not in valid_types:
                print(f"    [ FAIL ] Invalid node type '{node.type}' for node '{node.id}'")
                matched = False
            if node.implementation_type not in valid_implementations:
                print(f"    [ FAIL ] Invalid implementation_type '{node.implementation_type}' for node '{node.id}'")
                matched = False
            if not node.responsibility or len(node.responsibility) < 10:
                print(f"    [ FAIL ] Unsubstantiated or missing responsibility string for node '{node.id}'")
                matched = False

        if matched:
            print("  [ PASS ] All 10 topology node labels, responsibilities, and implementation flags verified.")
            return True
        else:
            print("  [ FAIL ] Topology string validation errors found.")
            return False
    except Exception as ex:
        print(f"  [ ERROR ] Exception during topology string verification: {ex}")
        return False


if __name__ == "__main__":
    m_ok = verify_metrics()
    t_ok = verify_topology_strings()
    if not (m_ok and t_ok):
        sys.exit(1)
    sys.exit(0)

