import pandas as pd
import numpy as np
import glob
import os
import gc
import json

def audit_parquet(file_path, label_col='Label', benign_val=0):
    df = pd.read_parquet(file_path)
    total_rows = len(df)
    file_size = os.path.getsize(file_path)
    
    benign_count = int((df[label_col] == benign_val).sum())
    attack_count = total_rows - benign_count
    
    dup_count = int(df.duplicated().sum())
    dup_rate = dup_count / total_rows if total_rows > 0 else 0
    
    cols = list(df.columns)
    dtypes = {c: str(df[c].dtype) for c in cols}
    
    nan_rates = {}
    inf_rates = {}
    const_cols = []
    
    for c in cols:
        nan_rates[c] = float(df[c].isna().sum() / total_rows)
        if pd.api.types.is_numeric_dtype(df[c]):
            inf_rates[c] = float(np.isinf(df[c]).sum() / total_rows)
        else:
            inf_rates[c] = 0.0
            
        if df[c].nunique(dropna=False) <= 1:
            const_cols.append(c)
            
    return {
        'total_rows': total_rows,
        'file_size': file_size,
        'columns': cols,
        'dtypes': dtypes,
        'benign_count': benign_count,
        'attack_count': attack_count,
        'duplicate_count': dup_count,
        'duplicate_rate': dup_rate,
        'nan_rates': nan_rates,
        'inf_rates': inf_rates,
        'constant_columns': const_cols
    }

def audit_csvs_chunked(file_pattern, label_col='label', benign_val='Benign', chunksize=500000):
    files = glob.glob(file_pattern)
    total_rows = 0
    file_size = sum(os.path.getsize(f) for f in files)
    
    benign_count = 0
    dup_count = 0
    row_hashes = set()
    
    col_names = None
    dtypes = {}
    nan_counts = {}
    inf_counts = {}
    col_mins = {}
    col_maxs = {}
    
    for f in files:
        for chunk in pd.read_csv(f, chunksize=chunksize, low_memory=False):
            if col_names is None:
                col_names = list(chunk.columns)
                dtypes = {c: str(chunk[c].dtype) for c in col_names}
                nan_counts = {c: 0 for c in col_names}
                inf_counts = {c: 0 for c in col_names}
                for c in col_names:
                    col_mins[c] = float('inf')
                    col_maxs[c] = float('-inf')

            total_rows += len(chunk)
            benign_count += (chunk[label_col] == benign_val).sum()
            
            hashes = pd.util.hash_pandas_object(chunk, index=False)
            for h in hashes:
                if h in row_hashes:
                    dup_count += 1
                else:
                    row_hashes.add(h)
                    
            for c in col_names:
                nan_counts[c] += int(chunk[c].isna().sum())
                if pd.api.types.is_numeric_dtype(chunk[c]):
                    inf_counts[c] += int(np.isinf(chunk[c]).sum())
                
                if pd.api.types.is_numeric_dtype(chunk[c]):
                    try:
                        cmin = chunk[c].min()
                        cmax = chunk[c].max()
                        if cmin < col_mins[c]: col_mins[c] = cmin
                        if cmax > col_maxs[c]: col_maxs[c] = cmax
                    except:
                        pass
        gc.collect()
        
    attack_count = total_rows - benign_count
    dup_rate = dup_count / total_rows if total_rows > 0 else 0
    
    nan_rates = {c: nan_counts[c] / total_rows for c in col_names}
    inf_rates = {c: inf_counts[c] / total_rows for c in col_names}
    const_cols = [c for c in col_names if pd.api.types.is_numeric_dtype(dtypes[c]) and col_mins.get(c) == col_maxs.get(c)]
    
    return {
        'total_rows': total_rows,
        'file_size': file_size,
        'columns': col_names,
        'dtypes': dtypes,
        'benign_count': int(benign_count),
        'attack_count': int(attack_count),
        'duplicate_count': dup_count,
        'duplicate_rate': dup_rate,
        'nan_rates': nan_rates,
        'inf_rates': inf_rates,
        'constant_columns': const_cols
    }

if __name__ == "__main__":
    out_file = "audit_metrics.json"
    results = {}
    if os.path.exists(out_file):
        with open(out_file) as f:
            results = json.load(f)
    
    def save():
        with open(out_file, "w") as f:
            json.dump(results, f, indent=2)
            
    if 'NF-ToN-IoT' not in results:
        print("Auditing NF-ToN-IoT...")
        if os.path.exists("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet"):
            results['NF-ToN-IoT'] = audit_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet", label_col='Label', benign_val=0)
            save()
            
    if 'TON_IoT' not in results:
        print("Auditing TON_IoT Network...")
        if os.path.exists("data/raw/ton_iot/train_test/Train_Test_Network_dataset/train_test_network.csv"):
            results['TON_IoT'] = audit_csvs_chunked("data/raw/ton_iot/train_test/Train_Test_Network_dataset/train_test_network.csv", label_col='label', benign_val=0)
            save()
            
    if 'BoT-IoT' not in results:
        print("Auditing BoT-IoT...")
        bot_files = glob.glob("data/raw/bot_iot/raw/BoT-IoT dataset/csv/*.csv")
        if bot_files:
            results['BoT-IoT'] = audit_csvs_chunked("data/raw/bot_iot/raw/BoT-IoT dataset/csv/*.csv", label_col='attack', benign_val=0)
            save()
            
    if 'CICIoT2023' not in results:
        print("Auditing CICIoT2023...")
        cic_files = glob.glob("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/*.csv")
        if cic_files:
            results['CICIoT2023'] = audit_csvs_chunked("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/*.csv", label_col='Label', benign_val='Benign')
            save()
            
    print("Done")
