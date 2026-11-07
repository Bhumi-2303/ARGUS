import os
import hashlib
import json
import csv

data_dirs = ["cic_iot_2023", "nf_ton_iot", "ton_iot", "hai", "bot_iot"]
results = {}

for ds in data_dirs:
    ds_path = os.path.join("data", ds)
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
    results[ds] = {
        "file_count": file_count,
        "total_bytes": total_bytes,
        "hashes": hashes
    }

with open("docs/data_metrics_baseline.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps({k: {"count": v["file_count"], "bytes": v["total_bytes"]} for k,v in results.items()}, indent=2))
