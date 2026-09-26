#!/usr/bin/env python3
import os
import gc
import glob
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib

# Ensure the plots don't try to open windows
plt.switch_backend('Agg')

def parse_args():
    parser = argparse.ArgumentParser(description="ARGUS Phase 2: Dynamic Preprocessing Pipeline")
    parser.add_argument("--dataset", type=str, required=True, help="Name of the dataset (e.g., nftoniotv2, ciciot2023)")
    return parser.parse_args()

def setup_directories(dataset: str):
    dirs = {
        "raw": Path(f"training/data/raw/{dataset}"),
        "processed": Path(f"training/data/processed/{dataset}"),
        "eda": Path(f"training/reports/eda/{dataset}"),
        "exports": Path(f"training/exports/{dataset}")
    }
    for k, v in dirs.items():
        if k != "raw":
            v.mkdir(parents=True, exist_ok=True)
    return dirs

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
        raise FileNotFoundError(f"No dataset files found in {raw_dir}. Please place files here.")
        
    print(f"[*] Found {len(csv_files)} CSV files and {len(parquet_files)} Parquet files.")
    chunks = []
    total_rows = 0
    max_rows = 500000 # Configurable limit for memory safety
    
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
    
    # 1. Dataset Statistics & Memory Usage
    summary = {
        "Shape": df.shape,
        "Memory_Usage_MB": df.memory_usage(deep=True).sum() / (1024**2),
        "Columns": list(df.columns),
        "Types": df.dtypes.astype(str).to_dict(),
        "Missing_Values": df.isnull().sum().to_dict(),
        "Duplicates": int(df.duplicated().sum())
    }
    
    with open(eda_dir / "dataset_statistics.json", "w") as f:
        json.dump(summary, f, indent=4)
        
    # 2. Categorical & Numerical Features
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    with open(eda_dir / "feature_types.json", "w") as f:
        json.dump({"Numerical": num_cols, "Categorical": cat_cols}, f, indent=4)
        
    stats = df[num_cols].describe().T
    stats.to_csv(eda_dir / "descriptive_statistics.csv")
    
    def save_plot(name: str):
        for ext in ['png', 'svg', 'pdf']:
            plt.savefig(eda_dir / f"{name}.{ext}", dpi=300, bbox_inches='tight')
        plt.close()

    # 3. Class Distribution
    target_col = 'Label' if 'Label' in df.columns else None
    if target_col:
        plt.figure(figsize=(8, 6))
        sns.countplot(data=df, x=target_col)
        plt.title("Target Class Distribution")
        save_plot("target_distribution")

    # Target leakage column preview
    attack_col = 'Attack' if 'Attack' in df.columns else None
    if attack_col:
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, y=attack_col, order=df[attack_col].value_counts().index)
        plt.title("Attack Category Distribution")
        save_plot("attack_distribution")
        
    # 4. Missing Values
    plt.figure(figsize=(12, 6))
    sample_df = df.sample(min(1000, len(df)))
    sns.heatmap(sample_df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title("Missing Value Matrix (Sampled 1000 rows)")
    save_plot("missing_value_matrix")
    
    # 5. Correlation Matrix
    if len(num_cols) > 0:
        plt.figure(figsize=(12, 10))
        corr = df[num_cols].corr()
        sns.heatmap(corr, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title("Correlation Heatmap")
        save_plot("correlation_heatmap")
        
    # 6. Feature Importance Preview (Quick RF on a small clean sample)
    if target_col and len(num_cols) > 1:
        try:
            print("[*] Generating Feature Importance Preview...")
            fi_df = df[num_cols + [target_col]].dropna().sample(min(10000, len(df)))
            X_fi = fi_df.drop(columns=[target_col])
            y_fi = fi_df[target_col]
            if len(y_fi.unique()) > 1:
                rf = RandomForestClassifier(n_estimators=50, max_depth=5, n_jobs=-1, random_state=42)
                rf.fit(X_fi, y_fi)
                importances = pd.Series(rf.feature_importances_, index=X_fi.columns).sort_values(ascending=False).head(20)
                
                plt.figure(figsize=(10, 8))
                sns.barplot(x=importances.values, y=importances.index)
                plt.title("Feature Importance Preview (Top 20)")
                save_plot("feature_importance_preview")
        except Exception as e:
            print(f"[!] Could not generate feature importance preview: {e}")
            
    print("[*] EDA Generation Complete.")

def drop_target_leakage(df: pd.DataFrame):
    """Drops any columns that constitute target leakage."""
    leakage_cols = ['Attack', 'Attack_Type', 'Label_Type', 'Category']
    dropped = []
    for col in leakage_cols:
        if col in df.columns:
            df = df.drop(columns=[col])
            dropped.append(col)
    if dropped:
        print(f"[*] Dropped leakage columns: {dropped}")
    return df

def perform_split(df: pd.DataFrame):
    """Data Splitting BEFORE any fitting to prevent Data Leakage."""
    print("[*] Splitting Data...")
    target_col = 'Label' if 'Label' in df.columns else None
    
    # Infer schema
    if target_col:
        X = df.drop(columns=[target_col])
        y = df[target_col]
        strat = y if len(y.unique()) > 1 else None
    else:
        print("[!] No 'Label' column found! Assuming inference mode.")
        X = df
        y = pd.Series(np.zeros(len(df)))
        strat = None
        
    # 80/10/10 Split
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.1, random_state=42, stratify=strat)
    
    strat_temp = y_temp if len(y_temp.unique()) > 1 else None
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.1111, random_state=42, stratify=strat_temp)
    
    return X_train, X_val, X_test, y_train, y_val, y_test

