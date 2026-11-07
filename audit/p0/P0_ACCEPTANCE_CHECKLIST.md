# ARGUS P0 Defect Remediation Acceptance Checklist

**Audit Date**: 2026-11-01  
**Git Commit**: `63224da`  
**Branch**: `v2-transformer-exploratory`  
**Review Status**: **ALL ACCEPTANCE CRITERIA VERIFIED (PASS)**

---

## 1. Non-Negotiable Execution Rules

| Rule # | Requirement | Status | Evidence / Verification Method |
|---|---|---|---|
| **R-01** | Inspect Git branch, commit, working tree, and source files before modifying anything | **PASS** | Checked via `git status`, `git log`, file inspection at startup. |
| **R-02** | Independently reproduce each defect before changing code | **PASS** | Reproduced LightGBM 73-vs-4 crash, SPA traversal 200 fallback, and CORS localhost bleed. |
| **R-03** | Do not overwrite unrelated user changes | **PASS** | `git status` verifies no modifications to existing uncommitted files. |
| **R-04** | Do not discard, reset, or clean uncommitted files | **PASS** | All untracked Excel workbooks and audit folders remain intact. |
| **R-05** | Do not modify datasets, model weights, training pipelines, or scientific conclusions | **PASS** | 0 changes in `data/`, `artifacts/models/`, `results/`, or paper claims. |
| **R-06** | No dummy implementations, hardcoded predictions, fake test results, or mocked success | **PASS** | Real LightGBM/TreeExplainer executions verified on disk; real Starlette middleware stack tested. |
| **R-07** | Do not silently reduce test coverage or weaken existing assertions | **PASS** | Expanded test coverage from 183 to 254 tests (+71 tests); no assertions removed. |
| **R-08** | Do not suppress exceptions simply to prevent failures | **PASS** | Strict ValueError/KeyError propagation with explicit error messages. |
| **R-09** | Do not change public API unnecessarily | **PASS** | Retained existing endpoint signatures, parameter names, and default response schemas. |
| **R-10** | Keep changes minimal, maintainable, documented, and backward-compatible | **PASS** | Minimal surgical edits; module-level `app` retained; 4-feature models unchanged. |
| **R-11** | Run tests against actual implementation and distinguish test categories | **PASS** | Unit, integration, security, and full regression tests cleanly categorized and executed. |
| **R-12** | Never claim a test passed unless execution output supports it | **PASS** | Raw pytest stdout logs documented in `P0_TEST_EVIDENCE.md`. |

---

## 2. P0-1: D3 Native Model Feature Mismatch

| Item ID | Acceptance Criterion | Status | Evidence / Test Identifier |
|---|---|---|---|
| **P0-1.1** | Native D3 inference receives exact feature schema trained on (73 features) | **PASS** | `D3_NATIVE_FEATURES` verified against `model_d3_native.txt` header. |
| **P0-1.2** | Preserve feature names and exact training ordering | **PASS** | Vector assembled strictly in order defined by booster (`bst.feature_name()`). |
| **P0-1.3** | Validate input dimensions before prediction | **PASS** | `_validate_and_prepare_features` checks exact column count. |
| **P0-1.4** | Produce clear, actionable error when required features are missing | **PASS** | `test_native_d3_missing_specific_feature_named` confirms missing column names in error. |
| **P0-1.5** | Reject unexpected feature schemas rather than silently accepting | **PASS** | `test_unexpected_extra_features_rejected` raises ValueError on unknown keys. |
| **P0-1.6** | Do not automatically pad missing columns with zeros | **PASS** | Any missing column raises ValueError immediately. |
| **P0-1.7** | Do not truncate 73 features to 4 | **PASS** | Verified full 73-dimensional vector passed to LightGBM. |
| **P0-1.8** | Do not change model weights | **PASS** | SHA-256 hash `0dcac73c8655...` verified identical against manifest. |
| **P0-1.9** | Valid native D3 input with all 73 features succeeds | **PASS** | `test_valid_native_d3_input_succeeds` (returns prob, label, threshold=0.50). |
| **P0-1.10** | Native D3 input with 72 features fails with clear validation error | **PASS** | `test_native_d3_input_with_72_features_rejected`. |
| **P0-1.11** | Native D3 input with 4 features fails with clear validation error | **PASS** | `test_native_d3_input_with_four_features_rejected`. |
| **P0-1.12** | Incorrect feature ordering in input dict correctly aligns by schema | **PASS** | `test_d3_feature_ordering_invariance`. |
| **P0-1.13** | Input with space-separated feature names normalizes cleanly | **PASS** | `test_d3_features_with_spaces_normalized`. |
| **P0-1.14** | Existing 4-feature models remain fully functional | **PASS** | `test_existing_four_feature_models_remain_functional` across 4 models. |
| **P0-1.15** | Invalid values (NaN, +Inf, -Inf) rejected consistently | **PASS** | `test_native_d3_rejects_nan`, `positive_inf`, `negative_inf`. |
| **P0-1.16** | Unverified model (`dann`) fails in controlled manner | **PASS** | `test_unavailable_model_dann_raises_not_implemented` (501). |
| **P0-1.17** | Batch prediction on (N, 73) succeeds; dimension mismatch rejected | **PASS** | `test_predict_batch_native_d3_succeeds`, `dimension_mismatch_rejected`. |
| **P0-1.18** | SHAP feature attribution generates attributions for all 73 features | **PASS** | `test_explain_native_d3_generates_all_73_attributions`. |
| **P0-1.19** | End-to-end integration test via `/api/v1/predict` succeeds | **PASS** | `test_api_predict_native_d3_with_73_features_succeeds` (200 OK). |
| **P0-1.20** | End-to-end integration test with 4 features returns 400 Bad Request | **PASS** | `test_api_predict_native_d3_with_four_features_returns_400`. |

