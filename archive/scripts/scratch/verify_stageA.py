import os
import hashlib
import json

data_dirs = ["cic_iot_2023", "nf_ton_iot", "ton_iot", "hai", "bot_iot"]
with open("docs/data_metrics_baseline.json") as f:
    baseline = json.load(f)

for ds in data_dirs:
    ds_path = os.path.join("data", "raw", ds)
    if not os.path.exists(ds_path):
        continue
    file_count = 0
    total_bytes = 0
    hashes = {}
    for root, dirs, files in os.walk(ds_path):
        for f in files:
            file_count += 1
            f_path = os.path.join(root, f)
            try:
                size = os.path.getsize(f_path)
                total_bytes += size
                if size < 100 * 1024 * 1024:
                    with open(f_path, "rb") as file_obj:
                        hashes[f_path] = hashlib.sha256(file_obj.read()).hexdigest()
            except Exception:
                pass
    
    b = baseline.get(ds, {})
    if file_count != b.get("file_count"):
        print(f"FAILED {ds} COUNT: {file_count} != {b.get('file_count')}")
    elif total_bytes != b.get("total_bytes"):
        print(f"FAILED {ds} BYTES: {total_bytes} != {b.get('total_bytes')}")
    else:
        # Check hashes
        b_hashes = b.get("hashes", {})
        match = True
        for k, v in b_hashes.items():
            # new key is data/raw/... old key was data/...
            new_k = k.replace(f"data/{ds}", f"data/raw/{ds}", 1)
            if hashes.get(new_k) != v:
                print(f"FAILED HASH for {new_k}")
                match = False
        if match:
            print(f"VERIFIED {ds}: {file_count} files, {total_bytes} bytes, hashes MATCH.")
