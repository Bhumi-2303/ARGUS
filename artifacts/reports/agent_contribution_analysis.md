# Agent Contribution Validation

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

```csv
Probability,Criticality,Detector_Pred,Initial_Risk_Tier,Decision_Confidence,Review_Triggered,Knowledge_Invoked,Final_Risk_Tier,Final_Action
0.5,1,Attack,Low,0.7,True,True,High,INVESTIGATE
0.5,3,Attack,Medium,0.7,True,True,High,INVESTIGATE
0.5,5,Attack,High,0.7,True,True,High,INVESTIGATE
0.6,1,Attack,Medium,0.7,True,True,High,INVESTIGATE
0.6,3,Attack,High,0.7,True,True,High,INVESTIGATE
0.6,5,Attack,High,0.7,True,True,High,INVESTIGATE
0.7,1,Attack,Medium,1.0,False,False,Medium,INVESTIGATE
0.7,3,Attack,High,1.0,False,False,High,INVESTIGATE
0.7,5,Attack,Critical,1.0,False,False,Critical,INVESTIGATE
0.8,1,Attack,Medium,1.0,False,False,Medium,INVESTIGATE
0.8,3,Attack,High,1.0,False,False,High,INVESTIGATE
0.8,5,Attack,Critical,1.0,False,False,Critical,INVESTIGATE
0.84,1,Attack,Medium,1.0,False,False,Medium,INVESTIGATE
0.84,3,Attack,High,1.0,False,False,High,INVESTIGATE
0.84,5,Attack,Critical,1.0,False,False,Critical,INVESTIGATE
0.85,1,Attack,Medium,1.0,False,False,Medium,INVESTIGATE
0.85,3,Attack,High,1.0,False,False,High,INVESTIGATE
0.85,5,Attack,Critical,1.0,False,False,Critical,INVESTIGATE
0.9,1,Attack,High,1.0,False,False,High,INVESTIGATE
0.9,3,Attack,High,1.0,False,False,High,INVESTIGATE
0.9,5,Attack,Critical,1.0,False,False,Critical,INVESTIGATE
```

## Findings
- **Deterministic Action:** The final action (`INVESTIGATE` vs `IGNORE`) is currently structurally hardcoded to the detector's binary prediction. The agents *modulate context, risk severity, and explanation depth*, but do not independently override the mathematical prediction block.
- **Measurable Review Impact:** The review loop quantitatively changes the output state. For uncertain probabilities (`0.50`), a low-criticality asset (`Crit=1`, Tier `Low`) gets artificially escalated during review to `Crit=5`, returning Tier `High`. This ensures uncertain threats against low-tier assets are treated with maximum precaution.
- **Scientific Claim:** ARGUS should NOT claim "fully autonomous multi-agent negotiation". It MUST claim a "deterministic conditionally-triggered multi-agent state machine", which is far more realistic for deterministic SCADA operations.
