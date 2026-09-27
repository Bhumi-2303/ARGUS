import pandas as pd
import glob
import os

bot_files = glob.glob("data/raw/bot_iot/raw/BoT-IoT dataset/csv/*.csv")
print("BoT-IoT files:", [os.path.basename(f) for f in bot_files])

benign_dfs = []
attack_dfs = []

for f in bot_files:
    for chunk in pd.read_csv(f, chunksize=1000000, low_memory=False):
        benign = chunk[chunk['attack'] == 0]
        attack = chunk[chunk['attack'] == 1]
        if len(benign) > 0:
            benign_dfs.append(benign)
        # We just need some attacks to compare, don't keep all 11M attacks in RAM
        if len(attack_dfs) < 10:
            attack_dfs.append(attack.head(10000))

benign_df = pd.concat(benign_dfs)
attack_df = pd.concat(attack_dfs)

print("\n--- BENIGN PROFILE ---")
print(f"Total benign: {len(benign_df)}")
print(f"Unique source addresses: {benign_df['saddr'].nunique()}")
print(f"Time span: {benign_df['stime'].min()} to {benign_df['stime'].max()} ({benign_df['stime'].max() - benign_df['stime'].min():.2f}s)")
print(f"Protocol mix:\n{benign_df['proto'].value_counts()}")

print("\n--- ATTACK PROFILE (sample) ---")
print(f"Unique source addresses: {attack_df['saddr'].nunique()}")
print(f"Protocol mix:\n{attack_df['proto'].value_counts()}")

