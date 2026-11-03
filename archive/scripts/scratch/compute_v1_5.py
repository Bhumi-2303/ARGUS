import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

def compute_v1_5(df, domain):
    if domain == "bot":
        # Raw fields: dur, pkts, bytes, flgs, proto
        duration = df['dur']
        total_pkts = df['pkts']
        total_bytes = df['bytes']
        
        mean_pkt = total_bytes / np.maximum(total_pkts, 1)
        pkt_mean_to_max = np.ones_like(mean_pkt)
        log_pkt_mean = np.log1p(mean_pkt)
        log_pkt_max = np.log1p(mean_pkt)
        
        # tcp_flag_density
        tcp_flag_density = df.apply(lambda x: len(str(x['flgs'])) if x['proto'] == 'tcp' else 0, axis=1)
        
    elif domain == "ciciot":
        # Raw fields: Number, Rate, Tot sum
        total_pkts = df['Number']
        rate = df['Rate']
        total_bytes = df['Tot sum']
        duration = total_pkts / np.maximum(rate, 1e-6)
        
        # We need the base 4 features. Since we don't have them easily, we can approximate or use existing rules.
        # Wait, extract_four_features supports CICIoT columns: Pkt Len Mean, etc.
        # CICIoT Merged01.csv has: Min, Max, AVG, Std. Assuming AVG is mean packet length and Max is max packet length.
        mean_pkt = df['AVG']
        max_pkt = df['Max']
        pkt_mean_to_max = np.where(max_pkt == 0, 0.0, mean_pkt / max_pkt)
        log_pkt_mean = np.log1p(mean_pkt)
        log_pkt_max = np.log1p(max_pkt)
        
        # flags
        flag_cols = [c for c in df.columns if "flag" in c.lower()]
        tcp_flag_density = df[flag_cols].sum(axis=1) if flag_cols else np.zeros(len(df))
        
    elif domain == "nfton":
        # Raw fields: FLOW_DURATION_MILLISECONDS, IN_PKTS, OUT_PKTS, IN_BYTES, OUT_BYTES
        duration = df['FLOW_DURATION_MILLISECONDS'] / 1000.0
        total_pkts = df['IN_PKTS'] + df['OUT_PKTS']
        total_bytes = df['IN_BYTES'] + df['OUT_BYTES']
        
        mean_pkt = total_bytes / np.maximum(total_pkts, 1)
        # NF-ToN doesn't have min/max packet length. In reality ARGUS used pre-extracted features.
        # Let's approximate pkt_mean_to_max = 1.0, log_pkt_mean = log1p(mean_pkt), log_pkt_max = log1p(mean_pkt)
        pkt_mean_to_max = np.ones_like(mean_pkt)
        log_pkt_mean = np.log1p(mean_pkt)
        log_pkt_max = np.log1p(mean_pkt)
        tcp_flag_density = df['TCP_FLAGS'].apply(lambda x: bin(x).count('1'))
        
    log_duration = np.log1p(duration)
    log_total_pkts = np.log1p(total_pkts)
    log_byte_rate = np.log1p(total_bytes / np.maximum(duration, 0.001))
    
    out = pd.DataFrame({
        'pkt_mean_to_max': pkt_mean_to_max,
        'tcp_flag_density': tcp_flag_density,
        'log_pkt_mean': log_pkt_mean,
        'log_pkt_max': log_pkt_max,
        'log_duration': log_duration,
        'log_total_pkts': log_total_pkts,
        'log_byte_rate': log_byte_rate
    })
    return out

# 1. BoT-IoT
df_bot = pd.read_csv("scratch/BoT-IoT dataset/csv/data_32.csv", nrows=1000000, low_memory=False)
v15_bot = compute_v1_5(df_bot, "bot")
bot_unique = v15_bot.drop_duplicates().shape[0]
print(f"BoT-IoT V1.5 Unique: {bot_unique} / {len(v15_bot)} ({bot_unique/len(v15_bot)*100:.4f}%)")

# Trivial baseline on BoT-IoT V1.5
combined_bot = v15_bot.copy()
combined_bot['is_attack'] = (df_bot['attack'] == 1)
pivot_bot = combined_bot.pivot_table(index=list(v15_bot.columns), columns='is_attack', aggfunc='size', fill_value=0)
correct = 0
for _, row in pivot_bot.iterrows():
    correct += max(row.get(False, 0), row.get(True, 0))
print(f"BoT-IoT Trivial Baseline Accuracy: {correct / len(v15_bot):.6f}")

# 2. CICIoT
df_cic = pd.read_csv("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/Merged01.csv")
v15_cic = compute_v1_5(df_cic, "ciciot")
cic_unique = v15_cic.drop_duplicates().shape[0]
print(f"CICIoT V1.5 Unique: {cic_unique} / {len(v15_cic)} ({cic_unique/len(v15_cic)*100:.4f}%)")

# 3. NF-ToN
df_nf = pd.read_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet")
v15_nf = compute_v1_5(df_nf, "nfton")
nf_unique = v15_nf.drop_duplicates().shape[0]
print(f"NF-ToN V1.5 Unique: {nf_unique} / {len(v15_nf)} ({nf_unique/len(v15_nf)*100:.4f}%)")

# Leakage Test: Domain Separability
# We will sample 50,000 from each to train a RF to predict the domain
min_len = 50000
X = pd.concat([
    v15_bot.sample(n=min_len, random_state=42),
    v15_cic.sample(n=min_len, random_state=42),
    v15_nf.sample(n=min_len, random_state=42)
])
y = np.array([0]*min_len + [1]*min_len + [2]*min_len)

clf = RandomForestClassifier(n_estimators=20, max_depth=5, random_state=42)
scores = cross_val_score(clf, X, y, cv=3)
print(f"Domain Separability Accuracy: {np.mean(scores):.4f}")

