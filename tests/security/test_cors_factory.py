"""Unit and isolation tests for P0-3: Application factory (create_app) and CORS isolation.

Verifies:
- Default app creation via create_app() builds functional app.
- Production app creation via create_app(prod_settings) binds strict CORS allowlist.
- Development app creation via create_app(dev_settings) binds development origin regex.
- Production CORS rejects unauthorized origins and permits configured origins.
- Development CORS permits localhost and 127.0.0.1 with arbitrary ports.
- Multiple application instances created with different settings remain strictly isolated without cross-contamination.
- Module-level 'app' singleton remains backward-compatible with existing ASGI imports.
"""

import copy
import pytest
from httpx import AsyncClient, ASGITransport
from configs.settings import get_settings
from argus.api.main import app as module_app, create_app


@pytest.fixture
def base_settings():
    """Return a deep copy of current settings for manipulation."""
    return copy.deepcopy(get_settings())


# ===========================================================================
# 1. FACTORY CREATION TESTS
# ===========================================================================


def _extract_routes(app):
    paths = []
    for r in app.routes:
        if hasattr(r, "path"):
            paths.append(r.path)
        elif hasattr(r, "original_router"):
            prefix = getattr(r.original_router, "prefix", "") or getattr(
                getattr(r, "include_context", None), "prefix", ""
            )
            for sub in r.original_router.routes:
                sub_path = getattr(sub, "path", "")
                paths.append(f"{prefix}{sub_path}")
    return paths


def test_default_app_creation():
    """Default app creation via create_app() returns a fully functional FastAPI app."""
    fresh_app = create_app()
    assert fresh_app is not None
    assert fresh_app.title == "ARGUS Cybersecurity Platform API"
    assert hasattr(fresh_app.state, "settings")
    # Verify routers are mounted
    route_paths = _extract_routes(fresh_app)
    assert "/health" in route_paths
    assert "/api/v1/predict" in route_paths
    assert "/api/v1/models" in route_paths


def test_module_level_app_backward_compatibility():
    """Existing module-level 'app' import remains fully functional."""
    assert module_app is not None
    assert module_app.title == "ARGUS Cybersecurity Platform API"
    route_paths = _extract_routes(module_app)
    assert "/health" in route_paths


# ===========================================================================
# 2. ISOLATION BETWEEN MULTIPLE APPS
# ===========================================================================


def test_two_apps_with_different_settings_isolated(base_settings):
    """Two app instances constructed with different settings maintain strict isolation."""
    prod_settings = copy.deepcopy(base_settings)
    prod_settings.env = "production"
    prod_settings.security.cors_origins = ["https://prod.internal"]

    dev_settings = copy.deepcopy(base_settings)
    dev_settings.env = "development"
    dev_settings.security.cors_origins = ["http://dev.internal"]

    app_prod = create_app(prod_settings)
    app_dev = create_app(dev_settings)

    assert app_prod.state.settings.is_production is True
    assert app_dev.state.settings.is_production is False

    assert app_prod.state.settings.security.cors_origins == ["https://prod.internal"]
    assert app_dev.state.settings.security.cors_origins == ["http://dev.internal"]


# ===========================================================================
# 3. PRODUCTION CORS TESTS
# ===========================================================================


@pytest.mark.asyncio
async def test_production_cors_rejects_unauthorized_origin(base_settings):
    """Production CORS rejects origins not explicitly in cors_origins."""
    prod_settings = copy.deepcopy(base_settings)
    prod_settings.env = "production"
    prod_settings.security.cors_origins = ["https://trusted.grid-defense.internal"]

    prod_app = create_app(prod_settings)

    async with AsyncClient(transport=ASGITransport(app=prod_app), base_url="http://test") as client:
        # Attack origin
        res = await client.options(
            "/health",
            headers={
                "Origin": "https://malicious-attacker.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res.headers.get("access-control-allow-origin") is None

        # Localhost rejected in production when not in cors_origins
        res_local = await client.options(
            "/health",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        assert res_local.headers.get("access-control-allow-origin") is None


@pytest.mark.asyncio
async def test_production_cors_permits_allowed_origin(base_settings):
    """Production CORS permits explicitly allowed origin."""
    trusted_origin = "https://trusted.grid-defense.internal"
    prod_settings = copy.deepcopy(base_settings)
    prod_settings.env = "production"
    prod_settings.security.cors_origins = [trusted_origin]

    prod_app = create_app(prod_settings)

    async with AsyncClient(transport=ASGITransport(app=prod_app), base_url="http://test") as client:
        res = await client.options(
            "/health", headers={"Origin": trusted_origin, "Access-Control-Request-Method": "GET"}
        )
        assert res.headers.get("access-control-allow-origin") == trusted_origin
        assert res.headers.get("access-control-allow-credentials") == "true"


# ===========================================================================
# 4. DEVELOPMENT CORS TESTS
# ===========================================================================


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dev_origin",
    [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
)
async def test_development_cors_permits_local_origins(base_settings, dev_origin):
    """Development CORS allows localhost and 127.0.0.1 origins on various ports."""
    dev_settings = copy.deepcopy(base_settings)
    dev_settings.env = "development"

    dev_app = create_app(dev_settings)

    async with AsyncClient(transport=ASGITransport(app=dev_app), base_url="http://test") as client:
        res = await client.options(
            "/health", headers={"Origin": dev_origin, "Access-Control-Request-Method": "GET"}
        )
        assert res.headers.get("access-control-allow-origin") == dev_origin


@pytest.mark.asyncio
async def test_cross_app_settings_do_not_bleed(base_settings):
    """Sequential instantiation of prod and dev apps does not pollute settings or middleware."""
    prod_settings = copy.deepcopy(base_settings)
    prod_settings.env = "production"
    prod_settings.security.cors_origins = ["https://only-prod.example.com"]

    dev_settings = copy.deepcopy(base_settings)
    dev_settings.env = "development"
    dev_settings.security.cors_origins = ["http://only-dev.example.com"]

    # 1. Instantiate prod app and verify localhost is rejected
    prod_app = create_app(prod_settings)
    async with AsyncClient(transport=ASGITransport(app=prod_app), base_url="http://test") as client:
        res = await client.options(
            "/health",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        assert res.headers.get("access-control-allow-origin") is None

    # 2. Instantiate dev app and verify localhost is allowed
    dev_app = create_app(dev_settings)
    async with AsyncClient(transport=ASGITransport(app=dev_app), base_url="http://test") as client:
        res = await client.options(
            "/health",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        assert res.headers.get("access-control-allow-origin") == "http://localhost:3000"

    # 3. Query prod app AGAIN to ensure dev app creation did not alter prod app
    async with AsyncClient(transport=ASGITransport(app=prod_app), base_url="http://test") as client:
        res = await client.options(
            "/health",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        assert res.headers.get("access-control-allow-origin") is None
