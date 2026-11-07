#!/bin/bash
set -e

# Task 1: List contents of zips
ZIPS=("ARGUS_Cross_Domain_Results.zip" "ARGUS_DA01_CORAL_DELIVERABLES.zip" "ARGUS_DA02_DANN_DELIVERABLES.zip" "ARGUS_NR04_NATIVE_DELIVERABLES.zip" "ARGUS_REP01_DELIVERABLES.zip" "ARGUS_XGBoost_Baseline_v1.zip")
for z in "${ZIPS[@]}"; do
    path="/home/bhumi/Downloads/$z"
    if [ -f "$path" ]; then
        echo "=== Contents of $z ==="
        timeout 300 unzip -l "$path" | grep -iE "(features\.csv|pred|proba|shap|checkpoint|coral|\.py$|\.ipynb$|\.md$)" || true
    fi
done

echo "=== Extracted ARGUS_Cross_Domain_Results Folder ==="
timeout 300 find /home/bhumi/Downloads/ARGUS_Cross_Domain_Results -type f -exec ls -lh {} + 

# Task 2: Analyze feature CSVs if they exist in the extracted folder
echo "=== Feature CSV Analysis ==="
for f in /home/bhumi/Downloads/ARGUS_Cross_Domain_Results/argus_coral_data/*.csv; do
    if [ -f "$f" ]; then
        echo "File: $f"
        ls -lh "$f"
        wc -l "$f"
        sha256sum "$f"
        echo "Header and First 3 rows:"
        head -n 4 "$f"
        echo ""
    fi
done

# Task 3: Search inside zips and extracted folder for feature-derivation code
echo "=== Searching for pkt_mean_to_max inside extracted folder ==="
timeout 300 grep -rn pkt_mean_to_max /home/bhumi/Downloads/ARGUS_Cross_Domain_Results || echo "Not found in extracted folder"

echo "=== Searching for pkt_mean_to_max inside ZIP files ==="
for z in "${ZIPS[@]}"; do
    path="/home/bhumi/Downloads/$z"
    if [ -f "$path" ]; then
        echo "Searching $z..."
        # Extract files ending in .py, .ipynb, .md to stdout and grep
        timeout 300 unzip -p "$path" "*.py" "*.ipynb" "*.md" 2>/dev/null | grep -an "pkt_mean_to_max" || true
    fi
done

# Task 4: CICIoT2023 Header
echo "=== CICIoT2023 Header ==="
timeout 300 head -n 1 data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/Merged01.csv 2>/dev/null || echo "File not found"

echo "=== Searching for CICIoT2023 documentation ==="
timeout 300 grep -rnwE "(Tot sum|Tot size)" docs/ reports/ data/ 2>/dev/null || true

