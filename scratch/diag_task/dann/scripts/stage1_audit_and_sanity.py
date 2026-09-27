#!/usr/bin/env python3
"""
ARGUS Project DA-02: Step 1 & Step 4 — Audit & Architecture Sanity Verification Script.
Audits historical baseline artifacts, verifies dataset partitions, tests GRL gradient reversal,
and initializes DA02_manifest.json and experiment_state.json.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

BASE = Path("/Volumes/BLACK-BOX/ARGUS")
EE = BASE / "experiment_execution"
NR = EE / "neural_robustness"
DA01 = NR / "domain_adaptation"
DA02 = DA01 / "DA02_DANN"
CORAL_DATA_DIR = BASE / "ARGUS_Cross_Domain_Results/argus_coral_data"

sys.path.append(str(DA02 / "scripts"))
from dann_model import DANNNetwork, GradReverse

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def run_audit_and_sanity():
    print("=========================================================================")
    print("ARGUS DA-02: STEP 1 & STEP 4 — AUDIT & ARCHITECTURE SANITY TEST")
    print("=========================================================================")

    # 1. Check Historical Baselines (FROZEN & READ-ONLY)
    print("\n[1] Verifying Historical Baselines (Frozen & Read-Only)...")
    
    # Baseline 1: FTT-SMALL
    ftt_ckpt = NR / "checkpoints/FTT_ARGUS4_D1_D3_seed42/best_model.pt"
    assert ftt_ckpt.exists(), f"Missing FTT-SMALL baseline checkpoint: {ftt_ckpt}"
    ftt_pred = NR / "predictions/NR01/D1_D3_seed42_predictions.csv"
    assert ftt_pred.exists(), f"Missing FTT-SMALL baseline predictions: {ftt_pred}"
    print(f"  [+] FTT-SMALL Baseline (B0) Checkpoint & Predictions: VERIFIED ({compute_sha256(ftt_ckpt)[:12]}...)")

    # Baseline 2: DA-01 CORAL
    coral_ckpt = DA01 / "checkpoints/DA01_FTT_CORAL_seed42/best_model.pt"
    assert coral_ckpt.exists(), f"Missing DA-01 CORAL checkpoint: {coral_ckpt}"
    coral_pred = DA01 / "predictions/DA01_seed42.csv"
    assert coral_pred.exists(), f"Missing DA-01 CORAL predictions: {coral_pred}"
    coral_comp = DA01 / "tables/DA01_FTT_BASELINE_vs_CORAL.csv"
    assert coral_comp.exists(), f"Missing DA-01 comparison table: {coral_comp}"
    print(f"  [+] DA-01 CORAL Baseline (B1) Checkpoint & Predictions: VERIFIED ({compute_sha256(coral_ckpt)[:12]}...)")

    # 2. Check Dataset Partitions
    print("\n[2] Verifying Dataset Partitions...")
    datasets = {
        "D1 Source Training (CICIoT2023)": (CORAL_DATA_DIR / "ciciot_train_features.csv", 5491971),
        "D3 Target Unlabeled Adaptation": (CORAL_DATA_DIR / "iec104_train_adaptation.csv", 2286249),
        "D3 Target Calibration Split": (CORAL_DATA_DIR / "iec104_train_calibration.csv", 571563),
        "D3 Target Frozen Test Partition": (CORAL_DATA_DIR / "iec104_test_features.csv", 714453)
    }

    expected_cols = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max', 'label']

    for name, (fpath, expected_n) in datasets.items():
        assert fpath.exists(), f"Missing dataset file: {fpath}"
        head = pd.read_csv(fpath, nrows=5)
        assert list(head.columns) == expected_cols, f"Column mismatch in {fpath}"
        with open(fpath, "r") as f:
            actual_n = sum(1 for _ in f) - 1
        assert actual_n == expected_n, f"Row count mismatch in {fpath}: {actual_n} != {expected_n}"
        print(f"  [+] {name}: {fpath.name} -> {actual_n:,} rows, Columns: {list(head.columns)}")

    # 3. Test DANN Architecture & Gradient Reversal
    print("\n[3] Testing DANN Architecture & Gradient Reversal Functionality...")
    model = DANNNetwork(input_dim=4, hidden_dim=64, latent_dim=32, dropout=0.10)
    p_info = model.count_parameters()
    print(f"  [+] Model Parameters Total: {p_info['total_parameters']:,}")
    print(f"      - Feature Encoder:     {p_info['feature_encoder_parameters']:,}")
    print(f"      - Attack Classifier:   {p_info['attack_classifier_parameters']:,}")
    print(f"      - Domain Classifier:   {p_info['domain_classifier_parameters']:,}")

    # Forward & Backward Sanity Test
    x = torch.randn(16, 4, requires_grad=True)
    y_att = torch.randint(0, 2, (16,)).float()
    y_dom = torch.randint(0, 2, (16,)).float()

    criterion_att = nn.BCEWithLogitsLoss()
    criterion_dom = nn.BCEWithLogitsLoss()

    # Forward pass with alpha=0.5
    att_logits, dom_logits, feats = model(x, alpha=0.5)
    loss_att = criterion_att(att_logits, y_att)
    loss_dom = criterion_dom(dom_logits, y_dom)
    total_loss = loss_att + 0.5 * loss_dom

    total_loss.backward()

    # Check that gradients exist for all submodules
    enc_has_grad = any(p.grad is not None and torch.norm(p.grad) > 0 for p in model.feature_encoder.parameters())
    att_has_grad = any(p.grad is not None and torch.norm(p.grad) > 0 for p in model.attack_classifier.parameters())
    dom_has_grad = any(p.grad is not None and torch.norm(p.grad) > 0 for p in model.domain_classifier.parameters())

    assert enc_has_grad and att_has_grad and dom_has_grad, "Gradient propagation failure!"
    print("  [+] Gradient Propagation Sanity Test: PASSED (All submodules received non-zero gradients)")

    # Test Gradient Reversal Sign Flip Explicitly
    x_test = torch.tensor([[1.0, 2.0]], requires_grad=True)
    rev_x = GradReverse.apply(x_test, 1.0)
    loss_test = (rev_x * 2.0).sum()
    loss_test.backward()
    # If loss = 2 * rev_x, grad w.r.t rev_x is +2.0, so grad w.r.t x_test MUST be -2.0
    assert torch.allclose(x_test.grad, torch.tensor([[-2.0, -2.0]])), f"GRL sign flip failed: {x_test.grad}"
    print(f"  [+] GRL Sign-Reversal Unit Test: PASSED (Expected [-2.0, -2.0], Got {x_test.grad.tolist()})")

    # 4. Initialize DA02 Manifest & Experiment State
    manifest = {
        "experiment_id": "DA-02",
        "experiment_name": "DANN Domain Adaptation Controlled Pilot Test",
        "timestamp_initialized": datetime.now().isoformat(),
        "hardware_platform": "Apple Silicon M4 (16 GB Unified Memory)",
        "device": "mps" if torch.backends.mps.is_available() else "cpu",
        "random_seed": 42,
        "pilot_lambda_values": [0.00, 0.10, 0.25, 0.50, 1.00],
        "batch_size": 128,
        "model_architecture": {
            "name": "DANNNetwork",
            "input_dimension": 4,
            "hidden_dimension": 64,
            "latent_dimension": 32,
            "dropout": 0.10,
            "parameter_count": p_info["total_parameters"]
        },
        "datasets": {
            "source_domain": "D1 (CICIoT2023, N=5,491,971)",
            "target_adaptation": "D3 (IEC 60870-5-104 Unlabeled, N=2,286,249)",
            "target_calibration": "D3 (IEC 60870-5-104 Labeled Calib, N=571,563)",
            "target_frozen_test": "D3 (IEC 60870-5-104 Frozen Test, N=714,453)"
        },
        "leakage_safeguards": {
            "frozen_test_isolated": True,
            "target_labels_in_adaptation": False,
            "model_selection_partition": "D3 Target Calibration Split Only"
        },
        "status": "INITIALIZED_READY_FOR_LAMBDA_SWEEP"
    }

    with open(DA02 / "DA02_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n[OK] Created DA02_manifest.json")

    state = {
        "current_stage": "STAGE_DA02_AUDIT_SANITY_PASSED",
        "current_experiment": "DA02-PILOT DANN Lambda Sweep (Seed 42)",
        "current_seed": 42,
        "current_lambda": None,
        "completed_lambdas": [],
        "best_lambda": None,
        "checkpoint_path": None,
        "last_successful_artifact": "DA02_manifest.json",
        "status": "READY_FOR_LAMBDA_SWEEP",
        "error": None,
        "timestamp": datetime.now().isoformat()
    }
    with open(DA02 / "experiment_state.json", "w") as f:
        json.dump(state, f, indent=2)
    print(f"[OK] Initialized DA02 experiment_state.json")
    print("\n=========================================================================")
    print("STEP 1 & STEP 4 COMPLETE. READY FOR CONTROLLED LAMBDA SWEEP PILOT.")
    print("=========================================================================")

if __name__ == "__main__":
    run_audit_and_sanity()
