with open("src/argus/registry/model_registry.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if '"target_domain": "ciciot",' in line:
        if 'xgb_source' not in ''.join(new_lines[-20:]):
            # For model_d1_baseline (ciciot) -> unverified/planned
            new_lines.append('        "status": "planned",\n')
        else:
            # For xgb_source -> unverified/planned
            new_lines.append('        "status": "planned",\n')
    elif '"target_domain": "nfton",' in line:
        new_lines.append('        "status": "verified",\n')
    elif '"target_domain": "iec104",' in line:
        new_lines.append('        "status": "partial",\n')

with open("src/argus/registry/model_registry.py", "w") as f:
    f.writelines(new_lines)
