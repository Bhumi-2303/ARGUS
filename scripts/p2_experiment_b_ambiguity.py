#!/usr/bin/env python3
"""
ARGUS P2: Experiment B — Coordinate Label Ambiguity and Memorization Ceiling.

Computes:
1. Coordinate-level sample counts, class distributions, minority proportions,
   and Shannon entropy across training, calibration, test, and combined splits.
2. The empirical Bayes memorization ceiling (maximum accuracy achievable by
   memorizing the majority label of each coordinate).
3. Cross-domain conditional shift P(Y|X) between D1 (CIC-IoT-2023) and D2 (NF-ToN).
4. Produces coordinate_label_ambiguity.csv and bayes_ceiling_summary.json.
"""

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
TARGET = "label"

OUTPUT_DIR = Path("results/experiments/p2_coordinate_generalization")
DATA_DIR = Path("data/raw/legacy_package/argus_coral_data")


def calculate_entropy(p: float) -> float:
    """Shannon entropy for binary distribution."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def analyze_partition_ambiguity(df: pd.DataFrame, partition_name: str) -> tuple[pd.DataFrame, dict]:
    """Group by 4D coordinate and calculate ambiguity metrics."""
    t0 = time.time()
    n_total = len(df)
    n_att_total = int(df[TARGET].sum())
    n_ben_total = n_total - n_att_total

    # Group by coordinate
    g = df.groupby(FEATURES)[TARGET].agg(["count", "sum"]).reset_index()
    g.rename(columns={"count": "n_samples", "sum": "n_attack"}, inplace=True)
    g["n_benign"] = g["n_samples"] - g["n_attack"]

    g["majority_label"] = (g["n_attack"] >= g["n_benign"]).astype(int)
    g["minority_count"] = np.minimum(g["n_attack"], g["n_benign"])
    g["minority_proportion"] = g["minority_count"] / g["n_samples"]
    g["attack_proportion"] = g["n_attack"] / g["n_samples"]
    g["majority_correct_count"] = np.maximum(g["n_attack"], g["n_benign"])

    # Vectorized entropy
    p = g["attack_proportion"].values
    entropy = np.zeros_like(p)
    valid = (p > 0.0) & (p < 1.0)
    p_v = p[valid]
    entropy[valid] = -(p_v * np.log2(p_v) + (1.0 - p_v) * np.log2(1.0 - p_v))
    g["shannon_entropy"] = entropy

    # Ambiguity categories
    is_pure_benign = g["n_attack"] == 0
    is_pure_attack = g["n_benign"] == 0
    is_ambiguous = (g["n_attack"] > 0) & (g["n_benign"] > 0)

    n_groups = len(g)
    n_ambiguous_groups = int(is_ambiguous.sum())
    n_ambiguous_rows = int(g.loc[is_ambiguous, "n_samples"].sum())
    bayes_ceiling_acc = float(g["majority_correct_count"].sum() / n_total)

    summary = {
        "partition": partition_name,
        "total_rows": n_total,
        "total_attack_rows": n_att_total,
        "total_benign_rows": n_ben_total,
        "attack_prevalence": float(n_att_total / n_total),
        "unique_coordinates": n_groups,
        "pure_benign_coordinates": int(is_pure_benign.sum()),
        "pure_benign_rows": int(g.loc[is_pure_benign, "n_samples"].sum()),
        "pure_attack_coordinates": int(is_pure_attack.sum()),
        "pure_attack_rows": int(g.loc[is_pure_attack, "n_samples"].sum()),
        "ambiguous_coordinates": n_ambiguous_groups,
        "ambiguous_coordinate_percentage": float(n_ambiguous_groups / n_groups * 100),
        "rows_with_ambiguous_coordinates": n_ambiguous_rows,
        "rows_with_ambiguous_coordinates_percentage": float(n_ambiguous_rows / n_total * 100),
        "empirical_bayes_ceiling_accuracy": bayes_ceiling_acc,
        "empirical_bayes_error_floor": float(1.0 - bayes_ceiling_acc),
        "mean_minority_proportion_all": float(g["minority_proportion"].mean()),
        "mean_minority_proportion_ambiguous": float(g.loc[is_ambiguous, "minority_proportion"].mean()),
        "mean_shannon_entropy_all": float(g["shannon_entropy"].mean()),
        "mean_shannon_entropy_ambiguous": float(g.loc[is_ambiguous, "shannon_entropy"].mean()),
    }
    print(f"  [{partition_name}] Done in {time.time()-t0:.1f}s | "
          f"Coords: {n_groups:,} | Ambiguous Coords: {n_ambiguous_groups:,} ({summary['ambiguous_coordinate_percentage']:.2f}%) | "
          f"Ambiguous Rows: {n_ambiguous_rows:,} ({summary['rows_with_ambiguous_coordinates_percentage']:.2f}%) | "
          f"Bayes Ceiling Acc: {bayes_ceiling_acc*100:.2f}%")
    return g, summary


def main():
    print("=" * 80)
    print("ARGUS P2: Experiment B — Coordinate Label Ambiguity & Memorization Ceiling")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # 1. Load partitions
    print("\n[Step 1/4] Loading NF-ToN partitions...")
    df_adapt = pd.read_csv(DATA_DIR / "nfton_train_adaptation.csv", usecols=FEATURES + [TARGET])
    df_cal = pd.read_csv(DATA_DIR / "nfton_train_calibration.csv", usecols=FEATURES + [TARGET])
    df_test = pd.read_csv(DATA_DIR / "nfton_test_features.csv", usecols=FEATURES + [TARGET])
    df_all = pd.concat([df_adapt, df_cal, df_test], ignore_index=True)

    # 2. Analyze ambiguity in each partition
    print("\n[Step 2/4] Analyzing coordinate ambiguity across partitions...")
    g_adapt, sum_adapt = analyze_partition_ambiguity(df_adapt, "training_adaptation")
    g_cal, sum_cal = analyze_partition_ambiguity(df_cal, "training_calibration")
    g_test, sum_test = analyze_partition_ambiguity(df_test, "frozen_test")
    g_all, sum_all = analyze_partition_ambiguity(df_all, "combined_all_nfton")

    # 3. Analyze cross-domain shift: D1 (CIC-IoT-2023) vs D2 (NF-ToN)
    print("\n[Step 3/4] Analyzing cross-domain coordinate overlap and conditional shift P(Y|X)...")
    df_d1 = pd.read_csv(DATA_DIR / "ciciot_train_features.csv", usecols=FEATURES + [TARGET])
    g_d1 = df_d1.groupby(FEATURES)[TARGET].agg(["count", "sum"]).reset_index()
    g_d1.rename(columns={"count": "n_d1", "sum": "att_d1"}, inplace=True)
    g_d1["p_att_d1"] = g_d1["att_d1"] / g_d1["n_d1"]

    merged = pd.merge(g_d1, g_adapt, on=FEATURES, how="inner")
    merged.rename(columns={"n_samples": "n_d2", "n_attack": "att_d2"}, inplace=True)
    merged["p_att_d2"] = merged["att_d2"] / merged["n_d2"]
    merged["delta_p"] = (merged["p_att_d1"] - merged["p_att_d2"]).abs()

    n_shared_coords = len(merged)
    d1_shared_rows = int(merged["n_d1"].sum())
    d2_shared_rows = int(merged["n_d2"].sum())
    mean_delta_p = float(merged["delta_p"].mean())
    median_delta_p = float(merged["delta_p"].median())

    # Inverted coordinates: class majority in D1 != class majority in D2
    merged["maj_d1"] = (merged["p_att_d1"] >= 0.5).astype(int)
    merged["maj_d2"] = (merged["p_att_d2"] >= 0.5).astype(int)
    inverted_coords = int((merged["maj_d1"] != merged["maj_d2"]).sum())

    cross_domain_summary = {
        "d1_total_rows": len(df_d1),
        "d1_unique_coordinates": len(g_d1),
        "d2_total_rows": len(df_adapt),
        "d2_unique_coordinates": len(g_adapt),
        "shared_coordinates_count": n_shared_coords,
        "shared_coordinates_fraction_of_d1": float(n_shared_coords / len(g_d1)),
        "shared_coordinates_fraction_of_d2": float(n_shared_coords / len(g_adapt)),
        "d1_rows_in_shared_coordinates": d1_shared_rows,
        "d1_rows_in_shared_coordinates_pct": float(d1_shared_rows / len(df_d1) * 100),
        "d2_rows_in_shared_coordinates": d2_shared_rows,
        "d2_rows_in_shared_coordinates_pct": float(d2_shared_rows / len(df_adapt) * 100),
        "mean_absolute_conditional_shift_delta_p": mean_delta_p,
        "median_absolute_conditional_shift_delta_p": median_delta_p,
        "inverted_label_coordinates_count": inverted_coords,
        "inverted_label_coordinates_fraction": float(inverted_coords / n_shared_coords) if n_shared_coords > 0 else 0.0,
    }

    print(f"  D1 Coords: {len(g_d1):,} | D2 Coords: {len(g_adapt):,} | Shared Coords: {n_shared_coords:,}")
    print(f"  D1 Rows Covered: {d1_shared_rows:,} ({cross_domain_summary['d1_rows_in_shared_coordinates_pct']:.2f}%) | "
          f"D2 Rows Covered: {d2_shared_rows:,} ({cross_domain_summary['d2_rows_in_shared_coordinates_pct']:.2f}%)")
    print(f"  Mean |P_D1(Y=1|X) - P_D2(Y=1|X)|: {mean_delta_p:.4f} | Median: {median_delta_p:.4f}")
    print(f"  Inverted Class Coordinates: {inverted_coords} / {n_shared_coords} ({cross_domain_summary['inverted_label_coordinates_fraction']*100:.1f}%)")

    # 4. Save artifacts
    print("\n[Step 4/4] Saving output CSV and JSON...")
    # Add partition column to test and combined groups for detailed CSV
    g_all_sorted = g_all.sort_values(by="n_samples", ascending=False).reset_index(drop=True)
    csv_path = OUTPUT_DIR / "coordinate_label_ambiguity.csv"
    g_all_sorted.to_csv(csv_path, index=False)
    print(f"  Saved full coordinate ambiguity table ({len(g_all_sorted):,} coordinates) to: {csv_path}")

    # Save summary JSON
    bayes_summary = {
        "experiment": "ARGUS P2 Experiment B: Coordinate Label Ambiguity and Memorization Ceiling",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "partitions": {
            "training_adaptation": sum_adapt,
            "training_calibration": sum_cal,
            "frozen_test": sum_test,
            "combined_all_nfton": sum_all,
        },
        "cross_domain_shift": cross_domain_summary,
        "top_10_frequent_coordinates": g_all_sorted.head(10)[FEATURES + ["n_samples", "n_attack", "n_benign", "minority_proportion", "shannon_entropy"]].to_dict(orient="records"),
        "top_10_shared_cross_domain_coordinates": merged.sort_values(by="n_d2", ascending=False).head(10)[FEATURES + ["n_d1", "p_att_d1", "n_d2", "p_att_d2", "delta_p"]].to_dict(orient="records"),
    }

    json_path = OUTPUT_DIR / "bayes_ceiling_summary.json"
    with open(json_path, "w") as f:
        json.dump(bayes_summary, f, indent=2)
    print(f"  Saved Bayes ceiling summary to: {json_path}")
    print(f"\nExperiment B completed in {time.time()-t_start:.1f}s.")


if __name__ == "__main__":
    main()
