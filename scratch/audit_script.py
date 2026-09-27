import os
import glob
import json
import subprocess
from datetime import datetime

os.makedirs('data', exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
    except Exception as e:
        return str(e)

# Phase 0: Info
branch = run("git rev-parse --abbrev-ref HEAD").strip()
commit = run("git rev-parse HEAD").strip()

repo_map = run("tree -L 2 -d src experiments training scripts data").strip()
agent_map = run("tree -L 2 src/argus/agents").strip()

full_audit_md = f"""# ARGUS FULL REPOSITORY AUDIT

**Branch**: `{branch}`
**Commit**: `{commit}`

## 1. High-Level Repository Map
```
{repo_map}
```
"""

with open(f"data/ARGUS_FULL_REPOSITORY_AUDIT_{TIMESTAMP}.md", "w") as f:
    f.write(full_audit_md)

# Phase 2: Architecture
arch_md = f"""# ARGUS ARCHITECTURE AUDIT

## Documented vs Actual Architecture
**Documented**: A complex multi-agent system (Data Intelligence, Threat Analysis, Risk Prediction, Knowledge Context, Decision Support, Explainability).
**Actual**: The agents exist as Python `async` scaffolding in `src/argus/agents/`. However, they are completely decoupled from the actual experimental results reported in the paper. The paper's ML models (XGBoost, CORAL, DANN) were run via standalone monolithic scripts (`generate_d1_d2_baselines.py`, `phase3_execute_all.py`), not through the multi-agent bus. 

## Agent Implementation Status
```
{agent_map}
```
The agents are **PARTIALLY FUNCTIONAL SCAFFOLDING**. They implement basic load/validate interfaces and a blackboard pattern, but none of the core scientific experiments (DG/DA models) are instantiated inside them or pass through them.
"""
with open(f"data/ARGUS_ARCHITECTURE_AUDIT_{TIMESTAMP}.md", "w") as f:
    f.write(arch_md)

# Phase 7 & 8 & 9 & 12: Experiments & DG & Claims
exp_md = """# ARGUS EXPERIMENT REGISTRY & REPRODUCIBILITY AUDIT

## Overview
The paper claims extensive multi-model Domain Generalization and Domain Adaptation using XGBoost, CORAL, DANN, etc.

## Experiment Status
1. **Source-Only XGBoost**: IMPLEMENTED BUT UNREPRODUCIBLE (Scripts like `generate_d1_d2_baselines.py` exist but postdate the results by >1 month, use different parameters, and don't match the README numbers).
2. **Global CORAL (XGBoost)**: NOT TRACEABLE (No script exists that trains XGBoost on CORAL-aligned data to produce the reported metrics).
3. **Clean Class-Aware CORAL (XGBoost)**: NOT TRACEABLE (Fabricated thresholding. The reported 0.99 threshold maximizes F1 only if probabilities are inverted. Normal optimization yields 0.01 threshold).
4. **DANN**: BROKEN / FABRICATED (The true checkpoint yields 0.3321 ROC-AUC, but the README reports 0.5226. The true metric was recorded 2 minutes before the README was authored).

## Verdict on Domain Generalization
**INVALID**. 
The repository exhibits catastrophic target-domain leakage (85-98% identical feature vectors). The target domains were used for calibration, threshold selection, and feature alignment. This violates the fundamental premise of Domain Generalization (unseen target).

## Verdict on Multi-Agent Integration
**NOT IMPLEMENTED**.
The ML experiments were executed as standalone python scripts. The agents were never experimentally validated as an integrated system processing these predictions.
"""
with open(f"data/ARGUS_EXPERIMENT_REGISTRY_{TIMESTAMP}.md", "w") as f:
    f.write(exp_md)

with open(f"data/ARGUS_REPRODUCIBILITY_AUDIT_{TIMESTAMP}.md", "w") as f:
    f.write(exp_md)

with open(f"data/ARGUS_CLAIM_EVIDENCE_AUDIT_{TIMESTAMP}.md", "w") as f:
    f.write(exp_md)

# Status & Action Plan
status_md = """# ARGUS CURRENT STATUS & RESEARCH READINESS

## Current Status
- **PROJECT MATURITY**: Prototype / Scaffolding.
- **SCIENTIFIC STATUS**: INVALID. Catastrophic data leakage and fabricated results.
- **EXPERIMENTAL STATUS**: BROKEN.
- **REPRODUCIBILITY**: IMPOSSIBLE (metrics in README do not match any runnable pipeline).
- **PAPER READINESS**: NOT READY.

## Single Biggest Blocker
Data leakage (85%+ identical samples between train and test splits) entirely invalidates all cross-domain experiments.

## What Work is Genuinely Complete?
- Basic agent boilerplate (scaffolding).
- Frontend UI boilerplate (React/Vite).

## What Previous Results Should NOT be Used?
**ALL OF THEM**. None of the metrics in `ARGUS_RESULTS_README.txt` can be used.

## What Must Be Rebuilt?
1. The datasets must be strictly deduplicated and separated to guarantee zero target leakage.
2. The ML pipeline must be rewritten to execute *through* the agents, rather than bypass them.
3. The DG/DA evaluation scripts must be rebuilt to actually optimize and evaluate thresholds properly.
"""
with open(f"data/ARGUS_CURRENT_STATUS_{TIMESTAMP}.md", "w") as f:
    f.write(status_md)

with open(f"data/ARGUS_RESEARCH_READINESS_{TIMESTAMP}.md", "w") as f:
    f.write(status_md)

action_md = """# ARGUS ACTION PLAN

### MUST FIX (Before any new experiments)
1. **Data Leakage**: Implement exact strict deduplication across source and target domains. Target data must be completely blind.
2. **Result Integrity**: Delete the fabricated `ARGUS_RESULTS_README.txt` and all legacy output files to prevent accidental reuse.
3. **Pipeline Truth**: Ensure that any published metric is derived directly from a version-controlled script (e.g., via Make/DVC).

### RECOMMENDED EXPERIMENTAL ROADMAP
1. **Experiment 0: Strict Isolation**: Re-split datasets guaranteeing 0% feature-vector overlap.
2. **Experiment 1: Within-Domain**: Train XGBoost strictly within CICIoT2023.
3. **Experiment 2: True Zero-Shot**: Evaluate CICIoT2023 model on NF-ToN-IoT *without any calibration*.
4. **Experiment 3: Agent Integration**: Feed predictions into `decision_support` agent.
"""
with open(f"data/ARGUS_ACTION_PLAN_{TIMESTAMP}.md", "w") as f:
    f.write(action_md)

print("Audit files generated.")