def clean_data(X_train, X_val, X_test):
    """Missing Value Handling (Fit on Train)."""
    print("[*] Handling Missing Values (Imputation via Training Set)...")
    
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
    """Feature Engineering."""
    def safe_div(a, b):
        return np.where(b == 0, 0, a / b)
        
    # Some common network features
    if 'IN_PKTS' in df.columns and 'FLOW_DURATION_MILLISECONDS' in df.columns:
        df['PacketsPerSecond'] = safe_div(df['IN_PKTS'], df['FLOW_DURATION_MILLISECONDS'] / 1000)
        
    if 'IN_BYTES' in df.columns and 'FLOW_DURATION_MILLISECONDS' in df.columns:
        df['BytesPerSecond'] = safe_div(df['IN_BYTES'], df['FLOW_DURATION_MILLISECONDS'] / 1000)
        
    if 'IN_BYTES' in df.columns and 'IN_PKTS' in df.columns:
        df['BytesPerPacket'] = safe_div(df['IN_BYTES'], df['IN_PKTS'])
        
    if 'IN_BYTES' in df.columns and 'OUT_BYTES' in df.columns:
        df['InboundRatio'] = safe_div(df['IN_BYTES'], (df['IN_BYTES'] + df['OUT_BYTES']))
        
    return df

def encode_and_scale(X_train, X_val, X_test, exports_dir: Path):
    """Categorical Encoding & Normalization (Fit on Train)."""
    print("[*] Encoding and Normalizing Data (Fit via Training Set)...")
    
    encoders = {}
    cat_cols = X_train.select_dtypes(include=['object', 'category']).columns
    
    for col in cat_cols:
        le = LabelEncoder()
        # Fit ONLY on train
        le.fit(X_train[col].astype(str))
        classes = list(le.classes_)
        if "UNKNOWN" not in classes:
            classes.append("UNKNOWN")
        le.classes_ = np.array(classes)
        
        for df in [X_train, X_val, X_test]:
            df[col] = df[col].astype(str)
            df[col] = df[col].apply(lambda x: x if x in le.classes_ else "UNKNOWN")
            df[col] = le.transform(df[col])
            
        encoders[col] = le
        
    if encoders:
        joblib.dump(encoders, exports_dir / "encoders.pkl")
    
    num_cols = X_train.select_dtypes(include=[np.number]).columns
    feature_cols = list(num_cols)
    
    scaler = StandardScaler()
    X_train[feature_cols] = scaler.fit_transform(X_train[feature_cols])
    X_val[feature_cols] = scaler.transform(X_val[feature_cols])
    X_test[feature_cols] = scaler.transform(X_test[feature_cols])
    joblib.dump(scaler, exports_dir / "scaler.pkl")
    
    print("[*] Saved encoders.pkl and scaler.pkl")
    return X_train, X_val, X_test, feature_cols

def export_datasets(X_train, y_train, X_val, y_val, X_test, y_test, processed_dir: Path):
    print("[*] Exporting Processed Datasets...")
    
    datasets = {
        "training": pd.concat([X_train, y_train], axis=1),
        "validation": pd.concat([X_val, y_val], axis=1),
        "testing": pd.concat([X_test, y_test], axis=1)
    }
    
    for name, dataset in datasets.items():
        print(f"[*] Saving {name} (Shape: {dataset.shape})...")
        dataset.to_parquet(processed_dir / f"{name}.parquet", index=False)
        dataset.to_csv(processed_dir / f"{name}.csv", index=False)

def generate_metadata(X_train, dataset_name: str, exports_dir: Path):
    print("[*] Generating Metadata & Feature List...")
    feature_list = list(X_train.columns)
    
    with open(exports_dir / "feature_list.json", "w") as f:
        json.dump(feature_list, f, indent=4)
        
    metadata = {
        "Dataset": dataset_name,
        "Processing_Date": datetime.now().isoformat(),
        "Number_of_Features": len(feature_list),
        "Scaling_Method": "StandardScaler",
        "Encoding_Method": "LabelEncoding",
        "Target_Leakage_Handled": True,
        "Data_Leakage_Handled": True,
        "Split": "80/10/10"
    }
    
    with open(exports_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

def main():
    args = parse_args()
    dataset = args.dataset
    print(f"\n=== ARGUS Phase 2 Pipeline Execution: {dataset} ===")
    
    dirs = setup_directories(dataset)
    
    # Data Type Validation & Chunked Loading
    df = load_data(dirs["raw"])
    
    # Duplicate Removal
    print(f"[*] Removing duplicates. Original shape: {df.shape}")
    df = df.drop_duplicates()
    print(f"[*] Shape after duplicate removal: {df.shape}")
    
    # EDA
    generate_eda(df, dirs["eda"])
    
    # Data prep
    df = drop_target_leakage(df)
    X_train, X_val, X_test, y_train, y_val, y_test = perform_split(df)
    
    # Data Cleaning (Imputation)
    X_train, X_val, X_test = clean_data(X_train, X_val, X_test)
    
    # Feature Engineering
    X_train = feature_engineering(X_train)
    X_val = feature_engineering(X_val)
    X_test = feature_engineering(X_test)
    
    # Categorical Encoding & Normalization (Scaling)
    X_train, X_val, X_test, feature_cols = encode_and_scale(X_train, X_val, X_test, dirs["exports"])
    
    # Save Feature Selection / Lists & Processed Data
    generate_metadata(X_train, dataset, dirs["exports"])
    export_datasets(X_train, y_train, X_val, y_val, X_test, y_test, dirs["processed"])
    
    print(f"=== Phase 2 Execution Complete for {dataset} ===")

if __name__ == "__main__":
    main()
