import re

with open("src/argus/services/decision_agent/main.py", "r") as f:
    code = f.read()

code = code.replace(
    'f1_name, f1_val = sorted_features[0] if len(sorted_features) > 0 else ("tcp_flag_density", 0.0)',
    'f1_name, f1_val = sorted_features[0] if len(sorted_features) > 0 else ("Unknown", 0.0)'
)
code = code.replace(
    'f2_name, f2_val = sorted_features[1] if len(sorted_features) > 1 else ("pkt_mean_to_max", 0.0)',
    'f2_name, f2_val = sorted_features[1] if len(sorted_features) > 1 else ("Unknown", 0.0)'
)

with open("src/argus/services/decision_agent/main.py", "w") as f:
    f.write(code)
