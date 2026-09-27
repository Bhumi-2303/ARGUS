import pandas as pd
import glob
import time
import os

start_time = time.time()
bot_files = glob.glob("data/raw/bot_iot/raw/BoT-IoT dataset/csv/*.csv")

category_counts = {}
proto_counts = {}
benign_proto_counts = {}
files_processed = 0
partial = False

for f in bot_files:
    if time.time() - start_time > 250:
        partial = True
        break
    
    # Use pyarrow engine if possible, but fallback to c if not supported chunks
    df = pd.read_csv(f, usecols=['attack', 'category', 'proto'], engine='pyarrow')
    
    cat = df['category'].value_counts(dropna=False).to_dict()
    for k, v in cat.items():
        category_counts[k] = category_counts.get(k, 0) + v
        
    prot = df['proto'].value_counts(dropna=False).to_dict()
    for k, v in prot.items():
        proto_counts[k] = proto_counts.get(k, 0) + v
        
    benign_df = df[df['attack'] == 0]
    b_prot = benign_df['proto'].value_counts(dropna=False).to_dict()
    for k, v in b_prot.items():
        benign_proto_counts[k] = benign_proto_counts.get(k, 0) + v
        
    files_processed += 1
    print(f"Processed {files_processed}/{len(bot_files)} files...")

report = ["\n## C. BoT-IoT Distribution"]
if partial:
    report.append("**[REQUIRES VERIFICATION] - Partial run due to timeout. Not all files were processed.**")

report.append(f"**Files Processed:** {files_processed} / {len(bot_files)}")

report.append("\n**Attack-Category Distribution:**")
for k, v in category_counts.items():
    report.append(f"- {k}: {v:,}")

report.append("\n**Protocol Mix (All Rows):**")
for k, v in proto_counts.items():
    report.append(f"- {k}: {v:,}")

report.append("\n**Protocol Mix (Benign Rows):**")
for k, v in benign_proto_counts.items():
    report.append(f"- {k}: {v:,}")

with open("reports/DG_DATA_AUDIT_addendum2.md", "a") as f:
    f.write("\n".join(report) + "\n")
print("Step C complete")
