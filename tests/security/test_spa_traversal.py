"""Security tests for P0-2: SPA catch-all route traversal handling.

Verifies:
- Legitimate frontend SPA routes return index.html with HTTP 200.
- Existing static assets are served with HTTP 200.
- Missing static assets and file-like paths return HTTP 404 (never falling back to index.html).
- Directory traversal sequences and encoded patterns return HTTP 400 or 404.
- Null byte injections return HTTP 400.
- Absolute system path injections return HTTP 400 or 404.
"""

import os
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from argus.api.main import app


@pytest.fixture
def any_asset_name():
    """Find an existing asset file from web/dist/assets or web/dist to test real file serving."""
    web_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/dist"))
    assets_dir = os.path.join(web_dist, "assets")
    if os.path.exists(assets_dir):
        files = [f for f in os.listdir(assets_dir) if os.path.isfile(os.path.join(assets_dir, f))]
        if files:
            return f"assets/{files[0]}"
    # Fallback to favicon.svg or icons.svg
    if os.path.exists(os.path.join(web_dist, "favicon.svg")):
        return "favicon.svg"
    return None


# ===========================================================================
# 1. VALID FRONTEND SPA ROUTES (200 OK with index.html)
# ===========================================================================


@pytest.mark.asyncio
async def test_valid_root_route_returns_index_html():
    """Valid root route '/' returns index.html with HTTP 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert "<!doctype html" in res.text.lower() or "<html" in res.text.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route",
    [
        "/dashboard",
        "/input",
        "/topology",
        "/explain",
        "/results",
        "/privacy",
        "/terms",
        "/models",
        "/shift",
        "/overview",
    ],
)
async def test_valid_client_side_routes_return_index_html(route):
    """Recognized client-side SPA routes return index.html with HTTP 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(route)
        assert res.status_code == 200, f"Route {route} failed: {res.status_code}"
        assert "<!doctype html" in res.text.lower() or "<html" in res.text.lower()


# ===========================================================================
# 2. STATIC ASSET SERVING & 404 ON MISSING ASSETS
# ===========================================================================


@pytest.mark.asyncio
async def test_valid_static_asset_returns_200(any_asset_name):
    """An existing static file in web/dist or web/dist/assets is served with HTTP 200."""
    if not any_asset_name:
        pytest.skip("No static assets built in web/dist.")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(f"/{any_asset_name}")
        assert res.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "missing_asset",
    [
        "/assets/missing.js",
        "/assets/nonexistent.css",
        "/assets/bundle.abc12345.js",
    ],
)
async def test_missing_static_assets_return_404(missing_asset):
    """Missing static assets in /assets/ must return HTTP 404, never index.html."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(missing_asset)
        assert res.status_code == 404
        assert "<!doctype html" not in res.text.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_path",
    [
        "/favicon.ico",
        "/robots.txt",
        "/sitemap.xml",
        "/nonexistent_file.png",
        "/styles.css",
    ],
)
async def test_missing_file_like_paths_return_404(file_path):
    """Missing file-like paths with extensions must return HTTP 404, never index.html."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(file_path)
        assert res.status_code == 404
        assert "<!doctype html" not in res.text.lower()


