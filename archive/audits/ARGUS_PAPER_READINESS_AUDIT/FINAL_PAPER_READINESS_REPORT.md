# FINAL ARGUS PAPER READINESS REPORT

**Auditor**: Researcher 3 (Scientific Contribution & Paper-Readiness Audit)  
**Project**: ARGUS — Adaptive Risk-aware Generalized Unified Security Framework  
**Audit Date**: August 27, 2026  
**Domains**: D1=CICIoT2023, D2=NF-ToN-IoT-v2, D3=IEC 60870-5-104 SCADA

---

## 1. OVERALL PAPER READINESS

# 🟡 READY AFTER LIMITED EXPERIMENTS

The core scientific narrative — **cross-domain transfer fails due to representation collapse** — is fully supported by verified multi-seed experiments. The paper is writable today with the existing evidence, but **3 P0 blocking experiments** must be completed to clean up the D3 protocol-aware evidence chain before final submission.

**Critical framing change**: The paper must be framed as an **empirical investigation of transfer failure**, NOT as a successful cross-domain IDS system.

---

## 2. WHAT ARGUS HAS PROVEN

1. **Cross-domain transfer from IoT to SCADA fails catastrophically** (ROC-AUC 0.44–0.56 on D3, near random chance; 5-seed verified on 714K test set)
2. **Failure direction is driven by source class priors** (97.64% attack prior → FP saturation; 72.58% → FN saturation)
3. **4-feature harmonization causes information-theoretic representation collapse** (714K flows → 1,392 unique tuples; entropy drops from 17.84 to 5.84 bits)
4. **Feature resolution scaling monotonically recovers discriminative power** (ROC-AUC: 0.626→0.653→0.654→0.674 across 4→6→8→73 features; 3-seed verified)
5. **Native SCADA CICFlow features recover non-random detection** (ROC-AUC=0.6744±0.0002, MCC=0.2494; 5-seed verified)
6. **Transfer completely collapses under realistic SOC FPR constraints** (Recall=0% at FPR≤1% for all transfer models; Native retains 8.5% recall at 96% precision)
7. **SHAP feature attribution is non-transferable across domains** (source top feature `log_pkt_max` 37.5% → negligible target gain)
8. **Protocol-aware SCADA detection using ASDU/APDU features achieves near-perfect native performance** (ROC-AUC=1.0 under 0% file-overlap grouped splits, surviving volume-matched subsample, DoS exclusion, command-only, and mixed-file confound controls)
9. **Threshold calibration recovers F1 without improving ranking separation** (F1: 0.109→0.372 but ROC-AUC invariant)
10. **FT-Transformer confirms failure is architecture-independent** (ROC-AUC=0.6460 native; transfer failure reproduced with neural attention model)

---

## 3. WHAT ARGUS HAS NOT PROVEN

1. **Cross-domain generalization** — Transfer fails on every tested direction to D3
2. **Risk-aware decision making** — No calibrated probabilities, risk scores, cost matrices, or model disagreement
3. **Multi-model ensemble/fusion benefit** — Models evaluated independently; no ensemble or disagreement analysis
4. **Autonomous multi-agent defense** — All 5 software agents are placeholder stubs
5. **Production deployment readiness** — FPR=87% for best transfer model
6. **Universal/zero-shot detection** — Requires target calibration labels
7. **≥80% cross-domain performance** — No balanced metric achieves 80% on cross-domain transfer
8. **Bidirectional domain adaptation symmetry** — D2→D1 not standardized on same representation

---

## 4. PAPER-READY RESULTS

| Result | Status | Evidence Quality |
|--------|--------|-----------------|
| D1→D3 transfer failure (5-seed) | ✅ GREEN | VERIFIED ORIGINAL |
| D2→D3 transfer failure (5-seed) | ✅ GREEN | VERIFIED ORIGINAL |
| UDA (CORAL/DANN) limits on D3 (5-seed) | ✅ GREEN | VERIFIED ORIGINAL |
| Full ARGUS fusion ceiling (5-seed) | ✅ GREEN | VERIFIED ORIGINAL |
| Native D3 73-feat performance (5-seed) | ✅ GREEN | VERIFIED ORIGINAL |
| FT-Transformer native D3 (5-seed) | ✅ GREEN | VERIFIED ORIGINAL |
| Representation cardinality analysis | ✅ GREEN | VERIFIED ORIGINAL |
| Feature resolution scaling (3-seed) | ✅ GREEN | VERIFIED ORIGINAL |
| Operational FPR-constrained evaluation | ✅ GREEN | VERIFIED ORIGINAL |
| SHAP explainability disconnect | ✅ GREEN | VERIFIED ORIGINAL |
| Prior-shift direction analysis | ✅ GREEN | VERIFIED ORIGINAL |
| Dummy baseline comparisons (5-seed) | ✅ GREEN | VERIFIED ORIGINAL |
| D1→D2 DANN (raw predictions) | ✅ GREEN | VERIFIED ORIGINAL |
| D1→D2 Clean Class-aware CORAL | 🟡 YELLOW | PARTIALLY VERIFIED (single-seed, no raw predictions) |
| D3 protocol-aware grouped detection | 🟡 YELLOW | VERIFIED but needs multi-seed + confound disclosure |
| D3 volume-matched protocol subsample | 🟡 YELLOW | VERIFIED but single-seed, small N |

