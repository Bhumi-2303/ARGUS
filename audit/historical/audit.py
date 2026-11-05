import pandas as pd
import json

datasets = {
    "CICIoT2023": "data/cic_iot_2023/raw/CSV/MERGED_CSV/Merged01.csv",
    "NF-ToN-IoT": "data/nf_ton_iot/processed/NF-ToN-IoT.parquet",
    "BoT-IoT": "data/bot_iot/raw/BoT-IoT dataset/csv/data_15.csv",
    "HAI_21_03": "data/hai/raw/hai-21.03/train1.csv",
    "TON_IoT_Network": "data/ton_iot/train_test/Train_Test_Network_dataset/train_test_network.csv"
}

results = {}

for name, path in datasets.items():
    print(f"Reading {name}...")
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
        sample = df.head(10000)
        num_rows = len(df)
    else:
        # Just read a chunk for quick analysis and count rows (or approximate)
        df_iter = pd.read_csv(path, chunksize=10000, nrows=20000, low_memory=False)
        sample = next(df_iter)
        num_rows = "N/A (Skipped full scan)"
    
    num_cols = len(sample.columns)
    columns = list(sample.columns)
    
    # Identify possible labels
    label_cols = [c for c in columns if 'label' in c.lower() or 'attack' in c.lower() or 'cat' in c.lower() or 'type' in c.lower()]
    labels_vals = {}
    for c in label_cols:
        labels_vals[c] = sample[c].dropna().unique().tolist()[:10]
        
    # Identify timestamps
    time_cols = [c for c in columns if 'time' in c.lower() or 'date' in c.lower() or 'stamp' in c.lower()]
    time_vals = {}
    for c in time_cols:
        time_vals[c] = {"min": str(sample[c].min()), "max": str(sample[c].max())}
        
    # Identify leakage
    leakage_cols = [c for c in columns if 'ip' in c.lower() or 'mac' in c.lower() or 'port' in c.lower() or 'id' in c.lower()]
    
    results[name] = {
        "columns": columns,
        "num_cols": num_cols,
        "label_cols": labels_vals,
        "time_cols": time_vals,
        "leakage_cols": leakage_cols,
        "dtypes": {str(k): str(v) for k, v in sample.dtypes.items()}
    }

with open("audit_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Done!")
