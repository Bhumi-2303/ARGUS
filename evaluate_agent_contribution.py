import os
import pandas as pd

def calculate_risk(probability: float, criticality: int):
    WEIGHT_PROBABILITY = 0.60
    WEIGHT_CRITICALITY = 0.40
    c_norm = criticality / 5.0
    score = (WEIGHT_PROBABILITY * probability + WEIGHT_CRITICALITY * c_norm) * 100.0
    score = round(score, 2)
    tier = "Low"
    if score >= 80.0: tier = "Critical"
    elif score >= 60.0: tier = "High"
    elif score >= 40.0: tier = "Medium"
    return score, tier

def simulate_agent_pipeline(prob, crit):
    pred = "Attack" if prob >= 0.50 else "Benign"
    risk_score, risk_tier = calculate_risk(prob, crit)
    
    conf = 1.0
    dist_from_threshold = abs(prob - 0.5)
    if dist_from_threshold < 0.1:
        conf -= 0.3
        
    review_triggered = conf < 0.85
    final_action = "INVESTIGATE" if pred == "Attack" else "IGNORE"
    
    if review_triggered:
        final_risk_score, final_risk_tier = calculate_risk(prob, 5)
    else:
        final_risk_score, final_risk_tier = risk_score, risk_tier
        
    return {
        'Probability': prob,
        'Criticality': crit,
        'Detector_Pred': pred,
        'Initial_Risk_Tier': risk_tier,
        'Decision_Confidence': round(conf, 2),
        'Review_Triggered': review_triggered,
        'Knowledge_Invoked': review_triggered,
        'Final_Risk_Tier': final_risk_tier,
        'Final_Action': final_action
    }

probs = [0.50, 0.60, 0.70, 0.80, 0.84, 0.85, 0.90]
crits = [1, 3, 5]

results = []
for p in probs:
    for c in crits:
        results.append(simulate_agent_pipeline(p, c))
        
df = pd.DataFrame(results)
os.makedirs('artifacts/metrics', exist_ok=True)
df.to_csv('artifacts/metrics/agent_review_behavior.csv', index=False)

md = """# Agent Contribution Validation

## Architectural Analysis
The ARGUS backend implements a deterministic sequential state-machine pipeline (Detector → Risk → Knowledge → Decision).
It is **NOT** an open-ended autonomous multi-agent negotiation system. The logic is hardcoded via the Orchestrator, which ensures strict performance latency and robustness.

## Confidence-Triggered Review Loop
The Orchestrator implements a conditional review loop: if the initial Decision Agent confidence falls below `0.85`, it triggers a secondary review pass.
Based on the Decision Agent implementation, confidence drops by `0.3` if `abs(probability - 0.5) < 0.1`.
Thus, any probability between `0.40` and `0.60` will result in confidence `0.70` (or lower), triggering the review.

During review:
1. **Knowledge Agent** is invoked to retrieve MITRE ATT&CK for ICS context.
2. **Risk Agent** artificially boosts the asset criticality to `5` ("safe mode").
3. **Decision Agent** generates a new explanation incorporating the context and heightened risk tier.

### Simulated Agent Review Behavior
"""
md += "\n```csv\n" + df.to_csv(index=False) + "```\n"
md += """
## Findings
- **Deterministic Action:** The final action (`INVESTIGATE` vs `IGNORE`) is currently structurally hardcoded to the detector's binary prediction. The agents *modulate context, risk severity, and explanation depth*, but do not independently override the mathematical prediction block.
- **Measurable Review Impact:** The review loop quantitatively changes the output state. For uncertain probabilities (`0.50`), a low-criticality asset (`Crit=1`, Tier `Low`) gets artificially escalated during review to `Crit=5`, returning Tier `High`. This ensures uncertain threats against low-tier assets are treated with maximum precaution.
- **Scientific Claim:** ARGUS should NOT claim "fully autonomous multi-agent negotiation". It MUST claim a "deterministic conditionally-triggered multi-agent state machine", which is far more realistic for deterministic SCADA operations.
"""
os.makedirs('artifacts/reports', exist_ok=True)
with open('artifacts/reports/agent_contribution_analysis.md', 'w') as f:
    f.write(md)

print("Phase 7 generated.")
