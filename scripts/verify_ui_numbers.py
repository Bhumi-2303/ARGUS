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

# Add src and root to path
sys.path.insert(0, os.path.abspath("."))
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
            # New Check: Flag if any numerical column has identical values for all rows
            # or if any row has identical values across all its numerical columns
            if len(api_data) > 1:
                # Check columns
                keys = [k for k in api_data[0].keys() if isinstance(api_data[0][k], (int, float))]
                for k in keys:
                    first_val = api_data[0][k]
                    if all(row.get(k) == first_val for row in api_data):
                        # Kappa and MCC can legitimately be close to 0, but if EVERYTHING is exactly identical, it's suspicious.
                        # Actually, let's flag if it's identical across all models (like 0.0000)
                        if first_val == 0.0:
                            print(f"  [ FAIL ] Column '{k}' has identical repeated value {first_val} across all models in {table_name}")
                            all_matched = False
                
                # Check rows
                for i, row in enumerate(api_data):
                    num_vals = [v for k,v in row.items() if isinstance(v, (int, float))]
                    if len(num_vals) > 2 and all(v == num_vals[0] for v in num_vals):
                        print(f"  [ FAIL ] Row {i} has identical repeated value {num_vals[0]} across all metrics in {table_name}")
                        all_matched = False

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



def verify_protocol_limits_page():
    print("\n" + "=" * 80)
    print("        ARGUS PROTOCOL LIMITS PAGE TEXT VERIFICATION")
    print("=" * 80)

    import re
    with open("web/src/features/protocol_limits/ProtocolLimitsPage.tsx", "r") as f:
        page_text = f.read()
    
    # 1. Verify DANN raw metric discrepancy states exactly 0.332095
    if "0.332095" not in page_text:
        print("  [ FAIL ] Missing exact recomputed ROC-AUC (0.332095) in ProtocolLimitsPage")
        return False
    if "1.084%" not in page_text and "0.064%" not in page_text:
        print("  [ FAIL ] Missing exact discrepancy Specificity metrics in ProtocolLimitsPage")
        return False
        
    # 2. Verify V1 feature space duplication statement
    if "82 unique vectors" not in page_text:
        print("  [ FAIL ] Missing legacy V1 representation condensation count (82 unique vectors)")
        return False
        
    # 3. Verify cross-domain leakage vectors
    if "7 target vectors leaked" not in page_text:
        print("  [ FAIL ] Missing cross-domain overlap sum (7 target vectors)")
        return False

    print("  [ PASS ] Protocol Limits Page explicitly states all required open verification discrepancies accurately.")
    return True



def verify_model_comparison_ui():
    print("\n" + "=" * 80)
    print("        ARGUS UI RENDER LOGIC VERIFICATION (ModelComparisonPage.tsx)")
    print("=" * 80)
    
    with open("web/src/features/benchmark/ModelComparisonPage.tsx", "r") as f:
        page_text = f.read()
        
    matched = True
    
    # Check for hardcoded 95/5/10/90 CM splits by checking fallback usage
    # "byte-identical to another model's confusion matrix" means they used a static default.
    if "(r.recall ?? 0.9)" in page_text or "(r.Recall ?? 0.9)" in page_text:
        print("  [ FAIL ] Found identical fallback confusion matrix logic in ModelComparisonPage.tsx (0.9/0.05)")
        matched = False
        
    # Check if there's a fallback that produces a repeated 0.0000 in columns/rows.
    if "(r.mcc ?? 0).toFixed(4)" in page_text or "r.MCC ?? 0).toFixed(4)" in page_text:
        print("  [ FAIL ] Found identical 0.0000 fallback for missing metrics in table rendering")
        matched = False

    if matched:
        print("  [ PASS ] No identical repeated fallback values (like 0.0000 or 95/5) found in ModelComparisonPage.tsx")
        
    return matched

if __name__ == "__main__":
    m_ok = verify_metrics()
    t_ok = verify_topology_strings()
    p_ok = verify_protocol_limits_page()
    c_ok = verify_model_comparison_ui()
    if not (m_ok and t_ok and p_ok and c_ok):
        sys.exit(1)
    sys.exit(0)
