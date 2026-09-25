with open("training/scripts/phase3_execute_all.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "EXPERIMENT E: D1 -> D3 DANN" in line:
        skip = True
    if "EXPERIMENT F: D2 -> D3 DANN" in line:
        skip = True
    if "ABLATION STUDIES" in line:
        skip = True
    if "SHAP (Explainability)" in line:
        skip = True
    if "Phase 4 Execution" in line:
        skip = False # wait, there is no phase 4 in this script
    
    if "7. EXPORT RESULTS" in line:
        skip = False
        
    if not skip:
        new_lines.append(line)
    else:
        # Just maintain indentation and add pass if it's a block, actually we can just drop it entirely, wait! 
        pass

with open("training/scripts/phase3_execute_all_fast.py", "w") as f:
    f.writelines(new_lines)
