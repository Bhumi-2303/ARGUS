"""Generate stratified sample datasets for API streaming and onboarding demos.

Creates parquet files in data/samples/ with 4 harmonized features, label, and domain.
"""
import os
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split

HARMONIZED_FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]

DATA_SOURCES = {
    "ciciot": "ARGUS_Cross_Domain_Results/argus_coral_data/ciciot_test_features.csv",
    "nfton": "ARGUS_Cross_Domain_Results/argus_coral_data/nfton_test_features.csv",
    "iec104": "ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv"
}

def make_demo_samples(sample_size: int = 30000, seed: int = 42, output_dir: str = "data/samples"):
    os.makedirs(output_dir, exist_ok=True)
    
    for domain, file_path in DATA_SOURCES.items():
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} for domain '{domain}' not found.")
            continue
            
        print(f"Processing domain '{domain}' from {file_path}...")
        df = pd.read_csv(file_path)
        
        # Verify required columns exist
        req_cols = HARMONIZED_FEATURES + ["label"]
        for col in req_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column {col} in {file_path}")
                
        df_clean = df[req_cols].copy()
        df_clean["domain"] = domain
        
        n_rows = len(df_clean)
        if n_rows > sample_size:
            _, sample_df = train_test_split(
                df_clean,
                test_size=sample_size,
                random_state=seed,
                stratify=df_clean["label"]
            )
        else:
            sample_df = df_clean
            
        out_path = os.path.join(output_dir, f"{domain}.parquet")
        sample_df.to_parquet(out_path, index=False)
        print(f"Saved {len(sample_df)} rows for '{domain}' to {out_path} (Attack ratio: {sample_df['label'].mean():.4f})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create stratified demo samples for ARGUS domains.")
    parser.add_argument("--sample-size", type=int, default=30000, help="Number of rows per domain sample")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    parser.add_argument("--output-dir", type=str, default="data/samples", help="Output directory")
    args = parser.parse_args()
    
    make_demo_samples(sample_size=args.sample_size, seed=args.seed, output_dir=args.output_dir)
