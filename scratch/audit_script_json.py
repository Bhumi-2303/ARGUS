import os
import json
import glob

# find timestamp
md_files = glob.glob('data/ARGUS_FULL_REPOSITORY_AUDIT_*.md')
if not md_files:
    TIMESTAMP = "now"
else:
    TIMESTAMP = md_files[0].split('_')[-2] + '_' + md_files[0].split('_')[-1].replace('.md', '')

repo_audit = {
    "project": "ARGUS",
    "status": "Scaffolding/Broken",
    "major_issues": ["Data Leakage", "Fabricated Results", "Disconnected Architecture"]
}

exp_registry = {
    "experiments": [
        {
            "name": "Source-only XGBoost",
            "status": "UNREPRODUCIBLE",
            "reproducibility": "NO"
        },
        {
            "name": "Global CORAL",
            "status": "NOT TRACEABLE",
            "reproducibility": "NO"
        },
        {
            "name": "Clean Class-Aware CORAL",
            "status": "NOT TRACEABLE",
            "reproducibility": "NO"
        },
        {
            "name": "DANN",
            "status": "BROKEN",
            "reproducibility": "NO"
        }
    ]
}

with open(f"data/ARGUS_FULL_REPOSITORY_AUDIT_{TIMESTAMP}.json", "w") as f:
    json.dump(repo_audit, f, indent=2)

with open(f"data/ARGUS_EXPERIMENT_REGISTRY_{TIMESTAMP}.json", "w") as f:
    json.dump(exp_registry, f, indent=2)

print("JSON files generated.")
