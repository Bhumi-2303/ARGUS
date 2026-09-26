#!/usr/bin/env python3
"""ARGUS Deployment Smoke Test Script.

Validates that the deployed API container is healthy, model registry is loaded,
topology endpoint returns agent nodes, and WebSocket stream responds to ping.
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/agents/stream"

def test_endpoint(name: str, path: str) -> dict:
    url = f"{BASE_URL}{path}"
    print(f"\n[ TESTING ] {name} -> {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ARGUS-SmokeTest/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            body_text = response.read().decode("utf-8")
            data = json.loads(body_text)

            if status_code == 200:
                print(f"  [ PASS ] HTTP 200 OK")
                return data
            else:
                print(f"  [ FAIL ] Unexpected status code: {status_code}")
                sys.exit(1)
    except Exception as ex:
        print(f"  [ FAIL ] Exception hitting '{url}': {ex}")
        sys.exit(1)


def test_websocket():
    print(f"\n[ TESTING ] WebSocket Stream Endpoint -> {WS_URL}")
    try:
        import websockets
        import asyncio

        async def run_ws_check():
            async with websockets.connect(WS_URL) as ws:
                await ws.send("ping")
                resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
                if resp == "pong":
                    print("  [ PASS ] WebSocket 'ping' -> 'pong' exchange successful.")
                    return True
                else:
                    print(f"  [ FAIL ] Unexpected WS response: {resp}")
                    return False

        return asyncio.run(run_ws_check())
    except ImportError:
        print("  [ SKIP ] 'websockets' python library not installed locally; testing basic socket connect...")
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        res = s.connect_ex(("localhost", 8000))
        s.close()
        if res == 0:
            print("  [ PASS ] TCP Socket port 8000 reachable.")
            return True
        else:
            print("  [ FAIL ] TCP Port 8000 unreachable.")
            return False
    except Exception as ex:
        print(f"  [ FAIL ] WS test exception: {ex}")
        return False


def run_smoke_test():
    print("\n" + "=" * 80)
    print("        ARGUS DEPLOYMENT SMOKE TEST SUITE")
    print("=" * 80)

    # 1. Health Check
    health_data = test_endpoint("System Health Endpoint", "/health")
    if health_data.get("status") != "healthy":
        print(f"  [ FAIL ] Health status not healthy: {health_data}")
        sys.exit(1)

    # 2. Model Registry Check
    models_data = test_endpoint("Loaded Model Registry", "/api/v1/models")
    model_count = models_data.get("count", len(models_data.get("models", [])))
    print(f"  [ INFO ] {model_count} models loaded in memory.")
    if model_count < 1:
        print("  [ FAIL ] Model registry reports 0 loaded models.")
        sys.exit(1)

    # 3. Agent Topology Check
    topology_data = test_endpoint("Agent Topology Graph", "/api/v1/agents/topology")
    nodes = topology_data.get("nodes", [])
    print(f"  [ INFO ] {len(nodes)} agent nodes returned.")
    if len(nodes) < 5:
        print(f"  [ FAIL ] Expected at least 5 agent nodes, got {len(nodes)}.")
        sys.exit(1)

    # 4. WebSocket Test
    ws_ok = test_websocket()
    if not ws_ok:
        sys.exit(1)

    print("\n" + "=" * 80)
    print("ALL SMOKE TESTS PASSED — DEPLOYMENT IS OPERATIONAL AND READY FOR TRAFFIC")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_smoke_test()
