import pandas as pd
import numpy as np

print("Running Sanity Check on Preprocessed Data...")

df = pd.read_parquet("training/data/processed/training.parquet")

if 'Attack' in df.columns:
    print("FAILED: 'Attack' column still exists in the dataset!")
    exit(1)

print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Label Distribution:\n{df['Label'].value_counts(normalize=True)}")

target_col = 'Label'
correlations = df.corr()[target_col].abs().sort_values(ascending=False)

print("\nTop 10 Feature Correlations with Label:")
print(correlations.head(11))

leakage_features = correlations[(correlations > 0.95) & (correlations.index != target_col)]

if len(leakage_features) > 0:
    print(f"\nFAILED: Found {len(leakage_features)} features with > 0.95 correlation with Label:")
    print(leakage_features)
    exit(1)

print("\nSUCCESS: No highly correlated (>0.95) leakage features found.")
