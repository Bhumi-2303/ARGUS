import pandas as pd
import json

ciciot = pd.read_csv("data/raw/cic_iot_2023/processed/part-00000-363d1ba3-8ab5-4f96-bc25-4d5862db7cb9-c000.csv", nrows=5)
nfton = pd.read_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet").head(5)
bot = pd.read_csv("data/raw/bot_iot/raw/BoT-IoT dataset/csv/data_32.csv", nrows=5)

def get_schema(df):
    return {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}

schemas = {
    "CICIoT2023": get_schema(ciciot),
    "NF-ToN-IoT": get_schema(nfton),
    "BoT-IoT": get_schema(bot)
}

print(json.dumps(schemas, indent=2))
