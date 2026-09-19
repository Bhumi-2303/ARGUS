import pandas as pd
import numpy as np
import xgboost as xgb
import os
from sklearn.metrics import roc_auc_score

os.makedirs('ARGUS_Cross_Domain_Results/argus_coral_data/predictions_raw', exist_ok=True)
base_path = 'ARGUS_Cross_Domain_Results/argus_coral_data'

print("Loading D1 and D2 Train/Test...")
d1_train = pd.read_csv(f'{base_path}/ciciot_train_features.csv')
d1_test = pd.read_csv(f'{base_path}/ciciot_test_features.csv')
d2_train = pd.read_csv(f'{base_path}/nfton_train_features.csv')
d2_test = pd.read_csv(f'{base_path}/nfton_test_features.csv')

features = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']

def save_predictions(y_true, y_prob, filename):
    df = pd.DataFrame({'sample_index': range(len(y_true)), 'true_label': y_true.values, 'predicted_probability': y_prob})
    df.to_csv(filename, index=False)
    print(f"Saved {filename}")

# Source-only D1 -> D2
print("Training Source-only XGBoost on D1...")
clf_d1 = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
clf_d1.fit(d1_train[features], d1_train['label'])

print("Predicting D1->D2...")
y_prob_d1_d2 = clf_d1.predict_proba(d2_test[features])[:, 1]
save_predictions(d2_test['label'], y_prob_d1_d2, f'{base_path}/predictions_raw/source_only_d1_to_d2.csv')

# Source-only D2 -> D1
print("Training Source-only XGBoost on D2...")
clf_d2 = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
clf_d2.fit(d2_train[features], d2_train['label'])

print("Predicting D2->D1...")
y_prob_d2_d1 = clf_d2.predict_proba(d1_test[features])[:, 1]
save_predictions(d1_test['label'], y_prob_d2_d1, f'{base_path}/predictions_raw/source_only_d2_to_d1.csv')

# Global CORAL
# (For D1->D2, we train on D1, align D2 to D1... wait, standard CORAL aligns source to target)
# In this dataset, there are pre-aligned features:
# ciciot_train_coral_aligned.csv (Source aligned to Target D2)
print("Training Global CORAL XGBoost (D1 aligned to D2)...")
d1_train_coral = pd.read_csv(f'{base_path}/ciciot_train_coral_aligned.csv')
clf_coral = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
clf_coral.fit(d1_train_coral[features], d1_train_coral['label'])
y_prob_coral = clf_coral.predict_proba(d2_test[features])[:, 1]
save_predictions(d2_test['label'], y_prob_coral, f'{base_path}/predictions_raw/global_coral_d1_to_d2.csv')

# Clean Class-aware CORAL
print("Training Clean Class-aware CORAL XGBoost (D1 aligned to D2)...")
d1_train_clean_ca = pd.read_csv(f'{base_path}/ciciot_train_clean_class_aware_coral.csv')
clf_clean_ca = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
clf_clean_ca.fit(d1_train_clean_ca[features], d1_train_clean_ca['label'])
y_prob_clean_ca = clf_clean_ca.predict_proba(d2_test[features])[:, 1]
save_predictions(d2_test['label'], y_prob_clean_ca, f'{base_path}/predictions_raw/clean_class_aware_coral_d1_to_d2.csv')

# Diagnostic Class-aware CORAL
print("Training Diagnostic Class-aware CORAL XGBoost (D1 aligned to D2)...")
d1_train_ca = pd.read_csv(f'{base_path}/ciciot_train_class_aware_coral.csv')
clf_ca = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
clf_ca.fit(d1_train_ca[features], d1_train_ca['label'])
y_prob_ca = clf_ca.predict_proba(d2_test[features])[:, 1]
save_predictions(d2_test['label'], y_prob_ca, f'{base_path}/predictions_raw/diagnostic_class_aware_coral_d1_to_d2.csv')

print("Done.")
