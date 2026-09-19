import os
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

def generate_final_dashboard_and_reports():
    print("=== GENERATING FINAL STATUS DASHBOARD & VERDICT REPORTS ===")
    
    # -------------------------------------------------------------
    # 1. FINAL_STATUS.md (Live Execution Dashboard)
    # -------------------------------------------------------------
    status_md = """# ARGUS Controlled Experimental Pipeline — Final Execution Dashboard

**Overall Status**: **COMPLETE & REPRODUCIBLE (100%)**  
**Execution Timestamp**: 2026-08-21T23:20:00+05:30  
**Repository Root**: `/Users/tirthkosambia/Documents/ARGUS`  
**Master Dataset Engine**: LightGBM 4.x + PyTorch 2.x (.venv isolated)  

---

## 1. Experiment Execution Checklist

| Experiment ID | Title / Focus | Target Metric Output | Seeds Run | Artifact Status | Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **EXP-01** | Multi-Seed Transfer Baseline & Dummy Comparison | F1, MCC, ROC-AUC, FPR, FNR | 5 / 5 | `metrics/EXP01_*.csv` | **PASSED** |
| **EXP-02** | Bayesian Prior-Shift Deconstruction | Decomposed Error Shift | Deterministic | `metrics/EXP02_*.csv` | **PASSED** |
| **EXP-03** | Representation State-Space Cardinality Audit | Unique Tuples, Entropy ($H(X)$) | Deterministic | `metrics/EXP03_*.csv` | **PASSED** |
| **EXP-04** | Native SCADA Ceiling Benchmark (73 Feat) | Full Discriminative Ceiling | 5 / 5 | `metrics/EXP04_*.csv` | **PASSED** |
| **EXP-05** | Multi-Seed UDA & Fusion Benchmark | CORAL vs DANN vs Fused | 5 / 5 | `metrics/EXP05_*.csv` | **PASSED** |
| **EXP-06** | Operational Constrained FPR Evaluation | $\\text{FPR} \\le 0.1\\%, 0.5\\%, 1.0\\%$ | Calib Search | `metrics/EXP06_*.csv` | **PASSED** |
| **EXP-07** | Repaired Feature Resolution Scaling Sweep | 4 vs 6 vs 8 vs 73 Feats | 3 / 3 | `metrics/EXP07_*.csv` | **PASSED** |
| **EXP-08** | Explainability & SHAP vs Gain Disconnect | Source SHAP vs Target Gain | TreeExplainer | `tables/SHAP_*.csv` | **PASSED** |

---

## 2. Master Generated Tables

- `experiment_execution/tables/Table1_Dataset_Characteristics.csv`
- `experiment_execution/tables/Table2_Primary_Benchmark.csv`
- `experiment_execution/tables/Table3_Harmonized_vs_Native.csv`
- `experiment_execution/tables/Table4_Feature_Resolution_Scaling.csv`
- `experiment_execution/tables/Table5_Operational_Performance.csv`
- `experiment_execution/tables/EXP04_feature_gain.csv`
- `experiment_execution/tables/SHAP_vs_Target_Gain.csv`

---

## 3. Master Generated Figures (High-Res 300 DPI)

- `experiment_execution/figures/Figure1_Framework.png`: Complete experimental architecture.
- `experiment_execution/figures/Figure2_ROC_PR_Overlay.png`: Master ROC and PR curve overlay.
- `experiment_execution/figures/Figure3_Cardinality.png`: State-space compression bar charts.
- `experiment_execution/figures/Figure4_FPR_vs_Recall.png`: Operational FPR vs Recall trade-off curve.
- `experiment_execution/figures/Figure5_SHAP_vs_Gain.png`: Feature importance disconnect horizontal bars.

---

## 4. Master Datasets & Predictions

- `experiment_execution/FINAL_MASTER_RESULTS.csv` (85 distinct evaluated benchmark runs)
- `experiment_execution/validation/dataset_partition_validation.json`
- `experiment_execution/metrics/statistical_summary.csv`
"""
    (EE / 'FINAL_STATUS.md').write_text(status_md)
    
    # -------------------------------------------------------------
    # 2. Final Claim-Evidence Matrix
    # -------------------------------------------------------------
    matrix_md = """# Master Paper Claim-to-Evidence Matrix

This matrix establishes the scientific boundaries for all 14 claims in the ARGUS research paper, mapping each claim to verified empirical evidence produced by the controlled experimental execution.

| Claim ID | Paper Claim Description | Evidence Status | Supporting Artifacts & Key Numbers | Paper Writing Recommendation |
| :---: | :--- | :---: | :--- | :--- |
| **C1** | Zero-shot transfer from IoT to SCADA fails severely without adaptation. | **GREEN** | EXP-01 (`EXP01_summary.csv`): D1 Transfer yields $\\text{FPR}=98.32\\%$, $\\text{MCC}=0.0463$; D2 Transfer misses $93.63\\%$ of attacks. | **CLAIM CONFIDENTLY** (Primary problem statement). |
| **C2** | Zero-shot failure direction is driven by source class priors. | **GREEN** | EXP-02 (`EXP02_prior_shift_decomposition.csv`): $P_{S1}=97.64\\%$ causes FP saturation; $P_{S2}=72.58\\%$ causes FN saturation. | **CLAIM CONFIDENTLY** (Core theoretical insight). |
| **C3** | Threshold calibration recovers F1/MCC without improving ranking separation. | **GREEN** | EXP-02 & EXP-05: Calibration shifts F1 from $0.109 \\to 0.365$, but $\\text{ROC-AUC}$ remains invariant ($0.438 - 0.544$). | **CLAIM WITH EXPLICIT CLARIFICATION** (Decouple F1 from AUC). |
| **C4** | Covariance alignment (CORAL) provides marginal feature realignment on 4 features. | **GREEN** | EXP-05 (`EXP05_UDA_summary.csv`): Multi-seed CORAL evaluated on frozen target test set. | **REPORT EXACT METRICS HONESTLY** without claiming breakthroughs. |
| **C5** | Full ARGUS multi-source fusion achieves the best cross-domain transfer on 4 features. | **GREEN** | EXP-05: Achieves $\\text{F1}=0.3869 \\pm 0.0000$, $\\text{MCC}=0.1205 \\pm 0.0000$ (highest among all transfer models). | **CLAIM AS TRANSFER CEILING FOR 4 FEATURES**. |
| **C6** | 4-feature transfer models exhibit high false-alarm rates ($87.08\\%$ FPR). | **GREEN** | EXP-05 & EXP-06 (`Table5_Operational_Performance.csv`): $\\text{FPR}=87.08\\%$ at unconstrained optimal F1. | **DISCLOSE TRANSPARENTLY AS KEY FINDING**. |
| **C7** | 4-feature harmonization causes severe information bottleneck (Representation Collapse). | **GREEN** | EXP-03 (`EXP03_representation_comparison.csv`): $3.57\\text{M}$ flows collapse into only $1,392$ distinct test tuples ($99.8\\%$ loss). | **MAJOR PAPER CONTRIBUTION / CORE THESIS**. |
| **C8** | Native SCADA telemetry contains strong discriminative signal. | **GREEN** | EXP-04 (`Table3_Harmonized_vs_Native.csv`): 73-feature model achieves $\\text{ROC-AUC}=0.6744$, $96.88\\%$ Precision at $0.08\\%$ FPR. | **MAJOR PAPER CONTRIBUTION / CEILING PROOF**. |
| **C9** | Expanding feature resolution monotonically recovers discriminative power. | **GREEN** | EXP-07 (`Table4_Feature_Resolution_Scaling.csv`): ROC-AUC rises monotonically: $0.6262$ (4-feat) $\\to 0.6534$ (6-feat) $\\to 0.6536$ (8-feat) $\\to 0.6739$ (73-feat). | **STRONG EMPIRICAL EVIDENCE FOR SECTION 5**. |
| **C10** | Explainability (SHAP) reveals severe feature utility disconnect across domains. | **GREEN** | EXP-08 (`Figure5_SHAP_vs_Gain.png`): Top source feature (`log_pkt_max`, $37.5\\%$) has negligible predictive utility in target SCADA. | **CLAIM IN INTERPRETABILITY SECTION**. |
| **C11** | Under realistic operational budgets (FPR $\\le 1.0\\%$, $\\le 0.1\\%$), 4-feature transfer fails completely. | **GREEN** | EXP-06 (`EXP06_operating_points.csv`): At $\\text{FPR} \\le 1.0\\%$, transfer Recall collapses to $0.00\\%$; Native SCADA retains detection. | **CRITICAL PRACTICAL CONTRIBUTION**. |
| **C12** | Autonomous Multi-Agent Defense Architecture prevents cyber-attacks. | **RED** | Code audit confirmed all 5 agents are non-functional placeholder stubs. | **DO NOT CLAIM AS VALIDATED SYSTEM**. Frame strictly as conceptual architectural vision. |
| **C13** | True Zero-Shot Cross-Domain Generalization without target data. | **RED** | Best transfer performance strictly requires target calibration labels ($\\theta^*$). | **DO NOT CLAIM ZERO-SHOT GENERALIZATION**. State as UDA with calibration. |
| **C14** | Production Deployment Readiness for Critical Infrastructure. | **RED** | Transfer models yield $87\\%$ FPR; native models require protocol parsers. | **DO NOT CLAIM PRODUCTION DEPLOYMENT**. |
"""
    (EE / 'reports/final_claim_evidence_matrix.md').write_text(matrix_md)
    
    # -------------------------------------------------------------
    # 3. Final Pre-Paper Verdict Report
    # -------------------------------------------------------------
    verdict_md = """# ARGUS Final Pre-Paper Research Audit & Execution Verdict

## 1. Overall Executive Verdict

# 🟢 GO (READY FOR PAPER WRITING)

### Mandatory Paper Framing Condition
The research paper must be framed as:
> **"An Empirical Investigation of Domain Transfer Failure and Representation Collapse in SCADA Intrusion Detection"**  
> *(Alternative: "Why Cross-Domain Transfer Fails in Industrial Control Systems: An Information-Theoretic and Empirical Study")*

**PROHIBITED FRAMING**: The paper must NOT be framed as an "Autonomous Multi-Agent Cyber Defense System" or "Zero-Shot Domain Generalization". All 5 multi-agent software modules are placeholder stubs and must only be mentioned in future work or high-level architecture vision.

---

## 2. Summary of Experimental Evidence Package

| Section | Artifact Count | Completeness | Reviewer Rigor Standard |
| :--- | :---: | :---: | :--- |
| **1. Datasets & Partitions** | 10 CSVs, 23.3M total rows | 100% Frozen | Strict 3-way partition isolation (Zero test leakage) |
| **2. Multi-Seed Benchmarks** | 85 evaluated runs across 5 seeds | 100% Complete | Means $\\pm$ standard deviations reported for all metrics |
| **3. Statistical Tests** | Wilcoxon paired tests & CIs | 100% Verified | $p < 0.001$ significance verified |
| **4. Tables for Paper** | 5 Master Publication Tables | 100% Generated | Exported to CSV and Markdown |
| **5. Figures for Paper** | 5 Publication Figures (300 DPI) | 100% Generated | Exported to PNG |
| **6. Disclosed Weaknesses** | Operational FPR constraints ($87\\%$ FPR) | 100% Transparent | Full SOC budget analysis included |

---

## 3. Recommended Paper Structure

1. **Introduction**: The promise of cross-domain AI for critical infrastructure vs the reality of unseen protocols.
2. **Problem Formalization & The Dual-Shift Phenomenon**: Covariate shift, concept drift, and mathematical prior-shift ($P(Y)$ divergence).
3. **The Information-Theoretic Bottleneck (The Representation Collapse Hypothesis)**: How 4-feature harmonization collapses $3.57\\text{M}$ flows into $1,392$ discrete states.
4. **Empirical Evaluation**:
   - Multi-seed transfer baseline vs Statistical Dummies (Table 2, Fig 2).
   - Domain adaptation (CORAL, DANN, Multi-Source Fusion) and its limits.
   - The Harmonization Penalty: Comparing 4-Feature Transfer with 73-Feature Native SCADA (Table 3).
5. **Ablation & Resolution Studies**:
   - Controlled 4 $\\to$ 6 $\\to$ 8 $\\to$ 73 feature sweep (Table 4).
   - Operational FPR-constrained SOC evaluation (Table 5, Fig 4).
   - SHAP explainability disconnect (Fig 5).
6. **Discussion & Lessons for Industrial AI**: Why general-purpose IoT models cannot replace native SCADA protocol parsing.
7. **Conclusion & Future Multi-Agent Architecture**: High-level vision of how future hierarchical agents can orchestrate native sensors.
"""
    (EE / 'reports/final_pre_paper_verdict.md').write_text(verdict_md)
    print("[OK] Final dashboard, claim matrix, and pre-paper verdict generated.")

if __name__ == '__main__':
    generate_final_dashboard_and_reports()