# ===========================================================================
# 3. DIRECTORY TRAVERSAL & MALICIOUS PATH REJECTION
# ===========================================================================


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        "../../../../etc/passwd",
        "../../etc/shadow",
        "../../../proc/self/environ",
        "../../../../Windows/System32/cmd.exe",
        "..\\..\\Windows\\win.ini",
    ],
)
async def test_traversal_sequence_rejected(payload):
    """Relative traversal patterns return HTTP 400 or HTTP 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(f"/{payload}")
        assert res.status_code in (400, 404), f"Payload '{payload}' returned {res.status_code}"
        assert "<!doctype html" not in res.text.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "encoded_payload",
    [
        "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "%2e%2e%5c%2e%2e%5cboot.ini",
        "....//....//etc/passwd",
    ],
)
async def test_encoded_traversal_rejected(encoded_payload):
    """URL-encoded and double-dot traversal sequences return HTTP 400 or HTTP 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(f"/{encoded_payload}")
        assert res.status_code in (400, 404)
        assert "<!doctype html" not in res.text.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_traversal",
    [
        "/api/v1/results/../../../../etc/passwd",
        "/api/v1/domains/..%2F..%2Fetc%2Fpasswd",
        "/api/v1/../../../../etc/passwd",
    ],
)
async def test_traversal_via_api_route_rejected(api_traversal):
    """Traversal attempts through API URL prefixes return HTTP 400 or HTTP 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(api_traversal)
        assert res.status_code in (400, 404)
        assert "<!doctype html" not in res.text.lower()


@pytest.mark.asyncio
async def test_null_byte_injection_rejected():
    """Null byte injection in path returns HTTP 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/index.html%00.png")
        assert res.status_code in (400, 404)
        assert "<!doctype html" not in res.text.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "abs_path",
    [
        "/etc/passwd",
        "/etc/shadow",
        "/var/log/syslog",
        "/proc/cpuinfo",
        "/sys/class/net",
        "/bin/bash",
    ],
)
async def test_absolute_system_path_injection_returns_404(abs_path):
    """Requests targeting system paths (e.g. /etc/passwd) return HTTP 404, never index.html."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(abs_path)
        assert res.status_code in (400, 404)
        assert "<!doctype html" not in res.text.lower()


# ===========================================================================
# 4. RAW ASGI DIRECT DISPATCH TESTS (BYPASSING CLIENT-SIDE NORMALIZATION)
# ===========================================================================


async def _dispatch_raw_asgi(path: str, raw_path: bytes):
    """Dispatch raw ASGI HTTP request directly to app, bypassing client URL normalization."""
    response_started = {}
    response_body = []

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": raw_path,
        "query_string": b"",
        "headers": [(b"host", b"testserver")],
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 80),
    }

    disconnect_event = asyncio.Event()
    sent_request = False

    async def receive():
        nonlocal sent_request
        if not sent_request:
            sent_request = True
            return {"type": "http.request", "body": b"", "more_body": False}
        await disconnect_event.wait()
        return {"type": "http.disconnect"}

    async def send(message):
        if message["type"] == "http.response.start":
            response_started.update(message)
        elif message["type"] == "http.response.body":
            response_body.append(message.get("body", b""))
            if not message.get("more_body", False):
                disconnect_event.set()

    await app(scope, receive, send)

    status_code = response_started.get("status", 500)
    headers = {
        k.decode("latin-1"): v.decode("latin-1") for k, v in response_started.get("headers", [])
    }
    body = b"".join(response_body).decode("latin-1", errors="ignore")
    return status_code, headers, body


@pytest.mark.asyncio
async def test_raw_asgi_unnormalized_traversal_rejected():
    """Raw unnormalized dot-dot traversal via ASGI returns HTTP 400 Bad Request."""
    status, headers, body = await _dispatch_raw_asgi(
        path="/../../../../etc/passwd", raw_path=b"/../../../../etc/passwd"
    )
    assert status == 400
    assert "Invalid path traversal" in body
    assert "root:x:0:0:" not in body
    assert "<!doctype html" not in body.lower()


@pytest.mark.asyncio
async def test_raw_asgi_double_encoded_traversal_rejected():
    """Raw double-encoded dot-dot traversal via ASGI returns HTTP 400 Bad Request."""
    status, headers, body = await _dispatch_raw_asgi(
        path="/%252e%252e/%252e%252e/etc/passwd", raw_path=b"/%252e%252e/%252e%252e/etc/passwd"
    )
    assert status == 400
    assert "Invalid path traversal" in body
    assert "root:x:0:0:" not in body
    assert "<!doctype html" not in body.lower()


@pytest.mark.asyncio
async def test_raw_asgi_backslash_traversal_rejected():
    """Raw Windows backslash traversal via ASGI returns HTTP 400 Bad Request."""
    status, headers, body = await _dispatch_raw_asgi(
        path="/..\\..\\Windows\\System32\\cmd.exe", raw_path=b"/..\\..\\Windows\\System32\\cmd.exe"
    )
    assert status == 400
    assert "Invalid path traversal" in body
    assert "<!doctype html" not in body.lower()


@pytest.mark.asyncio
async def test_raw_asgi_null_byte_rejected():
    """Raw null byte injection via ASGI returns HTTP 400 Bad Request."""
    status, headers, body = await _dispatch_raw_asgi(
        path="/index.html\x00.png", raw_path=b"/index.html\x00.png"
    )
    assert status == 400
    assert "Invalid path" in body
    assert "<!doctype html" not in body.lower()


@pytest.mark.asyncio
async def test_raw_asgi_absolute_path_returns_404():
    """Raw absolute system path /etc/passwd via ASGI returns HTTP 404."""
    status, headers, body = await _dispatch_raw_asgi(path="/etc/passwd", raw_path=b"/etc/passwd")
    assert status == 404
    assert "Resource not found" in body
    assert "root:x:0:0:" not in body
    assert "<!doctype html" not in body.lower()


@pytest.mark.asyncio
async def test_raw_asgi_valid_spa_route_returns_index_html():
    """Raw valid client-side route /dashboard via ASGI returns HTTP 200 with index.html."""
    status, headers, body = await _dispatch_raw_asgi(path="/dashboard", raw_path=b"/dashboard")
    assert status == 200
    assert "<!doctype html" in body.lower() or "<html" in body.lower()
    assert headers.get("content-type", "").startswith("text/html")
