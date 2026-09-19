# ARGUS Testing Guide

ARGUS has a professional, three-tier testing strategy that cleanly separates software validation from scientific machine learning experiments. This ensures continuous delivery of the software platform without incurring the heavy computational cost of retraining models.

## Testing Levels

### Level 1: Unit Tests
Unit tests validate the core logic components in isolation.
**Location:** `tests/unit/`, `tests/schemas/`, `tests/policy/`
**Coverage:**
- Feature transformations and schemas
- Risk calculation algorithms
- Policy evaluation logic
- Decision mapping
- Incident state transitions
- Configuration parsing

### Level 2: Integration Tests
Integration tests validate the sequence of agent execution using deterministic event fixtures.
**Location:** `tests/integration/`
**Workflow Tested:** `Detector -> Risk -> Knowledge -> Explainability -> Policy -> Decision`
**Fixtures:** We use standard, deterministic schemas representing:
- Low-criticality benign events
- Low-criticality false positives
- High-criticality attacks
- Uncertain events
- Degraded states (LLM/Knowledge unavailable)
- Policy failure events
*(No sensitive telemetry or live data is used in integration tests).*

### Level 3: End-to-End Tests
E2E tests validate the overarching event pipeline and persistence.
**Location:** `tests/e2e/`
**Workflow Tested:** `Security Event -> ARGUS processing -> Final Decision -> Incident Creation/Persistence`

## Running Tests Locally
To run the standard testing suite:
```bash
# Install dependencies
pip install -e ".[test]"

# Run tests
PYTHONPATH=src:. pytest tests/unit/ tests/schemas/ tests/policy/ tests/services/ tests/integration/ tests/e2e/
```

## Scientific Separation
Research experiments and model evaluations **must remain separate** from the software test suite. Multi-million-sample experiments should not be executed as part of ordinary CI tests.

For reproducing research and model training, use the dedicated research reproduction workflows.

### RESEARCH REPRODUCTION
```bash
python -m argus.experiments.run --config configs/research_config.yaml
```
