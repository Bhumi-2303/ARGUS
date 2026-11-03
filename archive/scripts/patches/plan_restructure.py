import os
import glob

plan = [
    ("| Current Path | Proposed Path | Reason |"),
    ("|---|---|---|")
]

def add_move(src, dst, reason):
    plan.append(f"| `{src}` | `{dst}` | {reason} |")

# 1. Data
for ds in ["cic_iot_2023", "nf_ton_iot", "ton_iot", "hai", "bot_iot"]:
    if os.path.exists(f"data/{ds}"):
        add_move(f"data/{ds}", f"data/raw/{ds}", "Raw data must be consolidated into data/raw/ (untouched)")
for doc in glob.glob("data/*.md") + glob.glob("data/*.json"):
    add_move(doc, f"reports/data_audits/{os.path.basename(doc)}", "Data audit reports move to reports/")

# 2. Results
for res in ["results", "phase3_results", "phase4_results", "ARGUS_Paper_Data", "ARGUS_POSTER_DATA_PACKAGE"]:
    if os.path.exists(res):
        add_move(res, f"results/legacy/{res}", "Existing results moved to legacy with MANIFEST.md")

# 3. Reports
for r in glob.glob("*REPORT.md") + ["RESULTS.md", "FUSION_PLAN.md", "RECIPE.md"]:
    if os.path.exists(r):
        add_move(r, f"reports/{r}", "Consolidate project reports")

# 4. Notebooks & Legacy Scripts
for n_dir in ["scratch", "training/notebooks"]:
    if os.path.exists(n_dir):
        add_move(n_dir, f"experiments/legacy/{os.path.basename(n_dir)}", "Notebooks and scratch go to experiments/legacy/")

# Move root standalone scripts to experiments/legacy/
root_scripts = [f for f in glob.glob("*.py") if f not in ["main.py", "plan_restructure.py"]]
for s in root_scripts:
    add_move(s, f"experiments/legacy/root_scripts/{s}", "Clean root directory, move legacy standalone scripts")

# 5. Configs
if os.path.exists("config"):
    add_move("config", "configs", "Rename config to configs and create subdirs")

# 6. Demo
if os.path.exists("frontend"):
    add_move("frontend", "demo/frontend", "Move frontend to demo/frontend")

# 7. Other folders
if os.path.exists("training"):
    add_move("training", "experiments/legacy/training", "Legacy training scripts")
if os.path.exists("verification"):
    add_move("verification", "experiments/legacy/verification", "Legacy verification scripts")
if os.path.exists("scripts"):
    add_move("scripts", "experiments/legacy/scripts", "Legacy scripts")

with open("DRY_RUN_PLAN.md", "w") as f:
    f.write("\n".join(plan))
print("Done")
