import pandas as pd
import json

datasets = {
    "CICIoT2023": "data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/Merged01.csv",
    "NF-ToN-IoT-v2": "data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet",
    "BoT-IoT": "scratch/BoT-IoT dataset/csv/data_32.csv",
    "HAI": "data/raw/hai/raw/hai-test1.csv",
    "TON_IoT": "data/raw/ton_iot/train_test/Train_Test_Network_dataset/train_test_network.csv"
}

output = {}

for name, path in datasets.items():
    print(f"Reading {name}...")
    try:
        if path.endswith('.csv'):
            df = pd.read_csv(path, nrows=5)
        else:
            df = pd.read_parquet(path)
            df = df.head(5)
            
        columns = {}
        for col in df.columns:
            columns[col] = str(df[col].dtype)
            
        output[name] = columns
    except Exception as e:
        print(f"Error reading {name}: {e}")

with open('scratch/schemas.json', 'w') as f:
    json.dump(output, f, indent=4)
