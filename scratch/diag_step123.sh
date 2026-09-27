#!/bin/bash
FILES="ciciot_train_features.csv|ciciot_train_coral_aligned.csv|ciciot_train_class_aware_coral.csv|ciciot_train_clean_class_aware_coral.csv|nfton_train_features.csv|nfton_train_adaptation.csv|nfton_train_calibration.csv|nfton_test_features.csv|ciciot_test_features.csv|CORAL_DATA_DIR"

echo "=== STEP 1: Live Repo Scripts ==="
MATCHES=$(grep -rlE "$FILES" src/ experiments/ training/ scripts/ ./*.py 2>/dev/null)

for f in $MATCHES; do
  echo "--- File: $f ---"
  git log -1 --format="Git Date: %ci" -- "$f"
  
  echo "XGBoost imports/instantiations:"
  grep -nE "(XGBClassifier|xgb\.train|xgboost)" "$f" || echo "None"
  
  echo "sklearn imports/instantiations:"
  grep -nE "(RandomForestClassifier|LogisticRegression|SVC|KNeighborsClassifier|DecisionTreeClassifier|sklearn)" "$f" || echo "None"
  
  echo "torch/nn.Module imports/instantiations:"
  grep -nE "(nn\.Module|torch)" "$f" || echo "None"
done

echo ""
echo "=== STEP 2: Other Deliverables ==="
mkdir -p scratch/diag_task/nr04 scratch/diag_task/rep01
unzip -qo ~/Downloads/ARGUS_NR04_NATIVE_DELIVERABLES.zip -d scratch/diag_task/nr04/
unzip -qo ~/Downloads/ARGUS_REP01_DELIVERABLES.zip -d scratch/diag_task/rep01/

echo "Grep XGB in NR04 & REP01:"
grep -rnE "(XGBClassifier|xgb\.train)" scratch/diag_task/nr04/ scratch/diag_task/rep01/ || echo "No XGB in these ZIPs"

echo "Grep CSV filenames in NR04 & REP01:"
grep -rnE "$FILES" scratch/diag_task/nr04/ scratch/diag_task/rep01/ || echo "No matching CSV filenames in these ZIPs"

echo ""
echo "=== STEP 3: Mtimes ==="
find data/raw/legacy_package/ -name "*.csv" -exec ls -la --time-style=full-iso {} + | awk '{print $6 " " $7 " " $9}' | sort

