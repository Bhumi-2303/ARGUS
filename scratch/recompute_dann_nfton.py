import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, confusion_matrix, matthews_corrcoef, recall_score, precision_score, accuracy_score, f1_score

csv_path = "ARGUS_Cross_Domain_Results/argus_coral_data/dann_results/dann_final_test_predictions.csv"
print(f"Reading raw DANN prediction CSV from {csv_path}...")
df = pd.read_csv(csv_path)

print(f"Columns: {list(df.columns)}")
print(f"Sample count N = {len(df)}")

y_true = df["label"].values
y_prob = df["probability"].values
y_pred = df["prediction"].values

roc_auc = roc_auc_score(y_true, y_prob)
acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, zero_division=0)
rec = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)
mcc = matthews_corrcoef(y_true, y_pred)

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
fpr = fp / (tn + fp) if (tn + fp) > 0 else 0.0
fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

print("\n" + "=" * 80)
print("     RAW PER-SAMPLE DANN (NF-ToN-IoT-v2 Test Set N=2,627,177) COMPUTED METRICS")
print("=" * 80)
print(f"Accuracy:                  {acc:.16f}")
print(f"Precision:                 {prec:.16f}")
print(f"Recall:                    {rec:.16f}")
print(f"F1 Score:                  {f1:.16f}")
print(f"MCC:                       {mcc:.16f}")
print(f"ROC-AUC (from raw prob):   {roc_auc:.16f}")
print(f"Confusion Matrix:          TN={tn}, FP={fp}, FN={fn}, TP={tp}")
print(f"Specificity (1-FPR):       {spec:.16f}")
print(f"False Positive Rate (FPR): {fpr:.16f}")
print(f"False Negative Rate (FNR): {fnr:.16f}")
print("=" * 80 + "\n")
