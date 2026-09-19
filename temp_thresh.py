import pandas as pd
import numpy as np

df = pd.read_csv("phase4_results/experiments/E5_fusion_CORAL_prior/predictions.csv")

counts = df.groupby(['y_prob', 'y_true']).size().unstack(fill_value=0).reset_index()
counts['total'] = counts[0] + counts[1]
print("Top 10 most common probabilities:")
print(counts.sort_values('total', ascending=False).head(10))

thresholds = [0.49, 0.50, 0.504, 0.5045, 0.505, 0.51, 0.60, 0.70, 0.80, 0.90, 0.95]
print("\nThreshold Analysis:")
print(f"{'Threshold':<10} | {'TP':<6} | {'TN':<6} | {'FP':<6} | {'FN':<6} | {'Precision':<9} | {'Recall':<6} | {'FPR':<6} | {'FNR':<6}")
for t in thresholds:
    y_pred = (df['y_prob'] >= t).astype(int)
    tp = ((y_pred == 1) & (df['y_true'] == 1)).sum()
    tn = ((y_pred == 0) & (df['y_true'] == 0)).sum()
    fp = ((y_pred == 1) & (df['y_true'] == 0)).sum()
    fn = ((y_pred == 0) & (df['y_true'] == 1)).sum()
    
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0
    
    print(f"{t:<10.4f} | {tp:<6} | {tn:<6} | {fp:<6} | {fn:<6} | {prec:<9.4f} | {rec:<6.4f} | {fpr:<6.4f} | {fnr:<6.4f}")
