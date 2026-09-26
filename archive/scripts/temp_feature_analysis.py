import pandas as pd
import numpy as np

# Load predictions and features
preds = pd.read_csv("phase4_results/experiments/E5_fusion_CORAL_prior/predictions.csv")
feats = pd.read_csv("ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv")

# Combine
df = pd.concat([feats, preds], axis=1)

# Find the majority bin
df_major = df[np.isclose(df['y_prob'], 0.504138, atol=1e-5)]

print(f"Total samples in major bin: {len(df_major)}")
print("Label distribution in major bin:")
print(df_major['label'].value_counts())

print("\nFeature values for the major bin:")
for col in ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']:
    print(df_major[col].value_counts().head(5))

# Also check the class distributions of source vs target
print("\nTarget (IEC104) test set class imbalance:")
print(df['label'].value_counts(normalize=True))

source_feats = pd.read_csv("ARGUS_Cross_Domain_Results/argus_coral_data/ciciot_test_features.csv")
print("\nSource (CICIoT2023) test set class imbalance:")
print(source_feats['label'].value_counts(normalize=True))

