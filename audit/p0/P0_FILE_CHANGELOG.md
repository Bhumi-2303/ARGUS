# ARGUS P0 File Changelog

**Execution Date**: 2026-11-01  
**Git Baseline**: Commit `63224da` (Branch `v2-transformer-exploratory`)  
**Scope**: Exact file changes and additions for P0-1, P0-2, and P0-3 defect remediation.

---

## 1. Summary of Changes

### Modified Files (Tracked):
1. `src/argus/registry/model_registry.py` (P0-1)
2. `src/argus/schemas/api.py` (P0-1)
3. `src/argus/api/routers/predict.py` (P0-1)
4. `src/argus/api/routers/explain.py` (P0-1)
5. `src/argus/api/main.py` (P0-2, P0-3)
6. `tests/security/test_adversarial_verification.py` (P0-2, P0-3)

### Added Files (New Tests & Deliverables):
1. `tests/unit/test_model_registry_d3.py` (P0-1 test suite)
2. `tests/security/test_spa_traversal.py` (P0-2 test suite)
3. `tests/security/test_cors_factory.py` (P0-3 test suite)
4. `audit/p0/P0_REMEDIATION_REPORT.md`
5. `audit/p0/P0_TEST_EVIDENCE.md`
6. `audit/p0/P0_FILE_CHANGELOG.md`
7. `audit/p0/P0_ACCEPTANCE_CHECKLIST.md`
8. `audit/p0/p0_validation_summary.json`

### Untracked User Files (Preserved Untouched):
- `ARGUS_ALL_RESEARCH_RESULTS.xlsx`
- `ARGUS_INDEPENDENT_AUDIT/`
- `paper/experiments/`
- `results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`
- `scripts/generate_master_research_excel.py`

---

## 2. Line-by-Line File Modifications

### 2.1 `src/argus/registry/model_registry.py`

#### Changes:
1. Defined `D3_NATIVE_FEATURES` (the exact 73 feature names).
2. Updated `MODEL_METADATA["model_d3_native"]["provenance"]["features"]` to point to `D3_NATIVE_FEATURES`.
3. Implemented `get_expected_features(self, model_name: str) -> List[str]`.
4. Implemented `_validate_and_prepare_features()` for schema checking, missing feature identification, unexpected column rejection, NaN/inf guards, and column alignment.
5. Refactored `predict()`, `predict_batch()`, and `explain()` to use model-specific feature schemas instead of hardcoding `HARMONIZED_FEATURES`.

#### Diff:
```diff
@@ -21,6 +21,22 @@ logger = structlog.get_logger("argus.registry")
 HARMONIZED_FEATURES = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
 
+D3_NATIVE_FEATURES = [
+    "Flow_Duration", "Tot_Fwd_Pkts", "Tot_Bwd_Pkts", "TotLen_Fwd_Pkts", "TotLen_Bwd_Pkts",
+    "Fwd_Pkt_Len_Max", "Fwd_Pkt_Len_Min", "Fwd_Pkt_Len_Mean", "Fwd_Pkt_Len_Std",
+    "Bwd_Pkt_Len_Max", "Bwd_Pkt_Len_Min", "Bwd_Pkt_Len_Mean", "Bwd_Pkt_Len_Std",
+    "Flow_Byts/s", "Flow_Pkts/s", "Flow_IAT_Mean", "Flow_IAT_Std", "Flow_IAT_Max", "Flow_IAT_Min",
+    "Fwd_IAT_Tot", "Fwd_IAT_Mean", "Fwd_IAT_Std", "Fwd_IAT_Max", "Fwd_IAT_Min",
+    "Bwd_IAT_Tot", "Bwd_IAT_Mean", "Bwd_IAT_Std", "Bwd_IAT_Max", "Bwd_IAT_Min",
+    "Bwd_PSH_Flags", "Fwd_Header_Len", "Bwd_Header_Len", "Fwd_Pkts/s", "Bwd_Pkts/s",
+    "Pkt_Len_Min", "Pkt_Len_Max", "Pkt_Len_Mean", "Pkt_Len_Std", "Pkt_Len_Var",
+    "FIN_Flag_Cnt", "SYN_Flag_Cnt", "RST_Flag_Cnt", "PSH_Flag_Cnt", "ACK_Flag_Cnt",
+    "Down/Up_Ratio", "Pkt_Size_Avg", "Fwd_Seg_Size_Avg", "Bwd_Seg_Size_Avg",
+    "Subflow_Fwd_Pkts", "Subflow_Fwd_Byts", "Subflow_Bwd_Pkts", "Subflow_Bwd_Byts",
+    "Init_Bwd_Win_Byts", "Fwd_Act_Data_Pkts",
+    "Active_Mean", "Active_Std", "Active_Max", "Active_Min",
+    "Idle_Mean", "Idle_Std", "Idle_Max", "Idle_Min",
+    "pkt_mean_to_max", "log_pkt_mean", "log_pkt_max", "tcp_flag_density",
+    "pkt_min_to_max", "pkt_range_ratio", "log_flow_activity", "log_flow_bytes",
+    "fwd_pkt_ratio", "log_flow_duration", "iat_cv"
+]
+
@@ -72,3 +88,3 @@ MODEL_METADATA = {
             "adaptation_method": "NONE",
-            "features": HARMONIZED_FEATURES,
+            "features": D3_NATIVE_FEATURES,
             "training_date": "2026-08-20",
@@ -288,3 +304,63 @@ class ModelRegistry:
         return res
 
+    def get_expected_features(self, model_name: str) -> List[str]:
+        """Return the expected list of feature names for a given model."""
+        if model_name not in MODEL_METADATA:
+            raise KeyError(f"Unknown model name '{model_name}'. Available: {list(MODEL_METADATA.keys())}")
+        meta = MODEL_METADATA[model_name]
+        return list(meta.get("provenance", {}).get("features", HARMONIZED_FEATURES))
+
+    def _validate_and_prepare_features(
+        self, model_name: str, features: Dict[str, float]
+    ) -> Tuple[np.ndarray, List[str]]:
+        """Validate input features against model schema and return aligned numpy array."""
+        expected_features = self.get_expected_features(model_name)
+        norm_features: Dict[str, Any] = {
+            k.replace(" ", "_"): v for k, v in features.items()
+        }
+        missing = [col for col in expected_features if col not in norm_features]
+        if missing:
+            raise ValueError(
+                f"Model '{model_name}' requires {len(expected_features)} features, "
+                f"but {len(missing)} required feature(s) are missing. "
+                f"Missing: {missing[:10]}{'...' if len(missing) > 10 else ''}."
+            )
+        extra = sorted(set(norm_features.keys()) - set(expected_features))
+        if extra:
+            raise ValueError(
+                f"Model '{model_name}' received {len(extra)} unexpected feature(s): "
+                f"{extra[:10]}{'...' if len(extra) > 10 else ''}. "
+                f"Expected exactly {len(expected_features)} features."
+            )
+        for col in expected_features:
+            val = norm_features[col]
+            if val is None or not isinstance(val, (int, float, np.number)) or np.isnan(val) or np.isinf(val):
+                raise ValueError(
+                    f"Feature '{col}' contains invalid non-finite value: {val!r} (type {type(val).__name__})."
+                )
+        x_vec = np.array(
+            [[float(norm_features[col]) for col in expected_features]],
+            dtype=np.float32
+        )
+        return x_vec, expected_features
```

