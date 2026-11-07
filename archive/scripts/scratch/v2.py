import pandas as pd
import numpy as np
import os
import glob
import time

def process_overlap(train_path, test_path, name):
    print(f"\n--- Overlap Diagnostics for {name} ---")
    df_train = pd.read_csv(train_path)
    df_test = pd.read_csv(test_path)
    
    # 1. Duplicate share in train
    total_train = len(df_train)
    unique_train_features = df_train.drop(columns=['label']).drop_duplicates()
    dupes_train = total_train - len(unique_train_features)
    print(f"Train duplicate share: {dupes_train} / {total_train} = {dupes_train/total_train*100:.2f}%")
    
    # 2. Test rows appearing in train
    features_train = set(tuple(x) for x in df_train.drop(columns=['label']).values)
    features_test = [tuple(x) for x in df_test.drop(columns=['label']).values]
    
    in_train_count = sum(1 for x in features_test if x in features_train)
    total_test = len(features_test)
    print(f"Test rows whose feature vector appears in train: {in_train_count} / {total_test} = {in_train_count/total_test*100:.2f}%")
    
    # 3. Conflicting labels in train
    # Group by feature vector, check if max(label) != min(label)
    # Using pandas groupby for speed
    feature_cols = [c for c in df_train.columns if c != 'label']
    label_variance = df_train.groupby(feature_cols)['label'].agg(['min', 'max'])
    conflicts = label_variance[label_variance['min'] != label_variance['max']]
    total_unique_vectors = len(label_variance)
    conflict_count = len(conflicts)
    print(f"Share of unique feature vectors with conflicting labels (Train): {conflict_count} / {total_unique_vectors} = {conflict_count/total_unique_vectors*100:.4f}%")
    
    del df_train, df_test

data_dir = "data/raw/legacy_package/argus_coral_data"
ciciot_train = os.path.join(data_dir, "ciciot_train_features.csv")
ciciot_test = os.path.join(data_dir, "ciciot_test_features.csv")
nfton_train = os.path.join(data_dir, "nfton_train_features.csv")
nfton_test = os.path.join(data_dir, "nfton_test_features.csv")

if os.path.exists(ciciot_train):
    process_overlap(ciciot_train, ciciot_test, "CICIoT2023")
if os.path.exists(nfton_train):
    process_overlap(nfton_train, nfton_test, "NF-ToN-IoT")

print("\nV2 complete.")
