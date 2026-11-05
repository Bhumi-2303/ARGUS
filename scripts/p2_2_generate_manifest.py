#!/usr/bin/env python3
"""
Generate Reproducibility Manifest for ARGUS P2.2.
Computes SHA-256 hashes, sizes, line counts, and metadata for all P2.2 artifacts and scripts.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone

BASE_DIR = "/home/bhumi/GitHub/ARGUS"

SCRIPTS = [
    "scripts/p2_2_multisplit_evaluation.py",
    "scripts/p2_2_statistical_audit.py",
    "scripts/p2_2_d1_d2_shift_robustness.py"
]

ARTIFACTS = {
    "P2_2_INDEPENDENT_SPLIT_METRICS.csv": {
        "path": "results/experiments/p2_2_robustness/P2_2_INDEPENDENT_SPLIT_METRICS.csv",
        "type": "CSV",
        "description": "Full performance metrics for XGBoost and LightGBM across 5 independently seeded coordinate-disjoint partitions, evaluated at default 0.50 threshold and calibration-selected threshold.",
        "reproduction_command": ".venv/bin/python3 scripts/p2_2_multisplit_evaluation.py"
    },
    "P2_2_THRESHOLD_TRANSFER_ANALYSIS.csv": {
        "path": "results/experiments/p2_2_robustness/P2_2_THRESHOLD_TRANSFER_ANALYSIS.csv",
        "type": "CSV",
        "description": "Decision threshold transfer evaluation comparing calibration-selected optimal threshold against default 0.50 threshold on novel coordinate test sets, documenting threshold drift.",
        "reproduction_command": ".venv/bin/python3 scripts/p2_2_multisplit_evaluation.py"
    },
    "P2_2_CLUSTER_BOOTSTRAP_RESULTS.json": {
        "path": "results/experiments/p2_2_robustness/P2_2_CLUSTER_BOOTSTRAP_RESULTS.json",
        "type": "JSON",
        "description": "Cluster-bootstrap statistical audit results for LightGBM, XGBoost, and Clean Class-Aware CORAL on benchmark coordinate-disjoint test partition, including 95% cluster-robust CIs and degenerate resample audit.",
        "reproduction_command": ".venv/bin/python3 scripts/p2_2_statistical_audit.py"
    },
    "P2_2_PAIRED_MODEL_COMPARISONS.json": {
        "path": "results/experiments/p2_2_robustness/P2_2_PAIRED_MODEL_COMPARISONS.json",
        "type": "JSON",
        "description": "Paired cluster-bootstrap difference in MCC between LightGBM and XGBoost, McNemar's test, paired group t-test, and Wilcoxon signed-rank test.",
        "reproduction_command": ".venv/bin/python3 scripts/p2_2_statistical_audit.py"
    },
    "P2_2_D1_D2_SHIFT_ROBUSTNESS.csv": {
        "path": "results/experiments/p2_2_robustness/P2_2_D1_D2_SHIFT_ROBUSTNESS.csv",
        "type": "CSV",
        "description": "Detailed statistical reassessment of all 27 shared coordinates between D1 and D2, flow independence analysis, Wilson score CIs, z-tests, Fisher's exact tests, and traffic archetype classifications.",
        "reproduction_command": ".venv/bin/python3 scripts/p2_2_d1_d2_shift_robustness.py"
    },
    "P2_2_CORRECTED_SCIENTIFIC_CLAIMS.md": {
        "path": "audit/research/P2_2_CORRECTED_SCIENTIFIC_CLAIMS.md",
        "type": "Markdown",
        "description": "Formal publication audit classifying claims into Supported, Partially Supported, and Unsupported with mandatory replacement texts.",
        "reproduction_command": "Manual scientific synthesis and peer audit."
    },
    "P2_2_FINAL_STATISTICAL_ROBUSTNESS_REPORT.md": {
        "path": "audit/research/P2_2_FINAL_STATISTICAL_ROBUSTNESS_REPORT.md",
        "type": "Markdown",
        "description": "Comprehensive independent research audit report and verdict for ARGUS P2.2 covering statistical robustness and publication readiness.",
        "reproduction_command": "Manual scientific synthesis and peer audit."
    }
}

def get_file_info(rel_path):
    full_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Missing required file: {full_path}")
    
    with open(full_path, "rb") as f:
        content = f.read()
    
    sha256 = hashlib.sha256(content).hexdigest()
    size_bytes = len(content)
    lines = content.count(b"\n")
    return {
        "sha256": sha256,
        "size_bytes": size_bytes,
        "lines": lines
    }

def main():
    manifest = {
        "manifest_version": "1.0.0",
        "audit_phase": "ARGUS P2.2 — Final Statistical Robustness and Publication Readiness Audit",
        "auditor": "Independent ML Research Auditor",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "base_directory": BASE_DIR,
        "execution_environment": {
            "python_executable": ".venv/bin/python3",
            "python_version": sys.version.split()[0],
            "os": "Linux x86_64"
        },
        "scripts": {},
        "artifacts": {}
    }
    
    for script in SCRIPTS:
        info = get_file_info(script)
        manifest["scripts"][script] = info
        print(f"Hashed script: {script} -> {info['sha256'][:16]}... ({info['lines']} lines)")
        
    for name, art_meta in ARTIFACTS.items():
        info = get_file_info(art_meta["path"])
        entry = {
            "path": art_meta["path"],
            "type": art_meta["type"],
            "sha256": info["sha256"],
            "size_bytes": info["size_bytes"],
            "lines": info["lines"],
            "description": art_meta["description"],
            "reproduction_command": art_meta["reproduction_command"]
        }
        manifest["artifacts"][name] = entry
        print(f"Hashed artifact: {name} -> {info['sha256'][:16]}... ({info['size_bytes']} bytes)")
        
    out_path = os.path.join(BASE_DIR, "results/experiments/p2_2_robustness/P2_2_REPRODUCIBILITY_MANIFEST.json")
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
        
    print(f"\nManifest successfully written to: {out_path}")

if __name__ == "__main__":
    main()
