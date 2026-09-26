"""FastAPI application entry point for ARGUS v1 API.

Provides production-ready configuration management, startup artifact verification,
CORS locking, request size limiting, and static SPA serving.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from argus.registry.model_registry import model_registry
from argus.api.routers.stream import global_bus
from argus.api.routers import health, domains, models, results, predict, stream, shift, explain, onboard, agents

logger = structlog.get_logger("argus.api")

# Configuration Management via Environment Variables
ARGUS_HOST = os.getenv("ARGUS_HOST", "0.0.0.0")
ARGUS_PORT = int(os.getenv("ARGUS_PORT", "8000"))
ARGUS_MODE = os.getenv("ARGUS_MODE", "demo").lower()  # "demo" or "production"
ALLOWED_ORIGINS_ENV = os.getenv(
    "ARGUS_ALLOWED_ORIGINS",
    "http://localhost,http://localhost:8000,http://localhost:3000,http://localhost:5173,http://127.0.0.1,http://127.0.0.1:8000,http://127.0.0.1:3000,http://127.0.0.1:5173"
)
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS_ENV.split(",") if o.strip()]

# Maximum allowed payload size for API endpoints (1 MB limit)
MAX_PAYLOAD_BYTES = 1024 * 1024


def verify_required_artifacts():
    """Verify that all required model artifacts, verified results, and sample files exist.
    
    Refuses to start and raises RuntimeError if any file is missing.
    """
    logger.info("startup_artifact_verification_initiated", mode=ARGUS_MODE)
    required_files = [
        "results/verified/five_model_complete_comparison.csv",
        "results/verified/dann_final_test_metrics.csv",
        "results/verified/d3_native_threshold_sweep.csv",
        "results/verified/SHAP_vs_Target_Gain.csv",
        "artifacts/models/model_d1_baseline.txt",
        "artifacts/models/model_d2_coral.txt",
        "artifacts/models/model_d3_native.txt",
        "artifacts/models/xgb_source.json",
        "artifacts/models/xgb_adapted.json",
        "data/samples/ciciot.parquet",
        "data/samples/nfton.parquet",
        "data/samples/iec104.parquet"
    ]

    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        error_msg = f"CRITICAL STARTUP FAILURE: {len(missing)} required artifact/sample file(s) missing:\n"
        for m in missing:
            error_msg += f"  - Missing file: '{m}'\n"
        logger.critical("startup_verification_failed", missing_files=missing)
        raise RuntimeError(error_msg)

    logger.info("startup_artifact_verification_passed", total_verified=len(required_files))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing model registry startup and message bus lifecycle."""
    logger.info("api_startup_initiating", mode=ARGUS_MODE)

    # 1. Startup Verification
    verify_required_artifacts()

    # 2. Load model artifacts into memory (fails loudly if invalid)
    model_registry.load_all()

    # 3. Start message bus for streaming pipeline
    await global_bus.start()

    logger.info("api_startup_complete", models_loaded=len(model_registry.loaded_models), mode=ARGUS_MODE)
    yield
    # Shutdown logic
    logger.info("api_shutdown_initiating")
    await global_bus.stop()
    logger.info("api_shutdown_complete")


app = FastAPI(
    title="ARGUS Cybersecurity Platform API",
    description="Autonomous Risk-aware Grid Understanding & Security Framework",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if ARGUS_MODE == "demo" else None,
    redoc_url="/redoc" if ARGUS_MODE == "demo" else None,
)

# Hardened CORS restricted strictly to configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Request Payload Size Limit Middleware for /api/v1/predict and /api/v1/onboard
@app.middleware("http")
async def limit_request_payload_size(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_PAYLOAD_BYTES:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": f"Payload size exceeds max limit of {MAX_PAYLOAD_BYTES} bytes."}
            )
    return await call_next(request)


# Root Health check
app.include_router(health.router)

# Versioned API v1 Routers
app.include_router(domains.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(results.router, prefix="/api/v1")
app.include_router(predict.router, prefix="/api/v1")
app.include_router(stream.router, prefix="/api/v1")
app.include_router(shift.router, prefix="/api/v1")
app.include_router(explain.router, prefix="/api/v1")
app.include_router(onboard.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1/agents")

# Mount Static Frontend SPA if built web/dist exists
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

web_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../web/dist"))

if os.path.exists(web_dist_path):
    assets_path = os.path.join(web_dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path == "health" or full_path.startswith("docs") or full_path.startswith("redoc"):
            return None
        file_path = os.path.join(web_dist_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(web_dist_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "Frontend build index.html not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("argus.api.main:app", host=ARGUS_HOST, port=ARGUS_PORT, reload=False)
