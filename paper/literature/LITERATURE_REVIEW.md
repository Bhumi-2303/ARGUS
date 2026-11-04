# ARGUS Comprehensive Literature Review & Theoretical Grounding

**Document Status**: Official Research Literature Survey  
**Target Publication Venues**: IEEE TDSC / IEEE TIFS / ACM TOPS  
**Associated Manuscript**: [`paper/manuscripts/main/ARGUS_paper_v2_representation_resolution.docx`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/main/ARGUS_paper_v2_representation_resolution.docx)

---

## 1. Executive Summary & Literature Framing

Machine learning-based Network Intrusion Detection Systems (NIDS) routinely achieve $\ge 98\%$ accuracy and ROC-AUC in closed-world, single-dataset laboratory benchmarks. However, when evaluated in cross-network or cross-domain deployments, their performance undergoes catastrophic collapse. The ARGUS research project investigates the root causes of this collapse across heterogeneous Enterprise IoT, Smart Home IoT, and Critical Infrastructure SCADA systems.

This literature review grounds the core empirical findings of ARGUS in six foundational theoretical bodies, while identifying literature expansions required for journal submission:
1. **The Closed-World Fallacy in Network Security**: Sommer & Paxson (2010), Apruzzese et al. (2022).
2. **Network Representation Standards & Synthesized Common Schemas**: Sarhan et al. (2022), Neto et al. (2023).
3. **Formal Dataset Shift Taxonomy**: Moreno-Torres et al. (2012).
4. **Second-Order and Adversarial Domain Adaptation**: Sun & Saenko (2016), Ganin & Lempitsky (2015).
5. **Modern Tabular Learning Architectures**: Chen & Guestrin (2016), Ke et al. (2017), Gorishniy et al. (2021).
6. **Feature Attribution & Model Interpretability**: Lundberg & Lee (2017).

---

## 2. Foundational Research Pillars (Verified Citations)

### 2.1 The Closed-World Fallacy in Network Intrusion Detection
- **Sommer & Paxson (2010)**, *"Outside the Closed World: On Using Machine Learning for Network Intrusion Detection"*, IEEE S&P 2010.
  - *Core Insight*: Established that network anomaly detection fundamentally differs from other ML domains due to high false-positive costs, massive diversity in benign traffic, semantic gaps between anomaly flags and operational intent, and non-stationarity of network distributions.
  - *Grounding in ARGUS*: ARGUS extends Sommer & Paxson's warning by demonstrating that even modern representation harmonization and domain adaptation techniques fail unless class conditional shifts and operational false-positive rate constraints ($\text{FPR} \le 0.1\%$) are explicitly incorporated into the objective function.
- **Apruzzese et al. (2022)**, *"The Cross-Evaluation of Machine Learning-Based Network Intrusion Detection Systems"*, IEEE TNSM 2022.
  - *Core Insight*: Conducted multi-dataset cross-evaluations revealing that classifiers trained on one benchmark drop to near-random discriminability on another, demonstrating pervasive dataset-specific overfitting.
  - *Grounding in ARGUS*: Confirms Apruzzese's macro-level cross-evaluation degradation, and provides a mechanistic explanation: **representation resolution collapse** under restricted common feature sets.

### 2.2 Standardized Network Flow Representations
- **Sarhan, Layeghy, and Portmann (2022)**, *"Towards a Standard Feature Set for Network Intrusion Detection System Datasets"*, Mobile Networks and Applications 2022.
  - *Core Insight*: Proposed standardizing flow features based on NetFlow-v9 / IPFIX (43 features) to enable interoperability across distinct NIDS datasets (e.g., NF-ToN-IoT, NF-BoT-IoT).
  - *Grounding in ARGUS*: ARGUS adopts Sarhan's standardized NetFlow paradigm for Domain 2 (NF-ToN-IoT-v2), and builds the 4-feature common core (`ARGUS-4`) to bridge between NetFlow and raw packet capture statistics.
- **Neto et al. (2023)**, *"CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment"*, Sensors 2023.
  - *Core Insight*: Generated a modern, 46-feature IoT intrusion dataset capturing large-scale DoS, DDoS, brute-force, and reconnaissance attacks across 33 physical IoT devices.
  - *Grounding in ARGUS*: Serves as Domain 1 (CICIoT2023, $N = 6.67\text{M}$ flows).

