import pandas as pd
nfton_path = "data/samples/nfton.parquet"
try:
    df_nf = pd.read_parquet(nfton_path).head(2)
    print("SUCCESS")
    print(df_nf)
except Exception as e:
    print("ERROR:", e)
