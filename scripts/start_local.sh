#!/usr/bin/env bash
# ==========================================================================
# ARGUS — Quick Local Startup (Docker Compose)
# ==========================================================================
# Builds and starts the core ARGUS pipeline services on localhost.
# Skips Kafka/Zookeeper/streaming for a fast initial test.
#
# Usage: bash scripts/start_local.sh
# ==========================================================================

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "=========================================="
echo " ARGUS — Local Startup"
echo "=========================================="
echo ""

# Step 1: Prepare model file
echo -e "${CYAN}[1/4]${NC} Preparing model file..."
mkdir -p models
if [ -f models/model_d2_coral.txt ]; then
    echo "  Model already present."
elif [ -f phase3_results/models/model_d2_coral.txt ]; then
    cp phase3_results/models/model_d2_coral.txt models/
    echo "  Copied from phase3_results."
else
    echo "  WARNING: No model file found. Detector API will fail to start."
    echo "  Run: export MODEL_ARTIFACT_URL=<your-url> && bash scripts/download_model.sh"
fi

# Step 2: Build core services
echo ""
echo -e "${CYAN}[2/4]${NC} Building Docker images (this may take a few minutes on first run)..."
docker compose build detector-api risk-agent knowledge-agent decision-agent orchestrator 2>&1 | tail -5

# Step 3: Start services
echo ""
echo -e "${CYAN}[3/4]${NC} Starting services..."
docker compose up -d detector-api risk-agent knowledge-agent decision-agent orchestrator
echo ""

# Step 4: Wait and verify
echo -e "${CYAN}[4/4]${NC} Waiting for services to become healthy..."
SERVICES=(
    "8000:Detector API"
    "8002:Risk Agent"
    "8003:Knowledge Agent"
    "8001:Decision Agent"
    "8004:Orchestrator"
)

sleep 10

ALL_HEALTHY=true
for svc in "${SERVICES[@]}"; do
    PORT="${svc%%:*}"
    NAME="${svc##*:}"
    printf "  %-25s " "$NAME (:$PORT)"
    
    READY=false
    for i in $(seq 1 12); do
        if curl -sf "http://localhost:$PORT/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ healthy${NC}"
            READY=true
            break
        fi
        sleep 5
    done
    
    if [ "$READY" = false ]; then
        echo -e "\033[0;31m✗ not ready\033[0m"
        ALL_HEALTHY=false
    fi
done

echo ""
if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}=========================================="
    echo " All services are running!"
    echo "==========================================${NC}"
    echo ""
    echo " Service URLs:"
    echo "   Detector API    : http://localhost:8000"
    echo "   Decision Agent  : http://localhost:8001"
    echo "   Risk Agent      : http://localhost:8002"
    echo "   Knowledge Agent : http://localhost:8003"
    echo "   Orchestrator    : http://localhost:8004"
    echo ""
    echo " API Docs (Swagger UI):"
    echo "   http://localhost:8000/docs"
    echo "   http://localhost:8004/docs"
    echo ""
    echo " Quick test:"
    echo "   bash scripts/localhost_test.sh"
    echo ""
    echo " Stop all services:"
    echo "   docker compose down"
else
    echo -e "${YELLOW}Some services failed to start. Check logs:${NC}"
    echo "  docker compose logs detector-api"
    echo "  docker compose logs orchestrator"
fi
