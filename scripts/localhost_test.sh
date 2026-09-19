#!/usr/bin/env bash
# ==========================================================================
# ARGUS Local Smoke Test Script
# ==========================================================================
# Tests all service endpoints on localhost after docker compose up.
# Usage: bash scripts/localhost_test.sh
# ==========================================================================

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

check() {
    local label="$1"
    local cmd="$2"
    printf "${CYAN}[TEST]${NC} %-50s " "$label"
    if output=$(eval "$cmd" 2>&1); then
        printf "${GREEN}PASS${NC}\n"
        PASS=$((PASS + 1))
    else
        printf "${RED}FAIL${NC}\n"
        echo "       $output" | head -3
        FAIL=$((FAIL + 1))
    fi
}

echo "=========================================="
echo " ARGUS Localhost Smoke Test"
echo "=========================================="
echo ""

# ---- Health Checks ----
echo "${YELLOW}--- Health Endpoints ---${NC}"
check "Detector API /health" \
    "curl -sf http://localhost:8000/health | python3 -m json.tool > /dev/null"

check "Risk Agent /health" \
    "curl -sf http://localhost:8002/health | python3 -m json.tool > /dev/null"

check "Knowledge Agent /health" \
    "curl -sf http://localhost:8003/health | python3 -m json.tool > /dev/null"

check "Decision Agent /health" \
    "curl -sf http://localhost:8001/health | python3 -m json.tool > /dev/null"

check "Orchestrator /health" \
    "curl -sf http://localhost:8004/health | python3 -m json.tool > /dev/null"

echo ""

# ---- Functional Tests ----
echo "${YELLOW}--- Functional Tests ---${NC}"

# Test 1: Detector prediction (attack flow)
check "Detector: attack flow prediction" \
    "curl -sf -X POST http://localhost:8000/predict \
      -H 'Content-Type: application/json' \
      -d '[{\"pkt_mean_to_max\":0.95,\"tcp_flag_density\":1.0,\"log_pkt_mean\":4.2,\"log_pkt_max\":4.3}]' \
      | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d[\"predictions\"][0][\"prediction\"]==1'"

# Test 2: Detector prediction (benign flow)
check "Detector: benign flow prediction" \
    "curl -sf -X POST http://localhost:8000/predict \
      -H 'Content-Type: application/json' \
      -d '[{\"pkt_mean_to_max\":0.05,\"tcp_flag_density\":0.0,\"log_pkt_mean\":1.0,\"log_pkt_max\":1.2}]' \
      | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d[\"predictions\"][0][\"prediction\"]==0'"

# Test 3: Risk score computation
check "Risk Agent: risk score for SCADA-MTU-01" \
    "curl -sf -X POST http://localhost:8002/risk_score \
      -H 'Content-Type: application/json' \
      -d '{\"asset_id\":\"SCADA-MTU-01\",\"detection_probability\":0.85}' \
      | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d[\"risk_score\"]>0'"

# Test 4: Knowledge context query
check "Knowledge Agent: MITRE ATT&CK query" \
    "curl -sf -X POST http://localhost:8003/context \
      -H 'Content-Type: application/json' \
      -d '{\"query\":\"SCADA Modbus command injection\",\"top_k\":3}' \
      | python3 -c 'import sys,json; d=json.load(sys.stdin); assert len(d[\"techniques\"])>0'"

# Test 5: Full orchestrator pipeline (attack)
check "Orchestrator: full pipeline (attack flow)" \
    "curl -sf -X POST http://localhost:8004/process_alert \
      -H 'Content-Type: application/json' \
      -d '{\"asset_id\":\"SCADA-MTU-01\",\"flow_record\":{\"pkt_mean_to_max\":0.95,\"tcp_flag_density\":1.0,\"log_pkt_mean\":4.2,\"log_pkt_max\":4.3}}' \
      | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d[\"short_circuited\"]==False'"

# Test 6: Full orchestrator pipeline (benign — should short-circuit)
check "Orchestrator: short-circuit (benign flow)" \
    "curl -sf -X POST http://localhost:8004/process_alert \
      -H 'Content-Type: application/json' \
      -d '{\"asset_id\":\"SENSOR-NODE-88\",\"flow_record\":{\"pkt_mean_to_max\":0.05,\"tcp_flag_density\":0.0,\"log_pkt_mean\":1.0,\"log_pkt_max\":1.2}}' \
      | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d[\"short_circuited\"]==True'"

echo ""
echo "=========================================="
printf " Results: ${GREEN}%d PASSED${NC}, ${RED}%d FAILED${NC}\n" "$PASS" "$FAIL"
echo "=========================================="

exit $FAIL
