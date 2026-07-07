#!/usr/bin/env python3
import os
import gc
import glob
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# Ensure the plots don't try to open windows
plt.switch_backend('Agg')

# Configuration
RAW_DATA_DIR = Path("training/data/raw/nftoniotv2")
PROCESSED_DATA_DIR = Path("training/data/processed")
EDA_REPORTS_DIR = Path("training/reports/eda")
ARTIFACTS_DIR = Path("training/exports")

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]):
            c_min = df[col].min()
            c_max = df[col].max()
            if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                df[col] = df[col].astype(np.int8)
            elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                df[col] = df[col].astype(np.int16)
            elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                df[col] = df[col].astype(np.int32)
            else:
                df[col] = df[col].astype(np.int64)
        elif pd.api.types.is_float_dtype(df[col]):
            c_min = df[col].min()
            c_max = df[col].max()
            if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                df[col] = df[col].astype(np.float32)
            else:
                df[col] = df[col].astype(np.float64)
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            num_unique_values = len(df[col].unique())
            num_total_values = len(df[col])
            if num_unique_values / num_total_values < 0.5:
                df[col] = df[col].astype('category')
    return df

def load_data(raw_dir: Path) -> pd.DataFrame:
    csv_files = glob.glob(str(raw_dir / "*.csv"))
    parquet_files = glob.glob(str(raw_dir / "*.parquet"))
    
    if not csv_files and not parquet_files:
        raise FileNotFoundError(f"No dataset files found in {raw_dir}")
        
    print(f"[*] Found {len(csv_files)} CSV files and {len(parquet_files)} Parquet files.")
    chunks = []
    total_rows = 0
    max_rows = 500000
    
    for file in csv_files:
        if total_rows >= max_rows: break
        print(f"[*] Processing CSV {file}...")
        for chunk in pd.read_csv(file, chunksize=100000, low_memory=False):
            if total_rows >= max_rows: break
            chunk = optimize_dtypes(chunk)
            chunks.append(chunk)
            total_rows += len(chunk)
            
    for file in parquet_files:
        if total_rows >= max_rows: break
        print(f"[*] Processing Parquet {file}...")
        import pyarrow.dataset as ds
        dataset = ds.dataset(file, format="parquet")
        for batch in dataset.to_batches(batch_size=100000):
            if total_rows >= max_rows: break
            chunk = batch.to_pandas()
            chunk = optimize_dtypes(chunk)
            chunks.append(chunk)
            total_rows += len(chunk)
            
    df = pd.concat(chunks, ignore_index=True)
    df = df.head(max_rows)
    del chunks
    gc.collect()
    print(f"[*] Data loaded successfully. Shape: {df.shape}")
    return df

