import os
import shutil
import csv
import json

data_dirs = ["cic_iot_2023", "nf_ton_iot", "ton_iot", "hai", "bot_iot"]

moves = []
for ds in data_dirs:
    src = os.path.join("data", ds)
    dst = os.path.join("data", "raw", ds)
    if os.path.exists(src):
        # Calculate size before move
        size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(src) for filename in filenames)
        moves.append((src, dst, "dir", size))

# Create dirs
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/interim", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("results/raw_predictions", exist_ok=True)

# Append to moves.csv
with open("docs/moves.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["old_path", "new_path", "type", "size"])
    for m in moves:
        writer.writerow(m)

# Execute moves
for src, dst, t, s in moves:
    print(f"Moving {src} to {dst}")
    os.rename(src, dst)

# Append to undo
with open("docs/undo_restructure.sh", "w") as f:
    f.write("#!/bin/bash\n")
    for m in moves:
        f.write(f"mv '{m[1]}' '{m[0]}'\n")

print("Stage A executed.")
