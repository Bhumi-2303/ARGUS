# ADR 0001: Modular Monolith Architecture for ARGUS

* **Status:** Accepted
* **Date:** 2026-11-04
* **Deciders:** ARGUS Core Engineering & Research Team
* **Context Branch:** `chore/cleanup`

---

## 1. Context and Problem Statement

ARGUS historically maintained two parallel architectural paradigms:

1. **Distributed Microservices Architecture:**
   - Multiple standalone container services located in `src/argus/services/` (`decision_agent`, `knowledge_agent`, `orchestrator`, `risk_agent`, `incident_service`, and Kafka replay streaming).
   - Six individual service Dockerfiles in `deployment/docker/*.Dockerfile` (`decision.Dockerfile`, `detector.Dockerfile`, `knowledge.Dockerfile`, `orchestrator.Dockerfile`, `risk.Dockerfile`, `streaming.Dockerfile`).
   - Multi-container orchestration in `deployment/compose/docker-compose.yml` requiring Apache Kafka, Zookeeper, Redis, and multi-service networking.

2. **In-Process Modular Monolith Architecture:**
   - A single FastAPI process (`src/argus/api/main.py`) serving REST endpoints, WebSocket streaming, and static React frontend assets (`web/dist/`).
   - The 6 autonomous agents (`DIA`, `TAA`, `EA`, `KCA`, `RPA`, `DSA` in `src/argus/agents/`) executing as typed, asynchronous internal Python modules coordinated by `PipelineOrchestrator` (`src/argus/orchestrator/pipeline.py`).
   - In-memory event bus (`src/argus/bus/`) and shared blackboard primitives (`src/argus/blackboard/`).

Maintaining both paradigms introduced cognitive overhead, duplicate schemas, split test suites, and operational friction. Crucially, the distributed microservices architecture cannot run on modern cloud free-tier hosting environments.

---

## 2. Free-Tier Hosting Analysis & Constraints

ARGUS is designed to be accessible to academic researchers, security analysts, and open-source contributors without requiring dedicated multi-node Kubernetes clusters or expensive cloud infrastructure.

Standard cloud free-tier and low-cost container environments (e.g., Render Free Tier, Fly.io, Railway Starter, HuggingFace Spaces) enforce strict hardware ceilings:

| Platform / Provider | Free / Starter RAM Budget | CPU Allocation | Container Limit |
| :--- | :---: | :---: | :---: |
| **Render** | 512 MB | 0.5 shared vCPU | 1 Web Service |
| **Hugging Face Spaces** | 16 GB (CPU Basic) / 2 vCPU | Shared vCPU | 1 Container |
| **Fly.io** | 256 MB – 512 MB | shared-cpu-1x | 1–2 VMs |
| **Railway** | 512 MB (Starter) | Shared | 1 Project |

### Resource Consumption Breakdown:

- **Distributed Microservice Footprint:**
  - Zookeeper + Kafka broker: ~1,024 MB – 1,536 MB
  - Redis cache/broker: ~128 MB
  - 6 independent Python container runtimes (each loading PyTorch, LightGBM, Pandas, Pydantic): $6 \times 350\text{ MB} \approx 2,100\text{ MB}$
  - Frontend static Nginx container: ~50 MB
  - **Total Required RAM:** $\mathbf{> 3,750\text{ MB} - 4,200\text{ MB}}$ (Exceeds free-tier memory limit by $7.5\times$, causing immediate Linux kernel OOM kills).

- **Modular Monolith Footprint:**
  - Single hardened Python 3.11/3.14 runtime (`Dockerfile`) loading model weights into memory once via `ModelRegistry`: ~220 MB – 380 MB
  - Built-in FastAPI static mount for compiled React SPA assets (`web/dist`): ~0 MB additional RAM
  - In-memory asyncio event queue for real-time WebSocket tracing: ~15 MB
  - **Total Required RAM:** $\mathbf{\approx 250\text{ MB} - 400\text{ MB}}$ (Comfortably operates under the **512 MB** Render free-tier budget).

---

## 3. Decision

We decide to adopt the **Modular Monolith** as ARGUS's sole production architecture:

1. **Single Unified Process:**
   - The production entry point is `argus.api.main:app` (executed via Uvicorn).
   - All 6 autonomous agents (`DataIntelligenceAgent`, `ThreatAnalysisAgent`, `ExplainabilityAgent`, `KnowledgeContextAgent`, `RiskPredictionAgent`, `DecisionSupportAgent`) are internal Python modules invoked in-process via `PipelineOrchestrator`.

2. **In-Process Communication:**
   - Inter-agent coordination occurs via typed async method calls and `AgentMessage` data structures, eliminating HTTP/gRPC network overhead, socket management, and JSON serialization costs.
   - Live browser updates use FastAPI WebSockets (`/ws/stream`) fed by the in-process `MessageBus`.

3. **Status of Legacy Microservices & Multi-Container Deployment:**
   - `src/argus/services/*`: Marked as **legacy/deprecated**. These standalone microservice entry points are preserved solely for backward compatibility with isolated unit tests and historical service benchmarks.
   - `deployment/docker/*.Dockerfile` and `deployment/compose/`: Moved to `docs/future/deployment/` and marked as **Future Distributed Architecture Blueprints**. They serve as reference designs if enterprise scale-out beyond a single node is ever required.
   - Root `Dockerfile` and root `docker-compose.yml`: Remain the authoritative container definitions for ARGUS production and local evaluation.

---

## 4. Consequences and Trade-offs

### Positive:
- **Zero OOM on Free-Tier Hosting:** ARGUS deploys seamlessly on 512 MB RAM environments (Render, Fly.io, Railway) as a single container.
- **Sub-Millisecond Inter-Agent Latency:** Zero network hops between agents during 6-stage telemetry evaluation; end-to-end trace latency drops from ~120ms to ~8ms.
- **Drastically Simplified Operations:** Single port (8000), single `/health` healthcheck endpoint, single security perimeter (OWASP headers + JWT middleware), zero distributed failure modes (no split-brain, network partitions, or broker disconnects).
- **Streamlined Local Developer Experience:** Developers run `uvicorn argus.api.main:app` or `make demo` without needing Docker, Docker Compose, Kafka, or Redis running locally.

### Negative / Limitations:
- **Vertical Scaling Only:** All 6 agents share CPU and memory within the same operating system process.
- **Resource Contention:** Heavy TreeSHAP computation in the Explainability Agent shares CPU cycles with FastAPI event loop threads. (Mitigated by running CPU-bound model inference in `asyncio.to_thread` pools).

### Future Scale-Out Path:
Should multi-node horizontal scaling become necessary in high-throughput enterprise deployments (e.g. >100,000 flows/sec), the clean contract boundaries (`BaseAgent`, `BaseTool`, Pydantic schemas) allow individual agents to be lifted out behind gRPC workers as documented in `docs/future/deployment/`.
