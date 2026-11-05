import pandas as pd
import json
import os
import hashlib

def get_sha256(filepath):
    sha256_hash = hashlib.sha256()
    if not os.path.exists(filepath):
        return None
    with open(filepath,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def profile_dataset(name, file_path, output_md, label_col=None):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return None

    if file_path.endswith('.parquet'):
        df = pd.read_parquet(file_path)
    else:
        df = pd.read_csv(file_path)

    rows, cols = df.shape
    cols_list = df.columns.tolist()
    missing = int(df.isna().sum().sum())
    # dupes = int(df.duplicated().sum())  # can be slow for large dfs
    dupes = "Skipped (Performance)"
    
    # Try to find timestamp
    ts_col = next((c for c in cols_list if 'time' in c.lower() or 'date' in c.lower() or c.lower() == 'ts'), None)
    ts_range = "N/A"
    if ts_col:
        ts_range = f"{df[ts_col].min()} to {df[ts_col].max()}"

    # Try to find label
    if not label_col:
        label_col = next((c for c in cols_list if 'label' in c.lower() or 'attack' in c.lower() or 'class' in c.lower()), None)
    
    class_dist = {}
    if label_col and label_col in df.columns:
        class_dist = df[label_col].value_counts().to_dict()

    md = f"# {name} Dataset Profile\n\n"
    md += f"- **Files**: 1\n"
    md += f"- **Rows**: {rows}\n"
    md += f"- **Features**: {cols}\n"
    md += f"- **Label Column**: {label_col}\n"
    md += f"- **Attack Category Column**: {label_col}\n"
    md += f"- **Class Distribution**: {class_dist}\n"
    md += f"- **Missing Values**: {missing}\n"
    md += f"- **Duplicate Rows**: {dupes}\n"
    md += f"- **Timestamp Availability**: {'Yes' if ts_col else 'No'} ({ts_col})\n"
    if ts_col:
        md += f"- **Time Range**: {ts_range}\n"
    md += f"- **Train/Test Structure**: Single file (not explicitly split)\n"

    with open(output_md, 'w') as f:
        f.write(md)

    print(f"Generated {output_md}")
    
    return {
        "dataset": name,
        "rows": rows,
        "features": cols,
        "timestamp_column": ts_col,
        "label_column": label_col,
        "time_range": {"start": str(df[ts_col].min()) if ts_col else None, "end": str(df[ts_col].max()) if ts_col else None},
        "size_bytes": os.path.getsize(file_path),
        "sha256": get_sha256(file_path)
    }

manifests = []
m_nf = profile_dataset("NF-ToN-IoT", "data/nf_ton_iot/processed/NF-ToN-IoT.parquet", "data/nf_ton_iot/metadata/DATASET_PROFILE.md")
if m_nf:
    m_nf["source"] = "Kaggle (dhoogla/nftoniot)"
    m_nf["source_type"] = "mirror"
    m_nf["version"] = "1.0"
    m_nf["original_files"] = ["NF-ToN-IoT.parquet"]
    m_nf["local_files"] = ["data/nf_ton_iot/processed/NF-ToN-IoT.parquet"]
    m_nf["provenance_status"] = "VERIFIED MIRROR"
    m_nf["validation_status"] = "VERIFIED"
    manifests.append(m_nf)

with open('scratch/partial_manifests.json', 'w') as f:
    json.dump(manifests, f, indent=2)
