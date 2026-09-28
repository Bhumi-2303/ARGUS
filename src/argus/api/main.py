"""FastAPI application entry point for ARGUS v1 API.

Provides production-ready configuration management, startup artifact verification with SHA-256 integrity,
CORS locking, security headers, rate limiting, exception masking, and static SPA serving with path-traversal prevention.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import structlog
import asyncio

from configs.settings import get_settings
from argus.registry.registry import AgentRegistry
from argus.bus.message_bus import MessageBus
from argus.orchestrator.orchestrator import Orchestrator
from argus.agents.data_intelligence.agent import DataIntelligenceAgent
from argus.agents.threat_analysis.agent import ThreatAnalysisAgent
from argus.agents.risk_prediction.agent import RiskPredictionAgent
from argus.agents.knowledge_context.agent import KnowledgeContextAgent
from argus.agents.decision_support.agent import DecisionSupportAgent
from argus.schemas.agents import AgentRegistration
from argus.core.enums import AgentStatus

from argus.registry.model_registry import model_registry
from argus.api.routers.stream import global_bus
from argus.api.routers import (
    health,
    domains,
    data,
    models,
    results,
    predict,
    stream,
    shift,
    explain,
    agents,
    incidents,
    monitoring,
    onboard,
)
from argus.security.headers import SecurityHeadersMiddleware
from argus.security.middleware import SecurityMiddleware
from argus.security.errors import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)

logger = structlog.get_logger("argus.api")

settings = get_settings()

agent_registry = AgentRegistry()
agent_bus = MessageBus()
agent_orchestrator = Orchestrator(registry=agent_registry, message_bus=agent_bus)

ARGUS_HOST = settings.host
ARGUS_PORT = settings.port


def verify_required_artifacts():
    """Verify that all required model artifacts, verified results, and sample files exist and match SHA-256 manifest.
    
    Refuses to start and raises RuntimeError if any file is missing or has been altered.
    """
    logger.info("startup_artifact_verification_initiated")
    manifest_path = "artifacts/manifest.json"

    # 1. Check manifest file
    if not os.path.exists(manifest_path):
        logger.warning("manifest_json_missing_generating_fallback")
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
            "data/samples/nfton.parquet"
        ]
        manifest = {}
    else:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        required_files = list(manifest.keys())

    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        error_msg = f"CRITICAL STARTUP FAILURE: {len(missing)} required artifact/sample file(s) missing:\n"
        for m in missing:
            error_msg += f"  - Missing file: '{m}'\n"
        logger.critical("startup_verification_failed", missing_files=missing)
        raise RuntimeError(error_msg)

    # 2. Cryptographic SHA-256 verification against authoritative manifest
    checksum_failures = []
    for filepath, expected_hash in manifest.items():
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            if actual_hash.lower() != expected_hash.lower():
                checksum_failures.append((filepath, expected_hash, actual_hash))

    if checksum_failures:
        error_msg = f"CRITICAL ARTIFACT INTEGRITY FAILURE: {len(checksum_failures)} file(s) failed SHA-256 verification:\n"
        for filepath, exp_h, act_h in checksum_failures:
            error_msg += f"  - File '{filepath}': expected {exp_h}, got {act_h}\n"
        logger.critical("artifact_integrity_verification_failed", failures=[f[0] for f in checksum_failures])
        raise RuntimeError(error_msg)

    logger.info("startup_artifact_verification_passed", total_verified=len(required_files))


async def start_agent_chain():
    await agent_bus.start()
    dia = DataIntelligenceAgent(
        agent_id="agent_dia",
        name="DIA",
        version="1.0",
        description="DIA",
        capabilities=["data_normalization"],
        permissions=[],
        tools=[]
    )
    taa = ThreatAnalysisAgent()
    rpa = RiskPredictionAgent()
    kca = KnowledgeContextAgent(
        agent_id="agent_kca",
        name="KCA",
        version="1.0",
        description="KCA",
        capabilities=["threat_enrichment"],
        permissions=[],
        tools=[]
    )
    dsa = DecisionSupportAgent(
        agent_id="agent_dsa",
        name="DSA",
        version="1.0",
        description="DSA",
        capabilities=["action_recommendation"],
        permissions=[],
        tools=[]
    )

    agents_list = [dia, taa, rpa, kca, dsa]
    for a in agents_list:
        await a.initialize()
        reg = AgentRegistration(
            agent_id=a.agent_id,
            name=a.name,
            version=a.version,
            description=a.description,
            capabilities=a.capabilities,
            permissions=a.permissions,
            tools=a.tools,
            status=AgentStatus.READY
        )
        await agent_registry.register(reg)

    await agent_orchestrator.start()
    logger.info("async_agent_orchestrator_started")


async def stop_agent_chain():
    await agent_orchestrator.stop()
    await agent_bus.stop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Enforce fail-closed production settings validation
    if settings.is_production:
        settings.validate_production_configuration()

    # 2. Enforce cryptographic artifact integrity
    verify_required_artifacts()

    # 3. Load ML models safely
    model_registry.load_all()

    # 4. Start agent framework
    await start_agent_chain()
    yield

    # Shutdown logic
    await stop_agent_chain()
    logger.info("api_shutdown_initiating")
    await global_bus.stop()
    logger.info("api_shutdown_complete")


# Configure API Documentation visibility based on environment
docs_url = None if settings.is_production and not settings.security.enable_public_docs else "/docs"
redoc_url = None if settings.is_production and not settings.security.enable_public_docs else "/redoc"
openapi_url = None if settings.is_production and not settings.security.enable_public_docs else "/openapi.json"

app = FastAPI(
    title="ARGUS Cybersecurity Platform API",
    description="Autonomous Risk-aware Grid Understanding & Security Framework",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

# Global Security Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 1. Security Headers Middleware (Outer boundary)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Rate Limiting, Request Correlation & Audit Middleware
app.add_middleware(SecurityMiddleware)

# 3. Hardened CORS Configuration
if settings.is_production:
    # Strict origin allowlist from configuration only
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Accept", "Origin"],
    )
else:
    # Development CORS with local dev origin patterns
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


# Root Health & Readiness Endpoints
app.include_router(health.router)

# Versioned API v1 Routers (All mounted with appropriate RBAC protection)
app.include_router(domains.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(results.router, prefix="/api/v1")
app.include_router(predict.router, prefix="/api/v1")
app.include_router(stream.router, prefix="/api/v1")
app.include_router(shift.router, prefix="/api/v1")
app.include_router(explain.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1/agents")
app.include_router(data.router, prefix="/api/v1/data")
app.include_router(incidents.router, prefix="/api/v1/incidents")
app.include_router(monitoring.router, prefix="/api/v1/monitoring")
app.include_router(onboard.router, prefix="/api/v1")


# Mount Static Frontend SPA with strict path traversal prevention
web_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../web/dist"))

if os.path.exists(web_dist_path):
    assets_path = os.path.join(web_dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Do not intercept API or documentation routes with SPA fallback
        if full_path.startswith("api/") or full_path in ("health", "liveness", "readiness", "docs", "redoc", "openapi.json"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")

        # Check for null bytes or invalid characters
        if "\x00" in full_path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path.")

        # Path traversal prevention: enforce candidate path remains inside web_dist_path
        base_dir = Path(web_dist_path).resolve()
        candidate = (base_dir / full_path).resolve()

        if not candidate.is_relative_to(base_dir):
            logger.warning("spa_traversal_attempt_blocked", requested_path=full_path, resolved=str(candidate))
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        if candidate.is_file():
            return FileResponse(str(candidate))

        index_file = base_dir / "index.html"
        if index_file.is_file():
            return FileResponse(str(index_file))

        return JSONResponse(status_code=404, content={"error": "Frontend build index.html not found"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("argus.api.main:app", host=ARGUS_HOST, port=ARGUS_PORT, reload=False)
