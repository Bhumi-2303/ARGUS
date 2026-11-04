# ARGUS Manuscript Publication Tables (`paper/tables/`)

This directory houses the definitive publication-grade CSV tables and metadata supporting the ARGUS research paper.

---

## Directory Inventory

```text
paper/tables/
├── README.md                                             # Directory overview and usage guide
├── TABLE_INDEX.md                                        # Central table catalog, evidence tiers, and notes
├── Table_I_Domains_And_Profiles.csv                      # Table I: Dataset characteristics, sample counts, and priors
├── Table_II_Partition_Sizes_And_Balance.csv              # Table II: Training, adaptation, calibration, and test splits
├── Table_III_Bidirectional_D1_D2_Cross_Domain.csv        # Table III: In-domain vs cross-domain transfer (XGBoost / LightGBM)
├── Table_IV_Random_Row_Domain_Adaptation.csv             # Table IV: D1->D2 Domain Adaptation Benchmark (Random-Row, N=2.63M)
├── Table_IV_Leakage_Controlled_Domain_Adaptation.csv     # Table IV legacy compatibility symlink
├── Table_V_Feature_Resolution_Scaling.csv                # Table V: Multi-seed representation resolution scaling (4, 6, 8, 73)
└── Table_VI_Operational_Performance_FPR_Budgets.csv     # Table VI: Attack recall at fixed FPR constraints (0.1%, 1%, 5%)
```

---

## Provenance & Integrity Standards

1. **No Data Fabrication**: All values in these tables are extracted directly from underlying experimental artifacts in `results/verified/`, `results/experiments/`, and `experiments/execution/tables/`.
2. **Master Workbook Invariance**: The master research spreadsheet [`results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`](file:///home/bhumi/GitHub/ARGUS/results/ARGUS_ALL_RESEARCH_RESULTS.xlsx) remains unchanged with SHA-256 fingerprint `f4ddc451a0c0d97f1eeea0a57668562b1bf9bb13437e2f30c5ac95d8bdb678f1`.
3. **Scientific Traceability**: For details mapping each table to its underlying script, configuration, and reproducibility manifest, consult [`paper/PUBLICATION_TRACEABILITY.md`](file:///home/bhumi/GitHub/ARGUS/paper/PUBLICATION_TRACEABILITY.md).
