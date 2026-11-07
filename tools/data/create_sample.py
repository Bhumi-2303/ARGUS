import pandas as pd
import numpy as np

# Create a fake dataset with 4 features (the prompt says "With only four features, note that it is coarse.")
data = {
    "f1": np.random.rand(100),
    "f2": np.random.rand(100),
    "f3": np.random.rand(100),
    "f4": np.random.rand(100),
}
df = pd.DataFrame(data)
import os
os.makedirs("tests/data", exist_ok=True)
df.to_parquet("tests/data/1_percent_sample.parquet")
