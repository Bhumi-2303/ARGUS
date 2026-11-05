import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import confusion_matrix
import os

print("\n--- STEP 4: Probability Orientation Check ---")
data_dir = "data/raw/legacy_package/argus_coral_data"
train_path = os.path.join(data_dir, "ciciot_train_clean_class_aware_coral.csv")
calib_path = os.path.join(data_dir, "nfton_train_calibration.csv")

df_train = pd.read_csv(train_path)
X_train = df_train.drop(columns=['label']).values
y_train = df_train['label'].values

# Guessed 'binary:logistic' because target is 0/1, unlike pickle which was multiclass
# [REQUIRES VERIFICATION] objective='binary:logistic'
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method='hist',
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

print(f"Training XGBoost on {len(X_train)} rows...")
model.fit(X_train, y_train)

print(f"\nmodel.classes_ = {model.classes_}")

df_calib = pd.read_csv(calib_path)
X_calib = df_calib.drop(columns=['label']).values
y_calib = df_calib['label'].values

print("Predicting on calibration set...")
raw_proba = model.predict_proba(X_calib)
# Assuming index 1 corresponds to class 1 (Attack) [REQUIRES VERIFICATION]
val_probs = raw_proba[:, 1]
print(f"Using predict_proba column index: 1 (corresponding to class {model.classes_[1]})")

print("\nConfusion Matrices at specific thresholds:")
for th in [0.01, 0.50, 0.90, 0.99]:
    p_val = (val_probs >= th).astype(int)
    cm = confusion_matrix(y_calib, p_val, labels=[0, 1])
    print(f"Threshold {th:.2f}:\n{cm}\n")

print("Running exact threshold selection code from stage_d_e_train_evaluate.py...")
best_th = 0.50
best_f1_cal = -1.0
for th in np.linspace(0.01, 0.99, 99):
    p_val = (val_probs >= th).astype(int)
    tp = np.sum((y_calib == 1) & (p_val == 1))
    fp = np.sum((y_calib == 0) & (p_val == 1))
    fn = np.sum((y_calib == 1) & (p_val == 0))
    f1_c = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
    if f1_c > best_f1_cal:
        best_f1_cal = f1_c
        best_th = float(th)

print(f"\nSelected best threshold: {best_th:.2f} (F1 = {best_f1_cal:.4f})")
if abs(best_th - 0.99) < 1e-4:
    print("MATCH: The new threshold matches 0.99.")
else:
    print(f"MISMATCH: The new threshold {best_th:.2f} does NOT match 0.99.")
