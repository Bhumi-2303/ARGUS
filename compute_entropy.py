import pandas as pd
import numpy as np

# Load the D3 (IEC104) test features in ARGUS-4 representation
df = pd.read_csv('ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv')
features = ['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']
X = df[features]

# Number of unique tuples
unique_tuples = X.drop_duplicates()
print(f"Total flows: {len(df)}")
print(f"Unique feature tuples: {len(unique_tuples)}")

# Entropy computation
# Count frequencies of each unique tuple
tuple_counts = X.groupby(features).size()
probabilities = tuple_counts / len(df)
entropy = -np.sum(probabilities * np.log2(probabilities))
print(f"Entropy: {entropy} bits")

# Theoretical max entropy for 714,453 unique rows would be log2(714453) = 19.44 bits.
# If original data had 17.84 bits, the representation dropped it to 5.84 bits.

with open('entropy_results.txt', 'w') as f:
    f.write(f"Total flows: {len(df)}\n")
    f.write(f"Unique feature tuples: {len(unique_tuples)}\n")
    f.write(f"Entropy: {entropy:.4f} bits\n")

