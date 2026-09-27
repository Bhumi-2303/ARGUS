import pandas as pd
import numpy as np
import hashlib
import json
import os

os.makedirs('data/reproduction', exist_ok=True)

# 1. Load the raw/processed files
print("Loading data...")
ciciot = pd.read_csv("data/raw/cic_iot_2023/processed/part-00000-363d1ba3-8ab5-4f96-bc25-4d5862db7cb9-c000.csv")
nfton = pd.read_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet")
bot = pd.read_csv("data/raw/bot_iot/raw/BoT-IoT dataset/csv/data_32.csv")

# 2. Extract canonical representation
# For protocol mapping, ensure strings are matched
protocol_map = {6: 'TCP', 17: 'UDP', 1: 'ICMP', 2054: 'ARP', 58: 'IPv6-ICMP', 0: 'Unknown'}

# CICIoT
df_cic = pd.DataFrame()
df_cic['total_pkts'] = ciciot['Number']
df_cic['total_bytes'] = ciciot['Tot sum']
# CICIoT protocol is mostly Protocol Type.
df_cic['protocol'] = ciciot['Protocol Type'].map(protocol_map).fillna('Unknown')
df_cic['label'] = (ciciot['label'] != 'BenignTraffic').astype(int)
df_cic['domain'] = 'CICIoT2023'

# NF-ToN
df_nft = pd.DataFrame()
df_nft['total_pkts'] = nfton['IN_PKTS'] + nfton['OUT_PKTS']
df_nft['total_bytes'] = nfton['IN_BYTES'] + nfton['OUT_BYTES']
df_nft['protocol'] = nfton['PROTOCOL'].map(protocol_map).fillna('Unknown')
df_nft['label'] = (nfton['Label'] == 1).astype(int)
df_nft['domain'] = 'NF-ToN-IoT'

# BoT-IoT
df_bot = pd.DataFrame()
df_bot['total_pkts'] = bot['pkts']
df_bot['total_bytes'] = bot['bytes']
# bot['proto'] is string like 'tcp', 'udp'
df_bot['protocol'] = bot['proto'].str.upper().fillna('Unknown')
df_bot['label'] = (bot['attack'] == 1).astype(int)
df_bot['domain'] = 'BoT-IoT'

# 3. Concatenate source domains and drop duplicates
df_source_raw = pd.concat([df_cic, df_nft], ignore_index=True)
df_target_raw = df_bot.copy()

print(f"Source size before deduplication: {len(df_source_raw)}")
df_source_dedup = df_source_raw.drop_duplicates(subset=['total_pkts', 'total_bytes', 'protocol'])
print(f"Source size after internal deduplication: {len(df_source_dedup)}")

print(f"Target size before deduplication: {len(df_target_raw)}")
df_target_dedup = df_target_raw.drop_duplicates(subset=['total_pkts', 'total_bytes', 'protocol'])
print(f"Target size after internal deduplication: {len(df_target_dedup)}")

# 4. Remove cross-domain leakage (remove ANY target feature vectors from source)
# Hash rows
def get_hashes(df):
    return df[['total_pkts', 'total_bytes', 'protocol']].astype(str).apply(lambda r: hashlib.md5(''.join(r).encode()).hexdigest(), axis=1)

src_hashes = get_hashes(df_source_dedup)
tgt_hashes = get_hashes(df_target_dedup)

leakage_hashes = set(src_hashes).intersection(set(tgt_hashes))
print(f"Found {len(leakage_hashes)} unique colliding feature vectors between source and target.")

# Filter source to remove target leakage
mask = ~src_hashes.isin(leakage_hashes)
df_source_clean = df_source_dedup[mask].copy()
print(f"Source size after removing target leakage: {len(df_source_clean)}")

# 5. Deterministic Train/Val split of Source (80/20)
# Shuffle with seed 42
df_source_clean = df_source_clean.sample(frac=1, random_state=42).reset_index(drop=True)
split_idx = int(len(df_source_clean) * 0.8)
df_train = df_source_clean.iloc[:split_idx]
df_val = df_source_clean.iloc[split_idx:]

df_test = df_target_dedup.copy() # Unseen Target

# Save datasets to disk to ensure reproducibility
df_train.to_csv("data/reproduction/source_train.csv", index=False)
df_val.to_csv("data/reproduction/source_val.csv", index=False)
df_test.to_csv("data/reproduction/target_test.csv", index=False)

manifest = {
    "protocol": "Strict Zero-Shot Leakage-Controlled Protocol",
    "domains": {
        "source": ["CICIoT2023", "NF-ToN-IoT"],
        "target": ["BoT-IoT"]
    },
    "canonical_features": ['total_pkts', 'total_bytes', 'protocol'],
    "source_internal_duplicates_removed": len(df_source_raw) - len(df_source_dedup),
    "target_internal_duplicates_removed": len(df_target_raw) - len(df_target_dedup),
    "cross_domain_collisons_removed_from_source": len(df_source_dedup) - len(df_source_clean),
    "final_train_size": len(df_train),
    "final_val_size": len(df_val),
    "final_test_size": len(df_test)
}

with open("data/reproduction/CLEAN_DATASET_MANIFEST.json", "w") as f:
    json.dump(manifest, f, indent=2)

with open("data/reproduction/CLEAN_DATASET_PROTOCOL.md", "w") as f:
    f.write("# Clean Dataset Construction Protocol\n")
    f.write("1. Data was loaded from raw/processed files.\n")
    f.write("2. Features mapped to Canonical Schema: total_pkts, total_bytes, protocol.\n")
    f.write("3. Internal duplicates strictly dropped from both Source and Target.\n")
    f.write("4. Target (BoT-IoT) feature vectors were hashed, and ANY exact match found in Source (CICIoT/NF-ToN) was REMOVED from the source training set to guarantee 0% overlap.\n")
    f.write("5. Source was split 80/20 (Train/Val) deterministically (seed 42).\n")
    f.write("6. BoT-IoT was completely frozen and isolated as Test.\n")
    
print("Clean dataset creation complete.")
