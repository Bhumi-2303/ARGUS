import pandas as pd
df = pd.read_csv("scratch/BoT-IoT dataset/csv/data_32.csv", nrows=1000000, low_memory=False)
v1_df = df[['pkts', 'bytes', 'proto']].copy()
print("V1 Unique Vectors (pkts, bytes, proto):", len(v1_df.drop_duplicates()))

# Let's do the class breakdown for V1
combined = v1_df.copy()
combined['is_attack'] = (df['attack'] == 1)

bucket_pivot = combined.pivot_table(index=['pkts', 'bytes', 'proto'], columns='is_attack', aggfunc='size', fill_value=0)
print(f"Bucket Pivot Shape: {bucket_pivot.shape}")
print(bucket_pivot.sort_values(by=True, ascending=False).head(20))

# What about the trivial classifier?
# A trivial classifier assigns the majority class of each bucket.
correct = 0
for _, row in bucket_pivot.iterrows():
    correct += max(row.get(False, 0), row.get(True, 0))
print(f"\nTrivial baseline accuracy: {correct / 1000000:.4f}")

# Cross-domain check: how many unique V1 vectors in CICIoT2023?
# The audit says:
# CICIoT2023 internal duplication: 86.2%
