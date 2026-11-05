import pandas as pd

for f in ['ciciot', 'nfton']:
    print(f"--- {f.upper()} ---")
    df = pd.read_parquet(f"data/samples/{f}.parquet")
    for col in df.columns:
        print(f"{col}: {df[col].dtype}")
    print("\n")
