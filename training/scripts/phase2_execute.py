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
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, RobustScaler
from sklearn.feature_selection import mutual_info_classif
import joblib

# Ensure the plots don't try to open windows
plt.switch_backend('Agg')

# Configuration
RAW_DATA_DIR = Path("training/data/raw/nftoniotv2")
PROCESSED_DATA_DIR = Path("training/data/processed")
EDA_REPORTS_DIR = Path("training/reports/eda")
ARTIFACTS_DIR = Path("training/exports")

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Optimizes the memory usage of a DataFrame by downcasting numeric types."""
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
            if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                df[col] = df[col].astype(np.float32) # using float32 instead of float16 for stability
            elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                df[col] = df[col].astype(np.float32)
            else:
                df[col] = df[col].astype(np.float64)
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            # Check if it makes sense to convert object/string to category
            num_unique_values = len(df[col].unique())
            num_total_values = len(df[col])
            if num_unique_values / num_total_values < 0.5:
                df[col] = df[col].astype('category')
    return df

def load_data(raw_dir: Path) -> pd.DataFrame:
    """Loads CSVs and Parquets, taking a 500k row sample to fit in 8GB RAM."""
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
    df = df.head(max_rows) # ensure exact size
    del chunks
    gc.collect()
    print(f"[*] Data loaded successfully (Sampled to prevent OOM). Shape: {df.shape}")
    return df

def generate_eda(df: pd.DataFrame, eda_dir: Path):
    """Generates basic EDA statistics and plots."""
    print("[*] Generating Exploratory Data Analysis (EDA) Reports...")
    eda_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Dataset Summary & Inspection
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
        
    # Stats
    numeric_df = df.select_dtypes(include=[np.number])
    stats = numeric_df.describe().T
    stats.to_csv(eda_dir / "descriptive_statistics.csv")
    
    # Plotting Functions
    def save_plot(name: str):
        for ext in ['png', 'svg', 'pdf']:
            plt.savefig(eda_dir / f"{name}.{ext}", dpi=300, bbox_inches='tight')
        plt.close()

    # Target Distribution
    target_col = 'Label' if 'Label' in df.columns else (df.columns[-1] if len(df.columns) > 0 else None)
    if target_col and target_col in df.columns:
        plt.figure(figsize=(8, 6))
        sns.countplot(data=df, x=target_col)
        plt.title("Target Distribution")
        save_plot("target_distribution")

    attack_col = 'Attack' if 'Attack' in df.columns else None
    if attack_col and attack_col in df.columns:
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, y=attack_col, order=df[attack_col].value_counts().index)
        plt.title("Attack Class Distribution")
        save_plot("attack_distribution")
        
    # Missing Value Matrix
    plt.figure(figsize=(12, 6))
    sample_df = df.sample(min(1000, len(df)))
    sns.heatmap(sample_df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title("Missing Value Matrix (Sampled 1000 rows)")
    save_plot("missing_value_matrix")
    
    # Correlation Heatmap
    if numeric_df.shape[1] > 0:
        plt.figure(figsize=(12, 10))
        corr = numeric_df.corr()
        sns.heatmap(corr, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title("Correlation Heatmap")
        save_plot("correlation_heatmap")
        
    print("[*] EDA Generation Complete.")

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Performs data cleaning: drop duplicates, handle NaNs, fix inf."""
    print("[*] Cleaning Data...")
    initial_shape = df.shape
    
    df = df.drop_duplicates()
    
    # Replace Infinite values with NaN
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Handle NaNs (Median for numeric, mode for categorical)
    for col in df.columns:
        if df[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "UNKNOWN")
                
    print(f"[*] Cleaned data. Original shape: {initial_shape}, New shape: {df.shape}")
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Generates dynamic features for network flows."""
    print("[*] Performing Feature Engineering...")
    # Safe division helper
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
        
    print(f"[*] Feature Engineering Complete. Total features now: {df.shape[1]}")
    return df

def encode_and_scale(df: pd.DataFrame, artifacts_dir: Path):
    """Encodes categoricals and scales numerics."""
    print("[*] Encoding and Scaling Data...")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    encoders = {}
    
    # Categoricals
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    target_cols = ['Label', 'Attack']
    
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        
    joblib.dump(encoders, artifacts_dir / "encoders.pkl")
    
    # Numerics
    num_cols = df.select_dtypes(include=[np.number]).columns
    # Exclude targets from scaling
    feature_cols = [c for c in num_cols if c not in target_cols]
    
    scaler = StandardScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    joblib.dump(scaler, artifacts_dir / "scaler.pkl")
    
    print("[*] Saved encoders.pkl and scaler.pkl")
    return df, feature_cols

def split_and_export(df: pd.DataFrame, output_dir: Path):
    """Splits the dataset and exports to CSV and Parquet."""
    print("[*] Splitting and Exporting Datasets...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    target_col = 'Label' if 'Label' in df.columns else (df.columns[-1] if len(df.columns) > 0 else None)
    
    X = df.drop(columns=[target_col]) if target_col else df
    y = df[target_col] if target_col else pd.Series(np.zeros(len(df)))
    
    # 80-10-10 split
    strat = y if len(y.unique()) > 1 else None
    
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.1, random_state=42, stratify=strat)
    
    strat_temp = y_temp if len(y_temp.unique()) > 1 else None
    relative_val_size = 0.1 / 0.9 # (10% of total is ~11.11% of the remaining 90%)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=relative_val_size, random_state=42, stratify=strat_temp)
    
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

def generate_final_metadata(df: pd.DataFrame, artifacts_dir: Path):
    """Generates final run metadata and summary."""
    print("[*] Generating Final Metadata...")
    metadata = {
        "Dataset_Version": "NF-ToN-IoT-v2-Processed",
        "Processing_Date": datetime.now().isoformat(),
        "Number_of_Records": len(df),
        "Number_of_Features": len(df.columns),
        "Scaling_Method": "StandardScaler",
        "Encoding_Method": "LabelEncoding",
        "Random_Seed": 42,
        "Status": "READY_FOR_PHASE_3"
    }
    
    with open(artifacts_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    # Generate an Excel Workbook report
    try:
        with pd.ExcelWriter(artifacts_dir / 'dataset_report.xlsx') as writer:
            pd.DataFrame([metadata]).to_excel(writer, sheet_name='Summary', index=False)
            df.head(100).to_excel(writer, sheet_name='Preview', index=False)
    except Exception as e:
        print(f"Failed to write Excel report: {e}")

    summary_md = f"""# Data Readiness Summary
