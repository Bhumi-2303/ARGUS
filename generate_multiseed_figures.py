import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs('artifacts/figures/scientific_validation', exist_ok=True)
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib_cache'

df = pd.read_csv('artifacts/metrics/phase4_multiseed_results.csv')

seeds = df['seed'].astype(str)

# F1
plt.figure(figsize=(8, 5))
plt.bar(seeds, df['F1'], color='blue', alpha=0.7)
plt.title('ARGUS Phase 4 F1-Score Across Seeds')
plt.xlabel('Random Seed')
plt.ylabel('F1 Score')
plt.ylim(0, 0.5)
for i, v in enumerate(df['F1']):
    plt.text(i, v + 0.01, f"{v:.4f}", ha='center')
plt.grid(True, axis='y')
plt.savefig('artifacts/figures/scientific_validation/Figure_Multiseed_F1.png')
plt.close()

# MCC
plt.figure(figsize=(8, 5))
plt.bar(seeds, df['MCC'], color='purple', alpha=0.7)
plt.title('ARGUS Phase 4 MCC Across Seeds')
plt.xlabel('Random Seed')
plt.ylabel('MCC Score')
plt.ylim(0, 0.2)
for i, v in enumerate(df['MCC']):
    plt.text(i, v + 0.005, f"{v:.4f}", ha='center')
plt.grid(True, axis='y')
plt.savefig('artifacts/figures/scientific_validation/Figure_Multiseed_MCC.png')
plt.close()

# FPR / FNR
plt.figure(figsize=(10, 5))
bar_width = 0.35
index = range(len(seeds))
plt.bar([i - bar_width/2 for i in index], df['FPR'], bar_width, label='FPR (False Positive Rate)', color='red', alpha=0.7)
plt.bar([i + bar_width/2 for i in index], df['FNR'], bar_width, label='FNR (False Negative Rate)', color='green', alpha=0.7)
plt.title('ARGUS Phase 4 FPR and FNR Across Seeds')
plt.xlabel('Random Seed')
plt.ylabel('Rate')
plt.xticks(index, seeds)
for i, v in enumerate(df['FPR']):
    plt.text(i - bar_width/2, v + 0.01, f"{v:.3f}", ha='center', fontsize=9)
for i, v in enumerate(df['FNR']):
    plt.text(i + bar_width/2, v + 0.01, f"{v:.3f}", ha='center', fontsize=9)
plt.legend()
plt.grid(True, axis='y')
plt.savefig('artifacts/figures/scientific_validation/Figure_Multiseed_FPR_FNR.png')
plt.close()

print("Figures generated.")
