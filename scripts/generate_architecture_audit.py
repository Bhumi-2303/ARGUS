#!/usr/bin/env python3
"""
Generate comprehensive file inventory and architectural audit metadata for ARGUS repository.
Outputs:
  - audit/architecture/repository_inventory.json
"""

import os
import sys
import json
import time
from pathlib import Path

REPO_ROOT = Path(".").resolve()
OUTPUT_DIR = REPO_ROOT / "audit" / "architecture"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Ignored directories for inventory file walk (virtualenv and VCS metadata)
IGNORED_DIRS = {".git", ".venv", ".pytest_cache", ".ruff_cache", "__pycache__", "node_modules"}

def classify_file(rel_path: str) -> tuple[str, str, bool, str, str]:
    """
    Returns (category, status, has_research_evidence, recommended_action, target_location)
    """
    p = rel_path.replace("\\", "/")
    parts = p.split("/")
    filename = parts[-1]
    ext = os.path.splitext(filename)[1].lower()

    # Default values
    category = "miscellaneous"
    status = "active"
    has_research_evidence = False
    action = "keep_in_place"
    target = p

    # 1. Core Source Code
    if p.startswith("src/argus/"):
        category = "source_code"
        status = "active"
        if "tests" in parts:
            category = "test"
        action = "keep_in_place"
        target = p

    # 2. Frontend Application
    elif p.startswith("web/"):
        category = "frontend"
        status = "active"
        action = "keep_in_place"
        target = p

    # 3. Tests
    elif p.startswith("tests/"):
        category = "test"
        status = "active"
        action = "keep_in_place"
        target = p

    # 4. Configurations
    elif p.startswith("configs/") or p.startswith("config/"):
        category = "config"
        status = "active" if p.startswith("configs/") else "obsolete"
        action = "keep_in_place" if p.startswith("configs/") else "archive"
        target = p if p.startswith("configs/") else f"archive/configs/{p}"

    # 5. Production Models & Artifacts
    elif p.startswith("artifacts/"):
        category = "artifacts"
        if p.startswith("artifacts/models/"):
            category = "model"
        status = "active"
        has_research_evidence = True
        action = "keep_in_place"
        target = p

    elif p.startswith("models/"):
        category = "model"
        status = "redundant"
        action = "consolidate"
        target = "artifacts/models/"

    # 6. Data & Datasets
    elif p.startswith("data/"):
        category = "data"
        has_research_evidence = True
        if filename.startswith("ARGUS_") and (filename.endswith(".md") or filename.endswith(".json")):
            category = "audit_report"
            status = "historical"
            action = "relocate"
            target = f"audit/historical/{filename}"
        else:
            status = "active"
            action = "keep_in_place"
            target = p

    elif p.startswith("dataset/"):
        category = "data"
        status = "active"
        has_research_evidence = True
        action = "keep_in_place"
        target = p

    # 7. Research Paper & Manuscripts
    elif p.startswith("paper/"):
        category = "research_paper"
        status = "active"
        has_research_evidence = True
        action = "keep_in_place"
        target = p

    # 8. Research Results & Verified Deliverables
    elif p.startswith("results/"):
        category = "results_data"
        has_research_evidence = True
        if p.startswith("results/experiments/"):
            category = "research_experiment"
        status = "active"
        action = "keep_in_place"
        target = p

    # 9. Experiments (Historical & Modular)
    elif p.startswith("experiments/"):
        category = "research_experiment"
        status = "historical"
        has_research_evidence = True
        action = "keep_in_place"
        target = p

    elif p.startswith("experiment_execution/"):
        category = "research_experiment"
        status = "redundant"
        has_research_evidence = True
        action = "archive"
        target = f"archive/{p}"

    # 10. Audit Documents
    elif p.startswith("audit/"):
        category = "audit_report"
        status = "active"
        has_research_evidence = True
        action = "keep_in_place"
        target = p

    elif p.startswith("ARGUS_INDEPENDENT_AUDIT/"):
        category = "audit_report"
        status = "active"
        has_research_evidence = True
        action = "relocate"
        target = f"audit/independent/{filename}"

    # 11. Documentation
    elif p.startswith("docs/"):
        category = "documentation"
        status = "active"
        if filename in ["moves.csv", "undo_restructure.sh", "PATH_MAP.md", "BACKUP_CHECKLIST.md"]:
            status = "historical"
            action = "archive"
            target = f"archive/docs_restructure_history/{filename}"
        else:
            action = "keep_in_place"
            target = p

    # 12. Deployment
    elif p.startswith("deployment/") or filename in ["docker-compose.yml", "Dockerfile", ".dockerignore"]:
        category = "deployment"
        status = "active"
        action = "keep_in_place"
        target = p

    # 13. Scripts
    elif p.startswith("scripts/"):
        category = "utility_script"
        status = "active"
        if filename.startswith("p2_") or filename.startswith("p1_") or "baseline" in filename:
            has_research_evidence = True
        action = "keep_in_place"
        target = p

    # 14. Scratch & Clone Directories
    elif p.startswith("scratch") or p.startswith("scratch_"):
        category = "scratch"
        status = "obsolete"
        action = "archive"
        target = f"archive/scratch/{p}"

    # 15. Archive Directory
    elif p.startswith("archive/"):
        category = "archive"
        status = "historical"
        action = "keep_in_place"
        target = p

    # 16. Stale frontend build directory
    elif p.startswith("frontend/"):
        category = "build_artifact"
        status = "obsolete"
        action = "delete_candidate"
        target = "DELETE (stale Sep 20 node_modules/dist, active frontend is web/)"

    # 17. Empty demo directory
    elif p.startswith("demo/"):
        category = "miscellaneous"
        status = "obsolete"
        action = "delete_candidate"
        target = "DELETE (empty directory)"

    # 18. Root Level Files
    elif "/" not in p:
        if filename.startswith("patch_") or filename.startswith("fix_") or filename in ["plan_restructure.py"]:
            category = "temporary_patch"
            status = "obsolete"
            action = "archive"
            target = f"archive/scripts/patches/{filename}"
        elif filename in ["compute_entropy.py", "compute_shap.py", "evaluate_agent_contribution.py", "evaluate_risk.py",
                          "evaluate_risk_analysis.py", "generate_d1_d2_baselines.py", "generate_figures.py",
                          "generate_final_report.py", "generate_multiseed_figures.py", "generate_phase3.py",
                          "generate_phase4_report.py", "generate_poster.py", "generate_token.py", "get_cm.py",
                          "investigate_fpr.py", "test_e2e_local.py", "test_load.py", "validate_dataset.py"]:
            category = "utility_script"
            status = "historical"
            action = "archive"
            target = f"archive/scripts/root_scripts/{filename}"
        elif filename in ["run_all_experiments.sh", "run_multiseed.sh", "run_multiseed_fast.sh",
                          "run_multiseed_fast2.sh", "run_multiseed_final.sh", "wait_for_all.sh"]:
            category = "research_experiment"
            status = "historical"
            has_research_evidence = True
            action = "archive"
            target = f"archive/scripts/experiment_runners/{filename}"
        elif filename in ["AUDIT.md", "BOT_IOT_COLLAPSE_ANALYSIS.md", "FEATURE_V1_5_VALIDATION.md",
                          "FOLLOWUP_AUDIT.md", "LIVE_CHECK.md", "SCHEMA_AUDIT.md", "V1_5_PAIRWISE_CHECK.md", "DEMO.md", "DRY_RUN_PLAN.md"]:
            category = "audit_report"
            status = "historical"
            has_research_evidence = True
            action = "relocate"
            target = f"audit/historical/{filename}"
        elif filename in ["audit.py", "audit_metrics.json", "audit_results.json"]:
            category = "audit_report"
            status = "historical"
            action = "relocate"
            target = f"audit/historical/{filename}"
        elif filename in ["ARGUS_ALL_RESEARCH_RESULTS.xlsx"]:
            category = "results_data"
            status = "redundant"
            has_research_evidence = True
            action = "consolidate"
            target = "results/ARGUS_ALL_RESEARCH_RESULTS.xlsx (keep results copy, archive root copy)"
        elif filename in ["run1.csv"]:
            category = "data"
            status = "historical"
            action = "archive"
            target = f"archive/data/{filename}"
        elif filename in ["TEST_ACCESS.log", "uvicorn.log", "final_eval_output.txt"]:
            category = "miscellaneous"
            status = "obsolete"
            action = "delete_candidate"
            target = f"archive/logs/{filename}"
        elif filename in ["README.md", "LICENSE", "pyproject.toml", "Makefile", ".gitignore", ".env.example", "uv.lock"]:
            category = "documentation" if filename in ["README.md", "LICENSE"] else "config"
            status = "active"
            action = "keep_in_place"
            target = p

    return category, status, has_research_evidence, action, target