---

## 5. RESULTS THAT MUST NOT BE USED

| Result | Status | Reason |
|--------|--------|--------|
| REP-01 FullCombined (R4) ROC-AUC≈0.9999 | 🔴 INVALID | `i_msg_ratio` contains explicit label leakage `y_sub*0.25` |
| REP-01 Protocol-aware (R2) ROC-AUC≈0.9999 | 🔴 INVALID | Same `i_msg_ratio` label leakage |
| REP-01 Temporal (R3) features | 🔴 INVALID | Rolling features computed post-shuffle; temporal causality destroyed |
| REP-01 multi-seed statistical significance | 🔴 INVALID | All 5 seeds contaminated by same leakage |
| D1→D2 Class-aware CORAL (diagnostic) | 🔴 LEAKAGE | Used test labels for covariance estimation |
| DANN Result Set A (ARGUS_RESULTS_README.txt) | 🔴 SUPERSEDED | ROC-AUC=0.5226 is incorrect; authoritative is 0.3321 |
| Any claim of ROC-AUC>0.90 on D3 cross-domain | 🔴 UNSUPPORTED | No legitimate cross-domain experiment achieves this |

---

## 6. D1→D2 STATUS

**PARTIALLY VERIFIED & PAPER-READY (with qualifications)**

| Model | ROC-AUC | MCC | Bal Acc | Evidence Status |
|-------|---------|-----|---------|----------------|
| Source-only XGBoost | 0.3230 | -0.031 | 0.497 | RECONSTRUCTED |
| Source-only LightGBM | 0.3230 | -0.031 | 0.497 | PARTIALLY VERIFIED |
| Global CORAL | 0.2852 | -0.161 | 0.445 | RECONSTRUCTED |
| Clean Class-aware CORAL | **0.5970** | **0.386** | **0.711** | PARTIALLY VERIFIED (WINNER) |
| DANN | 0.3321 | 0.013 | 0.500 | **VERIFIED ORIGINAL** |

**Key findings**: Clean Class-aware CORAL is the clear winner on balanced metrics. DANN and source-only models collapse into majority-class prediction (high F1 is misleading). All experiments use same frozen 2.6M-sample test set.

**Gaps**: Single-seed (42) only; raw predictions missing for non-DANN models.

---

## 7. D3 STATUS

**RED for cross-domain transfer | YELLOW for native | YELLOW for protocol-aware (pending cleanup)**

- **Cross-domain transfer to D3**: All methods fail. Best ROC-AUC = 0.5644 (D1→D3 DANN). Full ARGUS fused: MCC=0.12, FPR=87%.
- **Native D3 (73-feat CICFlow)**: ROC-AUC=0.6744, MCC=0.2494. Genuine but moderate signal.
- **Protocol-aware D3 (ASDU/APDU)**: ROC-AUC=1.0000 under grouped splits. Performance verified genuine via: volume-matched subsample (ROC-AUC=0.9999), U-message ablation (ROC-AUC=1.0000 without U-messages), i_msg_ratio ablation (ROC-AUC=0.9999 without i_msg_ratio), DoS exclusion (ROC-AUC=1.0000 on single-shot only), mixed-file-only evaluation (ROC-AUC=0.9999). **BUT**: Volume confound must be disclosed; protocol dataset is separate extraction (47K vs 714K).

---

## 8. DANN STATUS

**D1→D2 DANN**: VERIFIED ORIGINAL. Raw predictions (2.6M rows) match recomputation bit-for-bit. ROC-AUC=0.3321 (authoritative). Historical README value of 0.5226 is INVALID/SUPERSEDED.

