import os
import pandas as pd

# Creating feature_representation_comparison.csv
data = [
    {
        'Representation': 'Full/Native (70 features)',
        'Model': 'LightGBM (EXP-04)',
        'Evaluation': 'In-Domain Ceiling (IEC104)',
        'ROC-AUC': 0.6744,
        'PR-AUC': 0.4066,
        'F1': 0.4354,
        'MCC': 0.2494,
        'FPR': 0.722,
        'FNR': 0.0347,
        'Recall': 0.9653,
        'Precision': 0.2801
    },
    {
        'Representation': 'ARGUS-4 (4 features)',
        'Model': 'LightGBM Fusion (EXP05)',
        'Evaluation': 'Cross-Domain (CICIoT+NFToN -> IEC104)',
        'ROC-AUC': 0.5017,
        'PR-AUC': None,
        'F1': 0.3869,
        'MCC': 0.1205,
        'FPR': 0.8708,
        'FNR': 0.0392,
        'Recall': 0.9608,
        'Precision': 0.2435
    }
]

df = pd.DataFrame(data)
os.makedirs('artifacts/metrics', exist_ok=True)
df.to_csv('artifacts/metrics/feature_representation_comparison.csv', index=False)

md = """# Feature Representation Analysis

## Apples-to-Apples Comparison
We evaluate the 4-feature ARGUS representation against the Native SCADA (70-feature) representation.
The existing artifact `ARGUS_FULL_EXPERIMENTAL_PROGRESSION.csv` confirms that even a LightGBM model trained strictly in-domain on all 70 raw CICFlowMeter features produces an FPR of **72.2%**.

## Findings
- **Feature Ambiguity:** The high FPR (87.08% for cross-domain ARGUS) is only partially a result of the 4-feature dimensionality reduction. The underlying SCADA dataset intrinsically suffers from extreme class overlap and repetitive polling behavior, leading to a massive ambiguous feature cluster.
- **Cross-Domain Shift vs Representation:** Moving from 70-feature in-domain (72.2% FPR) to 4-feature cross-domain (87.08% FPR) incurs a ~15% penalty. The 70-feature model does achieve a slightly higher MCC (0.2494 vs 0.1205), but fundamentally fails to suppress false positives to a usable operational level (e.g. < 5%).
- **Conclusion:** The high FPR is primarily a *dataset label/feature ambiguity* problem intrinsic to IEC104 polling traffic, compounded secondarily by the *representation limitation* and *cross-domain shift*.
"""
os.makedirs('artifacts/reports', exist_ok=True)
with open('artifacts/reports/feature_representation_analysis.md', 'w') as f:
    f.write(md)

print("Phase 3 generated.")
