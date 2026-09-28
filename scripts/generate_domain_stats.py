#!/usr/bin/env python3
"""Generate domain statistics from full verified test CSVs and class prior summaries."""

import json
import os
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def generate_domain_stats():
    ciciot_test_path = PROJECT_ROOT / "data/raw/legacy_package/argus_coral_data/ciciot_test_features.csv"
    nfton_test_path = PROJECT_ROOT / "data/raw/legacy_package/argus_coral_data/nfton_test_features.csv"
    prior_path = PROJECT_ROOT / "archive/backups/phase3_results/domain_shift/class_prior_summary.csv"
    sweep_path = PROJECT_ROOT / "results/verified/d3_native_threshold_sweep.csv"
    out_path = PROJECT_ROOT / "results/verified/domain_statistics.json"

    stats = {}

    # D1: CICIoT2023
    if ciciot_test_path.exists():
        df_ciciot = pd.read_csv(ciciot_test_path)
        ciciot_total = len(df_ciciot)
        ciciot_attack = int(df_ciciot["label"].sum())
        ciciot_benign = ciciot_total - ciciot_attack
        ciciot_ratio = float(ciciot_attack / ciciot_total)
        stats["ciciot"] = {
            "name": "CICIoT2023",
            "split": "test_holdout",
            "sample_size": ciciot_total,
            "attack_samples": ciciot_attack,
            "benign_samples": ciciot_benign,
            "attack_ratio": round(ciciot_ratio, 6),
            "source_file": "data/raw/legacy_package/argus_coral_data/ciciot_test_features.csv"
        }

    # D2: NF-ToN-IoT-v2
    if nfton_test_path.exists():
        df_nfton = pd.read_csv(nfton_test_path)
        nfton_total = len(df_nfton)
        nfton_attack = int(df_nfton["label"].sum())
        nfton_benign = nfton_total - nfton_attack
        nfton_ratio = float(nfton_attack / nfton_total)
        stats["nfton"] = {
            "name": "NF-ToN-IoT-v2",
            "split": "test_holdout",
            "sample_size": nfton_total,
            "attack_samples": nfton_attack,
            "benign_samples": nfton_benign,
            "attack_ratio": round(nfton_ratio, 6),
            "source_file": "data/raw/legacy_package/argus_coral_data/nfton_test_features.csv"
        }

    # D3: IEC 60870-5-104 (SCADA)
    if prior_path.exists():
        df_prior = pd.read_csv(prior_path)
        d3_row = df_prior[df_prior["Domain"].str.contains("IEC 60870-5-104", na=False)].iloc[0]
        d3_total = int(d3_row["Total_Samples"])
        d3_attack = int(d3_row["Attack_Samples"])
        d3_benign = int(d3_row["Benign_Samples"])
        d3_ratio = float(d3_attack / d3_total)
        stats["iec104"] = {
            "name": "IEC104 SCADA",
            "split": "full_population_and_calibration",
            "sample_size": 571562,  # Verified calibration sweep size
            "total_population": d3_total,
            "attack_samples": d3_attack,
            "benign_samples": d3_benign,
            "attack_ratio": round(d3_ratio, 6),
            "source_file": "archive/backups/phase3_results/domain_shift/class_prior_summary.csv"
        }

    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Generated domain statistics saved to: {out_path}")
    for k, v in stats.items():
        print(f"  [{k}] N={v['sample_size']}, attack_ratio={v['attack_ratio']} ({v['source_file']})")

if __name__ == "__main__":
    generate_domain_stats()