**D1→D3 DANN**: VERIFIED. ROC-AUC=0.5644 (best transfer method on D3). Still near-random.

**D2→D3 DANN**: VERIFIED. ROC-AUC=0.4706. Negative MCC (-0.097). Worse than random.

---

## 9. REP-01 STATUS

# 🔴 FAIL — SCIENTIFICALLY INVALID

- **Explicit label leakage**: `i_msg_ratio = <raw> + (y_sub * 0.25)` — target label directly embedded in feature
- **Session/capture leakage**: Pure random `train_test_split` mixes same-session flows across splits
- **Temporal causality failure**: Rolling features computed after random shuffling
- **All ROC-AUC>0.90 claims from REP-01 are invalid**
- **5-seed results meaningless** — all seeds contaminated by same leakage

**However**: Verification reports independently confirm that protocol-aware detection WITHOUT `i_msg_ratio` still achieves ROC-AUC=0.9999 under proper grouped splits. The signal is genuine; only the REP-01 pipeline is invalid.

---

## 10. MULTI-MODEL STATUS

**YELLOW — Partially Demonstrated**

- ✅ LightGBM evaluated on D3 (5-seed, native and transfer)
- ✅ FT-Transformer evaluated on D3 (5-seed, native; small/medium/large capacity)
- ✅ XGBoost evaluated on D1→D2 (single-seed)
- ❌ No ensemble or model fusion combining multiple model families
- ❌ No calibrated multi-model disagreement analysis
- ❌ No same-task comparison of all three model families

**Can claim**: "Multiple model architectures independently confirm transfer failure and native detection"  
**Cannot claim**: "Multi-model ensemble" or "model disagreement-based detection"

---

## 11. RISK-AWARE STATUS

**RED — Conceptual Only**

- ✅ Threshold sweeps exist under FPR constraints (SOC budgets)
- ✅ FPR-Recall trade-off analysis completed
- ❌ No calibrated probabilities usable as confidence scores
- ❌ No model disagreement or uncertainty quantification
- ❌ No cost-sensitive decision framework
- ❌ No risk scores or risk level classification
- ❌ D3 transfer model probabilities are degenerate (70% of samples get same probability 0.759)

**Minimum experiment needed**: Platt scaling or isotonic calibration of native D3 model → calibrated probability → demonstrate confidence-based risk scoring on held-out test set.

---

## 12. EXPLAINABILITY STATUS

**YELLOW — Post-hoc Explanation Demonstrated, Not Intrinsic**

- ✅ SHAP TreeExplainer attribution on source-trained models
- ✅ Feature importance disconnect across domains quantified
- ✅ SHAP-driven MITRE ATT&CK vector retrieval demonstrated (differential queries work)
- ❌ No attribution stability analysis across seeds
- ❌ No SHAP on target-adapted models (only source models)
- ❌ Post-hoc explanation only, not intrinsically explainable cross-domain detection

**Can claim**: "Post-hoc SHAP analysis reveals that feature utility is fundamentally non-transferable across network domains"  
**Cannot claim**: "Explainable cross-domain detection"

---

## 13. P0 BLOCKING EXPERIMENTS

| # | Experiment | Estimated Effort | Critical Dependency |
|---|-----------|-----------------|-------------------|
| 1 | **Clean D3 protocol feature extraction** — Re-extract protocol features without `y_sub` label injection | LOW (ablation shows `i_msg_ratio` removal retains ROC-AUC=0.9999; just needs formal clean pipeline run) | Validates protocol-aware detection claims |
| 2 | **Clean D3 temporal features** — Re-compute rolling features with chronological ordering before splits | MODERATE (requires re-ordering dataset by timestamp before rolling window computation) | Validates temporal feature contribution |
| 3 | **D3 protocol-aware multi-seed** — Run grouped protocol model across 5 seeds | LOW (grouped split + LightGBM training, 5 runs on 47K flows) | Provides mean±SD for protocol claims |

**Important note**: P0 #1 may already be partially resolved. The `verification/i_msg_ratio_leakage_check.md` report shows that ablating `i_msg_ratio` entirely retains ROC-AUC=0.9999 under grouped splits. A formal clean pipeline run (without `y_sub` in feature computation, not just feature exclusion) would fully resolve this.

---

## 14. P1 HIGH-VALUE EXPERIMENTS

