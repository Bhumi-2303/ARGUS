"""ARGUS 4-Feature Extraction Module.

Calculates the 4 harmonized statistical features from network flow telemetry:
1. pkt_mean_to_max: Ratio of packet length mean to packet length max
2. log_pkt_mean: Natural log of packet length mean (+1)
3. log_pkt_max: Natural log of packet length max (+1)
4. tcp_flag_density: Sum of TCP flags present in flow
"""

import numpy as np
import pandas as pd


FEATURE_NAMES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]


def extract_four_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts the harmonized four statistical features from a network flow DataFrame.
    
    Args:
        df: Input DataFrame containing flow telemetry columns.
        
    Returns:
        DataFrame containing the four extracted features.
    """
    out = pd.DataFrame(index=df.index)
    
    # 1. pkt_mean_to_max
    if "pkt_mean_to_max" in df.columns:
        out["pkt_mean_to_max"] = df["pkt_mean_to_max"]
    elif "Pkt Len Max" in df.columns and "Pkt Len Mean" in df.columns:
        max_len = df["Pkt Len Max"].values
        mean_len = df["Pkt Len Mean"].values
        out["pkt_mean_to_max"] = np.where(max_len == 0, 0.0, mean_len / max_len)
    elif "Header_Length" in df.columns and "Duration" in df.columns:
        out["pkt_mean_to_max"] = np.where(df["Header_Length"] == 0, 0.0, df["Duration"] / df["Header_Length"])
    else:
        out["pkt_mean_to_max"] = 0.0

    # 2. tcp_flag_density
    if "tcp_flag_density" in df.columns:
        out["tcp_flag_density"] = df["tcp_flag_density"]
    else:
        flag_cols = [c for c in df.columns if "flag" in c.lower()]
        if flag_cols:
            out["tcp_flag_density"] = df[flag_cols].sum(axis=1)
        else:
            out["tcp_flag_density"] = 0.0

    # 3. log_pkt_mean
    if "log_pkt_mean" in df.columns:
        out["log_pkt_mean"] = df["log_pkt_mean"]
    elif "Pkt Len Mean" in df.columns:
        out["log_pkt_mean"] = np.log1p(np.clip(df["Pkt Len Mean"].values, a_min=0, a_max=None))
    elif "Rate" in df.columns:
        out["log_pkt_mean"] = np.log1p(np.clip(df["Rate"].values, a_min=0, a_max=None))
    else:
        out["log_pkt_mean"] = 0.0

    # 4. log_pkt_max
    if "log_pkt_max" in df.columns:
        out["log_pkt_max"] = df["log_pkt_max"]
    elif "Pkt Len Max" in df.columns:
        out["log_pkt_max"] = np.log1p(np.clip(df["Pkt Len Max"].values, a_min=0, a_max=None))
    elif "Size" in df.columns:
        out["log_pkt_max"] = np.log1p(np.clip(df["Size"].values, a_min=0, a_max=None))
    else:
        out["log_pkt_max"] = 0.0

    return out[FEATURE_NAMES]
