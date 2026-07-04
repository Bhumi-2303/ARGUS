# ARGUS Architecture

## System Overview

ARGUS (Autonomous Risk-aware Grid Understanding & Security) is a multi-agent cybersecurity platform designed to protect Smart Grid Infrastructure. The architecture follows a layered design where each layer is independently replaceable.

## Architectural Layers

### 1. Configuration Layer

**Purpose**: Centralized configuration management for the entire platform.

The configuration layer uses a hierarchical settings system built on Pydantic `BaseSettings`:

- **Environment Variables**: Primary configuration source, overrides all others
- **YAML Config Files**: Default values and complex structured configuration
- **Feature Flags**: Runtime toggleable capabilities
- **Secrets**: Environment-variable-based secret management (never logged, never serialized)

Settings are cached via `@lru_cache` and injected via FastAPI's dependency injection system.

### 2. Core Contracts Layer

**Purpose**: Defines the interfaces that all components must implement.

This layer contains zero implementation — only abstract base classes and protocols:

- `BaseAgent`: 10 lifecycle methods every agent must implement
- `BaseTool`: 5 methods every tool must implement
- `BaseRepository`: Generic async CRUD interface
- `BaseService`: Service layer abstraction
- Protocol classes (`IMessageBus`, `IBlackboard`, etc.) for structural typing

### 3. Schema Layer (Communication Protocol)

**Purpose**: Defines the data structures for all inter-component communication.

Every message in the system follows a standard format with these required fields:

| Field | Purpose |
|-------|---------|
| `request_id` | Unique request identifier for deduplication |
| `trace_id` | Distributed trace correlation |
| `agent_id` | Source agent identifier |
| `timestamp` | UTC timestamp |
| `priority` | Message priority level |
| `payload` | Message content (typed per message type) |
| `metadata` | Additional context |
| `signature` | HMAC-SHA256 signature for integrity |
| `version` | Protocol version for compatibility |

### 4. Message Bus Layer

**Purpose**: Async pub/sub message routing between components.

The message bus provides topic-based publish/subscribe using `asyncio.Queue` per subscriber. Key properties:

- **Topic isolation**: Messages only reach subscribers of the specific topic
- **Async delivery**: Non-blocking message dispatch
- **Dead letter queue**: Failed deliveries are retained for debugging
- **Metrics**: Messages sent/delivered/failed per topic

### 5. Shared Blackboard Layer

**Purpose**: Central shared memory for inter-agent coordination.

The blackboard is divided into typed sections:

| Section | Contents |
|---------|----------|
| `TASK_QUEUE` | Pending tasks awaiting assignment |
| `COMPLETED_TASKS` | Finished task results |
| `SHARED_CONTEXT` | Cross-agent shared state |
| `THREAT_RESULTS` | Threat analysis outputs |
| `KNOWLEDGE_RESULTS` | Knowledge graph query results |
| `RISK_RESULTS` | Risk assessment outputs |
| `DECISION_RESULTS` | Decision recommendations |

**Concurrency Model**:
- Read-write locks per section (multiple concurrent readers, exclusive writers)
- Optimistic locking with version numbers
- TTL-based entry expiration with background cleanup
- Conflict resolution: version check on write, reject stale updates

### 6. Agent Registry Layer

**Purpose**: Agent discovery and lifecycle tracking.

The registry stores:
- Agent metadata (name, version, capabilities, permissions)
- Health status and heartbeat timestamps
- Current load (active tasks) for load balancing
- Tools available to each agent

The orchestrator queries the registry to discover capable agents for task routing.

### 7. Agent Layer

**Purpose**: Houses the AI agents that perform cybersecurity analysis.

Every agent inherits `BaseAgent` and implements the full lifecycle:

```
initialize() → validate() → reason() → plan() → execute() →
call_tools() → update_memory() → publish() → health() → shutdown()
```

Currently, agents contain placeholder logic. The architecture allows replacing placeholder implementations with production AI models (LLMs, ML models, etc.) without changing any other layer.

### 8. Orchestrator Layer

**Purpose**: Task scheduling, routing, and failure management.

**Scheduling Algorithm**: Priority-weighted queue with load-aware routing.

1. Tasks enter a priority queue ordered by `(priority_value, timestamp)`
2. The router queries the registry for agents with matching capabilities
3. Among capable agents, the one with the lowest current load is selected
4. If all agents are at capacity, the task waits in the queue

