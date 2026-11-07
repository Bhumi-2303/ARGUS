#!/bin/bash
echo "=== Searching for ARGUS_RESULTS_README.txt and ARGUS_Cross_Domain_Results* ==="
timeout 300 find ~ /mnt /media -type d -name "ARGUS_Cross_Domain_Results*" -exec ls -ldh {} + 2>/dev/null
timeout 300 find ~ /mnt /media -type f -name "ARGUS_RESULTS_README.txt" -o -name "ARGUS_Cross_Domain_Results*" -exec ls -lh {} + 2>/dev/null

echo "=== Searching for large recent ZIP files ==="
timeout 300 find ~ /mnt /media -type f -name "*.zip" -size +1M -mtime -90 -exec ls -lh {} + 2>/dev/null

echo "=== Searching for model/prediction/SHAP files ==="
timeout 300 find ~ /mnt /media -type f \( -name "*.npy" -o -name "*.npz" -o -name "*.pkl" -o -name "*.joblib" -o -name "*.pt" -o -name "*.parquet" \) 2>/dev/null | grep -iE "(argus|dann|coral|xgb|lgbm|shap|pred|proba)" | xargs -r ls -lh

echo "=== ARGUS_Paper_Data/ (maxdepth 2) ==="
timeout 300 find ARGUS_Paper_Data/ -maxdepth 2 -type f -exec ls -lh {} + 2>/dev/null || echo "ARGUS_Paper_Data/ not found or empty"

echo "=== ~/Downloads (maxdepth 2) ==="
timeout 300 find ~/Downloads -maxdepth 2 -type f -exec ls -lh {} + 2>/dev/null || echo "~/Downloads empty"
