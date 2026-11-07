import pandas as pd
import numpy as np
import hashlib
import json
import os

print("--- Phase 1: Forensic Data Leakage Validation ---")
ciciot_processed = pd.read_csv("data/raw/cic_iot_2023/processed/part-00000-363d1ba3-8ab5-4f96-bc25-4d5862db7cb9-c000.csv")
nfton_processed = pd.read_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet")
bot_raw = pd.read_csv("data/raw/bot_iot/raw/BoT-IoT dataset/csv/data_32.csv")

print(f"Loaded CICIoT: {len(ciciot_processed)} rows")
print(f"Loaded NFToN: {len(nfton_processed)} rows")
print(f"Loaded BoTIoT (sample): {len(bot_raw)} rows")

def hash_df(df, cols):
    # Hashes rows based on specified columns
    df_sub = df[cols].astype(str)
    return df_sub.apply(lambda row: hashlib.md5(''.join(row).encode()).hexdigest(), axis=1)

# Raw overlap check between CICIoT and NF-ToN
# Wait, do they even share the same feature space in RAW format?
# CICIoT has 'Tot sum', 'Tot size', 'Number', 'Protocol Type'.
# NFToN has 'IN_BYTES', 'OUT_BYTES', 'IN_PKTS', 'OUT_PKTS', 'PROTOCOL'.
# To compare raw overlap, we must project them to the canonical schema!
print("Extracting canonical features from RAW datasets...")
ciciot_raw_canon = pd.DataFrame()
ciciot_raw_canon['total_pkts'] = ciciot_processed['Number']
ciciot_raw_canon['total_bytes'] = ciciot_processed['Tot sum']
ciciot_raw_canon['protocol'] = ciciot_processed['Protocol Type']

nfton_raw_canon = pd.DataFrame()
nfton_raw_canon['total_pkts'] = nfton_processed['IN_PKTS'] + nfton_processed['OUT_PKTS']
nfton_raw_canon['total_bytes'] = nfton_processed['IN_BYTES'] + nfton_processed['OUT_BYTES']
nfton_raw_canon['protocol'] = nfton_processed['PROTOCOL']

bot_raw_canon = pd.DataFrame()
bot_raw_canon['total_pkts'] = bot_raw['pkts']
bot_raw_canon['total_bytes'] = bot_raw['bytes']
bot_raw_canon['protocol'] = bot_raw['proto'].map({'tcp': 6, 'udp': 17, 'icmp': 1, 'arp': 2054, 'ipv6-icmp': 58}).fillna(0)

# Also load the legacy files
ciciot_train_legacy = pd.read_csv("data/raw/legacy_package/argus_coral_data/ciciot_train_features.csv")
ciciot_test_legacy = pd.read_csv("data/raw/legacy_package/argus_coral_data/ciciot_test_features.csv")
nfton_train_legacy = pd.read_csv("data/raw/legacy_package/argus_coral_data/nfton_train_features.csv")
nfton_test_legacy = pd.read_csv("data/raw/legacy_package/argus_coral_data/nfton_test_features.csv")

# For legacy, features are ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']
leg_cols = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']

def analyze_overlap(df1, df2, cols, name1, name2):
    h1 = hash_df(df1, cols)
    h2 = hash_df(df2, cols)
    set1 = set(h1)
    set2 = set(h2)
    intersection = set1.intersection(set2)
    overlap_count = h2.isin(intersection).sum()
    overlap_pct = (overlap_count / len(df2)) * 100 if len(df2) > 0 else 0
    print(f"[{name1} vs {name2}] Overlap: {overlap_count} / {len(df2)} ({overlap_pct:.2f}%)")
    return overlap_pct

print("\n--- Legacy Preprocessed Overlap ---")
analyze_overlap(ciciot_train_legacy, ciciot_test_legacy, leg_cols, "CIC-Train-Leg", "CIC-Test-Leg")
analyze_overlap(nfton_train_legacy, nfton_test_legacy, leg_cols, "NFT-Train-Leg", "NFT-Test-Leg")
analyze_overlap(ciciot_train_legacy, nfton_train_legacy, leg_cols, "CIC-Train-Leg", "NFT-Train-Leg")

print("\n--- RAW Canonical Overlap ---")
raw_cols = ['total_pkts', 'total_bytes', 'protocol']
analyze_overlap(ciciot_raw_canon, nfton_raw_canon, raw_cols, "CIC-Raw", "NFT-Raw")
analyze_overlap(ciciot_raw_canon, bot_raw_canon, raw_cols, "CIC-Raw", "BoT-Raw")
analyze_overlap(nfton_raw_canon, bot_raw_canon, raw_cols, "NFT-Raw", "BoT-Raw")