def generate_eda(df: pd.DataFrame, eda_dir: Path):
    print("[*] Generating Exploratory Data Analysis (EDA) Reports...")
    eda_dir.mkdir(parents=True, exist_ok=True)
    
    summary = {
        "Shape": df.shape,
        "Memory_Usage_MB": df.memory_usage(deep=True).sum() / (1024**2),
        "Columns": list(df.columns),
        "Types": df.dtypes.astype(str).to_dict(),
        "Missing_Values": df.isnull().sum().to_dict(),
        "Duplicates": int(df.duplicated().sum())
    }
    
    with open(eda_dir / "inspection_report.json", "w") as f:
        json.dump(summary, f, indent=4)
        
    numeric_df = df.select_dtypes(include=[np.number])
    stats = numeric_df.describe().T
    stats.to_csv(eda_dir / "descriptive_statistics.csv")
    
    def save_plot(name: str):
        for ext in ['png', 'svg', 'pdf']:
            plt.savefig(eda_dir / f"{name}.{ext}", dpi=300, bbox_inches='tight')
        plt.close()

    target_col = 'Label' if 'Label' in df.columns else None
    if target_col:
        plt.figure(figsize=(8, 6))
        sns.countplot(data=df, x=target_col)
        plt.title("Target Distribution")
        save_plot("target_distribution")

    attack_col = 'Attack' if 'Attack' in df.columns else None
    if attack_col:
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, y=attack_col, order=df[attack_col].value_counts().index)
        plt.title("Attack Class Distribution")
        save_plot("attack_distribution")
        
    plt.figure(figsize=(12, 6))
    sample_df = df.sample(min(1000, len(df)))
    sns.heatmap(sample_df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title("Missing Value Matrix (Sampled 1000 rows)")
    save_plot("missing_value_matrix")
    
    if numeric_df.shape[1] > 0:
        plt.figure(figsize=(12, 10))
        corr = numeric_df.corr()
        sns.heatmap(corr, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title("Correlation Heatmap")
        save_plot("correlation_heatmap")
        
    print("[*] EDA Generation Complete.")

def clean_data(X_train, X_val, X_test):
    """Clean data using imputers fit ONLY on the training set to prevent data leakage."""
    print("[*] Cleaning Data (Imputation via Training Set)...")
    
    for df in [X_train, X_val, X_test]:
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    for col in X_train.columns:
        if X_train[col].isnull().any() or X_val[col].isnull().any() or X_test[col].isnull().any():
            if pd.api.types.is_numeric_dtype(X_train[col]):
                fill_val = X_train[col].median()
            else:
                mode_s = X_train[col].mode()
                fill_val = mode_s[0] if not mode_s.empty else "UNKNOWN"
                
            X_train[col] = X_train[col].fillna(fill_val)
            X_val[col] = X_val[col].fillna(fill_val)
            X_test[col] = X_test[col].fillna(fill_val)
                
    return X_train, X_val, X_test

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    def safe_div(a, b):
        return np.where(b == 0, 0, a / b)
        
    if 'IN_PKTS' in df.columns and 'FLOW_DURATION_MILLISECONDS' in df.columns:
        df['PacketsPerSecond'] = safe_div(df['IN_PKTS'], df['FLOW_DURATION_MILLISECONDS'] / 1000)
        
    if 'IN_BYTES' in df.columns and 'FLOW_DURATION_MILLISECONDS' in df.columns:
        df['BytesPerSecond'] = safe_div(df['IN_BYTES'], df['FLOW_DURATION_MILLISECONDS'] / 1000)
        
    if 'IN_BYTES' in df.columns and 'IN_PKTS' in df.columns:
        df['BytesPerPacket'] = safe_div(df['IN_BYTES'], df['IN_PKTS'])
        
    if 'IN_BYTES' in df.columns and 'OUT_BYTES' in df.columns:
        df['InboundRatio'] = safe_div(df['IN_BYTES'], (df['IN_BYTES'] + df['OUT_BYTES']))
        
    return df

def encode_and_scale(X_train, X_val, X_test, artifacts_dir: Path):
    """Encode and Scale using parameters fit ONLY on the training set to prevent data leakage."""
    print("[*] Encoding and Scaling Data (Fit via Training Set)...")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    encoders = {}
    cat_cols = X_train.select_dtypes(include=['object', 'category']).columns
    
    for col in cat_cols:
        le = LabelEncoder()
        
        # Fit on train
        le.fit(X_train[col].astype(str))
        classes = list(le.classes_)
        if "UNKNOWN" not in classes:
            classes.append("UNKNOWN")
        le.classes_ = np.array(classes)
        
        # Transform all handling unseen classes
        for df in [X_train, X_val, X_test]:
            # Convert categorical back to string/object to apply lambda properly
            df[col] = df[col].astype(str)
            df[col] = df[col].apply(lambda x: x if x in le.classes_ else "UNKNOWN")
            df[col] = le.transform(df[col])
            
        encoders[col] = le
        
    joblib.dump(encoders, artifacts_dir / "encoders.pkl")
    
    num_cols = X_train.select_dtypes(include=[np.number]).columns
    feature_cols = list(num_cols)
    
    scaler = StandardScaler()
    X_train[feature_cols] = scaler.fit_transform(X_train[feature_cols])
    X_val[feature_cols] = scaler.transform(X_val[feature_cols])
    X_test[feature_cols] = scaler.transform(X_test[feature_cols])
    joblib.dump(scaler, artifacts_dir / "scaler.pkl")
    
    print("[*] Saved encoders.pkl and scaler.pkl")
    return X_train, X_val, X_test, feature_cols

def export_datasets(X_train, y_train, X_val, y_val, X_test, y_test, output_dir: Path):
    print("[*] Exporting Split Datasets...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    datasets = {
        "training": pd.concat([X_train, y_train], axis=1),
        "validation": pd.concat([X_val, y_val], axis=1),
        "testing": pd.concat([X_test, y_test], axis=1)
    }
    
    for name, dataset in datasets.items():
        print(f"[*] Exporting {name} (Shape: {dataset.shape})...")
        dataset.to_csv(output_dir / f"{name}.csv", index=False)
        dataset.to_parquet(output_dir / f"{name}.parquet", index=False)
        
    print("[*] Export Complete.")

def generate_final_metadata(X_train, artifacts_dir: Path):
    print("[*] Generating Final Metadata...")
    metadata = {
        "Dataset_Version": "NF-ToN-IoT-v2-Processed",
        "Processing_Date": datetime.now().isoformat(),
        "Number_of_Features": len(X_train.columns),
        "Scaling_Method": "StandardScaler",
        "Encoding_Method": "LabelEncoding",
        "Random_Seed": 42,
        "Status": "READY_FOR_PHASE_3"
    }
    
    with open(artifacts_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    summary_md = f"""# Data Readiness Summary (Leakage-Free)
**Dataset Status**: READY FOR PHASE 3
**Date Processed**: {metadata['Processing_Date']}

## Execution Result
The dataset was processed following rigorous leakage-free validation protocols.
- **Target Leakage Fixed**: The `Attack` column was dropped entirely.
- **Data Leakage Fixed**: Train/Test split occurred *before* imputation, scaling, and encoding.
- **Split**: 80% Train, 10% Validation, 10% Testing.
- **Export**: Data is available in `training/data/processed/` in `.csv` and `.parquet` formats.
"""
    with open(artifacts_dir / "Phase2_Summary.md", "w") as f:
        f.write(summary_md)

def main():
    print("=== ARGUS Phase 2 Pipeline Execution ===")
    
    df = load_data(RAW_DATA_DIR)
    
    df = df.drop_duplicates()
    
    generate_eda(df, EDA_REPORTS_DIR)
    
    # 1. FIX TARGET LEAKAGE: Drop 'Attack' column
    if 'Attack' in df.columns:
        print("[*] Dropping 'Attack' column to prevent Target Leakage.")
        df = df.drop(columns=['Attack'])
        
    # 2. SPLIT DATA FIRST
    target_col = 'Label' if 'Label' in df.columns else None
    X = df.drop(columns=[target_col]) if target_col else df
    y = df[target_col] if target_col else pd.Series(np.zeros(len(df)))
    
    strat = y if len(y.unique()) > 1 else None
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.1, random_state=42, stratify=strat)
    
    strat_temp = y_temp if len(y_temp.unique()) > 1 else None
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.1111, random_state=42, stratify=strat_temp)
    
    print(f"[*] Data split into Train ({len(X_train)}), Val ({len(X_val)}), Test ({len(X_test)})")
    
    # 3. CLEAN DATA (Fit on Train)
    X_train, X_val, X_test = clean_data(X_train, X_val, X_test)
    
    # 4. FEATURE ENGINEERING
    X_train = feature_engineering(X_train)
    X_val = feature_engineering(X_val)
    X_test = feature_engineering(X_test)
    
    # 5. ENCODE & SCALE (Fit on Train)
    X_train, X_val, X_test, feature_cols = encode_and_scale(X_train, X_val, X_test, ARTIFACTS_DIR)
    
    # 6. EXPORT
    export_datasets(X_train, y_train, X_val, y_val, X_test, y_test, PROCESSED_DATA_DIR)
    generate_final_metadata(X_train, ARTIFACTS_DIR)
    
    print("=== Phase 2 Execution Complete ===")

if __name__ == "__main__":
    main()