| # | Experiment | Estimated Effort |
|---|-----------|-----------------|
| 1 | D1→D2 multi-seed (5 seeds for Clean CORAL + DANN) | MODERATE |
| 2 | D1→D2 raw per-sample predictions for non-DANN models | LOW |
| 3 | Bootstrap 95% CIs for primary D3 metrics | LOW |
| 4 | Formal volume confound disclosure table | LOW (data exists) |

---

## 15. P2 OPTIONAL EXPERIMENTS

| # | Experiment | Estimated Effort |
|---|-----------|-----------------|
| 1 | DeLong ROC comparison test | LOW |
| 2 | D2→D1 reverse adaptation (standardized) | MODERATE |
| 3 | McNemar paired prediction test | LOW |

---

## 16. CLAIMS WE CAN MAKE

1. ✅ "Cross-domain transfer from IoT testbeds to operational SCADA protocols fails due to representation collapse"
2. ✅ "4-feature harmonization causes a 99.8% state-space compression and 12-bit entropy loss"
3. ✅ "Transfer failure direction is driven by source class priors"
4. ✅ "Standard domain adaptation (CORAL, DANN) cannot overcome the information-theoretic bottleneck"
5. ✅ "Threshold calibration recovers F1 without improving ranking separation (ROC-AUC invariant)"
6. ✅ "Feature resolution scaling monotonically recovers discriminative power"
7. ✅ "Native SCADA features provide genuine but moderate detection capability (ROC-AUC=0.67)"
8. ✅ "Transfer models completely collapse under realistic SOC false alarm budgets"
9. ✅ "Feature attribution (SHAP) is non-transferable across domains"
10. ✅ "Transfer failure is architecture-independent (verified on both GBDT and Transformer)"
11. ✅ (qualified) "Protocol-aware IEC 104 ASDU/APDU features achieve near-perfect native SCADA detection" (with confound disclosure)

---

## 17. CLAIMS WE CANNOT MAKE

1. ❌ "Generalizes across domains" → Transfer fails
2. ❌ "Robust cross-domain IDS" → MCC=0.12 maximum for cross-domain
3. ❌ "Risk-aware" → No calibrated confidence or cost framework
4. ❌ "Multi-model ensemble" → Models evaluated independently
5. ❌ "Explainable cross-domain detection" → Only post-hoc on source model
6. ❌ "SCADA-ready" → Only native in-domain detection works
7. ❌ "Deployment-ready" → FPR=87% for transfer
8. ❌ "Universal" → 3 domains, transfer fails
9. ❌ "≥80% balanced performance" → Not achieved cross-domain
10. ❌ "Zero-shot generalization" → Requires target calibration
11. ❌ "Autonomous multi-agent defense" → Stubs only
12. ❌ "REP-01 near-perfect SCADA detection" → Leakage invalidated

---

## 18. FINAL TABLE PLAN

### Main Paper (5 tables)
| Table | Content | Status |
|-------|---------|--------|
| Table 1 | Dataset characteristics (D1, D2, D3) | ✅ READY |
| Table 2 | Cross-domain transfer benchmark (5-seed, 11 methods + dummies) | ✅ READY |
| Table 3 | Harmonized 4-feat vs Native 73-feat | ✅ READY |
| Table 4 | Feature resolution scaling (4→6→8→73) | ✅ READY |
| Table 5 | Operational SOC FPR-constrained evaluation | ✅ READY |

### Supplementary (5 tables)
| Table | Content | Status |
|-------|---------|--------|
| Table 6 | D1→D2 adaptation comparison | ✅ READY (single-seed) |
| Table 7 | FT-Transformer regularization ablation | ✅ READY |
| Table 8 | Native model hierarchy (GBDT vs FTT scaling) | ✅ READY |
| Table 9 | Protocol-aware confound controls | ✅ READY (needs formatting) |
| Table 10 | SHAP feature importance table | ✅ READY |

---

## 19. FINAL FIGURE PLAN

### Main Paper (5 figures)
| Figure | Content | Status |
|--------|---------|--------|
| Fig 1 | ARGUS experimental framework | ✅ READY (300 DPI) |
| Fig 2 | ROC/PR curve overlay (all methods) | ✅ READY (300 DPI) |
| Fig 3 | State-space compression visualization | ✅ READY (300 DPI) |
| Fig 4 | FPR vs Recall operational curve | ✅ READY (300 DPI) |
| Fig 5 | SHAP vs Target Gain disconnect | ✅ READY (300 DPI) |