**Dataset Status**: READY FOR PHASE 3
**Date Processed**: {metadata['Processing_Date']}

## Execution Result
The dataset was successfully processed according to Phase 2 requirements.
- **Records**: {metadata['Number_of_Records']}
- **Features**: {metadata['Number_of_Features']}
- **Cleaning**: Deduplication and NaN imputation completed.
- **Encoding**: Categorical fields Label-encoded.
- **Scaling**: Numeric fields standardized (StandardScaler).
- **Split**: 80% Train, 10% Validation, 10% Testing.
- **Export**: Data is available in `training/data/processed/` in `.csv` and `.parquet` formats.

The pipeline executed efficiently using memory chunking and dtype downcasting to respect the 8GB RAM limit.
"""
    with open(artifacts_dir / "Phase2_Summary.md", "w") as f:
        f.write(summary_md)
    print(summary_md)

def main():
    print("=== ARGUS Phase 2 Pipeline Execution ===")
    
    df = load_data(RAW_DATA_DIR)
    
    generate_eda(df, EDA_REPORTS_DIR)
    
    df = clean_data(df)
    
    df = feature_engineering(df)
    
    df, feature_cols = encode_and_scale(df, ARTIFACTS_DIR)
    
    split_and_export(df, PROCESSED_DATA_DIR)
    
    generate_final_metadata(df, ARTIFACTS_DIR)
    
    print("=== Phase 2 Execution Complete ===")

if __name__ == "__main__":
    main()
