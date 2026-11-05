#!/usr/bin/env python3
"""
Generates results/experiments/p2_1_validation/P2_1_REPRODUCIBILITY_MANIFEST.json
with cryptographic SHA-256 hashes, exact byte sizes, line/row counts, and execution commands.
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path("/home/bhumi/GitHub/ARGUS")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def count_lines(path: Path) -> int:
    with open(path, "rb") as f:
        return sum(1 for _ in f)


def main():
    print("Generating P2.1 Reproducibility Manifest...")

    artifacts = [
        {
            "name": "P2_1_SAME_TEST_CROSS_DOMAIN_COMPARISON.csv",
            "path": "results/experiments/p2_1_validation/P2_1_SAME_TEST_CROSS_DOMAIN_COMPARISON.csv",
            "type": "CSV",
            "description": "Cross-domain and in-domain models evaluated on the identical 1,970,428 coordinate-disjoint test partition.",
            "reproduction_command": "python3 scripts/p2_1_same_test_comparison.py",
        },
        {
            "name": "P2_1_CORAL_MCC_RECONCILIATION.json",
            "path": "results/experiments/p2_1_validation/P2_1_CORAL_MCC_RECONCILIATION.json",
            "type": "JSON",
            "description": "Root-cause reconciliation of the MCC 0.3855 vs 0.3904 discrepancy with authoritative baseline identified.",
            "reproduction_command": "python3 scripts/p2_1_coral_mcc_reconciliation.py",
        },
        {
            "name": "P2_1_COORDINATE_LOOKUP_VALIDATION.csv",
            "path": "results/experiments/p2_1_validation/P2_1_COORDINATE_LOOKUP_VALIDATION.csv",
            "type": "CSV",
            "description": "Validation separating in-sample purity (94.61%), train-derived lookup, and novel coordinate performance.",
            "reproduction_command": "python3 scripts/p2_1_coordinate_lookup_validation.py",
        },
        {
            "name": "P2_1_STATISTICAL_VALIDATION.json",
            "path": "results/experiments/p2_1_validation/P2_1_STATISTICAL_VALIDATION.json",
            "type": "JSON",
            "description": "Cluster-robust coordinate-group bootstrap CIs, proof of XGBoost seed invariance, and paired group tests.",
            "reproduction_command": "python3 scripts/p2_1_statistical_validation.py",
        },
        {
            "name": "P2_1_D1_D2_SHIFT_ANALYSIS.csv",
            "path": "results/experiments/p2_1_validation/P2_1_D1_D2_SHIFT_ANALYSIS.csv",
            "type": "CSV",
            "description": "Audit of all 27 shared coordinates between CIC-IoT-2023 and NF-ToN-IoT-v2 with Wilson CIs and z-tests.",
            "reproduction_command": "python3 scripts/p2_1_d1_d2_shift_analysis.py",
        },
        {
            "name": "P2_1_D1_D2_SHIFT_SUMMARY.json",
            "path": "results/experiments/p2_1_validation/P2_1_D1_D2_SHIFT_SUMMARY.json",
            "type": "JSON",
            "description": "Summary metadata and rounding tolerance sensitivity for D1-D2 overlap.",
            "reproduction_command": "python3 scripts/p2_1_d1_d2_shift_analysis.py",
        },
        {
            "name": "P2_1_CORRECTED_SCIENTIFIC_CLAIMS.md",
            "path": "audit/research/P2_1_CORRECTED_SCIENTIFIC_CLAIMS.md",
            "type": "Markdown",
            "description": "Critical reassessment and correction of 5 previous scientific claims with defensible replacement text.",
            "reproduction_command": "Manual scientific synthesis and review.",
        },
        {
            "name": "P2_1_FINAL_VALIDATION_REPORT.md",
            "path": "audit/research/P2_1_FINAL_VALIDATION_REPORT.md",
            "type": "Markdown",
            "description": "Final independent research auditor report and verdict for ARGUS P2.1.",
            "reproduction_command": "Manual scientific synthesis and review.",
        },
    ]

    scripts = [
        "scripts/p2_1_same_test_comparison.py",
        "scripts/p2_1_coral_mcc_reconciliation.py",
        "scripts/p2_1_coordinate_lookup_validation.py",
        "scripts/p2_1_statistical_validation.py",
        "scripts/p2_1_d1_d2_shift_analysis.py",
    ]

    manifest = {
        "manifest_version": "1.0.0",
        "audit_phase": "ARGUS P2.1 — Final Scientific Validation and Cross-Domain Benchmark Correction",
        "auditor": "Independent ML Research Auditor",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_directory": str(BASE_DIR),
        "execution_environment": {
            "python_version": sys.version.split()[0],
            "os": "Linux x86_64",
        },
        "scripts": {},
        "artifacts": {},
    }

    for s in scripts:
        p = BASE_DIR / s
        if p.exists():
            manifest["scripts"][s] = {
                "sha256": sha256(p),
                "size_bytes": os.path.getsize(p),
                "lines": count_lines(p),
            }

    for a in artifacts:
        p = BASE_DIR / a["path"]
        if p.exists():
            manifest["artifacts"][a["name"]] = {
                "path": a["path"],
                "type": a["type"],
                "sha256": sha256(p),
                "size_bytes": os.path.getsize(p),
                "lines": count_lines(p),
                "description": a["description"],
                "reproduction_command": a["reproduction_command"],
            }

    out_path = BASE_DIR / "results/experiments/p2_1_validation/P2_1_REPRODUCIBILITY_MANIFEST.json"
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Saved manifest to {out_path}")


if __name__ == "__main__":
    main()
