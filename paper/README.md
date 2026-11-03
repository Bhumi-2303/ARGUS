# ARGUS Academic Publications & Manuscripts (`paper/`)

This directory houses the academic manuscripts, publication exhibit data, replication deliverables, and journal completion experiment suites for ARGUS.

---

## 1. Directory Structure

```text
paper/
├── manuscripts/                    # Formal academic manuscript drafts
│   ├── ARGUS_paper_v2_representation_resolution.docx # Authoritative Word manuscript (1.12 MB)
│   └── paper_text.txt              # Plaintext transcript of manuscript text (32.8 KB)
├── ARGUS_Paper_Data/               # Replication deliverables and exhibits
│   ├── 2_REP01_Deliverables/       # REP-01 representation extension replication package
│   │   ├── REP01_experiment_state.json # Execution state manifest
│   │   ├── configs/                # Configuration JSONs
│   │   ├── figures/                # 300 DPI publication plots (PR, ROC, SHAP, etc.)
│   │   ├── reports/                # Audit and leakage reports
│   │   ├── scripts/                # Experiment execution scripts
│   │   └── tables/                 # Feature audit, multi-seed results, representation comparison
│   ├── 3_Entropy_Computation/      # Information-theoretic entropy calculations
│   │   └── entropy_results.txt     # Empirical entropy loss across 4 vs 70 features
│   └── README.md                   # Exhibit documentation
└── experiments/                    # Journal completion experimental suite
    └── journal_completion/         # Multi-seed validation and calibration audit
        ├── configs/                # Experiment registry config
        ├── scripts/                # Execution runners (leakage, splits, seeds, calibration)
        ├── metrics/                # Output metric JSONs (exp01–exp04)
        ├── figures/                # Publication figures (error bars, reliability, ROC/PR)
        ├── tables/                 # Bootstrap CI, multi-seed metrics, operational thresholds
        └── logs/                   # Execution logs
```

---

## 2. Manuscript Inventory

| Manuscript Artifact | Location | Size | SHA-256 | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Journal Draft (DOCX)** | [`paper/manuscripts/ARGUS_paper_v2_representation_resolution.docx`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/ARGUS_paper_v2_representation_resolution.docx) | 1,119,018 B | `b074f4f0d064ecb7f36f82c9a6ae82bfcd936b26437b33bc7720d1612e7e1b25` | Primary manuscript containing all core claims, mathematical derivations, and figures. |
| **Plaintext Transcript** | [`paper/manuscripts/paper_text.txt`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/paper_text.txt) | 32,782 B | `6cae4ceedbaf19cb7561302bbd3a55ecdebd195983cb05b67a1eaacc3365586d` | Verbatim text transcript used for automated claim verification and audit text-matching. |

---

## 3. Scientific Status & Exhibit Traceability

1. **Replication Exhibits (`ARGUS_Paper_Data/2_REP01_Deliverables/`)**:
   - `REP01_MULTI_SEED_RESULTS.csv`: Verified multi-seed evaluation of representation scaling.
   - `REP01_REPRESENTATION_COMPARISON.csv`: Direct performance comparison across 4-feature harmonized and extended feature representations.
2. **Journal Completion Experiments (`paper/experiments/journal_completion/`)**:
   - `exp03_bootstrap_ci.csv`: Empirical confidence intervals for multi-seed stability.
   - `exp04_operational_threshold_table.csv`: Operating points under realistic SOC false alarm constraints ($\text{FPR} \le 1\%$).
