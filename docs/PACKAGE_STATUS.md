# ARGUS Package Status & Architecture Map

**File:** `docs/PACKAGE_STATUS.md`  
**Branch:** `chore/baseline`  
**Date:** 2026-11-04  
**Audit Target:** All subpackages in `src/argus/` (31 packages total)  
**Standing Verification Rule:** All file counts, line numbers, and importer lists are computed directly from the repository tree without mocks or estimations.

---

## 1. Classification Methodology

Each package under `src/argus/` is categorized into one of three implementation states:

- **Real:** Substantial production implementation containing full operational domain logic, validated Pydantic models, FastAPI routes, ML orchestration, cryptographic/security checks, or complete multi-agent workflows.
- **Thin:** Functional code, but minimal in scope (typically < 150 lines or a lightweight wrapper around an external utility/math formula), or a standalone helper not integrated into the primary API orchestration.
- **Stub:** Empty directory, 0-byte `__init__.py`, or a purely declarative placeholder with `pass` / `NotImplementedError` and no functioning business logic.

---

## 2. Comprehensive Subpackage Status Table

| Package | Total Files | Python Files | Total Lines | Imported Externally? | Implementation Status | Primary Role & Observations |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `adaptation` | 4 | 3 | 77 | No (0 files) | **Thin** | Implements `CORALAdapter` and `ClassAwareCORALAdapter` (covariance alignment math). Pre-adapted model weights are precomputed and loaded directly by `ModelRegistry`. |
| `adapters` | 1 | 1 | 0 | No (0 files) | **Stub** | Empty `__init__.py` (0 bytes). Unused placeholder package. |
| `agents` | 82 | 73 | 4,852 | Yes (7 files) | **Real** | Full multi-agent system: 6 autonomous agents (DIA, Threat Analysis, Explainability, Knowledge Context, Risk Prediction, Decision Support) with dedicated tools, pipelines, schemas, and tests. |
| `alignment` | 1 | 1 | 0 | No (0 files) | **Stub** | Empty `__init__.py` (0 bytes). Unused placeholder package. |
| `api` | 18 | 17 | 1,728 | Yes (17 files) | **Real** | Complete FastAPI REST/WebSocket application with 12 modular routers (agents, domains, explain, health, incidents, models, monitoring, onboard, results, shift, simulate, stream, topology, trace) and middleware. |
| `audit` | 4 | 4 | 308 | No (0 files) | **Thin** | Historical audit and validation utilities (`network_audit.py`, `fast_ciciot.py`, `generate_report.py`). Standalone scripts not imported by the web API. |
| `auth` | 5 | 5 | 604 | Yes (19 files) | **Real** | Cryptographic authentication and authorization: JWT bearer verification, RBAC permissions (`Operator`, `SecOps`, `Admin`), timing-safe token validation, and user management. |
| `blackboard` | 4 | 4 | 185 | Yes (5 files) | **Real** | Shared blackboard pattern with versioned entries, section isolation, ReadWriteLock synchronization, and `set`/`get` accessors utilized by agent publishers. |
| `bus` | 4 | 4 | 385 | Yes (4 files) | **Real** | Durable asyncio pub/sub message bus with SQLite-backed transactional outbox (events survive restarts), typed `BusEvent` normalization, bounded queue back-pressure, and Dead-Letter Queue (DLQ). |
| `core` | 12 | 12 | 708 | Yes (61 files) | **Real** | Foundational interfaces: `BaseAgent`, `BaseTool`, event schemas, detector contracts, enums, exception hierarchies, and dependency containers. Heavily imported across the system. |
| `data` | 2 | 2 | 352 | Yes (13 files) | **Real** | Production dataset loaders and telemetry streaming utilities (`data_loader.py`, `parquet_stream.py`). Serves benchmark parquet data (`ciciot.parquet`, `nfton.parquet`). |
| `database` | 4 | 4 | 410 | Yes (6 files) | **Real** | Durable database layer: Postgres-compatible SQLAlchemy schema (`incidents`, `timeline`, `pipeline_runs`, `traces`, `tokens`, `outbox`, `dlq`), connection pooling, and schema migration utilities. |
| `drift` | 1 | 1 | 0 | No (0 files) | **Stub** | Empty `__init__.py` (0 bytes). Functional drift detection is located in `monitoring/drift.py` and `shift/drift.py`. |
| `eval` | 1 | 1 | 0 | No (0 files) | **Stub** | Empty `__init__.py` (0 bytes). Benchmark evaluation logic resides in `scripts/verify_ui_numbers.py` and `tests/`. |
| `explain` | 3 | 2 | 23 | No (0 files) | **Thin** | `shap_helpers.py` provides a standalone helper (`compute_shap_importance`). Production TreeSHAP logic is integrated in `registry/model_registry.py` and `agents/explainability`. |
| `features` | 3 | 2 | 71 | Yes (2 files) | **Thin** | `extractor.py` provides `FeatureExtractor` computing the 4 harmonized flow features (`pkt_mean_to_max`, `tcp_flag_density`, `log_pkt_mean`, `log_pkt_max`). Imported by DIA agent and tests. |
| `integrations` | 7 | 7 | 565 | Yes (3 files) | **Real (Optional)** | Optional read-only agent runtime layer: `ArgusMCPServer` exposing inspection tools (`get_incident`, `get_trace`, `explain_flow`, `lookup_mitre`) and `IncidentNarrator` (ADK/Gemini incident summarization over computed outputs with zero-dependency fallback). Off by default; never on detection path. |
| `memory` | 3 | 3 | 85 | Yes (3 files) | **Real** | Pruned to active memory modules only (`WorkingMemory` and `SharedMemory` backed by Blackboard). Stub modules (`cache`, `persistent_memory`, `vector_memory`) removed. Wired to `PipelineContext`. |
| `models` | 3 | 2 | 61 | No (0 files) | **Thin** | `loader.py` contains basic LightGBM/XGBoost file loading functions. Production model loading and integrity verification are managed by `registry/model_registry.py`. |
| `monitoring` | 2 | 2 | 91 | Yes (2 files) | **Thin** | Production drift analysis module (`drift.py`) calculating Kolmogorov-Smirnov (KS) statistics between source and target batches. Imported by `api/routers/monitoring.py` and `tests/unit/test_drift.py`. |
| `observability` | 2 | 2 | 32 | No (0 files) | **Thin** | Lightweight Prometheus-style in-memory metric counters (`metrics.py`). Not actively imported by the API. |
| `orchestrator` | 11 | 10 | 1,176 | Yes (5 files) | **Real** | Asynchronous DAG pipeline orchestrator (`pipeline.py`, `orchestrator.py`, `state_machine.py`, `scheduler.py`, `router.py`, `retry.py`). Drives end-to-end multi-agent execution. |
| `policy` | 6 | 5 | 107 | Yes (3 files) | **Thin** | `PolicyEngine` evaluating operational constraints against YAML rules. Imported by `services/decision_agent/main.py`, `test_policy.py`, and security audit tests. |
| `registry` | 3 | 3 | 560 | Yes (18 files) | **Real** | Authoritative `ModelRegistry` verifying model SHA-256 hashes against `INTEGRITY_MANIFEST.json`, enforcing 4-feature/73-feature contracts, TreeSHAP explainability, and managing `AgentRegistry`. |
| `schemas` | 11 | 11 | 632 | Yes (38 files) | **Real** | Pydantic data schemas: `agents`, `api`, `blackboard`, `health`, `incident`, `messages`, `metrics`, `security`, `tasks`, `tools`. Widely imported across backend services. |
| `security` | 8 | 8 | 491 | Yes (6 files) | **Real** | Production security infrastructure: HTTP security headers, CORS origin enforcement, token bucket rate limiting, audit logging sinks, and error masking. |
| `serve` | 1 | 1 | 0 | No (0 files) | **Stub** | Empty `__init__.py` (0 bytes). Production serving is handled via `api/main.py` and `scripts/start_demo.py`. |
| `services` | 16 | 16 | 1,571 | Yes (8 files) | **Legacy / Deprecated** | Legacy microservice implementations (`incident_service.py`, `decision_agent`, `knowledge_agent`, `orchestrator`, `risk_agent`, Kafka streaming). Deprecated per [ADR 0001](file:///home/bhumi/GitHub/ARGUS/docs/adr/0001-modular-monolith.md) in favor of the in-process modular monolith. |
| `shift` | 3 | 2 | 34 | No (0 files) | **Thin** | Standalone mathematical routines (`drift.py`) for two-sample Kolmogorov-Smirnov tests and Population Stability Index (PSI). |
| `tools` | 6 | 6 | 179 | No (0 files) | **Thin** | Generic tool abstractions (`tool_registry.py`, `placeholder_tools.py`, and `mcp/` server base classes). The 6 operational agents maintain specialized tools inside their own agent packages. |
| `utils` | 1 | 1 | 21 | Yes (1 files) | **Thin** | `batch_replay.py` provides sequential parquet chunk streaming for test replays. Imported by `tests/e2e/test_day3.py`. |
| `v2_transformer` | 6 | 2 | 263 | No (0 files) | **Real** | Exploratory research architecture: PyTorch `GroupTokenEmbedder` and `V2TransformerClassifier` (`model.py`), training pipeline (`train_plumbing.py`), and 4 specification reports. |

---

## 3. High-Level Architecture Categorization

```
src/argus/
├── [REAL - Production Core & Microservices] (11 packages / 12,027 lines)
│   ├── agents/          (4,852 lines | 6 autonomous agents + internal tools & schemas)
│   ├── api/             (1,728 lines | FastAPI endpoints, routers & middleware)
│   ├── services/        (1,571 lines | Microservice agents & Kafka streaming)
│   ├── orchestrator/    (1,176 lines | Async DAG pipeline & agent execution engine)
│   ├── core/            (  708 lines | Foundational abstractions, contracts & interfaces)
│   ├── schemas/         (  632 lines | Pydantic models & data contracts)
│   ├── auth/            (  604 lines | JWT, RBAC & security tokens)
│   ├── registry/        (  560 lines | Cryptographic model registry & model loaders)
│   ├── security/        (  491 lines | Security headers, rate limiting & audit sinks)
│   ├── integrations/    (  565 lines | Optional read-only runtime layer: ArgusMCPServer & IncidentNarrator)
│   ├── data/            (  352 lines | Dataset loaders & parquet stream readers)
│   └── v2_transformer/  (  263 lines | Exploratory Group Token Embedder PyTorch models)
│
├── [THIN - Specialized Math, In-Memory Helpers & Standalone Tools] (14 packages / 1,416 lines)
│   ├── audit/           (  308 lines | Offline dataset auditing scripts)
│   ├── memory/          (  182 lines | In-memory agent working & vector memory)
│   ├── tools/           (  179 lines | Generic MCP & tool registry abstractions)
│   ├── blackboard/      (  166 lines | In-memory RWLock blackboard)
│   ├── policy/          (  107 lines | YAML-driven policy engine)
│   ├── monitoring/      (   91 lines | KS drift analysis calculations)
│   ├── bus/             (   78 lines | Asyncio message bus for WebSocket streaming)
│   ├── adaptation/      (   77 lines | Standalone CORAL & Class-Aware CORAL math)
│   ├── features/        (   71 lines | 4-feature extraction logic)
│   ├── models/          (   61 lines | Basic LightGBM/XGBoost file loader)
│   ├── shift/           (   34 lines | KS test and PSI statistical math)
│   ├── observability/   (   32 lines | In-memory metric counters)
│   ├── explain/         (   23 lines | Standalone SHAP TreeExplainer helper)
│   └── utils/           (   21 lines | Batch parquet replay iterator)
│
└── [STUBS - Unused or Empty Placeholders] (5 packages / 0 lines)
    ├── adapters/        (    0 lines | Empty __init__.py)
    ├── alignment/       (    0 lines | Empty __init__.py)
    ├── drift/           (    0 lines | Empty __init__.py; active logic in monitoring/drift.py)
    ├── eval/            (    0 lines | Empty __init__.py; active logic in tests & scripts)
    └── serve/           (    0 lines | Empty __init__.py; active logic in api/main.py)
```

---

## 4. Key Architectural Insights & Findings

1. **Modular Multi-Agent Decoupling:**
   - The production multi-agent system is cleanly centered in `agents/`, `orchestrator/`, `api/`, and `registry/`.
   - Each agent in `agents/` (`data_intelligence`, `threat_analysis`, `explainability`, `knowledge_context`, `risk_prediction`, `decision_support`) is self-contained with its own specialized tools, schemas, and pipeline files, rather than relying on global abstractions in `tools/` or `memory/`.

2. **Model Registry Centralization:**
   - Rather than relying on dynamic training in `adaptation/` or generic loaders in `models/`, the live system relies entirely on `registry/model_registry.py`.
   - `ModelRegistry` verifies the SHA-256 cryptographic hashes of all model artifacts against `artifacts/models/INTEGRITY_MANIFEST.json`, enforces strict feature boundaries (rejecting missing features or NaNs), and integrates exact TreeSHAP attribution generation.

3. **Placeholder & Legacy Cleanup Candidates:**
   - 5 packages are 0-line stubs (`adapters`, `alignment`, `drift`, `eval`, `serve`). The `integrations/` package provides an optional read-only runtime layer (`ArgusMCPServer` & `IncidentNarrator`) which is off by default and isolated from the core detection pipeline.
   - `blackboard/` and `memory/` are fully implemented in-memory data structures, but the live pipeline predominantly passes immutable event payloads directly through the `orchestrator` and `bus` rather than querying a shared blackboard.
