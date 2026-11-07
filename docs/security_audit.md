# ARGUS Repository Security Audit Report

**Audit Date**: 2026-11-07  
**Branch**: `security/audit`  
**Repository**: ARGUS (Autonomous Risk-aware Grid Understanding & Security)  
**Scope**: Read-only codebase security and data-integrity audit covering cross-domain IoT intrusion detection (CICIoT2023, NF-ToN-IoT, IEC 60870-5-104), model training/adaptation pipelines (CORAL, DANN, XGBoost, LightGBM), agent orchestrator, API serving, CI/CD, and dependency infrastructure.  
**Auditor**: Security Engineering & Research Audit Team  

---

## 1. Executive Summary

This security audit conducted a systematic, read-only analysis of the ARGUS repository across 8 core security, scientific, and architectural categories. The findings are summarized in the table below, followed by detailed technical evidence and defensive remediation guidance for each finding.

Every reported item has been verified against the physical codebase at the specified `file:line` location. Items requested for review that were not present in the repository have been explicitly marked **"not found in repo"**.

---

## 2. Findings Matrix

| ID | Finding | Severity | Evidence (file:line) | Recommended Fix |
|:---|:---|:---:|:---|:---|
| **SEC-DESER-01** | Arbitrary code execution via `joblib.load` without hash or signature verification | **High** | [src/argus/agents/threat_analysis/tools/model_loader.py:110](file:///home/bhumi/GitHub/ARGUS/src/argus/agents/threat_analysis/tools/model_loader.py#L110)<br>[src/argus/models/loader.py:31](file:///home/bhumi/GitHub/ARGUS/src/argus/models/loader.py#L31)<br>[src/argus/models/loader.py:40](file:///home/bhumi/GitHub/ARGUS/src/argus/models/loader.py#L40)<br>[src/argus/models/loader.py:48](file:///home/bhumi/GitHub/ARGUS/src/argus/models/loader.py#L48) | Replace `joblib.load` with safe serialization formats (ONNX, Safetensors, or native XGBoost/LightGBM JSON format). If Python object serialization is required, enforce strict pre-deserialization SHA-256 hash checks and digital signature validation. |
| **SEC-DESER-02** | Insecure deserialization via `torch.load` with explicit `weights_only=False` | **High** | [scripts/p2_1_same_test_comparison.py:312](file:///home/bhumi/GitHub/ARGUS/scripts/p2_1_same_test_comparison.py#L312)<br>[scripts/p2_3_reconciliation_audit.py:352](file:///home/bhumi/GitHub/ARGUS/scripts/p2_3_reconciliation_audit.py#L352) | Set `weights_only=True` in all `torch.load()` invocations to restrict deserialization exclusively to tensors, primitive types, and state dictionaries. |
| **SEC-DESER-03** | Insecure deserialization via `torch.load` without `weights_only=True` | **Medium** | [experiments/training/trainers/dann_model.py:303](file:///home/bhumi/GitHub/ARGUS/experiments/training/trainers/dann_model.py#L303)<br>[experiments/ablations/phase4_execute.py:441](file:///home/bhumi/GitHub/ARGUS/experiments/ablations/phase4_execute.py#L441)<br>[experiments/domain_adaptation/coral/stage_d_e_train_evaluate.py:266](file:///home/bhumi/GitHub/ARGUS/experiments/domain_adaptation/coral/stage_d_e_train_evaluate.py#L266)<br>[experiments/domain_adaptation/dann/stage3_final_evaluation_and_artifacts.py:131](file:///home/bhumi/GitHub/ARGUS/experiments/domain_adaptation/dann/stage3_final_evaluation_and_artifacts.py#L131)<br>[experiments/execution/neural_robustness/scripts/run_neural_experiments.py:194](file:///home/bhumi/GitHub/ARGUS/experiments/execution/neural_robustness/scripts/run_neural_experiments.py#L194) | Explicitly pass `weights_only=True` to all PyTorch checkpoint loading functions across experiment and training scripts. |
| **SEC-DESER-04** | Unsafe YAML deserialization (`yaml.load`) | **Low** | *Not found in repo* | Confirmed: All YAML parsing in the repository safely uses `yaml.safe_load()` (e.g. [src/argus/policy/config.py:9](file:///home/bhumi/GitHub/ARGUS/src/argus/policy/config.py#L9), [src/argus/api/routers/monitoring.py:35](file:///home/bhumi/GitHub/ARGUS/src/argus/api/routers/monitoring.py#L35)). |
| **SEC-DESER-05** | Dynamic code execution (`eval()` / `exec()`) | **Low** | *Not found in repo* | Confirmed: Codebase does not invoke Python's built-in `eval()` or `exec()`. Occurrences of `.eval()` are strictly PyTorch module evaluation mode switches (`model.eval()`). |
| **SEC-SECR-01** | Hardcoded default cryptographic secrets & 10-year admin token generator | **High** | [configs/settings.py:41-42](file:///home/bhumi/GitHub/ARGUS/configs/settings.py#L41-L42)<br>[tools/auth/generate_token.py:7-10](file:///home/bhumi/GitHub/ARGUS/tools/auth/generate_token.py#L7-L10) | Remove hardcoded fallback strings from `Field(default=...)`. Force generation of random secrets or require `SECRET_KEY` and `JWT_SECRET_KEY` in environment variables across all environments. Deprecate `tools/auth/generate_token.py` hardcoded signing keys and long-lived tokens. |
| **SEC-SECR-02** | Cloud AI API key leaked in HTTP URL query parameters | **Medium** | [src/argus/integrations/adk/narrator.py:254](file:///home/bhumi/GitHub/ARGUS/src/argus/integrations/adk/narrator.py#L254) | Transmit `api_key` via HTTP request header (`x-goog-api-key: {api_key}`) rather than URL query parameter to prevent exposure in reverse proxy access logs, referrers, and network telemetry. |
| **SEC-SECR-03** | Hardcoded absolute developer and local host filesystem paths | **Low** | [scripts/final_eval.py:13](file:///home/bhumi/GitHub/ARGUS/scripts/final_eval.py#L13)<br>[scripts/fit_fusion.py:8](file:///home/bhumi/GitHub/ARGUS/scripts/fit_fusion.py#L8)<br>[scripts/generate_p2_1_manifest.py:14](file:///home/bhumi/GitHub/ARGUS/scripts/generate_p2_1_manifest.py#L14)<br>[scripts/p2_2_generate_manifest.py:13](file:///home/bhumi/GitHub/ARGUS/scripts/p2_2_generate_manifest.py#L13)<br>[results/experiments/p2_1_validation/P2_1_REPRODUCIBILITY_MANIFEST.json:6](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_1_validation/P2_1_REPRODUCIBILITY_MANIFEST.json#L6) | Replace all absolute paths (`/home/bhumi/...`, `/Volumes/...`, `/Users/...`) with repository-relative paths anchored using `Path(__file__).resolve().parents[...]` or standard environment variables (`ARGUS_DATA_DIR`). |
| **SEC-SECR-04** | Hardcoded Kaggle tokens or API credentials | **Low** | *Not found in repo* | Confirmed: Kaggle references in the codebase are limited to public mirror download URLs and dataset acquisition manifests. No `kaggle.json` or private tokens are committed. |
| **SEC-LEAK-01** | Target label leakage in diagnostic Class-Aware CORAL adaptation | **Critical** | [src/argus/adaptation/class_aware_coral.py:14-25](file:///home/bhumi/GitHub/ARGUS/src/argus/adaptation/class_aware_coral.py#L14-L25)<br>[audit/historical/AUDIT.md:1284](file:///home/bhumi/GitHub/ARGUS/audit/historical/AUDIT.md#L1284)<br>[archive/scripts/scratch/v3_v4.py:94](file:///home/bhumi/GitHub/ARGUS/archive/scripts/scratch/v3_v4.py#L94) | `ClassAwareCORALAdapter.fit()` explicitly requires target ground truth labels (`y_target`) to compute class-conditional covariances, classifying it as Supervised Domain Adaptation (SDA) rather than Unsupervised Domain Adaptation (UDA). Disallow target test label consumption during adaptation; use true unsupervised CORAL ([src/argus/adaptation/coral.py:15-37](file:///home/bhumi/GitHub/ARGUS/src/argus/adaptation/coral.py#L15-L37)). |
| **SEC-LEAK-02** | Massive duplicate row leakage crossing random train/calibration/test splits (98.67% test coordinate overlap) | **High** | [audit/research/P1_1_INDEPENDENT_VERIFICATION/P1_1_LEAKAGE_AUDIT.md:18-31](file:///home/bhumi/GitHub/ARGUS/audit/research/P1_1_INDEPENDENT_VERIFICATION/P1_1_LEAKAGE_AUDIT.md#L18-L31)<br>[audit/research/P1_1_PARTITION_AND_DUPLICATE_AUDIT.json:34-47](file:///home/bhumi/GitHub/ARGUS/audit/research/P1_1_INDEPENDENT_VERIFICATION/P1_1_PARTITION_AND_DUPLICATE_AUDIT.json#L34-L47)<br>[scripts/evaluate_nfton_in_domain_baseline.py:166](file:///home/bhumi/GitHub/ARGUS/scripts/evaluate_nfton_in_domain_baseline.py#L166) | Due to the 4-feature compression, 98.67% of test rows share identical 4D feature vectors with training rows, and 79.04% of coordinates carry conflicting binary labels. In-domain models memorize training coordinate base rates. Enforce group-based, coordinate-disjoint, or chronological partitioning (by IP, session, or timestamp) rather than random row-level splitting. |
| **SEC-LEAK-03** | Methodological label and temporal leakage in D3 SCADA pipeline | **Critical** | [archive/audits/ARGUS_D3_VALIDITY_AUDIT/FINAL_D3_VALIDITY_REPORT.md:12-20](file:///home/bhumi/GitHub/ARGUS/archive/audits/ARGUS_D3_VALIDITY_AUDIT/FINAL_D3_VALIDITY_REPORT.md#L12-L20)<br>[archive/audits/ARGUS_D3_VALIDITY_AUDIT/generate_audit.py:29](file:///home/bhumi/GitHub/ARGUS/archive/audits/ARGUS_D3_VALIDITY_AUDIT/generate_audit.py#L29) | In D3 feature engineering, `i_msg_ratio` directly added `y_sub * 0.25` (true label), artificially inflating ROC-AUC to 0.9999. In addition, temporal rolling features were calculated after random shuffling. Feature extractors must never access label variables, and rolling temporal statistics must be computed strictly in chronological order before splitting. |
| **SEC-INPT-01** | Feature computation with division-by-zero risks, missing NaN/Inf sanitization, and unclipped bounds | **High** | [src/argus/features/extractor.py:28-72](file:///home/bhumi/GitHub/ARGUS/src/argus/features/extractor.py#L28-L72) | In `extract_four_features()`, `np.where(max_len == 0, 0.0, mean_len / max_len)` eagerly evaluates both branches, raising divide-by-zero runtime warnings. Pre-existing feature columns bypass all NaN/Inf/range checks. If `Pkt Len Mean` contains NaN, `np.clip` preserves NaN and `np.log1p` outputs NaN. Use `np.divide(..., where=...)`, clip ratios to `[0.0, 1.0]`, and run explicit `np.nan_to_num()` / finite sanitization before returning. |
| **SEC-INPT-02** | Unchecked mathematical and logarithmic operations in drift and transformer modules | **Medium** | [src/argus/shift/drift.py:27-39](file:///home/bhumi/GitHub/ARGUS/src/argus/shift/drift.py#L27-L39)<br>[src/argus/v2_transformer/train_plumbing.py:79-89](file:///home/bhumi/GitHub/ARGUS/src/argus/v2_transformer/train_plumbing.py#L79-L89) | `compute_psi()` computes `np.linspace(source_col.min(), ...)` without checking for NaN or degenerate (min==max) inputs, causing crashes or NaN propagation. `train_plumbing.py` computes `np.log1p()` on network metrics without non-negative clipping. Add array finite validation, clip inputs `a_min=0`, and handle degenerate bin boundaries. |
| **SEC-DEPS-01** | Unpinned dependency versions in `pyproject.toml` and `web/package.json` | **Medium** | [pyproject.toml:29-55](file:///home/bhumi/GitHub/ARGUS/pyproject.toml#L29-L55)<br>[pyproject.toml:58-76](file:///home/bhumi/GitHub/ARGUS/pyproject.toml#L58-L76)<br>[web/package.json:14-39](file:///home/bhumi/GitHub/ARGUS/web/package.json#L14-L39) | All 27+ Python dependencies use unpinned minimum bounds (`>=`) with no upper bounds (`<`). Frontend packages use caret (`^`) ranges. Specify upper version constraints in `pyproject.toml` to guard against breaking upstream changes. |
| **SEC-DEPS-02** | Missing dependency lockfile | **Low** | *Not found in repo* | Confirmed: Both Python (`uv.lock` at repo root) and Frontend (`web/package-lock.json`) maintain deterministic lockfiles committed to version control. |
| **SEC-DEPS-03** | In-notebook dependency installations (`pip install`) | **Low** | *Not found in repo* | Confirmed: No `.ipynb` notebook files exist in the repository (`find . -name "*.ipynb"` returns 0 files; `experiments/training/notebooks` contains only `.gitkeep`). |
| **SEC-CI-01** | CI actions unpinned / broad permissions / `pull_request_target` | **Low** | *Not found in repo* | Confirmed: `.github/workflows/ci.yml` strictly enforces least-privilege permissions (`permissions: contents: read` at [ci.yml:10-11](file:///home/bhumi/GitHub/ARGUS/.github/workflows/ci.yml#L10-L11)), pins all actions to 40-character commit SHAs, and uses standard `pull_request` rather than `pull_request_target`. |
| **SEC-CI-02** | Permissive CI gate ignoring static type-checking failures | **Low** | [.github/workflows/ci.yml:44-45](file:///home/bhumi/GitHub/ARGUS/.github/workflows/ci.yml#L44-L45) | MyPy static type checking runs with `continue-on-error: true`. Failures in type safety do not gate pull requests. Fix unresolved type errors and remove `continue-on-error: true`. |
| **SEC-MODL-01** | Missing cryptographic signatures on model artifacts | **High** | [artifacts/models/](file:///home/bhumi/GitHub/ARGUS/artifacts/models/)<br>[src/argus/models/loader.py:17-49](file:///home/bhumi/GitHub/ARGUS/src/argus/models/loader.py#L17-L49)<br>[src/argus/agents/threat_analysis/tools/model_loader.py:101-113](file:///home/bhumi/GitHub/ARGUS/src/argus/agents/threat_analysis/tools/model_loader.py#L101-L113) | Model artifacts stored in `artifacts/models/` lack digital signatures (e.g. Cosign/Sigstore, GPG, or Ed25519). Secondary model loaders (`src/argus/models/loader.py`, `src/argus/agents/threat_analysis/tools/model_loader.py`) perform zero hash verification prior to deserialization. |
| **SEC-MODL-02** | Conditional integrity check bypass in `ModelRegistry.load_all()` | **High** | [src/argus/registry/model_registry.py:292-293](file:///home/bhumi/GitHub/ARGUS/src/argus/registry/model_registry.py#L292-L293) | In `ModelRegistry.load_all()`, artifact verification is guarded by `if model_name in self._integrity_manifest:`. If an active model in `MODEL_METADATA` is omitted from `INTEGRITY_MANIFEST.json`, hash verification is skipped rather than failing closed. Remove the conditional check; fail closed if any model is absent from the manifest. |
| **SEC-SERV-01** | Fail-Open Policy Engine fallback on unknown or missing risk context | **Critical** | [src/argus/policy/policy_engine.py:14-24](file:///home/bhumi/GitHub/ARGUS/src/argus/policy/policy_engine.py#L14-L24)<br>[src/argus/policy/rules.py:20-21](file:///home/bhumi/GitHub/ARGUS/src/argus/policy/rules.py#L20-L21) | When `context.risk_tier` is missing or "unknown", `PolicyEngine.evaluate()` falls back to `ActionType.MONITOR` with `requires_human_approval=False`. Malformed or attacker-perturbed events that break risk scoring bypass defensive action and quiet down without human alerting. Fail closed: escalate to `ActionType.ESCALATE` / `ActionType.INVESTIGATE` with `requires_human_approval=True`. |
| **SEC-SERV-02** | In-memory token bucket rate limiter vulnerable to memory exhaustion DoS | **Medium** | [src/argus/security/rate_limiter.py:10-47](file:///home/bhumi/GitHub/ARGUS/src/argus/security/rate_limiter.py#L10-L47) | `TokenBucketRateLimiter._buckets` stores per-key state in an unbounded Python dictionary without key expiration or eviction. A distributed request flood with spoofed IPs or randomized paths will trigger unbounded memory growth. Add LRU eviction with a maximum capacity or use an external Redis backend with TTL. |
| **SEC-SERV-03** | Middleware rate limiting actor resolution execution order bug | **Low** | [src/argus/security/middleware.py:80-89](file:///home/bhumi/GitHub/ARGUS/src/argus/security/middleware.py#L80-L89) | `SecurityMiddleware` inspects `request.state.user_id` before endpoint route dependencies execute. Authentication has not yet run, so `actor_id` is always `None`, and all requests are rate-limited under public IP thresholds (`rate_limit_per_minute_public`), leaving authenticated rate limits unreachable. Resolve the user identity in an earlier middleware or before rate checking. |
| **SEC-SERV-04** | Unauthenticated administrative access default in non-production environments | **High** | [src/argus/auth/rbac.py:97-101](file:///home/bhumi/GitHub/ARGUS/src/argus/auth/rbac.py#L97-L101)<br>[docker-compose.yml:11](file:///home/bhumi/GitHub/ARGUS/docker-compose.yml#L11) | When `ENVIRONMENT != "production"` and `OIDC_ENABLED=false` (the default in `docker-compose.yml`), missing tokens automatically receive a development principal with full `admin` role and all system permissions (`admin:system`, `approve:response`). Ensure default deployments require explicit API tokens or loopback restriction. |
| **SEC-SERV-05** | Sensitive authentication bearer tokens accepted via URL query parameters | **Medium** | [src/argus/auth/rbac.py:52-54](file:///home/bhumi/GitHub/ARGUS/src/argus/auth/rbac.py#L52-L54)<br>[src/argus/auth/rbac.py:63-64](file:///home/bhumi/GitHub/ARGUS/src/argus/auth/rbac.py#L63-L64) | `get_current_user()` accepts authentication tokens via `?token=` query parameters on all HTTP endpoints, exposing tokens in access logs and referrer headers. Restrict query parameter authentication exclusively to WebSocket connection handshakes (`/ws/stream`). |

---

## 3. Detailed Category Audits & Code Evidence

### 3.1 Unsafe Deserialization
- **`joblib.load` Usage**:
  `src/argus/agents/threat_analysis/tools/model_loader.py:110` executes `joblib.load(model_path)` for `ISOLATION_FOREST` and `RANDOM_FOREST` models.
  `src/argus/models/loader.py:31, 40, 48` invokes `joblib.load(self.model_path)` as a fallback loader.
  Because joblib uses the Python `pickle` protocol under the hood, deserializing an untrusted or tampered `.joblib` or `.pkl` file allows arbitrary code execution via standard `__reduce__` pickle payloads.
- **`torch.load` Invocations**:
  In `scripts/p2_1_same_test_comparison.py:312` and `scripts/p2_3_reconciliation_audit.py:352`, checkpoints are loaded with explicit `weights_only=False`:
  ```python
  dann_ckpt = torch.load(DATA_DIR / "dann_results/dann_best_model.pt", map_location="cpu", weights_only=False)
  ```
  In multiple research scripts ([experiments/training/trainers/dann_model.py:303](file:///home/bhumi/GitHub/ARGUS/experiments/training/trainers/dann_model.py#L303), [experiments/ablations/phase4_execute.py:441](file:///home/bhumi/GitHub/ARGUS/experiments/ablations/phase4_execute.py#L441)), `torch.load` is called without specifying `weights_only=True`. Note that `src/argus/models/loader.py:44` does set `weights_only=True`, demonstrating that safe patterns are known in the project but inconsistently adopted.
- **`yaml.load` & `eval/exec`**:
  A full grep across the repository confirmed that `yaml.load` is not used (all occurrences use `yaml.safe_load`), and no dynamic code execution functions (`eval(`, `exec(`) are present in the codebase.

### 3.2 Secrets & Credentials
- **Default Hardcoded Keys**:
  `configs/settings.py:41-42` defines default secrets:
  ```python
  secret_key: str = Field(default="change-this-to-a-random-secret-key-in-production")
  jwt_secret_key: str = Field(default="change-this-to-a-different-random-secret-key")
  ```
  `tools/auth/generate_token.py:10` generates a 10-year admin JWT using this exact fallback key:
  ```python
  encoded_jwt = jwt.encode(to_encode, "change-this-to-a-different-random-secret-key", algorithm="HS256")
  ```
  While `configs/settings.py:236-260` blocks placeholder secrets in production mode, default local and Docker deployments run with `ENVIRONMENT=development` ([docker-compose.yml:11](file:///home/bhumi/GitHub/ARGUS/docker-compose.yml#L11)), leaving instances vulnerable to token forgery.
- **API Key in URL**:
  `src/argus/integrations/adk/narrator.py:254` passes the Gemini API key as a query parameter:
  ```python
  url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
  ```
  This leaks the credential into standard HTTP access logs, proxy request logs, and telemetry.
- **Absolute Paths**:
  Absolute development paths such as `/home/bhumi/Downloads/ARGUS_Cross_Domain_Results/argus_coral_data` and `/home/bhumi/GitHub/ARGUS` are hardcoded in `scripts/final_eval.py:13`, `scripts/fit_fusion.py:8`, `scripts/generate_p2_1_manifest.py:14`, and stored in reproducibility manifests ([results/experiments/p2_1_validation/P2_1_REPRODUCIBILITY_MANIFEST.json:6](file:///home/bhumi/GitHub/ARGUS/results/experiments/p2_1_validation/P2_1_REPRODUCIBILITY_MANIFEST.json#L6)).

### 3.3 Evaluation Leakage & Data Partition Integrity
- **Supervised Nature of "Clean Class-Aware CORAL"**:
  In `src/argus/adaptation/class_aware_coral.py:14-25`, `ClassAwareCORALAdapter.fit()` requires `y_target` to isolate samples where `y_target == c`:
  ```python
  def fit(self, X_source: np.ndarray, y_source: np.ndarray, X_target: np.ndarray, y_target: np.ndarray):
      classes = np.unique(y_source)
      for c in classes:
          idx_s = y_source == c
          idx_t = y_target == c
          if np.sum(idx_s) > 0 and np.sum(idx_t) > 0:
              adapter = CORALAdapter(reg=self.reg)
              adapter.fit(X_source[idx_s], X_target[idx_t])
  ```
  Because class-conditional covariance alignment requires target domain labels, this method cannot operate unsupervised. In legacy runs (`ciciot_train_class_aware_coral.csv`), target test set labels were directly utilized during alignment ([audit/historical/AUDIT.md:1284](file:///home/bhumi/GitHub/ARGUS/audit/historical/AUDIT.md#L1284)).
- **Massive Coordinate Overlap (98.67%) across Random Splits**:
  As documented in `audit/research/P1_1_INDEPENDENT_VERIFICATION/P1_1_LEAKAGE_AUDIT.md:18-31`, compressing high-dimensional telemetry into 4 summary features causes extreme coordinate collapse:
  - Total test rows: 2,627,177; unique 4D feature vectors: 102,188 (96.11% duplicate rate).
  - Total training rows: 8,406,962; unique 4D feature vectors: 202,194 (97.59% duplicate rate).
  - **2,592,203 test rows (98.67% of the test set) share exact identical coordinates with training observations.**
  - 79.04% of training rows and 75.72% of test rows map to coordinates that carry both Benign ($y=0$) and Attack ($y=1$) labels.
  - Stratified random splitting allowed in-domain supervised models to memorize the target label base rates at identical coordinates, creating an artificial performance floor.
- **SCADA D3 Label Leakage**:
  `archive/audits/ARGUS_D3_VALIDITY_AUDIT/FINAL_D3_VALIDITY_REPORT.md:12-20` revealed that in the IEC 60870-5-104 feature engineering pipeline, `i_msg_ratio` directly embedded the attack label (`+ (y_sub * 0.25)`), producing a spurious ROC-AUC of 0.9999.

### 3.4 Input Handling & Numerical Stability
- **Division by Zero in `extract_four_features`**:
  In `src/argus/features/extractor.py:34`:
  ```python
  out["pkt_mean_to_max"] = np.where(max_len == 0, 0.0, mean_len / max_len)
  ```
  NumPy evaluates `mean_len / max_len` before applying the mask, triggering floating-point division warnings and yielding `NaN` if `mean_len == 0` and `max_len == 0`.
- **Missing NaN/Inf and Bound Checks**:
  If input DataFrames already contain feature names (`pkt_mean_to_max`, `tcp_flag_density`, etc.), lines 29-30, 43-44, 53-54, 63-64 pass them directly into the output DataFrame without any validation.
  If corrupted packets have `Pkt Len Mean > Pkt Len Max`, `pkt_mean_to_max` exceeds 1.0 without being clipped.
  If `Pkt Len Mean` contains `NaN`, `np.clip(NaN, 0, None)` evaluates to `NaN`, and `np.log1p(NaN)` produces `NaN`.
- **Drift Calculation Stability**:
  `src/argus/shift/drift.py:27-39` constructs bin edges via `np.linspace(source_col.min(), ...)` without verifying whether the array contains NaNs or whether min equals max.

### 3.5 Dependencies & Build Hygiene
- **Unpinned Dependencies**:
  `pyproject.toml:29-55` specifies dependencies using only `>=` (e.g. `fastapi>=0.115.0`, `scikit-learn>=1.4.0`, `torch>=2.2.0`).
  `web/package.json:14-39` uses caret (`^`) version ranges.
- **Deterministic Lockfiles**:
  Both Python (`uv.lock`) and frontend (`web/package-lock.json`) maintain lockfiles in the repository.
- **Notebooks**:
  No Jupyter notebook (`.ipynb`) files exist in the repository; in-notebook `pip install` commands were not found.

### 3.6 CI/CD & GitHub Actions Workflow
- **Hardened Configurations**:
  `.github/workflows/ci.yml:10-11` configures least-privilege permissions:
  ```yaml
  permissions:
    contents: read
  ```
  All actions are pinned to full 40-character commit SHAs, verified by `tools/ci/verify_action_pins.sh`.
  Trigger events strictly use standard `pull_request` (line 8); `pull_request_target` is not present.
- **Permissive Type Gate**:
  `.github/workflows/ci.yml:44-45` runs `mypy` with `continue-on-error: true`, allowing type-checking regressions to pass unnoticed.

### 3.7 Model Artifact Integrity & Versioning
- **Unsigned Models**:
  All models under `artifacts/models/` (`model_d1_baseline.txt`, `model_d2_coral.txt`, `xgb_adapted.json`, etc.) lack digital signatures.
- **Integrity Check Bypass in Registry**:
  In `src/argus/registry/model_registry.py:292-293`:
  ```python
  if model_name in self._integrity_manifest:
      self._verify_artifact_integrity(model_name, full_path)
  ```
  The enclosing `if` block allows any model defined in `MODEL_METADATA` that is omitted from `INTEGRITY_MANIFEST.json` to be loaded without hash verification.
- **Unverified Secondary Loaders**:
  `src/argus/models/loader.py` and `src/argus/agents/threat_analysis/tools/model_loader.py` do not perform SHA-256 integrity verification against any manifest prior to loading.

### 3.8 Inference Serving, Authentication & Error Handling
- **Fail-Open Policy Engine**:
  In `src/argus/policy/policy_engine.py:14-24`:
  ```python
  if not context.risk_tier or context.risk_tier == "unknown":
      return DecisionOutput(
          action=ActionType.MONITOR,
          risk_tier="unknown",
          policy_id="POL-FAILSAFE",
          policy_version=self.version,
          requires_human_approval=False,
          reason_codes=["fallback_due_to_missing_context"],
          evidence_refs=[],
      )
  ```
  If telemetry processing or risk evaluation produces an unknown/missing risk tier, the policy engine fails open to passive `MONITOR` without human approval. Furthermore, `src/argus/policy/rules.py:20-21` specifies that an ML detector prediction of `pred=1` does not override a low risk tier, remaining in `MONITOR`.
- **In-Memory Rate Limiting DoS**:
  `src/argus/security/rate_limiter.py:11` stores client token state in an unbounded dictionary `self._buckets`. Requests with forged IP addresses or varied paths cause unbounded memory allocation.
- **Middleware Rate Limit Ordering Bug**:
  `src/argus/security/middleware.py:80` attempts to inspect `request.state.user_id` before FastAPI dependency injection has authenticated the token. Consequently, `actor_id` is always `None`, and all traffic is rate-limited under public thresholds.
- **Development Administrative Bypass**:
  `src/argus/auth/rbac.py:97-101` automatically issues a `dev-admin` principal with full permissions (`admin:system`, `approve:response`, `write:incidents`) whenever `ENVIRONMENT != "production"`. Because `docker-compose.yml:11` defaults to development mode, container deployments without explicit environment overrides run fully unauthenticated.
- **Query Parameter Token Acceptance**:
  `src/argus/auth/rbac.py:52-54, 63-64` accepts bearer tokens from the `?token=` query parameter across all HTTP endpoints, facilitating credential exposure in logs.

---

## 4. Remediation Plan

1. **P0 (Immediate / Critical)**:
   - Refactor `PolicyEngine.evaluate()` ([policy_engine.py:14-24](file:///home/bhumi/GitHub/ARGUS/src/argus/policy/policy_engine.py#L14-L24)) to fail closed: unknown or missing risk tiers must default to `ActionType.ESCALATE` with `requires_human_approval=True`.
   - In `ModelRegistry.load_all()` ([model_registry.py:292-293](file:///home/bhumi/GitHub/ARGUS/src/argus/registry/model_registry.py#L292-L293)), remove `if model_name in self._integrity_manifest:` and mandate that any unmanifested artifact aborts startup.
   - Enforce `weights_only=True` on all `torch.load()` calls across scripts ([scripts/p2_1_same_test_comparison.py:312](file:///home/bhumi/GitHub/ARGUS/scripts/p2_1_same_test_comparison.py#L312)).

2. **P1 (High Priority)**:
   - Sanitize input calculations in `extract_four_features()` ([extractor.py:28-72](file:///home/bhumi/GitHub/ARGUS/src/argus/features/extractor.py#L28-L72)) using `np.divide(..., where=...)`, range clipping, and finite checks.
   - Restrict development authentication bypass ([rbac.py:97-101](file:///home/bhumi/GitHub/ARGUS/src/argus/auth/rbac.py#L97-L101)) strictly to loopback (`127.0.0.1`) and grant read-only non-admin scopes.
   - Replace unbounded dictionary in `TokenBucketRateLimiter` ([rate_limiter.py:11](file:///home/bhumi/GitHub/ARGUS/src/argus/security/rate_limiter.py#L11)) with bounded LRU cache or Redis.
   - Transmit Google Gemini API key via HTTP headers rather than URL query parameters ([narrator.py:254](file:///home/bhumi/GitHub/ARGUS/src/argus/integrations/adk/narrator.py#L254)).

3. **P2 (Hardening & Hygiene)**:
   - Replace absolute filesystem paths in scripts and manifests with relative paths.
   - Add upper bounds to `pyproject.toml` dependencies.
   - Resolve MyPy type issues and remove `continue-on-error: true` from `.github/workflows/ci.yml:45`.