### 2.3 Dataset Shift & Covariate Shift Foundations
- **Moreno-Torres et al. (2012)**, *"A Unifying View on Dataset Shift in Classification"*, Pattern Recognition 2012.
  - *Core Insight*: Formalized the distinction between **covariate shift** ($P(x)$ changes while $P(y|x)$ remains invariant), **prior shift** ($P(y)$ changes while $P(x|y)$ remains invariant), and **concept drift** ($P(y|x)$ changes).
  - *Grounding in ARGUS*: Proves that cross-domain NIDS transfer violates pure covariate shift. Transfer between D1 (attack prior 97.64%), D2 (attack prior 72.58%), and D3 (attack prior 22.46%) induces acute prior shift, requiring Bayesian likelihood-ratio adjustment.

### 2.4 Unsupervised Domain Adaptation (UDA)
- **Sun and Saenko (2016)**, *"Deep CORAL: Correlation Alignment for Deep Domain Adaptation"*, ECCV Workshops 2016.
  - *Core Insight*: Aligns source and target distributions by minimizing the Frobenius distance between their second-order covariance matrices:
    $$\mathcal{L}_{\text{CORAL}} = \frac{1}{4d^2} \|C_s - C_t\|_F^2$$
  - *Grounding in ARGUS*: ARGUS demonstrates that Global CORAL suffers from **specificity collapse** ($\text{MCC} = -0.161$, specificity $2.44\%$) under severe class imbalance, because marginal covariance alignment is dominated by the majority class. ARGUS's **Class-Aware CORAL** resolves this by conditioning alignment on class labels.
- **Ganin and Lempitsky (2015)**, *"Unsupervised Domain Adaptation by Backpropagation"*, ICML 2015.
  - *Core Insight*: Introduced the Domain-Adversarial Neural Network (DANN) featuring a Gradient Reversal Layer (GRL) that learns domain-invariant representations.
  - *Grounding in ARGUS*: Resolves an earlier experimental conflict in the ARGUS codebase, confirming authoritative recomputation: DANN achieves $\text{ROC-AUC} = 0.332$ and $\text{MCC} = +0.013$, collapsing into majority-class prediction due to adversarial feature erasure.

### 2.5 Tabular Learning Architectures & Explainability
- **Chen and Guestrin (2016)**, *"XGBoost: A Scalable Tree Boosting System"*, ACM SIGKDD 2016.
- **Ke et al. (2017)**, *"LightGBM: A Highly Efficient Gradient Boosting Decision Tree"*, NeurIPS 2017.
  - *Grounding*: Primary workhorse tabular classifiers achieving verified ceiling performance in native domains.
- **Gorishniy et al. (2021)**, *"Revisiting Deep Learning Models for Tabular Data"*, NeurIPS 2021.
  - *Grounding*: Introduced Feature Tokenizer Transformer (FT-Transformer), demonstrating that modern tabular Transformers still fail under cross-domain transfer when compact representations omit discriminative fields.
- **Lundberg and Lee (2017)**, *"A Unified Approach to Interpreting Model Predictions"*, NeurIPS 2017.
  - *Grounding*: TreeSHAP attribution is leveraged to prove **attribution disconnect**: features with top attribution in source domain D1 show zero or negative feature gain in target domain D2.

---

## 3. Required Literature Expansions (Identified for Journal Submission)

Based on the Senior Reviewer audit ([`audit/independent/RESEARCH_PAPER_READINESS.md`](file:///home/bhumi/GitHub/ARGUS/audit/independent/RESEARCH_PAPER_READINESS.md)), the following literature areas must be integrated into Section II of the manuscript prior to final journal submission:

1. **Few-Shot Domain Adaptation (FSDA)**:
   - *Issue*: ARGUS's "Clean Class-Aware CORAL" requires access to class labels on the target adaptation split. In classical UDA, target labels are strictly unavailable.
   - *Framing*: Reframe the method as **Few-Shot Supervised Domain Adaptation**, comparing against methods that utilize limited labeled target exemplars (e.g., Motiian et al., ICCV 2017).
2. **Conditional Adversarial Domain Adaptation (CDAN)**:
   - *Reference*: Long et al., *"Conditional Adversarial Domain Adaptation"*, NeurIPS 2018.
   - *Relevance*: CDAN conditions adversarial domain discrimination on classifier predictions $\hat{y}$ to avoid DANN's mode collapse. Citing CDAN will provide theoretical validation for why class-conditioning is essential.
3. **SCADA Intrusion Benchmarks**:
   - *References*: Shin et al., *"HAI 1.0: Hardware-in-the-Loop Security Dataset"*, 2021; Electra dataset, 2023.
   - *Relevance*: Grounds Domain 3 (IEC 60870-5-104 power grid telemetry) within current industrial control system literature.