**Failure Recovery**:
- Exponential backoff retry (configurable per task type)
- Circuit breaker per agent (trips after N consecutive failures)
- Timeout enforcement via `asyncio.wait_for()`
- Dead letter queue for permanently failed tasks

### 9. Tool Layer

**Purpose**: Standardized interface for external tool integration.

Every tool follows the `BaseTool` contract:
- `initialize()`: Set up connections and state
- `execute()`: Perform the tool's function
- `validate()`: Check inputs before execution
- `shutdown()`: Clean up resources
- `metadata()`: Return tool capabilities description

The tool registry manages tool lifecycle and enforces permission checks before execution.

### 10. MCP Compatibility Layer

**Purpose**: Support for Model Context Protocol servers.

Provides abstract interfaces for MCP servers without implementing specific servers:
- `BaseMCPServer`: Abstract interface for MCP tool/resource providers
- `MCPRegistry`: Runtime registration of MCP servers
- Protocol schemas for MCP communication

Future MCP servers (MITRE, NVD, CISA, etc.) implement `BaseMCPServer` and register with the `MCPRegistry` — no code changes needed elsewhere.

### 11. Memory Layer

**Purpose**: Multi-tier memory system for agent state management.

| Memory Type | Scope | Persistence | Use Case |
|-------------|-------|-------------|----------|
| Working Memory | Per-agent | None (ephemeral) | Current task context |
| Shared Memory | Cross-agent | Blackboard-backed | Agent coordination |
| Persistent Memory | Global | SQLite | Historical data |
| Cache | Global | In-memory (TTL) | Frequently accessed data |
| Vector Memory | Global | ChromaDB | Semantic search |

### 12. Security Layer

**Purpose**: Defense in depth across the entire platform.

| Component | Function |
|-----------|----------|
| JWT Authentication | Token-based API authentication |
| RBAC Authorization | Role-based access control |
| Input Validation | Payload size and schema validation |
| Prompt Injection Detection | Pattern-based injection detection |
| Message Signing | HMAC-SHA256 message integrity |
| Audit Logging | Immutable security event log |
| Rate Limiting | Token bucket per API key/endpoint |
| Secret Management | Environment-based secret handling |
| Data Masking | Sensitive data redaction in logs |

### 13. Persistence Layer

**Purpose**: Durable data storage through the repository pattern.

- **SQLite** (via SQLAlchemy async): Tasks, agents, audit entries, metrics
- **ChromaDB**: Vector embeddings for semantic search
- **Repository Pattern**: All database access goes through typed repositories — no direct SQL anywhere in business logic

### 14. API Layer

**Purpose**: FastAPI REST API and WebSocket interface.

All endpoints under `/api/v1/`:

| Resource | Endpoints |
|----------|-----------|
| `/agents` | CRUD + health for agent management |
| `/tasks` | Create, list, cancel, get results |
| `/blackboard` | Read/write blackboard sections |
| `/health` | Liveness, readiness, component health |
| `/metrics` | System and per-agent metrics |
| `/config` | Runtime configuration management |
| `/tools` | Tool listing and execution |
| `/ws` | WebSocket for real-time updates |

### 15. Observability Layer

**Purpose**: Structured logging, metrics, and distributed tracing.

- **Structlog**: JSON logs in production, colored console in development
- **In-process metrics**: Counters, gauges, histograms
- **Trace context**: Request ID and trace ID propagation across all layers

### 16. Google ADK Integration

**Purpose**: Bridge between ARGUS agents and Google's Agent Development Kit.

The adapter pattern wraps ARGUS `BaseAgent` instances as ADK-compatible agents:

1. `ArgusADKAdapter` implements ADK's `BaseAgent._run_async_impl()`
2. Inside, it calls the ARGUS agent's `process_task()` lifecycle
3. Results are mapped to ADK `Event` objects
4. ADK can discover, plan with, and orchestrate wrapped agents

This means any future ARGUS agent automatically works with ADK — no extra code needed.

### 17. Frontend Layer

**Purpose**: React 19 SOC dashboard for security operations.

The frontend is a standalone React application that communicates exclusively with the FastAPI backend via REST APIs and WebSockets. It never accesses databases or AI logic directly.

Key technologies: React 19, Vite, TypeScript, Tailwind CSS, shadcn/ui, Recharts, Framer Motion, React Flow, Cytoscape.js.