def build_inventory():
    print("Building repository inventory...")
    t0 = time.time()
    
    # Pre-index text files for reference scanning
    code_files = []
    for root, dirs, files in os.walk(REPO_ROOT):
        if any(p in root for p in [".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"]):
            continue
        for f in files:
            if f.endswith((".py", ".sh", ".yaml", ".yml", ".md", ".json", ".ts", ".tsx", ".html", ".toml")):
                code_files.append(os.path.join(root, f))

    print(f"Loaded {len(code_files)} reference source files.")

    # Read reference contents
    reference_cache = {}
    for cf in code_files:
        try:
            with open(cf, "r", errors="ignore") as f:
                reference_cache[cf] = f.read()
        except Exception:
            pass

    records = []
    category_counts = {}
    status_counts = {}
    action_counts = {}

    for root, dirs, files in os.walk(REPO_ROOT):
        # Exclude ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for f in files:
            full_path = Path(root) / f
            rel_path = str(full_path.relative_to(REPO_ROOT)).replace("\\", "/")
            
            try:
                stat = full_path.stat()
                sz = stat.st_size
            except Exception:
                sz = 0

            # Line count for text files
            lines = 0
            if full_path.suffix.lower() in [".py", ".sh", ".yaml", ".yml", ".md", ".json", ".ts", ".tsx", ".html", ".toml", ".txt", ".csv"]:
                try:
                    with open(full_path, "r", errors="ignore") as fp:
                        lines = sum(1 for _ in fp)
                except Exception:
                    lines = 0

            cat, stat_val, has_res, act, tgt = classify_file(rel_path)

            # References scan for root and key files
            refs = []
            if "/" not in rel_path or full_path.suffix in [".py", ".sh", ".md", ".json"]:
                base_name = f
                for cf, content in reference_cache.items():
                    cf_rel = str(Path(cf).relative_to(REPO_ROOT)).replace("\\", "/")
                    if cf_rel != rel_path and base_name in content:
                        refs.append(cf_rel)

            record = {
                "path": rel_path,
                "name": f,
                "extension": full_path.suffix.lower(),
                "size_bytes": sz,
                "line_count": lines,
                "category": cat,
                "status": stat_val,
                "has_research_evidence": has_res,
                "reference_count": len(refs),
                "referenced_by_sample": refs[:5],
                "recommended_action": act,
                "target_location": tgt,
            }
            records.append(record)

            category_counts[cat] = category_counts.get(cat, 0) + 1
            status_counts[stat_val] = status_counts.get(stat_val, 0) + 1
            action_counts[act] = action_counts.get(act, 0) + 1

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_files": len(records),
        "total_size_mb": round(sum(r["size_bytes"] for r in records) / (1024 * 1024), 2),
        "category_breakdown": category_counts,
        "status_breakdown": status_counts,
        "action_breakdown": action_counts,
        "files": records,
    }

    out_file = OUTPUT_DIR / "repository_inventory.json"
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Inventory completed in {time.time()-t0:.2f}s. Saved to: {out_file}")
    print(f"Summary: {len(records)} files, {summary['total_size_mb']} MB")
    print("Categories:", category_counts)
    print("Status:", status_counts)
    print("Recommended Actions:", action_counts)

if __name__ == "__main__":
    build_inventory()
