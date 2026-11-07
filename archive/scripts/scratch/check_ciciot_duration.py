import pandas as pd

df = pd.read_csv("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/Merged01.csv", nrows=100)
# 'Number' is likely total packets, 'Rate' is packets/sec.
# Let's see if Duration = Number / Rate
df['derived_dur'] = df['Number'] / (df['Rate'] + 1e-9)
print(df[['Number', 'Rate', 'derived_dur', 'IAT', 'Tot sum', 'Tot size']].head(10))
