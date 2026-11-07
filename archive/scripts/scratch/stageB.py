import os
import shutil

moves = [
    ("DAY_1_REPORT.md", "reports/legacy/DAY_1_REPORT.md"),
    ("DAY_3_REPORT.md", "reports/legacy/DAY_3_REPORT.md"),
    ("DAY_5_REPORT.md", "reports/legacy/DAY_5_REPORT.md"),
    ("FUSION_PLAN.md", "reports/legacy/FUSION_PLAN.md"),
    ("SECURITY_HARDENING_REPORT.md", "reports/legacy/SECURITY_HARDENING_REPORT.md"),
    ("IDENTITY_RBAC_OIDC_READINESS_REPORT.md", "reports/legacy/IDENTITY_RBAC_OIDC_READINESS_REPORT.md"),
    ("OIDC_JWKS_FRONTEND_SECURITY_REPORT.md", "reports/legacy/OIDC_JWKS_FRONTEND_SECURITY_REPORT.md"),
]

# Create Skeleton
dirs_to_create = [
    "configs/datasets",
    "configs/features",
    "src/argus/adapters",
    "src/argus/features",
    "src/argus/models",
    "src/argus/alignment",
    "src/argus/eval",
    "src/argus/drift",
    "src/argus/serve",
    "tests",
    "docs",
    "experiments",
    "demo/backend",
    "reports/legacy",
    "results/metrics",
    "results/figures",
    "results/tables",
]

for d in dirs_to_create:
    os.makedirs(d, exist_ok=True)
    if d.startswith("src/argus/"):
        open(os.path.join(d, "__init__.py"), "a").close()

# Move the safe files
executed_moves = []
for src, dst in moves:
    if os.path.exists(src):
        os.rename(src, dst)
        executed_moves.append((src, dst))

# Add README to results
readme_content = """# Results

Pre-existing subfolders and files in this directory (e.g. `ARGUS_POSTER_DATA_PACKAGE`, `poster_results.csv`, etc.) are legacy paper inputs and must not be modified by new code.

New-run outputs should be strictly placed inside:
- `raw_predictions/`
- `metrics/`
- `figures/`
- `tables/`
"""
with open("results/README.md", "w") as f:
    f.write(readme_content)

# Update moves.csv and undo script
import csv
with open("docs/moves.csv", "a", newline="") as f:
    writer = csv.writer(f)
    for m in executed_moves:
        writer.writerow([m[0], m[1], "file", os.path.getsize(m[1])])

with open("docs/undo_restructure.sh", "a") as f:
    for m in executed_moves:
        f.write(f"mv '{m[1]}' '{m[0]}'\n")

print("Stage B executed.")
