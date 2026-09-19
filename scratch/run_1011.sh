#!/bin/bash
set -e
seed=1011
echo "Cleaning old artifacts to force retraining..."
rm -rf phase3_results/experiments/*
rm -rf phase3_results/models/*.txt
rm -rf phase3_results/checkpoints/*.pt
rm -rf phase4_results/experiments/*

echo "Starting Phase 3 (Training)..."
.venv/bin/python3 training/scripts/phase3_execute_all_fast.py $seed

echo "Starting Phase 4 (Fusion)..."
.venv/bin/python3 experiments/ablations/phase4_execute_fast.py $seed

echo "Saving outputs for seed $seed..."
mkdir -p "artifacts/models/phase4/seed_${seed}/"
cp phase3_results/models/*.txt "artifacts/models/phase4/seed_${seed}/"
mkdir -p "artifacts/predictions/phase4/seed_${seed}/"
cp phase4_results/experiments/E5_fusion_CORAL_prior/predictions.csv "artifacts/predictions/phase4/seed_${seed}/"
cp phase4_results/metrics/final_comparison.csv "artifacts/metrics/phase4_multiseed/final_comparison_seed_${seed}.csv"
echo "All done"
