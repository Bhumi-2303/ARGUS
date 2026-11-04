# ARGUS Research Supervisor & Editorial Handoff Briefing (`paper/RESEARCH_SUPERVISOR_HANDOFF.md`)

**Date**: November 4, 2026  
**Recipient**: Research Supervisor / Principal Investigator / Academic Collaborator  
**Subject**: Publication Repository Architecture, Empirical Evidence Inventory & Journal Submission Readiness  

---

## 1. Primary Manuscript Location

The primary academic draft is housed in [`paper/manuscripts/main/`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/main/):

- **Authoritative Manuscript (DOCX)**:
  [`paper/manuscripts/main/ARGUS_paper_v2_representation_resolution.docx`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/main/ARGUS_paper_v2_representation_resolution.docx)  
  *Size*: 1,119,018 bytes | *SHA-256*: `b074f4f0d064ecb7f36f82c9a6ae82bfcd936b26437b33bc7720d1612e7e1b25`  
  *Content*: Complete journal article containing full narrative, mathematical derivations, exhibit references, and embedded figures.
- **Verbatim Text Transcript (TXT)**:
  [`paper/manuscripts/main/paper_text.txt`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/main/paper_text.txt)  
  *Size*: 32,782 bytes | *SHA-256*: `6cae4ceedbaf19cb7561302bbd3a55ecdebd195983cb05b67a1eaacc3365586d`  
  *Purpose*: Exact text transcript used for automated claim audits and text-matching.

*Compatibility Note*: Symbolic links are maintained at `paper/manuscripts/` for existing paths.

---

## 2. Methodology Documentation Location

