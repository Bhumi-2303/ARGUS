with open("experiments/ablations/phase4_execute.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip_loop = False
skip_group = False
for line in lines:
    if 'for dann_id in ["D1_D3_DANN", "D2_D3_DANN"]:' in line:
        skip_loop = True
    elif skip_loop and line.startswith("    ") and not line.startswith("        ") and line.strip() != "" and not line.strip().startswith("#"):
        skip_loop = False

    if "p3_exp_ids =" in line:
        line = line.replace(', "D1_D3_DANN", "D2_D3_DANN"', "")
        
    if "GROUP F — DANN ALTERNATIVE" in line:
        skip_group = True
    elif skip_group and "STEP 10" in line:
        skip_group = False
        
    skip = skip_loop or skip_group

    if "dann" in line.lower() and skip == False:
        if "dann_trainable_parameters" in line or "D1 DANN" in line or "D2 DANN" in line:
            continue
        if "add_comparison" in line and "DANN" in line:
            continue
        if "sheet_name=\"DANN\"" in line:
            continue
        if "log(f\"\\nDANN:\")" in line:
            continue

    if not skip:
        new_lines.append(line)

with open("experiments/ablations/phase4_execute_fast.py", "w") as f:
    f.writelines(new_lines)