---

### 2.2 `src/argus/schemas/api.py`

#### Changes:
1. Imported `ConfigDict` from `pydantic`.
2. Added `model_config = ConfigDict(extra="allow")` to `FeatureInput` to preserve non-harmonized native features when received by the API.

#### Diff:
```diff
@@ -3,3 +3,3 @@ import math
 from typing import Dict, List, Any, Optional, Generic, TypeVar
-from pydantic import BaseModel, Field, field_validator
+from pydantic import BaseModel, Field, field_validator, ConfigDict
 
@@ -62,2 +62,4 @@ class ResultTableResponse(BaseModel):
 class FeatureInput(BaseModel):
     """Input feature vector with strict finite number and range bounds."""
+    model_config = ConfigDict(extra="allow")
+
```

---

### 2.3 `src/argus/api/routers/predict.py` and `explain.py`

#### Changes:
1. Caught `(KeyError, ValueError)` in route handlers to map schema validation errors directly to HTTP 400 Bad Request instead of returning generic HTTP 500 errors.

#### Diff:
```diff
--- a/src/argus/api/routers/predict.py
+++ b/src/argus/api/routers/predict.py
@@ -34,4 +34,4 @@ async def predict_flow(
-    except KeyError as ke:
+    except (KeyError, ValueError) as ke:
         logger.warning("predict_unknown_model_or_feature", model=model_name, error=str(ke))
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
-            detail=f"Unknown model '{model_name}' or invalid feature structure."
+            detail=str(ke)
         )

--- a/src/argus/api/routers/explain.py
+++ b/src/argus/api/routers/explain.py
@@ -35,5 +35,5 @@ async def explain_flow(
-    except KeyError:
-        logger.warning("explain_unknown_model", model=model_name)
+    except (KeyError, ValueError) as ke:
+        logger.warning("explain_unknown_model_or_feature", model=model_name, error=str(ke))
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
-            detail=f"Model '{model_name}' is not configured for SHAP feature attribution."
+            detail=str(ke)
         )
```

---

### 2.4 `src/argus/api/main.py`

#### Changes:
1. Added `create_app(settings: Optional[Any] = None) -> FastAPI` application factory.
2. Encapsulated middleware configuration, exception handlers, router registration, and static file serving within `create_app`.
3. Retained module-level `app = create_app()` for ASGI backward compatibility.
4. Hardened `serve_spa()` to reject path traversal patterns (`..`, `\\`, `%2e%2e`, `%2f`, null bytes), check document root containment, reject missing static assets/files (returning 404), reject system directory prefixes, and restrict `index.html` fallback to legitimate SPA routes.

