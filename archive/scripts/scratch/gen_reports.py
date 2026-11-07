import json
import os

with open('/home/bhumi/.gemini/antigravity-cli/brain/c771ab50-b140-41c4-b6f6-e84b2b821574/scratch/ton_iot_analysis.json', 'r') as f:
    data = json.load(f)

# TON_IOT_DATA_PROFILE.md
md1 = "# TON_IoT Data Profile\n\n"
md1 += "| File | Modality | Rows | Columns | Label | Classes | Timestamp | Main Evidence |\n"
md1 += "|------|----------|------|---------|-------|---------|-----------|---------------|\n"

# LABEL_ANALYSIS.md
md2 = "# TON_IoT Label Analysis\n\n"
md2 += "| Dataset | Label column | Classes | Normal samples | Attack samples | Imbalance |\n"
md2 += "|---------|--------------|---------|----------------|----------------|-----------|\n"

for path, info in sorted(data.items()):
    filename = info['filename']
    if 'IoT' in filename:
        if 'Processed' in path:
            mod = 'Processed IoT'
        else:
            mod = 'IoT/IIoT telemetry'
    elif 'Network' in path:
        mod = 'Network'
    elif 'Linux' in path:
        mod = 'Linux host'
    elif 'Windows' in path:
        mod = 'Windows host'
    else:
        mod = 'Unknown'
        
    rows = info['rows']
    cols = info['columns']
    label_col = info['label_column'] or 'N/A'
    classes = info['unique_labels'] if info.get('unique_labels') else 'N/A'
    
    # Timestamp logic
    has_time = False
    for c in info['column_names']:
        c_low = c.lower()
        if c_low in ['date', 'time', 'ts']:
            has_time = True
            break
    ts_val = "Yes" if has_time else "No"
    
    # Main evidence logic
    if mod == 'Network':
        ev = "Network flows (IPs, ports, protocols, HTTP/DNS/SSL metadata)"
    elif 'IoT' in mod:
        ev = "Sensor readings and device states"
    elif mod == 'Linux host':
        if 'disk' in filename.lower():
            ev = "Disk I/O statistics per PID"
        elif 'memory' in filename.lower():
            ev = "Memory usage statistics per PID"
        elif 'process' in filename.lower():
            ev = "CPU and process state statistics per PID"
        else:
            ev = "Host performance metrics"
    elif mod == 'Windows host':
        ev = "Windows performance counters (CPU, Memory, Network, Process)"
    else:
        ev = "Unknown metrics"
        
    md1 += f"| {filename} | {mod} | {rows} | {cols} | {label_col} | {classes} | {ts_val} | {ev} |\n"
    
    if label_col != 'N/A':
        dist = info['label_distribution']
        normal = dist.get('0', dist.get('0.0', dist.get('normal', dist.get('Normal', 0))))
        attack = sum(v for k,v in dist.items() if str(k) not in ['0', '0.0', 'normal', 'Normal'])
        imbalance = f"{round((attack/(normal+attack+1e-9))*100, 1)}% attack"
        md2 += f"| {filename} | {label_col} | {classes} | {normal} | {attack} | {imbalance} |\n"

with open('data/ton_iot/metadata/TON_IOT_DATA_PROFILE.md', 'w') as f:
    f.write(md1)

with open('data/ton_iot/metadata/LABEL_ANALYSIS.md', 'w') as f:
    f.write(md2)

print("Generated TON_IOT_DATA_PROFILE.md and LABEL_ANALYSIS.md")
