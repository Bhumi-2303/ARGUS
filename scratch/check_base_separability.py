import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

df_bot = pd.read_csv("scratch/BoT-IoT dataset/csv/data_32.csv", nrows=100000)
bot = pd.DataFrame({
    'pkt_mean_to_max': 1.0,
    'tcp_flag_density': 0,
    'log_pkt_mean': np.log1p(df_bot['bytes'] / np.maximum(df_bot['pkts'], 1)),
    'log_pkt_max': np.log1p(df_bot['bytes'] / np.maximum(df_bot['pkts'], 1))
})

df_cic = pd.read_csv("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/Merged01.csv", nrows=100000)
mean_pkt = df_cic['AVG']
max_pkt = df_cic['Max']
flag_cols = [c for c in df_cic.columns if "flag" in c.lower()]
cic = pd.DataFrame({
    'pkt_mean_to_max': np.where(max_pkt == 0, 0.0, mean_pkt / max_pkt),
    'tcp_flag_density': df_cic[flag_cols].sum(axis=1) if flag_cols else 0,
    'log_pkt_mean': np.log1p(mean_pkt),
    'log_pkt_max': np.log1p(max_pkt)
})

df_nf = pd.read_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet").head(100000)
mean_pkt_nf = (df_nf['IN_BYTES'] + df_nf['OUT_BYTES']) / np.maximum(df_nf['IN_PKTS'] + df_nf['OUT_PKTS'], 1)
nf = pd.DataFrame({
    'pkt_mean_to_max': 1.0,
    'tcp_flag_density': df_nf['TCP_FLAGS'].apply(lambda x: bin(x).count('1')),
    'log_pkt_mean': np.log1p(mean_pkt_nf),
    'log_pkt_max': np.log1p(mean_pkt_nf)
})

min_len = 50000
X = pd.concat([
    bot.sample(n=min_len, random_state=42),
    cic.sample(n=min_len, random_state=42),
    nf.sample(n=min_len, random_state=42)
])
y = np.array([0]*min_len + [1]*min_len + [2]*min_len)

clf = RandomForestClassifier(n_estimators=20, max_depth=5, random_state=42)
scores = cross_val_score(clf, X, y, cv=3)
print(f"Base 4-Feature Domain Separability Accuracy: {np.mean(scores):.4f}")