### Supplementary (7 figures)
| Figure | Content | Status |
|--------|---------|--------|
| Fig 6 | Cross-domain degradation progression | ✅ READY |
| Fig 7 | Feature resolution scaling progression | ✅ READY (needs reformatting) |
| Fig 8 | Multi-seed stability error bars | ✅ READY |
| Fig 9 | Calibration reliability diagram | ✅ READY |
| Fig 10 | Probability distribution histogram | ✅ READY |
| Fig 11 | Confusion matrices composite | 🟡 Needs assembly |
| Fig 12 | Protocol feature importance | 🟡 Needs assembly |

---

## 20. 6–7 PAGE PAPER STRUCTURE

### Section 1 — Introduction (0.75 pages)
- **Purpose**: Frame the transfer failure problem for SCADA IDS
- **Evidence**: EXP-01 headline failure numbers
- **Tables**: None
- **Figures**: Fig 1 (Framework)

### Section 2 — Problem Formalization (0.75 pages)
- **Purpose**: Formalize dual-shift phenomenon mathematically
- **Evidence**: EXP-02 prior-shift analysis
- **Tables**: Table 1 (Datasets)
- **Figures**: None

### Section 3 — Methodology (1 page)
- **Purpose**: CORAL/DANN/Fusion pipeline and zero-leakage protocol
- **Evidence**: Pipeline architecture, split protocol
- **Tables**: None
- **Figures**: Fig 1 (Framework)

### Section 4 — Experimental Evaluation (2 pages)
- **Purpose**: Present all results
- **Evidence**: EXP-01 through EXP-08, EXP-04, NR-04
- **Tables**: Tables 2–5
- **Figures**: Figs 2–5

### Section 5 — Discussion (0.75 pages)
- **Purpose**: Interpret representation collapse; implications for ICS
- **Evidence**: Cardinality analysis, protocol comparison
- **Tables**: None
- **Figures**: None

### Section 6 — Limitations (0.5 pages)
- **Purpose**: Transparent disclosure of all limitations
- **Evidence**: Volume confound, REP-01 invalidation, single-seed D1→D2
- **Tables**: None
- **Figures**: None

### Section 7 — Conclusion (0.25 pages)
- **Purpose**: Summarize findings and future directions
- **Evidence**: Summary statistics
- **Tables**: None
- **Figures**: None

---

## 21. SINGLE MOST IMPORTANT NEXT EXPERIMENT

### **Clean D3 Protocol Feature Extraction (P0 #1)**

**Objective**: Formally re-extract all protocol features for the IEC 60870-5-104 dataset without any label (`y_sub`) injection, then re-train and evaluate under grouped file-split across 5 seeds.

**Why**: This single experiment resolves the entire REP-01 invalidation chain. Existing ablation evidence (removing `i_msg_ratio` retains ROC-AUC=0.9999) strongly suggests the signal is genuine. A clean pipeline run would:
1. Validate protocol-aware detection claims
2. Enable paper inclusion of SCADA-native protocol results
3. Complete the narrative from "transfer fails" → "protocol-aware detection succeeds"
4. Provide the strongest positive result for the paper

**Estimated effort**: LOW — the leakage is isolated to a single feature computation line. A clean re-extraction and 5-seed evaluation on 47K flows should complete in <2 hours.

---

## FINAL ANSWER

> **"What exactly can we defend in a peer-reviewed paper today, what is still missing, and what is the minimum work required to make the paper publication-ready?"**

### What we can defend today:
A rigorous empirical investigation proving that cross-domain transfer from IoT testbeds to SCADA protocols fails due to information-theoretic representation collapse. This is supported by 85+ evaluated runs across 5 seeds, comprehensive dummy baseline comparisons, domain adaptation experiments (CORAL, DANN, fusion), feature resolution scaling, operational SOC evaluation, neural architecture controls, and explainability analysis. All on a frozen 714,453-sample test set with zero leakage.

### What is still missing:
1. Clean D3 protocol features (without label leakage) — blocks SCADA-native positive result
2. Multi-seed protocol-aware evaluation — blocks statistical confidence on native SCADA
3. Clean temporal features — blocks temporal feature contribution claims

### Minimum work to publication-ready:
**3 experiments, estimated total effort: 1-2 days**
1. Clean protocol feature extraction + 5-seed grouped evaluation (~2 hours)
2. Clean temporal feature extraction with chronological ordering (~4 hours)
3. 5-seed grouped protocol model runs (~1 hour)

After these 3 experiments, the paper is **fully ready for submission** as an empirical investigation of transfer failure with a strong positive result showing protocol-aware native detection as the solution.
