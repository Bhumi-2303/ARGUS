# ARGUS

**Autonomous Risk-aware Grid Understanding & Security**

> AI-powered multi-agent cybersecurity platform for protecting Smart Grid Infrastructure.

---

## Overview

ARGUS is a production-grade platform that orchestrates multiple AI agents to detect, analyze, and respond to cybersecurity threats targeting smart grid infrastructure. The platform provides:

- **Multi-Agent Architecture**: Five specialized AI agents working collaboratively through a shared blackboard
- **Real-Time Threat Detection**: Continuous monitoring with MITRE ATT&CK mapping
- **Risk Prediction**: ML-powered risk scoring and vulnerability assessment
- **Decision Support**: AI-synthesized recommendations with human-in-the-loop approval
- **Enterprise Dashboard**: React-based SOC dashboard with live visualizations

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│              (SOC Dashboard + WebSocket)                 │
├─────────────────────────────────────────────────────────┤
│                    FastAPI Backend                        │
│           (REST API + WebSocket + JWT Auth)               │
├──────────┬──────────┬──────────┬────────────────────────┤
│ Orchestr │ Registry │ Msg Bus  │    Security Layer       │
├──────────┴──────────┴──────────┤                        │
│         Shared Blackboard       │  Auth · RBAC · Audit   │
├────────────────────────────────┤  Signing · Validation   │
│  Data  │ Threat │ Know │ Risk │ Decision │              │
│  Intel │ Analy  │ Ctx  │ Pred │ Support  │              │
├────────┴────────┴──────┴──────┴──────────┤              │
│          Tool Layer + MCP                 │              │
├────────────────────────────────┬─────────┴──────────────┤
│       Memory Layer             │   Google ADK            │
│  Working · Shared · Vector     │   Integration           │
├────────────────────────────────┴────────────────────────┤
│  SQLite (Structured)  │  ChromaDB (Vector)  │  Cache     │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 22+
- Docker (optional)

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/your-org/ARGUS.git
cd ARGUS

# 2. Set up Python environment
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test]"

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings (especially SECRET_KEY and JWT_SECRET_KEY)

# 4. Initialize the database
python scripts/init_db.py

# 5. Start the backend
uvicorn argus.main:app --reload --host 0.0.0.0 --port 8000

# 6. Start the frontend (in another terminal)
cd frontend
npm install
npm run dev

# 7. Open the dashboard
open http://localhost:5173
```

### Docker

```bash
# Development (with frontend dev server)
docker compose --profile dev up --build

# Production
docker compose up --build
```

### API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
ARGUS/
├── config/          # Configuration files (YAML + Python settings)
├── src/argus/       # Backend source code
│   ├── core/        # Abstract base classes and contracts
│   ├── schemas/     # Pydantic data models
│   ├── agents/      # AI agent implementations
│   ├── orchestrator/# Task scheduling and routing
│   ├── blackboard/  # Shared memory system
│   ├── registry/    # Agent discovery
│   ├── bus/         # Message bus
│   ├── memory/      # Memory layer (working, shared, vector)
│   ├── tools/       # Tool interfaces + MCP compatibility
│   ├── security/    # Auth, RBAC, validation, audit
│   ├── services/    # Business logic layer
│   ├── repositories/# Data access layer
│   ├── database/    # SQLAlchemy models and engine
│   ├── api/         # FastAPI routers
│   ├── middleware/   # Request processing pipeline
│   ├── observability/# Logging, metrics, tracing
│   ├── integrations/# Google ADK integration
│   └── utils/       # Shared utilities
├── frontend/        # React 19 SOC Dashboard
├── tests/           # Test suite
├── scripts/         # Utility scripts
├── docs/            # Documentation
└── docker-compose.yml
```

## Agents

| Agent | Purpose | Status |
|-------|---------|--------|
| **Data Intelligence** | Ingests, normalizes, and correlates smart grid data | Placeholder |
| **Threat Analysis** | MITRE ATT&CK mapping, anomaly detection | Placeholder |
| **Knowledge & Context** | Knowledge graph queries, context enrichment | Placeholder |
| **Risk Prediction** | ML-based risk scoring and prediction | Placeholder |
| **Decision Support** | Synthesizes recommendations for operators | Placeholder |

All agents follow the `BaseAgent` contract with 10 lifecycle methods. Replace placeholder logic with production AI models without changing the architecture.

## Testing

```bash
# All tests
pytest tests/ -v --cov=src/argus

# Unit tests only
pytest tests/unit/ -v

# Security tests
pytest tests/security/ -v

# Integration tests
pytest tests/integration/ -v
```

## Documentation

- [Architecture Deep-Dive](docs/architecture.md)
- [Agent Contract](docs/agent_contract.md)
- [Communication Protocol](docs/communication_protocol.md)
- [Security Model](docs/security_model.md)
- [Deployment Guide](docs/deployment.md)
- [API Reference](docs/api_reference.md)

## License

MIT License — see [LICENSE](LICENSE) for details.
