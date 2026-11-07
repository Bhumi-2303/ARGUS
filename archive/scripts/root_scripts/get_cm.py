import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import confusion_matrix, matthews_corrcoef
import json

df_test = pd.read_csv("/home/bhumi/Downloads/ARGUS_Cross_Domain_Results/argus_coral_data/nfton_test_features.csv")
X_test = df_test[['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']].values
y_test = df_test['label'].values

model_source = xgb.XGBClassifier()
model_source.load_model("artifacts/models/xgb_source.json")
p_src = model_source.predict_proba(X_test)[:, 1]

th1 = 0.70
pred1 = (p_src >= th1).astype(int)
cm1 = confusion_matrix(y_test, pred1)
mcc1 = matthews_corrcoef(y_test, pred1)

th2 = 0.98
pred2 = (p_src >= th2).astype(int)
cm2 = confusion_matrix(y_test, pred2)
mcc2 = matthews_corrcoef(y_test, pred2)

print(f"th=0.70 (New Source-Only Threshold):")
print(f"MCC: {mcc1:.4f}")
print("Confusion Matrix:")
print(f"TN: {cm1[0][0]}, FP: {cm1[0][1]}")
print(f"FN: {cm1[1][0]}, TP: {cm1[1][1]}")
print()
print(f"th=0.98 (Old Target-Leaked Threshold):")
print(f"MCC: {mcc2:.4f}")
print("Confusion Matrix:")
print(f"TN: {cm2[0][0]}, FP: {cm2[0][1]}")
print(f"FN: {cm2[1][0]}, TP: {cm2[1][1]}")
