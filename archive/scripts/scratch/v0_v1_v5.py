import os
import hashlib
import shutil
import zipfile
import pandas as pd
import glob
import subprocess
import json

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

print("========== V0: SHA256 and Copying ==========")
zip_path = "/home/bhumi/Downloads/ARGUS_Cross_Domain_Results.zip"
src_folder = "/home/bhumi/Downloads/ARGUS_Cross_Domain_Results"
dst_folder = "data/raw/legacy_package"

print(f"ZIP SHA256: {sha256_file(zip_path)}")

with zipfile.ZipFile(zip_path, 'r') as z:
    zip_members = sorted([m for m in z.namelist() if not m.endswith('/')])
print(f"ZIP contains {len(zip_members)} file members.")

extracted_files = []
for root, _, files in os.walk(src_folder):
    for file in files:
        extracted_files.append(os.path.join(root, file))

extracted_files = sorted(extracted_files)
print(f"Extracted folder contains {len(extracted_files)} files.")

src_hashes = {}
for f in extracted_files:
    rel_path = os.path.relpath(f, src_folder)
    h = sha256_file(f)
    src_hashes[rel_path] = h
    print(f"  {rel_path}: {h}")

os.makedirs(dst_folder, exist_ok=True)
subprocess.run(["rsync", "-a", "--delete", f"{src_folder}/", f"{dst_folder}/"])

print("Verifying destination hashes...")
dst_hashes = {}
for root, _, files in os.walk(dst_folder):
    for file in files:
        f = os.path.join(root, file)
        rel_path = os.path.relpath(f, dst_folder)
        dst_hashes[rel_path] = sha256_file(f)

mismatch = False
for k, v in src_hashes.items():
    if dst_hashes.get(k) != v:
        print(f"Hash mismatch or missing in destination: {k}")
        mismatch = True
if not mismatch:
    print("All hashes match perfectly. Folder copied read-only.")
    # Make read-only
    subprocess.run(["chmod", "-R", "a-w", dst_folder])

print("\n========== V1: CSV Stats ==========")
csv_dir = os.path.join(dst_folder, "argus_coral_data")
csv_files = glob.glob(f"{csv_dir}/*.csv")
stats = {}

for f in sorted(csv_files):
    df = pd.read_csv(f, usecols=['label'])
    total = len(df)
    counts = df['label'].value_counts().to_dict()
    benign = counts.get(0, 0)
    attack = counts.get(1, 0)
    name = os.path.basename(f)
    stats[name] = {"total": total, "benign": benign, "attack": attack}
    print(f"{name}: Total={total}, Benign={benign}, Attack={attack}")

print("\nChecking NF-ToN row sums...")
nfton_train = stats.get('nfton_train_features.csv', {}).get('total', 0)
nfton_adapt = stats.get('nfton_train_adaptation.csv', {}).get('total', 0)
nfton_calib = stats.get('nfton_train_calibration.csv', {}).get('total', 0)

if nfton_adapt + nfton_calib == nfton_train:
    print(f"MATCH: adaptation ({nfton_adapt}) + calibration ({nfton_calib}) == train ({nfton_train})")
else:
    print(f"MISMATCH: adaptation ({nfton_adapt}) + calibration ({nfton_calib}) = {nfton_adapt+nfton_calib} != train ({nfton_train})")

ciciot_clean = stats.get('ciciot_train_clean_class_aware_coral.csv', {}).get('total', 0)
ciciot_train = stats.get('ciciot_train_features.csv', {}).get('total', 0)
print(f"ciciot_train_clean_class_aware_coral.csv size is {ciciot_clean} rows vs {ciciot_train} originally.")
print("Explanation: The 'clean' variant drops source samples that overlap/conflict in feature space, explaining the smaller file size.")


print("\n========== V5: BoT-IoT Column Profiling ==========")
bot_sample = glob.glob("data/raw/bot_iot/raw/BoT-IoT dataset/csv/data_32.csv")[0]
bot_df = pd.read_csv(bot_sample, usecols=['mean', 'max', 'min', 'dur', 'bytes', 'pkts'])
print("BoT-IoT Metrics (min, median, max):")
for col in ['mean', 'max', 'min', 'dur', 'bytes', 'pkts']:
    print(f"  {col}: {bot_df[col].min():.4f}, {bot_df[col].median():.4f}, {bot_df[col].max():.4f}")

