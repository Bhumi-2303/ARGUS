import os
import pandas as pd
import numpy as np

os.makedirs("models/best_model", exist_ok=True)
with open("models/best_model/model.joblib", "w") as f:
    f.write("placeholder")

os.makedirs("data/samples", exist_ok=True)

df = pd.DataFrame({
    "pkt_mean_to_max": np.random.rand(10),
    "tcp_flag_density": np.random.rand(10),
    "log_pkt_mean": np.random.rand(10),
    "log_pkt_max": np.random.rand(10),
    "label": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    "domain": ["demo_sample"] * 10
})

df.to_parquet("data/samples/ciciot.parquet", index=False)
df.to_parquet("data/samples/nfton.parquet", index=False)
df.to_parquet("data/samples/iec104.parquet", index=False)
print("Created demo fixtures")
