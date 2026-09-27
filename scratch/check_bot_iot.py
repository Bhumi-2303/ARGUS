import pandas as pd
df = pd.read_csv("scratch/BoT-IoT dataset/csv/data_32.csv", nrows=100000)
print("Unique (pkts, bytes, dur):", df[['pkts', 'bytes', 'dur']].drop_duplicates().shape[0])
print("Unique (pkts, bytes):", df[['pkts', 'bytes']].drop_duplicates().shape[0])
