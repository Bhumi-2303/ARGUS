import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs('artifacts/figures/scientific_validation', exist_ok=True)
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib_cache'

# 1. Figure 1: Ambiguous Feature Cluster
# We just create a bar chart of the dataset composition
labels = ['Ambiguous Cluster (Identical Features)', 'Unique/Other Flows']
sizes = [501417, 714453 - 501417]
plt.figure(figsize=(6, 6))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff'])
plt.title('Figure 1: High-FPR Ambiguous Cluster in IEC104 Test Set')
plt.savefig('artifacts/figures/scientific_validation/Figure_1_Ambiguous_Cluster.png')
plt.close()

# 2. Figure 2: Threshold Sensitivity
df_metrics = pd.read_csv('artifacts/metrics/fpr_ambiguity_analysis.csv')
plt.figure(figsize=(8, 5))
plt.plot(df_metrics['Threshold'], df_metrics['FPR'], label='FPR (False Positive Rate)', marker='o', color='red')
plt.plot(df_metrics['Threshold'], df_metrics['Recall'], label='Recall (True Positive Rate)', marker='s', color='green')
plt.axvline(x=0.5041, color='black', linestyle='--', label='Cluster Probability (0.5041)')
plt.xlim(0.48, 0.52)
plt.title('Figure 2: Extreme Threshold Sensitivity around Ambiguous Cluster')
plt.xlabel('Detection Threshold')
plt.ylabel('Rate')
plt.legend()
plt.grid(True)
plt.savefig('artifacts/figures/scientific_validation/Figure_2_Threshold_Sensitivity.png')
plt.close()

# 3. Figure 4: Risk-aware behavior
df_risk = pd.read_csv('artifacts/metrics/risk_decision_analysis.csv')
plt.figure(figsize=(8, 5))
bar_width = 0.35
index = df_risk['Criticality']
plt.bar(index - bar_width/2, df_risk['FP_Suppression_Rate'], bar_width, label='FP Suppression Rate', color='blue')
plt.bar(index + bar_width/2, df_risk['Attack_Escalation_Rate'], bar_width, label='Attack Escalation Rate', color='red')
plt.title('Figure 4: Operational Consequence by Asset Criticality')
plt.xlabel('Asset Criticality (1=Low, 5=High)')
plt.ylabel('Rate')
plt.xticks(index)
plt.legend()
plt.grid(True, axis='y')
plt.savefig('artifacts/figures/scientific_validation/Figure_4_Risk_Awareness.png')
plt.close()

print("Figures generated.")
