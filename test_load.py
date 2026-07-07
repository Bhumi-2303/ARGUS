import pandas as pd
import numpy as np
import pyarrow.dataset as ds
from pathlib import Path
import time
import sys

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]):
            c_min, c_max = df[col].min(), df[col].max()
            if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                df[col] = df[col].astype(np.int8)
            elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                df[col] = df[col].astype(np.int16)
            elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                df[col] = df[col].astype(np.int32)
        elif pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype(np.float32)
    return df

print("Loading...")
sys.stdout.flush()
file = "training/data/raw/nftoniotv2/NF-ToN-IoT-V2.parquet"
dataset = ds.dataset(file, format="parquet")
chunks = []
for batch in dataset.to_batches(batch_size=500000):
    chunk = batch.to_pandas()
    chunk = optimize_dtypes(chunk)
    chunks.append(chunk)

df = pd.concat(chunks, ignore_index=True)
print(f"Shape: {df.shape}")
sys.stdout.flush()

print("Generating EDA...")
sys.stdout.flush()
try:
    numeric_df = df.select_dtypes(include=[np.number])
    stats = numeric_df.describe().T
    print("Describe success!")
except Exception as e:
    print(f"Describe failed: {e}")
sys.stdout.flush()

print("Scaling...")
sys.stdout.flush()
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
try:
    scaler.fit_transform(numeric_df)
    print("Scale success!")
except Exception as e:
    print(f"Scale failed: {e}")

