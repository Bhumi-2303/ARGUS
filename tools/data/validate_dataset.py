import os
import pandas as pd
import hashlib
import datetime

DATA_DIR = "data/ton_iot"
VALIDATION_REPORT = os.path.join(DATA_DIR, "metadata", "validation_report.txt")
SOURCES_MD = os.path.join(DATA_DIR, "metadata", "SOURCES.md")

sources_info = {
    "Train_Test_datasets": {
        "source_url": "https://huggingface.co/datasets/m-hesam-moradian/ToN_IoT_Train_Test_datasets/resolve/main/Train_Test_datasets.zip",
        "category": "Train_Test_datasets",
        "mirror": "Hugging Face (m-hesam-moradian)"
    },
    "Processed_IoT_dataset": {
        "source_url": "https://www.kaggle.com/datasets/medworldmed/ton-iot-datasets",
        "category": "Processed datasets",
        "mirror": "Kaggle (medworldmed)"
    }
}

def sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

with open(VALIDATION_REPORT, "w") as vr, open(SOURCES_MD, "w") as smd:
    smd.write("# SOURCES MANIFEST\n\n")
    vr.write("TON_IOT DATASET VALIDATION REPORT\n")
    vr.write(f"Generated at: {datetime.datetime.now()}\n\n")
    
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".csv"):
                filepath = os.path.join(root, file)
                filename = os.path.basename(filepath)
                size = os.path.getsize(filepath)
                hash_val = sha256(filepath)
                
                # Determine source
                if "train_test" in filepath:
                    src_info = sources_info["Train_Test_datasets"]
                elif "processed" in filepath:
                    src_info = sources_info["Processed_IoT_dataset"]
                else:
                    continue
                
                # Validation
                try:
                    df = pd.read_csv(filepath, low_memory=False)
                    opened = "Yes"
                    num_rows = len(df)
                    num_cols = len(df.columns)
                    cols = df.columns.tolist()
                    label_cols = [c for c in cols if 'label' in c.lower() or 'type' in c.lower()]
                    time_cols = [c for c in cols if 'time' in c.lower() or 'date' in c.lower()]
                    missing = df.isnull().sum().sum()
                    
                    vr.write(f"File: {filename}\n")
                    vr.write(f"  Source: {src_info['mirror']} ({src_info['source_url']})\n")
                    vr.write(f"  Size: {size} bytes\n")
                    vr.write(f"  SHA256: {hash_val}\n")
                    vr.write(f"  Successfully Opened: {opened}\n")
                    vr.write(f"  Rows: {num_rows}\n")
                    vr.write(f"  Columns: {num_cols}\n")
                    vr.write(f"  Label columns: {label_cols}\n")
                    vr.write(f"  Timestamp columns: {time_cols}\n")
                    vr.write(f"  Missing values total: {missing}\n")
                    vr.write("-" * 40 + "\n")
                    
                except Exception as e:
                    opened = "No"
                    vr.write(f"File: {filename}\n")
                    vr.write(f"  Error: {e}\n")
                    vr.write("-" * 40 + "\n")
                    
                smd.write(f"## File: {filename}\n")
                smd.write(f"- **Category:** {src_info['category']}\n")
                smd.write(f"- **Local Path:** {filepath}\n")
                smd.write(f"- **Source URL:** {src_info['source_url']}\n")
                smd.write(f"- **File Size:** {size} bytes\n")
                smd.write(f"- **SHA256:** {hash_val}\n")
                smd.write(f"- **Status:** Downloaded\n")
                smd.write(f"- **Notes:** Mirrored source ({src_info['mirror']})\n\n")

print("Validation completed.")
