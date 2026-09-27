import pandas as pd
import numpy as np

df = pd.read_csv("scratch/BoT-IoT dataset/csv/data_32.csv", nrows=1000000, low_memory=False)

# Compute the 4 features properly for BoT-IoT
df['mean_pkt'] = df['bytes'] / df['pkts']
df['log_pkt_mean'] = np.log1p(df['mean_pkt'])

# Assuming max pkt is mean pkt since it's a flood (or we don't have max pkt)
df['log_pkt_max'] = np.log1p(df['mean_pkt'])

# Ratio is 1.0
df['pkt_mean_to_max'] = 1.0

# TCP flags density: length of flgs string if tcp, else 0
df['tcp_flag_density'] = df.apply(lambda x: len(str(x['flgs'])) if x['proto'] == 'tcp' else 0, axis=1)

features = df[['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']]

unique_vectors = features.drop_duplicates()
print("ARGUS 4-feature Unique Vectors:", len(unique_vectors))

combined = features.copy()
combined['is_attack'] = (df['attack'] == 1)

bucket_pivot = combined.pivot_table(index=['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max'], columns='is_attack', aggfunc='size', fill_value=0)
print(f"Bucket Pivot Shape: {bucket_pivot.shape}")
print(bucket_pivot.sort_values(by=True, ascending=False).head(20))
