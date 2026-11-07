#!/usr/bin/env python3
"""Script to reproduce the 79.04% and 75.72% coordinate-degeneracy and label-conflict metrics.

Audits NF-ToN-IoT-v2 adaptation, calibration, and test splits across the 4 harmonized features:
['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max'].
"""

import json
from pathlib import Path
import pandas as pd

FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
DATA_DIR = Path("data/raw/legacy_package/argus_coral_data")
OUTPUT_DIR = Path("results")

SPLITS = [
    ("NF-ToN Adaptation (Train)", DATA_DIR / "nfton_train_adaptation.csv"),
    ("NF-ToN Calibration", DATA_DIR / "nfton_train_calibration.csv"),
    ("NF-ToN Test", DATA_DIR / "nfton_test_features.csv"),
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    summary_rows = []

    for name, path in SPLITS:
        print(f"Auditing {name} from {path}...")
        df = pd.read_csv(path, usecols=FEATURES + ["label"])
        total_rows = len(df)

        grouped = df.groupby(FEATURES)["label"].nunique()
        n_unique_coords = len(grouped)
        duplicate_rows = total_rows - n_unique_coords
        duplicate_pct = (duplicate_rows / total_rows) * 100.0

        conflicting_coords = set(grouped[grouped > 1].index)
        is_conflicting = df.set_index(FEATURES).index.isin(conflicting_coords)
        conflicting_rows = int(is_conflicting.sum())
        conflicting_pct = (conflicting_rows / total_rows) * 100.0

        split_summary = {
            "total_rows": total_rows,
            "unique_coordinates": n_unique_coords,
            "duplicate_rows": duplicate_rows,
            "duplicate_row_percentage": round(duplicate_pct, 4),
            "conflicting_coordinates": len(conflicting_coords),
            "rows_on_conflicting_coordinates": conflicting_rows,
            "conflicting_row_percentage": round(conflicting_pct, 4),
        }
        results[name] = split_summary
        summary_rows.append({"split": name, **split_summary})

        print(f"  {name}: {conflicting_rows:,} rows ({conflicting_pct:.2f}%) on conflicting coordinates")

    json_path = OUTPUT_DIR / "coordinate_degeneracy_reproduction.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    csv_path = OUTPUT_DIR / "coordinate_degeneracy_reproduction.csv"
    pd.DataFrame(summary_rows).to_csv(csv_path, index=False)

    print(f"\nArtifacts saved successfully:\n  JSON: {json_path}\n  CSV:  {csv_path}")


if __name__ == "__main__":
    main()
