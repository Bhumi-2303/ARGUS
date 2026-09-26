import os
from pathlib import Path

files_to_fix = [
    "experiments/domain_adaptation/coral/stage_a_env_check.py",
    "experiments/domain_adaptation/coral/stage_b_c_coral.py",
    "experiments/domain_adaptation/coral/stage_d_e_train_evaluate.py",
    "experiments/domain_adaptation/coral/stage_f_generate_all_artifacts.py",
    "experiments/domain_adaptation/dann/stage1_audit_and_sanity.py",
    "experiments/domain_adaptation/dann/stage2_pilot_lambda_sweep.py",
    "experiments/domain_adaptation/dann/stage3_final_evaluation_and_artifacts.py",
    "experiments/ablations/phase4_execute.py",
    "experiments/analysis/feature_resolution_study.py"
]

for f in files_to_fix:
    if not os.path.exists(f):
        print(f"File not found: {f}")
        continue
    with open(f, 'r') as file:
        content = file.read()
    
    # Replace BASE for coral and dann
    if "/Volumes/BLACK-BOX/ARGUS" in content:
        content = content.replace('import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
BASE = _curr', 'BASE = Path(__file__).resolve().parent.parent.parent.parent')
    
    # Replace PROJECT_ROOT for ablations and analysis
    if "/Users/tirthkosambia/Documents/ARGUS" in content:
        content = content.replace('import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
PROJECT_ROOT = _curr', 'PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent')

    with open(f, 'w') as file:
        file.write(content)
    print(f"Fixed paths in {f}")

