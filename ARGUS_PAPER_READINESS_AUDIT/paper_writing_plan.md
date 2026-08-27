# ARGUS Paper Writing Plan

## Approved Title
**"An Empirical Investigation of Domain Transfer Failure and Representation Collapse in SCADA Intrusion Detection"**

*Alternative: "Why Cross-Domain Transfer Fails in Industrial Control Systems: An Information-Theoretic and Empirical Study"*

## Paper Length Target
6–7 pages (IEEE double-column or similar conference format)

---

## Prohibited Framings
- ❌ "Autonomous Multi-Agent Cyber Defense System" (agents are placeholder stubs)
- ❌ "Zero-Shot Domain Generalization" (requires target calibration)
- ❌ "Production Deployment-Ready IDS" (FPR=87% for transfer)
- ❌ "Universal Cross-Domain Detection" (fails on SCADA)
- ❌ "≥80% Cross-Domain Performance" (aspirational, not achieved)

---

## Strongest Defensible Narrative

```
Cross-domain transfer failure on SCADA (verified, 5-seed)
    ↓
Failure direction driven by source class priors (verified)
    ↓
Information-theoretic representation collapse (verified, entropy quantified)
    ↓
Feature resolution scaling monotonically recovers signal (verified, 3-seed)
    ↓
Native SCADA features recover discriminative power (verified, 5-seed, ROC-AUC 0.67)
    ↓
Protocol-aware features achieve near-perfect native detection (verified with confound controls)
    ↓
Explainability (SHAP) reveals complete feature utility disconnect (verified)
    ↓
Operational SOC constraints expose total transfer collapse (verified)
```

**Stages NOT experimentally supported (do not include in narrative):**
- Risk-aware decision making (conceptual only)
- Multi-model ensemble disagreement (not implemented)
- Calibrated cross-domain confidence (probabilities are degenerate)
- Autonomous multi-agent orchestration (stubs only)

---

## Section Outline

### Section 1: Introduction (~0.75 pages)
- The promise of transferable AI for critical infrastructure
- The specific challenge: IoT testbeds vs operational SCADA protocols
- Key question: Can models trained on CICIoT2023/NF-ToN-IoT-v2 detect attacks on IEC 60870-5-104?
- Contribution summary: Rigorous empirical investigation revealing representation collapse

### Section 2: Problem Formalization (~0.75 pages)
- Dual-shift decomposition: $P_S(X) \neq P_T(X)$, $P_S(Y|X) \neq P_T(Y|X)$, $P_S(Y) \neq P_T(Y)$
- Prior shift direction theorem: High $P_S(Y=1)$ → FP saturation; Low $P_S(Y=1)$ → FN saturation
- **Table 1** (Dataset characteristics)

### Section 3: Methodology (~1 page)
- 4-feature harmonized representation and its motivation
- CORAL alignment operator (source-to-target covariance alignment)
- DANN adversarial feature invariance
- Multi-source fusion with prior correction
- Zero-leakage evaluation protocol (train/adapt/calib/test isolation)
- **Figure 1** (Framework)

### Section 4: Experimental Evaluation (~2 pages)
#### 4.1 Cross-Domain Transfer Fails
- Multi-seed benchmark vs dummy baselines (**Table 2**, **Figure 2**)
- All transfer ROC-AUC 0.44–0.56 (near random)
- UDA (CORAL, DANN) cannot overcome 4-feature bottleneck

#### 4.2 The Representation Collapse Hypothesis
- 714K flows → 1,392 unique tuples; entropy 17.84 → 5.84 bits (**Figure 3**)
- Feature resolution scaling: 4→6→8→73 features monotonically recovers AUC (**Table 4**)

#### 4.3 Native SCADA Ceiling
- 73-feature native LightGBM: ROC-AUC=0.6744, MCC=0.2494 (**Table 3**)
- FT-Transformer comparison: ROC-AUC=0.6460 (architecture-independent confirmation)

#### 4.4 Operational Evaluation
- SOC FPR constraints: Transfer collapses at FPR≤1%; Native retains 8.5% recall at 96% precision (**Table 5**, **Figure 4**)

#### 4.5 Explainability Disconnect
- Source SHAP: `log_pkt_max` 37.5% importance
- Target Gain: `Fwd Header Len` dominates
- Feature importance is non-transferable (**Figure 5**)

### Section 5: Discussion (~0.75 pages)
- Why generic features fail: SCADA attacks operate at ASDU/APDU layer
- The harmonization tax: Cross-domain compatibility vs domain-specific signal
- Implications for ICS security: Protocol-native sensors are necessary

### Section 6: Limitations (~0.5 pages)
- Volume confound in D3 protocol dataset (disclose with matched subsample evidence)
- D1→D2 is single-seed (acknowledged)
- REP-01 invalidation (leakage identified and quarantined)
- No true risk-aware or ensemble validation
- Three domains may not generalize to all ICS protocols

### Section 7: Conclusion (~0.25 pages)
- Cross-domain IDS transfer fails due to representation collapse
- Native domain-specific features are essential for SCADA
- Future work: Protocol-aware hierarchical detection; multi-agent orchestration

---

## Main Paper Tables (5)
1. Table 1: Dataset characteristics
2. Table 2: Cross-domain transfer benchmark (5-seed)
3. Table 3: Harmonized vs Native representation
4. Table 4: Feature resolution scaling
5. Table 5: Operational SOC false alarm evaluation

## Main Paper Figures (5)
1. Fig 1: Framework architecture
2. Fig 2: ROC/PR overlay
3. Fig 3: State-space compression
4. Fig 4: FPR vs Recall operational curve
5. Fig 5: SHAP vs Gain disconnect

---

## Supplementary Material
- D1→D2 adaptation comparison (Table 6)
- Neural robustness ablation (Table 7)
- Native model hierarchy (Table 8)
- Protocol-aware confound controls (Table 9)
- SHAP feature table (Table 10)
- Extended figures (7–12)
- Multi-seed individual run results
- Runtime statistics
- Full confusion matrices
- Extended SHAP analysis
- D3 validity audit and REP-01 leakage report
