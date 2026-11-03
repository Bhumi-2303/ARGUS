import pandas as pd
import numpy as np
import time

t0 = time.time()
df_ref = pd.read_parquet('data/samples/ciciot.parquet')
df_tgt = pd.read_parquet('data/samples/nfton.parquet')
print("Loaded in", time.time() - t0)

features = ['log_pkt_max', 'tcp_flag_density', 'log_pkt_mean', 'pkt_mean_to_max']

from scipy.stats import ks_2samp

results = []
for f in features:
    s_col = df_ref[f].values
    t_col = df_tgt[f].values
    
    ks_stat, ks_pval = ks_2samp(s_col, t_col)
    
    # PSI
    num_bins = 10
    bins = np.linspace(min(s_col.min(), t_col.min()), max(s_col.max(), t_col.max()), num_bins + 1)
    s_counts, _ = np.histogram(s_col, bins=bins)
    t_counts, _ = np.histogram(t_col, bins=bins)
    s_pct = np.where(s_counts == 0, 1e-4, s_counts) / len(s_col)
    t_pct = np.where(t_counts == 0, 1e-4, t_counts) / len(t_col)
    psi = np.sum((t_pct - s_pct) * np.log(t_pct / s_pct))
    
    results.append({
        'feature': f,
        'ks_statistic': float(ks_stat),
        'ks_pvalue': float(ks_pval),
        'psi_statistic': float(psi)
    })
    
print(results)
