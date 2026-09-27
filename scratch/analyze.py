import sys
sys.path.insert(0, 'src')
import pandas as pd
from argus.features.extractor import extract_four_features

df = pd.read_csv("scratch/BoT-IoT dataset/csv/data_32.csv", nrows=1000000)
print(f"Loaded BoT-IoT: {df.shape}")
print("Columns:", list(df.columns))

# Let's apply extract_four_features directly.
features_df = extract_four_features(df)
print("\nExtracted features summary:")
print(features_df.describe())

# Count unique vectors
unique_count = features_df.drop_duplicates().shape[0]
print(f"\nUnique vectors: {unique_count}")

# Let's break it down by class
df['is_attack'] = (df['attack'] == 1)
combined = features_df.copy()
combined['is_attack'] = df['is_attack']

unique_vectors_by_class = combined.drop_duplicates()
print(f"Unique vectors with class: {unique_vectors_by_class.shape[0]}")

bucket_counts = combined.groupby(list(features_df.columns)).size().reset_index(name='count')
print("\nBucket counts (top 10):")
print(bucket_counts.sort_values('count', ascending=False).head(10))

# Break down the 82 vectors by class: how many of the 82 are benign vs attack
# Let's just group by the features AND class to get the buckets
bucket_class_counts = combined.groupby(list(features_df.columns) + ['is_attack']).size().reset_index(name='count')
print("\nBucket class breakdown (top 10):")
print(bucket_class_counts.sort_values('count', ascending=False).head(10))

# Let's see how many buckets have ONLY attack, ONLY benign, or MIXED
bucket_pivot = combined.pivot_table(index=list(features_df.columns), columns='is_attack', aggfunc='size', fill_value=0)
print(f"\nBucket Pivot Shape: {bucket_pivot.shape}")
print(bucket_pivot)

