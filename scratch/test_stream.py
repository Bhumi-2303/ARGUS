import pandas as pd
df = pd.read_parquet("data/samples/nfton.parquet")
df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
print("Label sequence for first 80 flows:", df["label"].head(80).tolist())
