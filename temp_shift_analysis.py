import pandas as pd
import numpy as np

# Let's load the full native dataset if available.
# We don't have the original csv in memory easily, but the feature resolution script used it.
# Let's check `phase4_results/feature_resolution/feature_audit.csv`
audit = pd.read_csv("phase4_results/feature_resolution/feature_audit.csv")
print(audit)
