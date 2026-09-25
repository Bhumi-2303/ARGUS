#!/usr/bin/env bash
set -e

echo "================================================================================"
echo "        ARGUS DEPLOYMENT SMOKE TEST SUITE (BASH)"
echo "================================================================================"

HOST="${ARGUS_HOST:-localhost}"
PORT="${ARGUS_PORT:-8000}"
BASE_URL="http://${HOST}:${PORT}"

echo "[ 1/4 ] Checking /health ..."
curl -sf "${BASE_URL}/health" | grep -q '"status":"healthy"' || (echo "[ FAIL ] Health check failed" && exit 1)
echo "  [ PASS ] Health check OK"

echo "[ 2/4 ] Checking /api/v1/models ..."
curl -sf "${BASE_URL}/api/v1/models" | grep -q '"models"' || (echo "[ FAIL ] Models endpoint failed" && exit 1)
echo "  [ PASS ] Models endpoint OK"

echo "[ 3/4 ] Checking /api/v1/agents/topology ..."
curl -sf "${BASE_URL}/api/v1/agents/topology" | grep -q '"nodes"' || (echo "[ FAIL ] Topology endpoint failed" && exit 1)
echo "  [ PASS ] Topology endpoint OK"

echo "[ 4/4 ] Running python verification script ..."
python scripts/smoke_test_deployment.py

echo "================================================================================"
echo "ALL SMOKE TESTS PASSED — DEPLOYMENT IS OPERATIONAL"
echo "================================================================================"
