import pandas as pd
import numpy as np

# Load predictions and features
feats = pd.read_csv("ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv")
shap_vals = pd.read_csv("ARGUS_Cross_Domain_Results/argus_coral_data/predictions_raw/shap_values_after_adaptation.csv")

# Combine
df = pd.concat([feats, shap_vals.add_suffix('_shap')], axis=1)

# Find the majority bin
df_major = df[np.isclose(df['pkt_mean_to_max'], 1.0) & 
              np.isclose(df['tcp_flag_density'], 0.0) & 
              np.isclose(df['log_pkt_mean'], 3.135494) & 
              np.isclose(df['log_pkt_max'], 3.135494)]

print("SHAP values for the major bin:")
for col in ['pkt_mean_to_max_shap', 'tcp_flag_density_shap', 'log_pkt_mean_shap', 'log_pkt_max_shap']:
    print(df_major[col].value_counts().head(2))