---

## 3. P0-2: SPA Catch-All Route Path Traversal Handling

| Item ID | Acceptance Criterion | Status | Evidence / Test Identifier |
|---|---|---|---|
| **P0-2.1** | Legitimate SPA routes continue returning `index.html` with HTTP 200 | **PASS** | `test_valid_root_route_returns_index_html`, `test_valid_client_side_routes_return_index_html`. |
| **P0-2.2** | Existing static assets served correctly with HTTP 200 | **PASS** | `test_valid_static_asset_returns_200`. |
| **P0-2.3** | Missing static assets (`.js`, `.css`) return HTTP 404, never `index.html` | **PASS** | `test_missing_static_assets_return_404`. |
| **P0-2.4** | Missing file-like paths (`/favicon.ico`, `/robots.txt`) return HTTP 404 | **PASS** | `test_missing_file_like_paths_return_404`. |
| **P0-2.5** | Directory traversal sequence `../../../../etc/passwd` rejected with 400/404 | **PASS** | `test_traversal_sequence_rejected`. |
| **P0-2.6** | URL-encoded traversal `%2e%2e%2f` rejected with 400/404 | **PASS** | `test_encoded_traversal_rejected`. |
| **P0-2.7** | Traversal via API routes rejected with 400/404 | **PASS** | `test_traversal_via_api_route_rejected`. |
| **P0-2.8** | Null byte injection rejected with HTTP 400 | **PASS** | `test_null_byte_injection_rejected`. |
| **P0-2.9** | Absolute system path injection (`/etc/passwd`, `/sys/class/net`) returns 404 | **PASS** | `test_absolute_system_path_injection_returns_404`. |
| **P0-2.10** | Paths attempting to escape document root return 400/403 | **PASS** | Enforced via `candidate.is_relative_to(base_dir)`. |
| **P0-2.11** | Return codes are semantically appropriate (400, 404, 200) | **PASS** | Verified across all 39 tests in `test_spa_traversal.py`. |
| **P0-2.12** | Adversarial suite path traversal test passes | **PASS** | `test_path_traversal_all_vectors_rejected` in `test_adversarial_verification.py`. |

---

## 4. P0-3: Application Factory and CORS Test Isolation

| Item ID | Acceptance Criterion | Status | Evidence / Test Identifier |
|---|---|---|---|
| **P0-3.1** | Introduce `create_app(settings=None)` in `src/argus/api/main.py` | **PASS** | Function implemented and exported. |
| **P0-3.2** | Builds and returns fully configured FastAPI application | **PASS** | Verified in `test_default_app_creation`. |
| **P0-3.3** | Uses default settings when settings not provided | **PASS** | Verified via `app.state.settings`. |
| **P0-3.4** | All middleware, exception handlers, routers, SPA mounts attached in factory | **PASS** | Verified routes and middleware stacks. |
| **P0-3.5** | Module-level `app = create_app()` retained for backward compatibility | **PASS** | `test_module_level_app_backward_compatibility`. |
| **P0-3.6** | Production app creation configures production CORS allowlist without regex | **PASS** | `test_production_cors_rejects_unauthorized_origin`. |
| **P0-3.7** | Development app creation configures development CORS with localhost regex | **PASS** | `test_development_cors_permits_local_origins`. |
| **P0-3.8** | Production CORS rejects unauthorized origins (including localhost) | **PASS** | Verified in `test_cors_rejects_unauthorized_origins`. |
| **P0-3.9** | Production CORS permits explicitly configured origins | **PASS** | `test_production_cors_permits_allowed_origin`. |
| **P0-3.10** | Two apps with different settings maintain strict state isolation | **PASS** | `test_two_apps_with_different_settings_isolated`. |
| **P0-3.11** | Sequential instantiation does not bleed state across apps | **PASS** | `test_cross_app_settings_do_not_bleed`. |
| **P0-3.12** | Adversarial suite CORS test passes against isolated prod app | **PASS** | `test_cors_rejects_unauthorized_origins` in `test_adversarial_verification.py`. |

---

## 5. Verification & Release Gate Signoff

| Verification Pillar | Criterion | Target | Actual Result | Signoff |
|---|---|---|---|---|
| **Test Suite Pass Rate** | Full pytest execution | 100% pass | **254 passed, 0 failed** (100%) | **APPROVED** |
| **Regression Failures** | Failures in existing tests | 0 | **0** | **APPROVED** |
| **Ground Truth Numbers** | `verify_ui_numbers.py` | 100% match | **All 5 tables match 100%** | **APPROVED** |
| **Artifact Immutability** | Model weights / datasets | Unaltered | **0 files altered** | **APPROVED** |
| **Audit Dossier** | All 5 deliverables in `audit/p0/` | Complete | **All 5 files created** | **APPROVED** |

### Release Gate Status: **CLEARED (PASS)**
All three P0 engineering defects are remediated, tested, and verified. The repository is cleared for research execution.
