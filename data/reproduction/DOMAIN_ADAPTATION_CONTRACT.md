# ARGUS DOMAIN ADAPTATION CONTRACT

## EXPERIMENTAL PROTOCOL
**SOURCE DOMAINS**: CICIoT2023, NF-ToN-IoT
**UNSEEN TARGET DOMAIN**: BoT-IoT
**TARGET LABEL USAGE**: Strictly hidden until final model evaluation. No usage during feature selection, normalization, model selection, early stopping, or threshold calibration.

## FEATURE SPACE (V2)
The validated common input representation for domain adaptation is exactly the 7 features mapped in `feature_space_contract.json`:
1. `duration` (Numerical, Scaled)
2. `total_pkts` (Numerical, Scaled)
3. `total_bytes` (Numerical, Scaled)
4. `bytes_per_packet` (Numerical, Scaled)
5. `packet_rate` (Numerical, Scaled)
6. `byte_rate` (Numerical, Scaled)
7. `protocol` (Categorical, One-Hot Encoded)

## PREPROCESSING PROTOCOL
`StandardScaler` and `OneHotEncoder` are fitted **EXCLUSIVELY** on the combined CICIoT2023 + NF-ToN-IoT Source Train split. The Target BoT-IoT dataset is transformed blindly using these frozen parameters.

## ADAPTATION OPERATION BOUNDARIES

### 1. CORAL (Classical Covariance Alignment)
**Input Representation**: The preprocessed 7-feature semantic space (plus one-hot expansions). Let this space be $X \in \mathbb{R}^d$.
**Adaptation Mechanism**: Unsupervised alignment of Source covariance $C_S$ to Target unlabeled covariance $C_T$ using $X_{aligned} = X_{source} \cdot C_S^{-1/2} \cdot C_T^{1/2}$.
**Classifier**: XGBoost operates on $X_{aligned}$.

### 2. DANN (Neural Gradient Reversal)
**Input Representation**: The preprocessed semantic space $X \in \mathbb{R}^d$.
**Latent Representation**: The final 16-dimensional activation output of the Feature Extractor MLP `(Linear(d, 32) -> ReLU -> Linear(32, 16) -> ReLU)`.
**Adaptation Mechanism**: Domain classifier operates directly on this 16-dimensional latent representation, reversed via the Gradient Reversal Layer during backward passes. The Attack classifier operates on the exact same 16-dimensional latent vector.

## THRESHOLDING
Thresholds are selected **strictly** by maximizing the F1-score on the isolated Source Validation split. Target data is not used for thresholding.
