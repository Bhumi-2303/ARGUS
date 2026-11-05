import pandas as pd
import glob
import gc
import numpy as np

print("=== 2. TON_IoT ===")
df_ton = pd.read_csv("data/raw/ton_iot/train_test/Train_Test_Network_dataset/train_test_network.csv")
print("Label Counts:")
print(df_ton['label'].value_counts(dropna=False))
print("\nAttack Type Distribution:")
print(df_ton['type'].value_counts(dropna=False))
del df_ton
gc.collect()

print("\n=== 3. BoT-IoT ===")
bot_files = glob.glob("data/raw/bot_iot/raw/BoT-IoT dataset/csv/*.csv")
bot_cat = {}
bot_proto = {}
for f in bot_files:
    for chunk in pd.read_csv(f, usecols=['category', 'proto'], chunksize=500000, low_memory=False):
        for k, v in chunk['category'].value_counts(dropna=False).items():
            bot_cat[k] = bot_cat.get(k, 0) + v
        for k, v in chunk['proto'].value_counts(dropna=False).items():
            bot_proto[k] = bot_proto.get(k, 0) + v
print("Category Distribution:", bot_cat)
print("Protocol Mix:", bot_proto)
print("Benign Protocol Mix (Known from previous run): tcp: 232, udp: 213, arp: 17")

print("\n=== 4. CICIoT2023 Conflicting Labels ===")
ciciot_files = glob.glob("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/*.csv")
# To find rows with identical features but different labels:
# Group by hash of features, and count unique labels.
hash_to_labels = {}
conflict_count = 0
for f in ciciot_files:
    for chunk in pd.read_csv(f, chunksize=1000000, low_memory=False):
        features = chunk.drop(columns=['Label'])
        hashes = pd.util.hash_pandas_object(features, index=False).values
        labels = chunk['Label'].values
        for h, l in zip(hashes, labels):
            if h not in hash_to_labels:
                hash_to_labels[h] = set([l])
            else:
                hash_to_labels[h].add(l)

total_conflicts = 0
for h, lbl_set in hash_to_labels.items():
    if len(lbl_set) > 1:
        total_conflicts += 1

print(f"Number of unique feature vectors with multiple different labels: {total_conflicts}")

