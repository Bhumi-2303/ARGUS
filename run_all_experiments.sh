#!/bin/bash
set -e

echo "=========================================================="
echo "          ARGUS Multi-Dataset Training Orchestrator       "
echo "=========================================================="

echo "[*] Ensuring Python environment..."
# Assuming running within active venv or system python 3.11
PYTHON_CMD="python3.11"

echo "=========================================================="
echo "[*] Executing Phase 2: Dynamic Preprocessing"
echo "=========================================================="
$PYTHON_CMD training/scripts/phase2_execute.py --dataset nftoniotv2
# NOTE: CICIoT2023 must be present in training/data/raw/ciciot2023/
if [ -d "training/data/raw/ciciot2023" ] && [ "$(ls -A training/data/raw/ciciot2023)" ]; then
    $PYTHON_CMD training/scripts/phase2_execute.py --dataset ciciot2023
else
    echo "[!] WARNING: ciciot2023 raw data not found. Skipping Phase 2 for ciciot2023."
fi

echo "=========================================================="
echo "[*] Executing Phase 3: Model Training & Evaluation"
echo "=========================================================="
# Default to 50 trials per instructions, adjustable via CLI flag
TRIALS=${1:-50}

# Experiment 1
echo "[*] Experiment 1: NF-ToN-IoT-v2 -> NF-ToN-IoT-v2"
$PYTHON_CMD training/scripts/phase3_execute.py --train-dataset nftoniotv2 --test-dataset nftoniotv2 --trials $TRIALS

# Experiment 2, 3, 4 depend on CICIoT2023
if [ -d "training/data/processed/ciciot2023" ]; then
    echo "[*] Experiment 2: CICIoT2023 -> CICIoT2023"
    $PYTHON_CMD training/scripts/phase3_execute.py --train-dataset ciciot2023 --test-dataset ciciot2023 --trials $TRIALS

    echo "[*] Experiment 3: NF-ToN-IoT-v2 -> CICIoT2023"
    $PYTHON_CMD training/scripts/phase3_execute.py --train-dataset nftoniotv2 --test-dataset ciciot2023 --trials $TRIALS

    echo "[*] Experiment 4: CICIoT2023 -> NF-ToN-IoT-v2"
    $PYTHON_CMD training/scripts/phase3_execute.py --train-dataset ciciot2023 --test-dataset nftoniotv2 --trials $TRIALS
else
    echo "[!] WARNING: Skipping Experiments 2, 3, 4 because processed ciciot2023 data is missing."
fi

echo "=========================================================="
echo "[*] Executing Phase 4: Generalization Report"
echo "=========================================================="
$PYTHON_CMD training/scripts/phase4_report.py

echo "=========================================================="
echo "[*] Orchestration Complete!"
echo "=========================================================="
