import re

with open("scratch/step1_out.txt") as f:
    content = f.read()

parts = content.split("--- File: ")
for p in parts[1:]:
    lines = p.split('\n')
    filename = lines[0].strip(" -")
    date = lines[1].replace("Git Date: ", "").strip()
    
    xgb_lines = []
    sk_lines = []
    torch_lines = []
    
    mode = None
    for l in lines[2:]:
        if "XGBoost imports" in l: mode = "xgb"; continue
        if "sklearn imports" in l: mode = "sk"; continue
        if "torch/nn.Module imports" in l: mode = "torch"; continue
        if l.startswith("--- File:") or l.startswith("==="): break
        
        if mode == "xgb" and l.strip() and "None" not in l: xgb_lines.append(l)
        if mode == "sk" and l.strip() and "None" not in l: sk_lines.append(l)
        if mode == "torch" and l.strip() and "None" not in l: torch_lines.append(l)

    print(f"File: {filename}")
    print(f"Date: {date}")
    if xgb_lines: print("XGBoost:", xgb_lines[0].strip())
    else: print("XGBoost: None")
    
    if sk_lines: print("Sklearn:", sk_lines[0].strip())
    else: print("Sklearn: None")
    
    if torch_lines: print("Torch:", torch_lines[0].strip())
    else: print("Torch: None")
    print()
