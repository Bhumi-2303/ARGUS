# ARGUS Research Paper Table Index (`paper/tables/`)

This catalog indexes all official empirical tables prepared for the ARGUS academic manuscript: **"Cross-Domain Generalization Failure in IoT/SCADA Intrusion Detection: Representation Resolution and Class-Aware Adaptation"**.

Every table is backed by verified experimental outputs, frozen test sets, and cryptographic checksums.

---

## Central Publication Table Index

| Table ID | Manuscript Title | Source Workbook / Result File | Relevant Experiment | Target Dataset | Evidence Tier | Publication Suitability | Canonical CSV Path |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Table I** | Domains Used in Study | `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx` Sheet `Table1_Dataset_Profiles` | Pre-Experiment Profiling | D1, D2, D3 | **Tier 1 (Verified)** | **Ready for Publication** | [`paper/tables/Table_I_Domains_And_Profiles.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_I_Domains_And_Profiles.csv) |
| **Table II** | Partition Sizes and Class Balance | `results/verified/domain_statistics.json`, `paper_text.txt` Table II | Dataset Preparation | D1, D2, D3 | **Tier 1 (Verified)** | **Ready for Publication** | [`paper/tables/Table_II_Partition_Sizes_And_Balance.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_II_Partition_Sizes_And_Balance.csv) |
| **Table III** | D1↔D2 In-Domain vs. Cross-Domain Performance | `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx` Sheet `Verified_Primary_Benchmark` | EXP-01 / D1↔D2 Supervised | D1 (CICIoT), D2 (NF-ToN) | **Tier 1 (Verified)** | **Ready for Publication** | [`paper/tables/Table_III_Bidirectional_D1_D2_Cross_Domain.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_III_Bidirectional_D1_D2_Cross_Domain.csv) |
| **Table IV** | D1→D2 Domain Adaptation Benchmark (Random-Row Held-Out Partition, N=2,627,177) | `results/verified/five_model_complete_comparison.csv` | EXP-02 / UDA Benchmark | D2 (NF-ToN Test, $N=2.63\text{M}$) | **Tier 1 (Verified)** | **Ready for Publication** | [`paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv) |
| **Table V** | Representation Resolution Scaling Sweep | `experiments/execution/tables/Table4_Feature_Resolution_Scaling.csv` | EXP-REP-01 / Resolution Scaling | D3 (IEC-104 SCADA, $N=714\text{K}$) | **Tier 1 (Verified)** | **Ready for Publication** | [`paper/tables/Table_V_Feature_Resolution_Scaling.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_V_Feature_Resolution_Scaling.csv) |
| **Table VI** | D3 Native Operational Performance at Fixed FPR Budgets | `paper/experiments/journal_completion/tables/exp04_operational_threshold_table.csv` | EXP-04 / Operational Sweeps | D3 (IEC-104 SCADA, $N=714\text{K}$) | **Tier 1 (Verified)** | **Ready for Publication** | [`paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv) |

---

## Detailed Table Profiles & Scientific Annotations

### Table I: Domains Used in Study
- **Canonical File**: [`paper/tables/Table_I_Domains_And_Profiles.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_I_Domains_And_Profiles.csv)
- **Scientific Role**: Documents domain environments, sample counts, protocol splits, and attack prevalence across Enterprise IoT (D1: CICIoT2023, 97.64% attack), Smart Home NetFlow IoT (D2: NF-ToN-IoT-v2, 72.58% attack), and Industrial SCADA Power Substation (D3: IEC-104, 22.46% attack).
- **Caveat**: D1 and D2 have extreme majority-class attack skews, while D3 has a benign-majority distribution, presenting severe prior shift in cross-domain transfer.

### Table II: Partition Sizes and Class Balance
- **Canonical File**: [`paper/tables/Table_II_Partition_Sizes_And_Balance.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_II_Partition_Sizes_And_Balance.csv)
- **Scientific Role**: Formalizes training, adaptation, calibration, and test splits. Confirms test sets are strictly frozen and evaluated blind.
- **Caveat**: D1↔D2 partitions are single-run historical splits; D3 SCADA uses coordinate-disjoint grouped splits. Total pool accounting: 8,406,962 (adaptation) + 2,101,742 (calibration) + 2,627,177 (frozen test) = 13,135,881 total observations (historical 11,034,141 count was an arithmetic line-count artifact omitting calibration).