#### Diff:
```diff
@@ -9,2 +9,3 @@ import json
 import hashlib
+from typing import Optional, Any
 from pathlib import Path
@@ -185,5 +186,8 @@ async def stop_agent_chain():
 @asynccontextmanager
 async def lifespan(app: FastAPI):
-    # 1. Enforce fail-closed production settings validation
-    if settings.is_production:
-        settings.validate_production_configuration()
+    app_settings = getattr(app.state, "settings", None)
+    if app_settings is None:
+        app_settings = get_settings()
+
+    if app_settings.is_production:
+        app_settings.validate_production_configuration()
@@ -211,4 +215,86 @@ async def lifespan(app: FastAPI):
 
+VALID_SPA_ROUTES = {
+    "",
+    "overview",
+    "input",
+    "topology",
+    "explain",
+    "results",
+    "privacy",
+    "terms",
+    "dashboard",
+    "models",
+    "shift",
+    "benchmark",
+    "analysis",
+    "protocol_limits",
+    "settings",
+    "demo",
+}
+
+BLOCKED_PATH_PREFIXES = (
+    "etc", "proc", "sys", "var", "dev", "bin", "sbin", "usr",
+    "home", "root", "boot", "opt", "tmp", "windows", "system32", "assets",
+)
+
+def _configure_spa(app: FastAPI, web_dist_path: str) -> None:
+    if not os.path.exists(web_dist_path):
+        return
+    assets_path = os.path.join(web_dist_path, "assets")
+    if os.path.exists(assets_path):
+        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
+
+    @app.get("/{full_path:path}")
+    async def serve_spa(full_path: str, request: Request):
+        if full_path.startswith("api/") or full_path.startswith("api\\") or full_path in ("health", "liveness", "readiness", "docs", "redoc", "openapi.json"):
+            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")
+
+        raw_path = request.url.path
+        if "\x00" in full_path or "\x00" in raw_path:
+            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path.")
+
+        traversal_patterns = ("..", "\\", "%2e%2e", "%2f", "%5c", "..%2f", "%2e%2e%2f")
+        lower_raw = raw_path.lower()
+        lower_full = full_path.lower()
+        if any(pat in lower_full or pat in lower_raw for pat in traversal_patterns):
+            logger.warning("spa_traversal_attempt_blocked", requested_path=full_path, raw_path=raw_path)
+            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path traversal sequence.")
+
+        base_dir = Path(web_dist_path).resolve()
+        try:
+            candidate = (base_dir / full_path).resolve()
+        except Exception:
+            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path.")
+
+        if not candidate.is_relative_to(base_dir):
+            logger.warning("spa_traversal_attempt_blocked", requested_path=full_path, resolved=str(candidate))
+            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access denied.")
+
+        if candidate.is_file():
+            return FileResponse(str(candidate))
+
+        has_extension = bool(candidate.suffix) or ("." in Path(full_path).name)
+        if has_extension or full_path.startswith("assets/"):
+            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Static asset '{full_path}' not found.")
+
+        clean_path = full_path.strip("/")
+        first_segment = clean_path.split("/")[0].lower() if clean_path else ""
+        if first_segment in BLOCKED_PATH_PREFIXES:
+            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")
+
+        if clean_path in VALID_SPA_ROUTES or (len(Path(full_path).parts) <= 1 and not has_extension):
+            index_file = base_dir / "index.html"
+            if index_file.is_file():
+                return FileResponse(str(index_file))
+            return JSONResponse(status_code=404, content={"error": "Frontend build index.html not found"})
+
+        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")
+
+def create_app(settings: Optional[Any] = None) -> FastAPI:
+    app_settings = settings if settings is not None else get_settings()
+    # ... attaches middleware, exception handlers, routers, SPA ...
+    return application
+
+app = create_app()
```

---

### 2.5 `tests/security/test_adversarial_verification.py`

#### Changes:
1. Imported `create_app` from `argus.api.main`.
2. Updated `test_cors_rejects_unauthorized_origins` to create a dedicated production app instance with `mock_prod_environment` (`prod_app = create_app(mock_prod_environment)`), isolating CORS verification from the module-level development app.

#### Diff:
```diff
@@ -23,3 +23,3 @@ from argus.auth.jwks import JWKSClient
 from argus.auth.jwt import JWTValidator
 from argus.auth.models import UserPrincipal
-from argus.api.main import app
+from argus.api.main import app, create_app
 from argus.security.audit import AuditLogger
@@ -507,3 +507,4 @@ async def test_cors_rejects_unauthorized_origins(mock_prod_environment):
     """Unauthorized origins do not receive Access-Control-Allow-Origin."""
-    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
+    prod_app = create_app(mock_prod_environment)
+    async with AsyncClient(transport=ASGITransport(app=prod_app), base_url="http://test") as client:
         # Malicious origin
```

---

## 3. Verification of Zero Inadvertent Changes

1. **No changes to ML weights**: Git diff confirms 0 changes in `artifacts/models/`. SHA-256 integrity manifest check passes 100%.
2. **No changes to datasets or samples**: 0 changes in `data/`.
3. **No changes to evaluation results**: 0 changes in `results/verified/` or `results/diagnostic/`.
4. **No uncommitted files removed**: Untracked user spreadsheets and independent audit folders remain in place.
