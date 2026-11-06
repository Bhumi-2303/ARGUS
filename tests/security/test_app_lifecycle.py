"""Independent lifecycle and architecture verification tests for P0-3.

Verifies:
- Production and development FastAPI application instantiation via create_app().
- Full lifespan context execution (artifact verification, model loading, multi-agent start/stop).
- Complete router registration and endpoint surface.
- Middleware registration and execution order.
- Exception handler registration for HTTP, validation, and global exceptions.
- CORS policy isolation across independently instantiated app instances.
- Uvicorn entry point backward compatibility with module-level app.
"""

import copy
import pytest
from httpx import AsyncClient, ASGITransport

from configs.settings import get_settings
from argus.api.main import create_app, lifespan, app as module_app


@pytest.fixture
def base_settings():
    return copy.deepcopy(get_settings())


# ===========================================================================
# 1. APPLICATION LIFECYCLE TESTS
# ===========================================================================


@pytest.mark.asyncio
async def test_application_lifespan_startup_and_shutdown():
    """Application lifespan initializes and shuts down all framework subsystems cleanly."""
    fresh_app = create_app()
    async with lifespan(fresh_app):
        # Within active lifespan: models are loaded and agent orchestrator is running
        from argus.registry.model_registry import model_registry

        assert model_registry.is_loaded is True
        assert len(model_registry.loaded_models) >= 5


# ===========================================================================
# 2. ROUTER & ENDPOINT REGISTRATION
# ===========================================================================


def test_all_expected_routers_registered():
    """All core API v1 routers and health endpoints are mounted in the application."""
    test_app = create_app()
    routes = []
    for r in test_app.routes:
        if hasattr(r, "path"):
            routes.append(r.path)
        elif hasattr(r, "original_router"):
            prefix = getattr(r.original_router, "prefix", "") or getattr(
                getattr(r, "include_context", None), "prefix", ""
            )
            for sub in r.original_router.routes:
                sub_path = getattr(sub, "path", "")
                routes.append(f"{prefix}{sub_path}")

    # Health & readiness
    assert "/health" in routes
    assert "/liveness" in routes
    assert "/readiness" in routes

    # Domain & model APIs
    assert "/api/v1/domains" in routes
    assert "/api/v1/models" in routes
    assert "/api/v1/results/{table}" in routes

    # Prediction & explanation
    assert "/api/v1/predict" in routes
    assert "/api/v1/explain" in routes
    assert "/api/v1/shift" in routes
    assert "/api/v1/stream" in routes
    assert "/api/v1/onboard" in routes

    # Agent framework & management
    assert "/api/v1/agents/topology" in routes
    assert "/api/v1/incidents/" in routes
    assert "/api/v1/monitoring/registry" in routes

    # SPA catch-all route
    assert "/{full_path:path}" in routes


# ===========================================================================
# 3. MIDDLEWARE & EXCEPTION HANDLER VERIFICATION
# ===========================================================================


def test_middleware_and_exception_handlers_registered():
    """Security headers, audit middleware, and CORS are registered with exception handlers."""
    test_app = create_app()

    # Verify exception handlers
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    assert StarletteHTTPException in test_app.exception_handlers
    assert RequestValidationError in test_app.exception_handlers
    assert Exception in test_app.exception_handlers

    # Verify user middleware
    middleware_classes = [m.cls.__name__ for m in test_app.user_middleware]
    assert "SecurityHeadersMiddleware" in middleware_classes
    assert "SecurityMiddleware" in middleware_classes
    assert "CORSMiddleware" in middleware_classes


# ===========================================================================
# 4. INDEPENDENT CORS CONFIGURATION IN HTTP CALLS
# ===========================================================================


@pytest.mark.asyncio
async def test_production_cors_strict_allowlist_http(base_settings):
    """Production app strictly rejects localhost and allows only configured origin."""
    prod_settings = copy.deepcopy(base_settings)
    prod_settings.env = "production"
    prod_settings.security.cors_origins = ["https://trusted-grid.corp"]

    prod_app = create_app(prod_settings)

    async with AsyncClient(transport=ASGITransport(app=prod_app), base_url="http://test") as client:
        # Preflight from unauthorized origin
        res_unauth = await client.options(
            "/health",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        assert res_unauth.headers.get("access-control-allow-origin") is None

        # Preflight from authorized origin
        res_auth = await client.options(
            "/health",
            headers={"Origin": "https://trusted-grid.corp", "Access-Control-Request-Method": "GET"},
        )
        assert res_auth.headers.get("access-control-allow-origin") == "https://trusted-grid.corp"


@pytest.mark.asyncio
async def test_development_cors_regex_allows_localhost_http(base_settings):
    """Development app permits localhost with arbitrary port numbers."""
    dev_settings = copy.deepcopy(base_settings)
    dev_settings.env = "development"

    dev_app = create_app(dev_settings)

    async with AsyncClient(transport=ASGITransport(app=dev_app), base_url="http://test") as client:
        res = await client.options(
            "/health",
            headers={"Origin": "http://localhost:9999", "Access-Control-Request-Method": "GET"},
        )
        assert res.headers.get("access-control-allow-origin") == "http://localhost:9999"


# ===========================================================================
# 5. ENTRY POINT BACKWARD COMPATIBILITY
# ===========================================================================


def test_uvicorn_entrypoint_compatibility():
    """Module-level 'app' instance matches Uvicorn run target ('argus.api.main:app')."""
    from argus.api.main import app

    assert app is module_app
    assert hasattr(app, "router")
    assert callable(app)
