import os
import subprocess

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def git_mv(src, dest):
    import glob
    # Handle wildcards
    if '*' in src:
        files = glob.glob(src)
        if not files: return
        os.makedirs(dest, exist_ok=True)
        for f in files:
            run_cmd(f"git mv {f} {dest} || mv {f} {dest}")
    else:
        if not os.path.exists(src):
            return
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        run_cmd(f"git mv {src} {dest} || mv {src} {dest}")

def main():
    dirs = [
        "docs/architecture", "docs/experiments", "docs/research", "docs/api", "docs/deployment",
        "src/argus/core/config", "src/argus/core/schemas", "src/argus/core/logging", "src/argus/core/exceptions",
        "src/argus/models/xgboost", "src/argus/models/lightgbm", "src/argus/models/ft_transformer", "src/argus/models/dann", "src/argus/models/fusion",
        "src/argus/adaptation/coral", "src/argus/adaptation/prior_correction", "src/argus/adaptation/calibration",
        "src/argus/explainability/shap", "src/argus/explainability/llm",
        "experiments/configs/datasets", "experiments/configs/models", "experiments/configs/adaptation", "experiments/configs/experiments",
        "experiments/datasets/cic_iot", "experiments/datasets/nf_ton", "experiments/datasets/iec104",
        "experiments/preprocessing", "experiments/baselines", "experiments/domain_adaptation/coral", "experiments/domain_adaptation/dann",
        "experiments/fusion", "experiments/ablations", "experiments/evaluation", "experiments/analysis",
        "artifacts/models", "artifacts/predictions", "artifacts/metrics", "artifacts/figures", "artifacts/reports", "artifacts/logs",
        "deployment/docker", "deployment/compose",
        "tests/unit", "tests/integration", "tests/experiments", "tests/e2e",
        "scripts/setup", "scripts/run", "scripts/maintenance"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    git_mv("api/Dockerfile", "deployment/docker/detector.Dockerfile")
    git_mv("agent/Dockerfile", "deployment/docker/decision.Dockerfile")
    git_mv("knowledge_agent/Dockerfile", "deployment/docker/knowledge.Dockerfile")
    git_mv("orchestrator/Dockerfile", "deployment/docker/orchestrator.Dockerfile")
    git_mv("risk_agent/Dockerfile", "deployment/docker/risk.Dockerfile")
    git_mv("streaming/Dockerfile", "deployment/docker/streaming.Dockerfile")
    
    # Remove old root backend folders - they should be in src/argus/services
    run_cmd("git rm -rf api agent knowledge_agent orchestrator risk_agent streaming || rm -rf api agent knowledge_agent orchestrator risk_agent streaming")

    git_mv("docker-compose.yml", "deployment/compose/docker-compose.yml")

    git_mv("experiment_execution/neural_robustness/domain_adaptation/DA02_DANN/scripts/*", "experiments/domain_adaptation/dann/")
    git_mv("experiment_execution/neural_robustness/domain_adaptation/ARGUS_DA01_CORAL_DELIVERABLES/scripts/*", "experiments/domain_adaptation/coral/")
    git_mv("phase4_results/feature_resolution_study.py", "experiments/analysis/")
    git_mv("phase4_results/phase4_execute.py", "experiments/ablations/")
    
    git_mv("phase3_results/models/*", "artifacts/models/")
    git_mv("phase4_results/models/*", "artifacts/models/")
    
    git_mv("phase3_results/metrics", "artifacts/metrics/phase3")
    git_mv("phase4_results/metrics", "artifacts/metrics/phase4")
    git_mv("phase3_results/plots", "artifacts/figures/phase3")
    git_mv("phase4_results/plots", "artifacts/figures/phase4")
    
    git_mv("ARGUS_Final_Research_Validation.md", "artifacts/reports/")
    git_mv("ARGUS_Paper_Evidence_Package.md", "artifacts/reports/")
    git_mv("ARGUS_FPR_Investigation_Report.md", "artifacts/reports/")

    git_mv("docs/specifications/*", "docs/architecture/")
    
    # Generate the README and documentation
    with open("docs/experiments/experiment_index.md", "w") as f:
        f.write("# ARGUS Experiment Index\n\n| Experiment | Purpose | Script | Config | Input | Output | Status |\n| ---------- | ------- | ------ | ------ | ----- | ------ | ------ |\n| EXP05 | Multi-source cross-domain fusion | phase4_execute.py | default | CICIoT + NF-ToN -> IEC104 | artifacts/metrics/phase4 | Completed |")
        
    print("Structure created.")

if __name__ == "__main__":
    main()
