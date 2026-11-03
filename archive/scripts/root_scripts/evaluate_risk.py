import os
import pandas as pd
import numpy as np

features_path = "ARGUS_Cross_Domain_Results/argus_coral_data/iec104_test_features.csv"
preds_path = "phase4_results/experiments/E5_fusion_CORAL_prior/predictions.csv"

# Load data
df_feat = pd.read_csv(features_path)
df_pred = pd.read_csv(preds_path)

df = pd.concat([df_feat[['label']], df_pred['y_prob']], axis=1)

def calculate_risk(probability: float, criticality: int):
    WEIGHT_PROBABILITY = 0.60
    WEIGHT_CRITICALITY = 0.40
    c_norm = criticality / 5.0
    score = (WEIGHT_PROBABILITY * probability + WEIGHT_CRITICALITY * c_norm) * 100.0
    score = round(score, 2)
    
    if score >= 80.0:
        tier = "Critical"
    elif score >= 60.0:
        tier = "High"
    elif score >= 40.0:
        tier = "Medium"
    else:
        tier = "Low"
        
    return score, tier

def determine_action(pred, tier):
    # Based on the actual decision agent fallback logic:
    return "INVESTIGATE" if pred == 1 else "IGNORE"

# Let's generate a probability matrix specifically for the cluster
ambiguous_prob = 0.5041
# And some other test points
probs = [0.50, 0.5041, 0.51, 0.55, 0.60, 0.70, 0.80, 0.90]
criticalities = [1, 2, 3, 4, 5]

results = []
for p in probs:
    pred = 1 if p >= 0.50 else 0
    row = {'Probability': p}
    for c in criticalities:
        score, tier = calculate_risk(p, c)
        # We also record the action
        action = determine_action(pred, tier)
        row[f'Crit_{c}_Score'] = score
        row[f'Crit_{c}_Tier'] = tier
        row[f'Crit_{c}_Action'] = action
    results.append(row)

res_df = pd.DataFrame(results)
print(res_df[['Probability', 'Crit_1_Tier', 'Crit_3_Tier', 'Crit_5_Tier']])

# Let's analyze the 501,417-flow cluster which has probability ~0.504138
# Actual exact probability from earlier:
cluster_prob = df['y_prob'].value_counts().index[0]
print(f"Ambiguous Cluster Prob: {cluster_prob}")

for c in [1,3,5]:
    score, tier = calculate_risk(cluster_prob, c)
    print(f"Cluster at Crit {c}: {score} -> {tier}")