### Table III: Bidirectional D1↔D2 In-Domain vs. Cross-Domain Performance
- **Canonical File**: [`paper/tables/Table_III_Bidirectional_D1_D2_Cross_Domain.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_III_Bidirectional_D1_D2_Cross_Domain.csv)
- **Scientific Role**: Demonstrates severe asymmetric degradation upon zero-adaptation transfer under the harmonized ARGUS-4 representation. In-domain models achieve $\text{MCC} \ge +0.647$ to $+0.831$, but collapse to $\text{MCC} \le -0.031$ when transferred.
- **Caveat**: Reconstructed from verified multi-export aggregate tables; D1↔D2 results currently represent single-seed runs.

### Table IV: D1→D2 Domain Adaptation Benchmark (Random-Row Held-Out Partition, N=2,627,177)
- **Canonical File**: [`paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_IV_Random_Row_Domain_Adaptation.csv) (legacy alias: [`paper/tables/Table_IV_Leakage_Controlled_Domain_Adaptation.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_IV_Leakage_Controlled_Domain_Adaptation.csv))
- **Description**: Evaluates D1 (NF-BoT-IoT) to D2 (NF-ToN-IoT) transfer on the frozen random-row held-out test partition ($N=2,627,177$). Note: This partition is disjoint at the observation level but shares IP address space with training data. For coordinate-disjoint (IP/subnet-disjoint) evaluation, see Section IV-C and Phase 2.3 benchmarks.
- **Scientific Role**: Core finding resolving RQ3. Shows Global CORAL degrades performance ($\text{MCC} = -0.161$) and DANN collapses to majority class ($\text{MCC} = +0.013$, $\text{ROC-AUC} = 0.332$). Clean Class-Aware CORAL with prior correction and calibration ($\tau^* = 0.99$) achieves $\text{MCC} = +0.3855$ and Balanced Accuracy $= 71.09\%$. Note: Historical audit draft mention of 0.3896 was an editorial transcription error / threshold misattribution.
- **Caveat**: Diagnostic Class-Aware CORAL uses target test labels and is reported strictly as a failure mechanism diagnostic, excluded from all validity claims. Clean Class-Aware CORAL requires access to class labels on the adaptation split.

### Table V: Verified Representation Resolution Scaling
- **Canonical File**: [`paper/tables/Table_V_Feature_Resolution_Scaling.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_V_Feature_Resolution_Scaling.csv)
- **Scientific Role**: Refutes the unverified assumption of monotonic scaling. Shows ARGUS-8 ($\text{ROC-AUC} = 0.6536$) offers no meaningful gain over ARGUS-6 ($\text{ROC-AUC} = 0.6534$), and cross-domain transfer models are strictly bounded below the native SCADA 73-feature ceiling ($\text{ROC-AUC} = 0.6739$).
- **Caveat**: Evaluated across 3 seeds on IEC-104 test set ($N = 714,453$).

### Table VI: D3 Native Operational Performance at Fixed FPR Budgets
- **Canonical File**: [`paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv`](file:///home/bhumi/GitHub/ARGUS/paper/tables/Table_VI_Operational_Performance_FPR_Budgets.csv)
- **Scientific Role**: Highlights the operational gap between aggregate metrics and SOC reality. Under strict false alarm limits ($\text{FPR} \le 0.1\%$), attack recall drops below $1\%$, and under $\text{FPR} \le 1.0\%$, recall remains below $4\%$ for FT-Transformer and $21\%$ for Native SCADA LightGBM.
- **Caveat**: Supported by 5-seed mean $\pm$ SD uncertainty intervals from `paper/experiments/journal_completion/tables/exp04_operational_threshold_table.csv`.
