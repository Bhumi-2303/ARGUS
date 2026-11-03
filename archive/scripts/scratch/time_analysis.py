import pandas as pd
import json
import glob
import os

results = {}

# Analyze IoT Telemetry time range
print("Analyzing IoT Telemetry time range...")
iot_files = glob.glob('data/ton_iot/processed/Processed_IoT_dataset/IoT_*.csv')
iot_min_ts = None
iot_max_ts = None

for f in iot_files:
    df = pd.read_csv(f, usecols=['date', 'time'])
    # Combine date and time, then parse
    # IoT format: date: 31-Mar-19, time: 12:36:52
    df['datetime'] = pd.to_datetime(df['date'].str.strip() + ' ' + df['time'].str.strip(), format='%d-%b-%y %H:%M:%S', errors='coerce')
    
    file_min = df['datetime'].min()
    file_max = df['datetime'].max()
    
    if pd.notnull(file_min):
        if iot_min_ts is None or file_min < iot_min_ts:
            iot_min_ts = file_min
    if pd.notnull(file_max):
        if iot_max_ts is None or file_max > iot_max_ts:
            iot_max_ts = file_max

print(f"IoT Min: {iot_min_ts}, IoT Max: {iot_max_ts}")

net_file = 'data/ton_iot/network_timestamped/Network_dataset_1.csv'
net_min_ts = None
net_max_ts = None

if os.path.exists(net_file):
    print(f"Analyzing {net_file} time range...")
    df_net = pd.read_csv(net_file)
    if 'ts' in df_net.columns:
        df_net['datetime'] = pd.to_datetime(df_net['ts'], unit='s', errors='coerce')
        net_min_ts = df_net['datetime'].min()
        net_max_ts = df_net['datetime'].max()
        print(f"Net Min: {net_min_ts}, Net Max: {net_max_ts}")

    # Generate stats for the network dataset
    stats = {
        "file": net_file,
        "rows": len(df_net),
        "columns": len(df_net.columns),
        "missing_values": int(df_net.isna().sum().sum()),
        "duplicates": int(df_net.duplicated().sum())
    }
    
    if 'label' in df_net.columns:
        stats['label_distribution'] = df_net['label'].value_counts().to_dict()
    if 'type' in df_net.columns:
        stats['type_distribution'] = df_net['type'].value_counts().to_dict()
        
    print("Network Stats:", stats)

with open('scratch/time_analysis.json', 'w') as f:
    json.dump({
        'iot_min': str(iot_min_ts),
        'iot_max': str(iot_max_ts),
        'net_min': str(net_min_ts),
        'net_max': str(net_max_ts),
        'net_stats': stats if os.path.exists(net_file) else None
    }, f, indent=2)
