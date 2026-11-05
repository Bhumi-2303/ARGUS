import pandas as pd
import glob
import json

ciciot_files = glob.glob("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/*.csv")
total_rows = 0
benign = 0
for f in ciciot_files:
    for chunk in pd.read_csv(f, usecols=['Label'], chunksize=500000, low_memory=False):
        total_rows += len(chunk)
        benign += (chunk['Label'] == 'Benign').sum()

print(f"Total: {total_rows}, Benign: {benign}, Attack: {total_rows - benign}")