All methodological specifications are modularly organized in [`paper/methodology/`](file:///home/bhumi/GitHub/ARGUS/paper/methodology/):

1. **Datasets & Partitions**: [`paper/methodology/01_DATASETS_AND_PREPROCESSING.md`](file:///home/bhumi/GitHub/ARGUS/paper/methodology/01_DATASETS_AND_PREPROCESSING.md)  
   Details on CICIoT2023 (D1), NF-ToN-IoT-v2 (D2), and SCADA IEC-104 (D3), including sample counts, class distributions, and frozen test splits.
2. **Feature Harmonization & Scaling**: [`paper/methodology/02_FEATURE_HARMONIZATION.md`](file:///home/bhumi/GitHub/ARGUS/paper/methodology/02_FEATURE_HARMONIZATION.md)  
   Mathematical formulas for ARGUS-4 (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`), resolution scaling probes (ARGUS-6, ARGUS-8), and the 73-feature native SCADA ceiling (62 standard flow features + 11 derived features; historically referenced as 70/71 in informal shorthand).
3. **Domain Adaptation Mathematics**: [`paper/methodology/03_DOMAIN_ADAPTATION_FORMULATION.md`](file:///home/bhumi/GitHub/ARGUS/paper/methodology/03_DOMAIN_ADAPTATION_FORMULATION.md)  
   Rigorous equations for Global CORAL covariance alignment, Class-Aware CORAL ($A_c = C_{s,c}^{-1/2} C_{t,c}^{1/2}$), Bayesian prior shift likelihood correction, and DANN adversarial minimax optimization.
4. **Evaluation & Operating Constraints**: [`paper/methodology/04_EVALUATION_PROTOCOLS_AND_METRICS.md`](file:///home/bhumi/GitHub/ARGUS/paper/methodology/04_EVALUATION_PROTOCOLS_AND_METRICS.md)  
   Matthews Correlation Coefficient (MCC), Balanced Accuracy, 5-seed cluster-bootstrap uncertainty ($B=1,000$), paired DeLong tests, and operational recall under SOC false-positive budgets ($\text{FPR} \le 0.1\%, 1\%, 5\%$).

---

## 3. Literature Reviews & Bibliographic References

- **Literature Survey**: [`paper/literature/LITERATURE_REVIEW.md`](file:///home/bhumi/GitHub/ARGUS/paper/literature/LITERATURE_REVIEW.md)  
  Surveys the closed-world fallacy (Sommer & Paxson 2010), cross-evaluation failures (Apruzzese et al. 2022), dataset shift theory (Moreno-Torres et al. 2012), CORAL (Sun & Saenko 2016), DANN (Ganin & Lempitsky 2015), tabular trees & transformers, and SHAP interpretability.
- **Master BibTeX Database**: [`paper/references/references.bib`](file:///home/bhumi/GitHub/ARGUS/paper/references/references.bib)  
  Standardized BibTeX entries for all 11 manuscript references and extension works.
- **Annotated Bibliography**: [`paper/references/BIBLIOGRAPHY.md`](file:///home/bhumi/GitHub/ARGUS/paper/references/BIBLIOGRAPHY.md)  
  Human-readable catalog with verified publisher DOIs and integration notes.

---

## 4. Publication Figures and Tables Location

### Publication Figures (`paper/figures/`)
- **Central Figure Catalog**: [`paper/figures/FIGURE_INDEX.md`](file:///home/bhumi/GitHub/ARGUS/paper/figures/FIGURE_INDEX.md)  
  Catalogs all figures with categories, evidence tiers, and cryptographic SHA-256 fingerprints.
- **Architecture & Protocol Diagrams**: [`paper/figures/architecture/`](file:///home/bhumi/GitHub/ARGUS/paper/figures/architecture/)  
  Vector SVGs and 300 DPI PNGs for System Architecture (`fig01`) and Frozen-Test Protocol (`fig02`).
- **Methodology Diagrams**: [`paper/figures/methodology/`](file:///home/bhumi/GitHub/ARGUS/paper/figures/methodology/)  
  Feature Harmonization (`fig01`) and CORAL Covariance Alignment (`fig02`).
- **Experimental Results**: [`paper/figures/experimental_results/`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/)  
  137 publication plots across 10 sections, plus the **Top 8 Publication Composite Panels** in [`paper/figures/experimental_results/10_publication_figures/`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/10_publication_figures/) and [`paper/figures/experimental_results/TOP_8_FOR_PROFESSOR/`](file:///home/bhumi/GitHub/ARGUS/paper/figures/experimental_results/TOP_8_FOR_PROFESSOR/).

### Publication Tables (`paper/tables/`)
- **Central Table Catalog**: [`paper/tables/TABLE_INDEX.md`](file:///home/bhumi/GitHub/ARGUS/paper/tables/TABLE_INDEX.md)
- **Table I (Domains & Profiles)**: [`paper/tables/Table_I_Domains_And_Profiles.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_I_Domains_And_Profiles.csv)
- **Table II (Partition Sizes & Balance)**: [`paper/tables/Table_II_Partition_Sizes_And_Balance.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_II_Partition_Sizes_And_Balance.csv)
- **Table III (Bidirectional D1↔D2 Transfer)**: [`paper/tables/Table_III_Bidirectional_D1_D2_Cross_Domain.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_III_Bidirectional_D1_D2_Cross_Domain.csv)
- **Table IV (D1→D2 Random-Row Benchmark)**: [`paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv)
- **Table V (Resolution Scaling Sweep)**: [`paper/tables/Table_V_Feature_Resolution_Scaling.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_V_Feature_Resolution_Scaling.csv)
- **Table VI (FPR-Constrained Operational Performance)**: [`paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv)

---

## 5. Where Verified Research Evidence Is Stored

1. **Master Research Spreadsheet**:  
   [`results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`](file:///home/bhumi/GitHub/ARGUS/results/ARGUS_ALL_RESEARCH_RESULTS.xlsx)  
   Contains all 17 authoritative worksheets (75,463 bytes, SHA-256 `f4ddc451a0c0d97f1eeea0a57668562b1bf9bb13437e2f30c5ac95d8bdb678f1`).
2. **Authoritative Production Benchmark Metrics**:  
   [`results/verified/five_model_complete_comparison.csv`](file:///home/bhumi/GitHub/ARGUS/results/verified/five_model_complete_comparison.csv) (Table IV backing data).
3. **P1–P2.3 Research Deliverables**:  
   Under [`results/experiments/`](file:///home/bhumi/GitHub/ARGUS/results/experiments/):
   - `p1_1_nfton_in_domain/`: In-domain NF-ToN supervised reference baseline.
   - `p2_coordinate_generalization/`: Coordinate-disjoint splits and label ambiguity analysis.
   - `p2_1_validation/`: Same-test-set cross-domain evaluation with bootstrap CIs and DeLong tests.
   - `p2_2_robustness/`: 5-split evaluations and 1,000-resample cluster bootstrap.
   - `p2_3_reconciliation/`: Adversarial partition identity reconciliation and sample ordering audit.
4. **Replication Exhibits & Packages**:  
   Under [`paper/data/2_REP01_Deliverables/`](file:///home/bhumi/GitHub/ARGUS/paper/data/2_REP01_Deliverables/): REP-01 multi-seed representation comparison tables and logs.

---

## 6. Evidence That Still Requires Verification (Open Items)

In keeping with strict academic integrity, the following items are flagged as requiring verification or future experimental work before final submission:

1. **Tuple Cardinality & Entropy Mechanism**:  
   The paper notes that representation collapse may stem from severe state-space compression (few unique feature tuples). While intuitive, the specific mathematical causality between entropy loss and classification failure remains an **unverified hypothesis** rather than a proven theorem.
2. **Multi-Seed Uncertainty for D1↔D2 Transfer**:  
   Table III (Bidirectional D1↔D2 transfer) is derived from single-run historical exports. Running 5-seed replications with DeLong paired statistical tests on D1↔D2 would strengthen the manuscript to the same level of rigor as D3.
3. **Few-Shot Label Scarcity Curves**:  
   Clean Class-Aware CORAL is evaluated on the full adaptation split ($N=10.5\text{M}$ flows). A parametric experiment showing performance as a function of available target labels ($k \in \{10, 50, 100, 500, 1000\}$) would solidify the few-shot supervised adaptation claim.

---

## 7. Manuscript Elements Not Yet Publication-Ready

Based on the Senior Reviewer audit ([`audit/independent/RESEARCH_PAPER_READINESS.md`](file:///home/bhumi/GitHub/ARGUS/audit/independent/RESEARCH_PAPER_READINESS.md)), the current manuscript draft score is **73.5% (Revise Before Submission)**:

1. **Supervised Target Ceiling in Manuscript Text**:  
   The manuscript text in Table IV does not yet explicitly present the supervised target ceiling (in-domain NF-ToN classifier achieving $F1 = 0.9547$, $\text{MCC} = +0.831$) alongside the adaptation baselines. Reviewers will demand this reference point.
2. **Clarification of Supervised vs. Unsupervised Adaptation**:  
   Section III of the manuscript must explicitly clarify that "Clean Class-Aware CORAL" operates in a **Few-Shot Supervised Adaptation** regime, rather than pure unsupervised domain adaptation (UDA).
3. **Formalization of Prior Shift Transformation**:  
   The Bayesian prior shift formula documented in [`paper/methodology/03_DOMAIN_ADAPTATION_FORMULATION.md`](file:///home/bhumi/GitHub/ARGUS/paper/methodology/03_DOMAIN_ADAPTATION_FORMULATION.md) needs to be inserted into Section III-B of the Word manuscript text.
