import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

def extract_features(df, domain):
    if domain == "ciciot":
        total_pkts = df['Number']
        rate = df['Rate']
        total_bytes = df['Tot sum']
        duration = total_pkts / np.maximum(rate, 1e-6)
        
        mean_pkt = df['AVG']
        max_pkt = df['Max']
        pkt_mean_to_max = np.where(max_pkt == 0, 0.0, mean_pkt / max_pkt)
        log_pkt_mean = np.log1p(mean_pkt)
        log_pkt_max = np.log1p(max_pkt)
        
        flag_cols = [c for c in df.columns if "flag" in c.lower()]
        tcp_flag_density = df[flag_cols].sum(axis=1) if flag_cols else np.zeros(len(df))
        
    elif domain == "nfton":
        duration = df['FLOW_DURATION_MILLISECONDS'] / 1000.0
        total_pkts = df['IN_PKTS'] + df['OUT_PKTS']
        total_bytes = df['IN_BYTES'] + df['OUT_BYTES']
        
        mean_pkt = total_bytes / np.maximum(total_pkts, 1)
        pkt_mean_to_max = np.ones_like(mean_pkt)
        log_pkt_mean = np.log1p(mean_pkt)
        log_pkt_max = np.log1p(mean_pkt)
        tcp_flag_density = df['TCP_FLAGS'].apply(lambda x: bin(x).count('1'))

    log_duration = np.log1p(duration)
    log_total_pkts = np.log1p(total_pkts)
    log_byte_rate = np.log1p(total_bytes / np.maximum(duration, 0.001))
    
    return pd.DataFrame({
        'pkt_mean_to_max': pkt_mean_to_max,
        'tcp_flag_density': tcp_flag_density,
        'log_pkt_mean': log_pkt_mean,
        'log_pkt_max': log_pkt_max,
        'log_duration': log_duration,
        'log_total_pkts': log_total_pkts,
        'log_byte_rate': log_byte_rate
    })

# Load Data
df_cic = pd.read_csv("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/Merged01.csv")
df_nf = pd.read_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet")

v15_cic = extract_features(df_cic, "ciciot")
v15_nf = extract_features(df_nf, "nfton")

# Sample
min_len = 50000
cic_sample = v15_cic.sample(n=min_len, random_state=42)
nf_sample = v15_nf.sample(n=min_len, random_state=42)

# Features
base_cols = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']
v15_cols = base_cols + ['log_duration', 'log_total_pkts', 'log_byte_rate']

X_base = pd.concat([cic_sample[base_cols], nf_sample[base_cols]])
X_v15 = pd.concat([cic_sample[v15_cols], nf_sample[v15_cols]])
y = np.array([0]*min_len + [1]*min_len)

clf = RandomForestClassifier(n_estimators=20, max_depth=5, random_state=42)

# Base 4-Feature
scores_base = cross_val_score(clf, X_base, y, cv=3)
print(f"4-Feature Pairwise (CICIoT vs NF-ToN): {np.mean(scores_base):.4f}")

# V1.5 7-Feature
scores_v15 = cross_val_score(clf, X_v15, y, cv=3)
print(f"V1.5 Pairwise (CICIoT vs NF-ToN): {np.mean(scores_v15):.4f}")

# Feature Importances
clf.fit(X_v15, y)
importances = clf.feature_importances_
for name, imp in zip(v15_cols, importances):
    print(f"Importance of {name}: {imp:.4f}")

