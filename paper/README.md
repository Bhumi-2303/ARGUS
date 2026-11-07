# ARGUS Academic Publications & Manuscripts (`paper/`)

This directory houses the academic manuscripts, publication exhibit data, replication deliverables, publication figures, empirical tables, literature grounding, and journal completion experiment suites for ARGUS.

---

## 1. Directory Structure

```text
paper/
├── README.md                                             # Master publication guide (this file)
├── PUBLICATION_TRACEABILITY.md                           # End-to-end scientific provenance matrix
├── RESEARCH_SUPERVISOR_HANDOFF.md                        # Executive briefing for supervisor / collaborators
├── manuscripts/                                          # Academic manuscripts and drafts
│   ├── README.md                                         # Manuscript version index
│   ├── main/                                             # Authoritative current journal drafts
│   │   ├── ARGUS_paper_v2_representation_resolution.docx # Authoritative Word manuscript (1.12 MB)
│   │   └── paper_text.txt                                # Plain-text transcript for audits (32.8 KB)
│   ├── drafts/                                           # Active section drafts and revisions
│   └── archived_versions/                                # Superseded historical outlines
├── literature/                                           # Literature reviews and grounding
│   ├── README.md                                         # Literature categories & verification status
│   └── LITERATURE_REVIEW.md                              # Critical survey of NIDS, UDA, shift theory, and gaps
├── methodology/                                          # Formal mathematical and procedural specifications
│   ├── README.md                                         # Methodology module index
│   ├── 01_DATASETS_AND_PREPROCESSING.md                  # Environments, flow counts, priors, and splits
│   ├── 02_FEATURE_HARMONIZATION.md                       # ARGUS-4, 6, 8, and native 70 schemas
│   ├── 03_DOMAIN_ADAPTATION_FORMULATION.md               # CORAL, Class-Aware, Prior Shift, DANN math
│   └── 04_EVALUATION_PROTOCOLS_AND_METRICS.md            # FPR budgets, MCC, cluster bootstrap, SHAP
├── figures/                                              # Central figure repository
│   ├── README.md                                         # Figure guidelines and formats
│   ├── FIGURE_INDEX.md                                   # Central catalog with SHA-256 fingerprints
│   ├── architecture/                                     # System architecture and evaluation protocols
│   ├── methodology/                                      # Feature harmonization and covariance alignment
│   ├── system_implementation/                            # Live SOC monitoring console
│   └── experimental_results/                             # 137 publication plots across 10 sections
│       └── TOP_8_FOR_PROFESSOR/                          # High-res package of Top 8 composite figures
├── tables/                                               # Central manuscript tables
│   ├── README.md                                         # Tables guide and provenance standards
│   ├── TABLE_INDEX.md                                    # Master table catalog and evidence tiers
│   ├── Table_I_Domains_And_Profiles.csv                  # Table I: Datasets, flow counts, priors
│   ├── Table_II_Partition_Sizes_And_Balance.csv          # Table II: Disjoint split definitions
│   ├── Table_III_Bidirectional_D1_D2_Cross_Domain.csv    # Table III: In-domain vs cross-domain transfer
│   ├── Table_IV_Leakage_Controlled_Domain_Adaptation.csv # Table IV: UDA comparison on NF-ToN
│   ├── Table_V_Feature_Resolution_Scaling.csv            # Table V: Multi-seed resolution scaling
│   └── Table_VI_Operational_Performance_FPR_Budgets.csv # Table VI: Operational recall at fixed FPRs
├── references/                                           # Bibliographic references
│   ├── README.md                                         # Citation conventions
│   ├── references.bib                                    # Standard BibTeX database
│   └── BIBLIOGRAPHY.md                                   # Formatted annotated bibliography with DOIs
├── data/                                                 # Packaged replication deliverables (REP01)
│   ├── 2_REP01_Deliverables/                             # Representation extension package (scripts, tables, reports)
│   ├── 3_Entropy_Computation/                            # Information-theoretic entropy calculations
│   └── README.md                                         # Exhibit documentation
└── experiments/                                          # Journal completion experimental suite
    └── journal_completion/                               # Multi-seed validation and calibration audit
        ├── configs/                                      # Registry configuration JSONs
        ├── scripts/                                      # Execution runners (leakage, splits, seeds, calibration)
        ├── metrics/                                      # Output metric JSONs (exp01–exp04)
        ├── figures/                                      # Error bar and reliability plots
        ├── tables/                                       # Operational threshold tables
        └── logs/                                         # Execution logs
```

---

## 2. Manuscript Inventory

| Manuscript Artifact | Canonical Path | Size | SHA-256 Fingerprint | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Journal Draft (DOCX)** | [`paper/manuscripts/main/ARGUS_paper_v2_representation_resolution.docx`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/main/ARGUS_paper_v2_representation_resolution.docx) | 1,119,018 B | `b074f4f0d064ecb7f36f82c9a6ae82bfcd936b26437b33bc7720d1612e7e1b25` | Primary authoritative draft containing all core claims, mathematical derivations, figures, and tables. |
| **Plain-Text Transcript** | [`paper/manuscripts/main/paper_text.txt`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/main/paper_text.txt) | 32,782 B | `6cae4ceedbaf19cb7561302bbd3a55ecdebd195983cb05b67a1eaacc3365586d` | Verbatim text transcript used for automated claim verification and audit text-matching. |

---

## 3. Scientific Evidence Classification

Artifacts in this directory adhere to three strict evidence tiers:

- **Tier 1 — Verified Evidence**: Supported by frozen test sets, reproducible scripts, and verified output CSVs (e.g., Table I–VI, Figures 1–8).
- **Tier 2 — Exploratory Evidence**: Completed experiments requiring additional multi-seed or calibration verification (e.g., tuple entropy calculations in `data/3_Entropy_Computation/`).
- **Tier 3 — Illustrative Material**: Conceptual architecture diagrams and monitoring UI mockups (e.g., `figures/architecture/fig01`, `figures/system_implementation/fig01`).

For detailed audit ratings, see [`audit/independent/RESEARCH_PAPER_READINESS.md`](file:///home/bhumi/GitHub/ARGUS/audit/independent/RESEARCH_PAPER_READINESS.md).
