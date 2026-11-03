import pandas as pd
import numpy as np
import glob
import os

files = glob.glob("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/*.csv")
total_expected_rows = 45019243 # From earlier run

# Allocate uint64 array for all hashes
hashes = np.empty(total_expected_rows + 100000, dtype=np.uint64)
idx = 0

col_mins = {}
col_maxs = {}
num_cols = []

first = True

for f in files:
    for chunk in pd.read_csv(f, chunksize=1000000, low_memory=False):
        if first:
            num_cols = chunk.select_dtypes(include=[np.number]).columns.tolist()
            for c in num_cols:
                col_mins[c] = float('inf')
                col_maxs[c] = float('-inf')
            first = False
            
        # Update min/max
        for c in num_cols:
            cmin = chunk[c].min(skipna=True)
            cmax = chunk[c].max(skipna=True)
            if not pd.isna(cmin) and cmin < col_mins[c]: col_mins[c] = cmin
            if not pd.isna(cmax) and cmax > col_maxs[c]: col_maxs[c] = cmax

        h = pd.util.hash_pandas_object(chunk, index=False).values.astype(np.uint64)
        n = len(h)
        hashes[idx:idx+n] = h
        idx += n

hashes = hashes[:idx]
hashes.sort()
unique_count = np.unique(hashes).size
dup_count = len(hashes) - unique_count
dup_rate = dup_count / len(hashes)

const_cols = [c for c in num_cols if col_mins[c] == col_maxs[c]]

print(f"Total Rows: {len(hashes)}")
print(f"Duplicates: {dup_count}")
print(f"Duplicate Rate: {dup_rate:.6f}")
print(f"Constant columns: {const_cols}")
