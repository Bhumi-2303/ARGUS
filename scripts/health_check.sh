#!/usr/bin/env bash
# ==================================================================
# ARGUS Health Check Script
# ==================================================================
# Used by Docker HEALTHCHECK to verify the API is responsive.
# Returns exit code 0 if healthy, 1 if unhealthy.
# ==================================================================

set -euo pipefail

HEALTH_URL="${ARGUS_HEALTH_URL:-http://localhost:${ARGUS_PORT:-8000}/api/v1/health/live}"
TIMEOUT="${ARGUS_HEALTH_TIMEOUT:-5}"

response=$(curl -sf --max-time "$TIMEOUT" "$HEALTH_URL" 2>/dev/null) || exit 1

# Check that the response contains "alive" or "healthy"
echo "$response" | grep -qE '"status"\s*:\s*"(alive|healthy)"' || exit 1

exit 0
