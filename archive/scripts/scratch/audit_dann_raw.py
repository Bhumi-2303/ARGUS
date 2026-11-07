import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, confusion_matrix, matthews_corrcoef, recall_score, precision_score, accuracy_score

df = pd.read_csv("experiments/execution/neural_robustness/domain_adaptation/DA02_DANN/predictions/DA02_D1_D3_seed42_predictions.csv")

y_true = df["true_label"].values
y_prob = df["predicted_probability"].values
y_pred_def = df["predicted_class_default"].values
y_pred_cal = df["predicted_class_calibrated"].values

roc_auc = roc_auc_score(y_true, y_prob)

tn_def, fp_def, fn_def, tp_def = confusion_matrix(y_true, y_pred_def).ravel()
spec_def = tn_def / (tn_def + fp_def) if (tn_def + fp_def) > 0 else 0.0
rec_def = tp_def / (tp_def + fn_def) if (tp_def + fn_def) > 0 else 0.0
mcc_def = matthews_corrcoef(y_true, y_pred_def)

tn_cal, fp_cal, fn_cal, tp_cal = confusion_matrix(y_true, y_pred_cal).ravel()
spec_cal = tn_cal / (tn_cal + fp_cal) if (tn_cal + fp_cal) > 0 else 0.0
rec_cal = tp_cal / (tp_cal + fn_cal) if (tp_cal + fn_cal) > 0 else 0.0
mcc_cal = matthews_corrcoef(y_true, y_pred_cal)

print("=== RAW DANN PER-SAMPLE PREDICTIONS AUDIT ===")
print(f"Total Samples: {len(df)}")
print(f"ROC-AUC (from raw probabilities): {roc_auc:.6f}")
print("\nDEFAULT THRESHOLD (0.50):")
print(f"  Confusion Matrix: TN={tn_def}, FP={fp_def}, FN={fn_def}, TP={tp_def}")
print(f"  Specificity (1-FPR): {spec_def:.6f} (FPR={fp_def/(tn_def+fp_def):.6f})")
print(f"  Recall (TPR):        {rec_def:.6f}")
print(f"  MCC:                 {mcc_def:.6f}")

print("\nCALIBRATED THRESHOLD:")
print(f"  Confusion Matrix: TN={tn_cal}, FP={fp_cal}, FN={fn_cal}, TP={tp_cal}")
print(f"  Specificity (1-FPR): {spec_cal:.6f} (FPR={fp_cal/(tn_cal+fp_cal):.6f})")
print(f"  Recall (TPR):        {rec_cal:.6f}")
print(f"  MCC:                 {mcc_cal:.6f}")
