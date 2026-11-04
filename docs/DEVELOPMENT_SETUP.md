# ARGUS Development & Environment Setup Guide (`docs/DEVELOPMENT_SETUP.md`)

This guide walks through configuring your local development environment for building, testing, and running both the production ARGUS multi-agent platform and its research reproduction tooling.

---

## 1. System Prerequisites

| Component | Minimum Version | Recommended Version | Verification Command |
| :--- | :--- | :--- | :--- |
| **Operating System** | Linux / macOS / Windows WSL2 | Ubuntu 22.04 LTS / 24.04 LTS | `uname -a` |
| **Python** | 3.11.0 | 3.11 or 3.12 | `python3 --version` |
| **Node.js** | 18.0.0 | 20.x LTS | `node --version` |
| **npm** | 9.0.0 | 10.x | `npm --version` |
| **Git** | 2.34.0 | 2.40+ | `git --version` |

---

## 2. Environment Initialization

### Step 1: Clone Repository
```bash
git clone https://github.com/Bhumi-2303/ARGUS.git
cd ARGUS
```

### Step 2: Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Python Dependencies
Install the package in editable mode with development and testing dependencies:
```bash
pip install -e .[dev,test]
```

To install optional scientific research packages (such as `psutil` for host telemetry):
```bash
pip install -e .[research]
```

### Step 4: Compile Frontend Assets
Build the production React 19 + TypeScript bundle into `web/dist/`:
```bash
cd web
npm install
npm run build
cd ..
```

---

## 3. Running the Unified Live Platform

ARGUS features a single-port production server that delivers both the FastAPI REST/WebSocket backend and the compiled React dashboard on **`http://localhost:8000`**:

```bash
make demo
# Or directly:
python scripts/start_demo.py
```

### Accessible Endpoints
- **Main Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive 3D Multi-Agent Topology**: [http://localhost:8000/topology](http://localhost:8000/topology)
- **Flow Ingestion & Live Inference**: [http://localhost:8000/input](http://localhost:8000/input)
- **TreeSHAP Explainability View**: [http://localhost:8000/explain](http://localhost:8000/explain)
- **Empirical Results & Drift Analysis**: [http://localhost:8000/results](http://localhost:8000/results)
- **OpenAPI Interactive Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 4. Running Verification & Automated Tests

### Full Test Suite Execution
Execute the entire test suite (283 tests spanning unit, integration, and security checks):
```bash
pytest -v
```

### Targeted Test Commands
```bash
# Multi-agent end-to-end integration pipeline tests
pytest tests/e2e/test_real_pipeline.py -v

# HTTP security headers, CSP, and CORS validation
pytest tests/security/test_security_headers_and_cors.py -v

# ModelRegistry and feature schema validation
pytest tests/unit/test_model_registry_d3.py -v
```

### Integrity Verification Scripts
```bash
# Verify that all model binaries, weights, and manifests match SHA-256 signatures
python scripts/startup_check.py

# Verify that UI numbers match the authoritative research CSV tables
python scripts/verify_ui_numbers.py
```

---

## 5. Development Workflow & Code Quality

### Linting & Formatting
We enforce `ruff` for fast Python linting and code formatting:
```bash
# Check code style
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Type checking
mypy src/argus
```

### Frontend Development Mode (Hot Reload)
To run Vite with hot-module reloading during UI development:
```bash
cd web
npm run dev
# Vite runs on http://localhost:5173 and proxies API requests to localhost:8000
```

---

## 6. Troubleshooting & Common Issues

### Matplotlib Cache Directory Warnings
If running in restricted or containerized environments where `$HOME` is not writable, configure a temporary cache directory:
```bash
export MPLCONFIGDIR=/tmp/matplotlib_cache
```

### Port 8000 In Use
If port 8000 is occupied by another process:
```bash
# Find and terminate occupying process
lsof -ti :8000 | xargs kill -9
```

### Python Hash Seed Reproducibility
For identical random-state behavior across unit test runs:
```bash
export PYTHONHASHSEED=42
```
