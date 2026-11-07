import os
import pandas as pd
import numpy as np

seeds = [42, 123, 456, 789, 1011]
target_method = "D1+D2 CORAL + prior fusion"
results = []

# Seed 42
df_42 = pd.read_csv("artifacts/metrics/phase4/final_comparison.csv")
row_42 = df_42[df_42['Method'] == target_method].iloc[0]
results.append({
    'seed': 42,
    'threshold': row_42['Threshold'],
    'F1': row_42['F1'],
    'MCC': row_42['MCC'],
    'FPR': row_42['FPR'],
    'FNR': row_42['FNR'],
    'ROC_AUC': row_42['ROC_AUC'],
    'Balanced_Accuracy': row_42['Balanced_Accuracy'],
    'Precision': row_42['Precision'],
    'Recall': row_42['Recall'],
    'N_test': 714453,
    'N_attack': 160509,
    'N_benign': 553944
})

# Other seeds
for s in [123, 456, 789, 1011]:
    df_s = pd.read_csv(f"artifacts/metrics/phase4_multiseed/final_comparison_seed_{s}.csv")
    row_s = df_s[df_s['Method'] == target_method].iloc[0]
    results.append({
        'seed': s,
        'threshold': row_s['Threshold'],
        'F1': row_s['F1'],
        'MCC': row_s['MCC'],
        'FPR': row_s['FPR'],
        'FNR': row_s['FNR'],
        'ROC_AUC': row_s['ROC_AUC'],
        'Balanced_Accuracy': row_s['Balanced_Accuracy'],
        'Precision': row_s['Precision'],
        'Recall': row_s['Recall'],
        'N_test': 714453,
        'N_attack': 160509,
        'N_benign': 553944
    })

res_df = pd.DataFrame(results)
res_df.to_csv("artifacts/metrics/phase4_multiseed_results.csv", index=False)

# Calculate stats
stats = []
metrics = ['F1', 'MCC', 'FPR', 'FNR', 'ROC_AUC', 'Balanced_Accuracy', 'Precision', 'Recall']
for m in metrics:
    stats.append({
        'Metric': m,
        'Mean': res_df[m].mean(),
        'Std': res_df[m].std(),
        'Min': res_df[m].min(),
        'Max': res_df[m].max()
    })

stats_df = pd.DataFrame(stats)
stats_df.to_csv("artifacts/metrics/phase4_multiseed_summary.csv", index=False)

# Paper Table
paper_table = []
for idx, row in res_df.iterrows():
    paper_table.append({
        'Model / Method': f"ARGUS seed {int(row['seed'])}",
        'F1': f"{row['F1']:.4f}",
        'MCC': f"{row['MCC']:.4f}",
        'FPR': f"{row['FPR']:.4f}",
        'FNR': f"{row['FNR']:.4f}",
        'ROC-AUC': f"{row['ROC_AUC']:.4f}",
        'Balanced Accuracy': f"{row['Balanced_Accuracy']:.4f}"
    })

mean_row = {
    'Model / Method': 'ARGUS Mean ± Std',
    'F1': f"{stats_df.loc[stats_df['Metric']=='F1', 'Mean'].values[0]:.4f} ± {stats_df.loc[stats_df['Metric']=='F1', 'Std'].values[0]:.4f}",
    'MCC': f"{stats_df.loc[stats_df['Metric']=='MCC', 'Mean'].values[0]:.4f} ± {stats_df.loc[stats_df['Metric']=='MCC', 'Std'].values[0]:.4f}",
    'FPR': f"{stats_df.loc[stats_df['Metric']=='FPR', 'Mean'].values[0]:.4f} ± {stats_df.loc[stats_df['Metric']=='FPR', 'Std'].values[0]:.4f}",
    'FNR': f"{stats_df.loc[stats_df['Metric']=='FNR', 'Mean'].values[0]:.4f} ± {stats_df.loc[stats_df['Metric']=='FNR', 'Std'].values[0]:.4f}",
    'ROC-AUC': f"{stats_df.loc[stats_df['Metric']=='ROC_AUC', 'Mean'].values[0]:.4f} ± {stats_df.loc[stats_df['Metric']=='ROC_AUC', 'Std'].values[0]:.4f}",
    'Balanced Accuracy': f"{stats_df.loc[stats_df['Metric']=='Balanced_Accuracy', 'Mean'].values[0]:.4f} ± {stats_df.loc[stats_df['Metric']=='Balanced_Accuracy', 'Std'].values[0]:.4f}"
}
paper_table.append(mean_row)

paper_df = pd.DataFrame(paper_table)
paper_df.to_csv("artifacts/metrics/phase4_multiseed_paper_table.csv", index=False)
