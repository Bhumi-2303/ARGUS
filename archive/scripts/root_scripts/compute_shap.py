import pandas as pd
import xgboost as xgb
import shap
import os

base_path = 'ARGUS_Cross_Domain_Results/argus_coral_data'
features = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']

print("Loading data...")
d1_train = pd.read_csv(f'{base_path}/ciciot_train_features.csv')
d1_train_clean_ca = pd.read_csv(f'{base_path}/ciciot_train_clean_class_aware_coral.csv')
d2_test = pd.read_csv(f'{base_path}/nfton_test_features.csv')

# Before Adaptation
print("Training Before-adaptation model...")
clf_before = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
clf_before.fit(d1_train[features], d1_train['label'])

print("Computing SHAP values (Before adaptation)...")
explainer_before = shap.TreeExplainer(clf_before)
shap_values_before = explainer_before.shap_values(d2_test[features])
df_before = pd.DataFrame(shap_values_before, columns=features)
df_before.to_csv(f'{base_path}/predictions_raw/shap_values_before_adaptation.csv', index=False)

# After Adaptation
print("Training After-adaptation model (Clean Class-aware CORAL)...")
clf_after = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
clf_after.fit(d1_train_clean_ca[features], d1_train_clean_ca['label'])

print("Computing SHAP values (After adaptation)...")
explainer_after = shap.TreeExplainer(clf_after)
shap_values_after = explainer_after.shap_values(d2_test[features])
df_after = pd.DataFrame(shap_values_after, columns=features)
df_after.to_csv(f'{base_path}/predictions_raw/shap_values_after_adaptation.csv', index=False)

print("Done.")
