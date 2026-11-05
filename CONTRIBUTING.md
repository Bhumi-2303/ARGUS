# Contributing to ARGUS

Thank you for contributing to **ARGUS** (Autonomous Risk-aware Grid Understanding & Security).

ARGUS bridges academic research in cyber-physical intrusion detection with production-grade autonomous multi-agent defense for Industrial Control Systems (ICS), SCADA networks, and Smart Grids. We maintain strict standards for both software quality and empirical research reproducibility.

---

## 1. Development Principles & Code of Conduct

1. **Scientific Integrity First**: Never manufacture, smooth, or alter experimental evaluation metrics. All reported numbers must be verifiable against frozen test sets and raw prediction artifacts.
2. **Deterministic Agent Execution**: The 6-agent autonomous pipeline (`DIA`, `TAA`, `EA`, `KCA`, `RPA`, `DSA`) must execute genuine inference and TreeSHAP calculations. Do not introduce hardcoded mock outputs into production pipelines.
3. **Defense-in-Depth**: Follow strict cybersecurity practices. All API endpoints must adhere to OWASP security headers, Content Security Policy (CSP), role-based access control (RBAC), and input validation via Pydantic schemas.
4. **Preserve Checksums**: The master research workbook (`results/ARGUS_ALL_RESEARCH_RESULTS.xlsx`) and model artifacts (`artifacts/models/`) are cryptographically verified. Any modifications require formal justification and audit documentation.

---

## 2. Branching & Commit Conventions

### Branch Naming Conventions
- `main` / `master`: Stable production and validated research release branch.
- `v2-transformer-exploratory`: Active consolidation and research integration branch.
- `feat/<feature-name>`: New architectural features or API enhancements.
- `fix/<issue-name>`: Bug fixes and security patches.
- `exp/<experiment-id>`: Experimental protocols and model evaluation probes.
- `docs/<topic>`: Documentation, paper manuscripts, and audit updates.

### Commit Messages
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat(agent)`: Add new capability to an autonomous agent.
- `fix(security)`: Address security vulnerability or header misconfiguration.
- `perf(inference)`: Optimize model inference or TreeSHAP computation.
- `test(e2e)`: Add end-to-end multi-agent or API integration tests.
- `docs(paper)`: Update manuscript text, tables, or documentation.
- `chore(deps)`: Dependency upgrades or build tool configuration.

Example:
```bash
git commit -m "feat(orchestrator): add timeout handling to sequential agent context"
```

---

## 3. Local Environment Setup

### Prerequisites
- **Python**: `>=3.11` (tested on 3.11, 3.12, 3.14)
- **Node.js**: `>=18.0.0`
- **npm**: `>=9.0.0`

### Python Virtual Environment Setup
```bash
# Clone the repository
git clone https://github.com/Bhumi-2303/ARGUS.git
cd ARGUS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install base package with dev and test dependencies
pip install -e .[dev,test]

# Optional research dependencies (telemetry, PyTorch for DANN analysis)
pip install -e .[research]
```

### Frontend Build Setup
```bash
cd web
npm install
npm run build
cd ..
```

---

## 4. Verification & Quality Gates

Before submitting any Pull Request, all of the following verification gates must pass:

### Gate 1: Backend Automated Test Suite
All 283 tests must pass with zero failures:
```bash
pytest -v
```

### Gate 2: Code Quality & Typing
Run linter and type checker:
```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/argus
```

### Gate 3: Frontend Compilation
The React 19 + TypeScript + Vite build must compile with zero errors:
```bash
cd web
npm run build
cd ..
```

### Gate 4: Startup & Numerical Integrity Verification
Ensure models load and UI ground truth numbers match the authoritative tables:
```bash
python scripts/startup_check.py
python scripts/verify_ui_numbers.py
```

### Gate 5: Model Artifact Checksums
Verify that model weights match [`artifacts/models/INTEGRITY_MANIFEST.json`](artifacts/models/INTEGRITY_MANIFEST.json):
```bash
python -c "
import json, hashlib
with open('artifacts/models/INTEGRITY_MANIFEST.json') as f:
    manifest = json.load(f)
for name, meta in manifest['models'].items():
    path = meta['file_path']
    with open(path, 'rb') as mf:
        h = hashlib.sha256(mf.read()).hexdigest()
    assert h == meta['sha256'], f'Hash mismatch in {name}!'
print('All model weights verified.')
"
```

---

## 5. Submitting Pull Requests

1. **Fork & Branch**: Create a feature branch off `v2-transformer-exploratory` or `main`.
2. **Atomic Commits**: Keep commits focused and logically grouped.
3. **Test Coverage**: Accompany every functional change with unit or integration tests in `tests/`.
4. **PR Checklist**:
   - [ ] All 283 pytest test cases pass.
   - [ ] Frontend compiles cleanly (`npm run build`).
   - [ ] No unhashed or untracked binary model files added.
   - [ ] No secrets, API keys, or private IP addresses committed.
   - [ ] Relevant documentation in `docs/` and `README.md` updated.
5. **Review**: Submit the PR for review by repository maintainers.
