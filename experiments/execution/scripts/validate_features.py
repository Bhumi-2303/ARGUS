import json
import pandas as pd
from pathlib import Path

import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
BASE = _curr
EE = BASE / 'experiment_execution'

def validate_features():
    print("=== STEP 4: FEATURE DEFINITIONS FREEZE AND VALIDATION ===")
    
    feature_report_md = """# ARGUS Feature Definitions & Representation Freeze Report

This document records the exact feature engineering formulas, source column mappings, and representation tiers used across all ARGUS experiments.

## 1. Harmonized 4-Feature Set (ARGUS-4)
Used across all primary cross-domain transfer models (D1 -> D3, D2 -> D3, CORAL, DANN, Fused).

| Feature Name | Source Formula / Extraction | Data Type | Missing Treatment | Log Transform | Cross-Domain Semantic Alignment |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `pkt_mean_to_max` | $\\text{Pkt Len Mean} / (\\text{Pkt Len Max} + 10^{-10})$ | float64 | Impute 0 | No | Ratio of average to peak payload size |
| `tcp_flag_density` | $\\sum \\text{TCP Flags (SYN, ACK, FIN, RST, PSH, URG)}$ | float64 | Impute 0 | No | Sum / Multiplicity of active control flags |
| `log_pkt_mean` | $\\ln(1 + \\max(0, \\text{Pkt Len Mean}))$ | float64 | Impute 0 | `log1p` | Log-transformed mean packet length |
| `log_pkt_max` | $\\ln(1 + \\max(0, \\text{Pkt Len Max}))$ | float64 | Impute 0 | `log1p` | Log-transformed maximum packet length |

---

## 2. Expanded Feature Sets (Feature Resolution Study)

### ARGUS-6 (ARGUS-4 + 2 Volume/Duration Features)
- `log_tot_pkts`: $\\ln(1 + \\max(0, \\text{Tot Fwd Pkts} + \\text{Tot Bwd Pkts}))$
- `log_flow_duration`: $\\ln(1 + \\max(0, \\text{Flow Duration in } \\mu\\text{s}))$

### ARGUS-8 (ARGUS-6 + 2 Variance/Minimum Features)
- `log_pkt_std`: $\\ln(1 + \\max(0, \\text{Pkt Len Std}))$
- `log_pkt_min`: $\\ln(1 + \\max(0, \\text{Pkt Len Min}))$

---

## 3. Native SCADA Feature Set (Native-73)
Used exclusively on target IEC 60870-5-104 flow data (`data/IEC104/extracted_csvs/`) to evaluate the target discriminative ceiling.
- **Dimensionality**: 73 numeric flow statistics.
- **Includes**: Forward/Backward IAT (Mean, Std, Max, Min), TCP Header Lengths, Flow Bytes/s, Sub-flow packets/bytes, Active/Idle timing statistics, and Window Size parameters.
"""
    (EE / 'reports/feature_freeze_report.md').write_text(feature_report_md)
    print("[OK] Feature freeze report saved to experiment_execution/reports/feature_freeze_report.md")

if __name__ == '__main__':
    validate_features()
