# Annotated Research Bibliography (`paper/references/`)

This document provides a human-readable annotated bibliography for all works cited in the ARGUS academic research paper, with direct links to official publisher DOIs and verification statuses.

---

## 1. Primary Manuscript Citations ([1] – [11])

1. **[1] CICIoT2023 Benchmark**:
   - **Full Citation**: E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, and A. A. Ghorbani, *"CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment,"* *Sensors*, vol. 23, no. 13, p. 5941, 2023.
   - **DOI**: [10.3390/s23135941](https://doi.org/10.3390/s23135941)
   - **BibTeX Key**: `neto2023ciciot2023`
   - **Role in ARGUS**: Defines Domain 1 (D1) Enterprise IoT benchmark.
   - **Status**: **Verified**.

2. **[2] Standardized NetFlow Feature Set**:
   - **Full Citation**: M. Sarhan, S. Layeghy, and M. Portmann, *"Towards a Standard Feature Set for Network Intrusion Detection System Datasets,"* *Mobile Networks and Applications*, vol. 27, no. 1, pp. 357–370, 2022.
   - **DOI**: [10.1007/s11036-021-01843-0](https://doi.org/10.1007/s11036-021-01843-0)
   - **BibTeX Key**: `sarhan2022towards`
   - **Role in ARGUS**: Provides the 43-feature NetFlow-v9 standardized schema for Domain 2 (NF-ToN-IoT-v2).
   - **Status**: **Verified**.

3. **[3] Closed-World Fallacy in Network Security**:
   - **Full Citation**: R. Sommer and V. Paxson, *"Outside the Closed World: On Using Machine Learning for Network Intrusion Detection,"* in *Proc. IEEE Symposium on Security and Privacy (S&P)*, 2010, pp. 305–316.
   - **DOI**: [10.1109/SP.2010.25](https://doi.org/10.1109/SP.2010.25)
   - **BibTeX Key**: `sommer2010outside`
   - **Role in ARGUS**: Foundational conceptual motivation framing real-world deployment challenges.
   - **Status**: **Verified**.

4. **[4] Cross-Evaluation of NIDS**:
   - **Full Citation**: G. Apruzzese, P. Laskov, and J. Schneider, *"The Cross-Evaluation of Machine Learning-Based Network Intrusion Detection Systems,"* *IEEE Transactions on Network and Service Management*, vol. 19, no. 4, pp. 5152–5169, 2022.
   - **DOI**: [10.1109/TNSM.2022.3175440](https://doi.org/10.1109/TNSM.2022.3175440)
   - **BibTeX Key**: `apruzzese2022cross`
   - **Role in ARGUS**: Empirically proves the prevalence of cross-dataset generalization failure across ML classifiers.
   - **Status**: **Verified**.

5. **[5] Taxonomy of Dataset Shift**:
   - **Full Citation**: J. G. Moreno-Torres, T. Raeder, R. Alaiz-Rodríguez, N. V. Chawla, and F. Herrera, *"A Unifying View on Dataset Shift in Classification,"* *Pattern Recognition*, vol. 45, no. 1, pp. 521–530, 2012.
   - **DOI**: [10.1016/j.patcog.2011.06.019](https://doi.org/10.1016/j.patcog.2011.06.019)
   - **BibTeX Key**: `moreno2012unifying`
   - **Role in ARGUS**: Provides formal definitions of covariate shift vs prior shift vs concept drift.
   - **Status**: **Verified**.

6. **[6] Deep CORAL (Correlation Alignment)**:
   - **Full Citation**: B. Sun and K. Saenko, *"Deep CORAL: Correlation Alignment for Deep Domain Adaptation,"* in *Proc. European Conference on Computer Vision Workshops (ECCVW)*, 2016, pp. 443–450.
   - **DOI**: [10.1007/978-3-319-49409-8_35](https://doi.org/10.1007/978-3-319-49409-8_35)
   - **BibTeX Key**: `sun2016deep`
   - **Role in ARGUS**: Theoretical basis for second-order covariance alignment across domains.
   - **Status**: **Verified**.

7. **[7] Domain-Adversarial Neural Networks (DANN)**:
   - **Full Citation**: Y. Ganin and V. Lempitsky, *"Unsupervised Domain Adaptation by Backpropagation,"* in *Proc. 32nd International Conference on Machine Learning (ICML)*, 2015, pp. 1180–1189.
   - **BibTeX Key**: `ganin2015unsupervised`
   - **Role in ARGUS**: Minimax adversarial baseline using Gradient Reversal Layer (GRL).
   - **Status**: **Verified**.

8. **[8] XGBoost**:
   - **Full Citation**: T. Chen and C. Guestrin, *"XGBoost: A Scalable Tree Boosting System,"* in *Proc. 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD)*, 2016, pp. 785–794.
   - **DOI**: [10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785)
   - **BibTeX Key**: `chen2016xgboost`
   - **Role in ARGUS**: Primary tree-based baseline classifier.
   - **Status**: **Verified**.

9. **[9] LightGBM**:
   - **Full Citation**: G. Ke et al., *"LightGBM: A Highly Efficient Gradient Boosting Decision Tree,"* in *Advances in Neural Information Processing Systems (NeurIPS)*, 2017, pp. 3146–3154.
   - **BibTeX Key**: `ke2017lightgbm`
   - **Role in ARGUS**: High-throughput gradient boosting baseline and SCADA native model.
   - **Status**: **Verified**.

10. **[10] FT-Transformer**:
    - **Full Citation**: Y. Gorishniy, I. Rubachev, V. Khrulkov, and A. Babenko, *"Revisiting Deep Learning Models for Tabular Data,"* in *Advances in Neural Information Processing Systems (NeurIPS)*, 2021, pp. 18932–18943.
    - **BibTeX Key**: `gorishniy2021revisiting`
    - **Role in ARGUS**: Tabular Transformer architecture used for D3 native benchmarks and capacity scaling.
    - **Status**: **Verified**.

11. **[11] SHAP (SHapley Additive exPlanations)**:
    - **Full Citation**: S. M. Lundberg and S.-I. Lee, *"A Unified Approach to Interpreting Model Predictions,"* in *Advances in Neural Information Processing Systems (NeurIPS)*, 2017, pp. 4765–4774.
    - **BibTeX Key**: `lundberg2017unified`
    - **Role in ARGUS**: Model-agnostic and TreeSHAP feature attribution analysis.
    - **Status**: **Verified**.

---

## 2. Supplemental & Expansion Citations

12. **[12] CDAN (Conditional Adversarial Domain Adaptation)**:
    - **Full Citation**: M. Long, Z. Cao, J. Wang, and M. I. Jordan, *"Conditional Adversarial Domain Adaptation,"* in *Advances in Neural Information Processing Systems (NeurIPS)*, 2018, pp. 1640–1650.
    - **BibTeX Key**: `long2018conditional`
    - **Role in ARGUS**: Provides theoretical justification for conditioning domain adaptation on class structures.
    - **Status**: **Target for Integration**.

13. **[13] HAI SCADA Benchmark**:
    - **Full Citation**: H.-K. Shin, W. Lee, J.-H. Yun, and H. Kim, *"HAI 1.0: HIL-based Augmented ICS Security Dataset,"* *arXiv preprint arXiv:2102.04635*, 2021.
    - **BibTeX Key**: `shin2021hai`
    - **Role in ARGUS**: Industrial control systems (ICS) and SCADA comparative baseline.
    - **Status**: **Target for Integration**.
