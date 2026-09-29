"""Agent router providing topology layout, live status WebSocket, and flow simulation."""

import uuid
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status, Depends, Request, Body
from pydantic import BaseModel, Field

from configs.settings import get_settings
from argus.auth.rbac import get_current_user, require_permission
from argus.auth.models import UserPrincipal
from argus.auth.jwt import jwt_validator
from argus.security.audit import AuditLogger, SecurityAuditEvent
from argus.schemas.agents import AgentHealthReport, AgentRegistration
from argus.schemas.api import APIResponse

router = APIRouter()

# Topology Schemas
class TopologyNode(BaseModel):
    id: str = Field(..., description="Unique node ID")
    name: str = Field(..., description="Display name")
    type: str = Field(..., description="Node type: bus, gateway, engine, or agent")
    responsibility: str = Field(..., description="Agent or engine responsibility description")
    status: str = Field("idle", description="Live status: idle, busy, blocked, or failed")
    implementation_type: str = Field("full", description="Implementation state: full or stub")
    layer: str = Field("inner", description="Layout layer: center, inner, or outer")

class TopologyEdge(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: str = Field(..., description="Edge connection description")
    event_types: List[str] = Field(default_factory=list, description="Supported event types along edge")

class TopologyResponse(BaseModel):
    nodes: List[TopologyNode]
    edges: List[TopologyEdge]

class FlowEventItem(BaseModel):
    event_id: str
    correlation_id: str
    source_node: str
    target_node: str
    event_type: str
    timestamp: str
    summary: str
    payload: Dict[str, Any]

class TraceExecutionResponse(BaseModel):
    correlation_id: str
    flow_status: str
    total_events: int
    events: List[FlowEventItem]


# Dynamic Topology Registry
TOPOLOGY_NODES: List[TopologyNode] = [
    TopologyNode(
        id="orchestrator",
        name="Orchestrator Engine",
        type="engine",
        responsibility="Central workflow orchestration, state machine evaluation, and agent task dispatching.",
        status="idle",
        implementation_type="full",
        layer="center"
    ),
    TopologyNode(
        id="message_bus",
        name="Event Message Bus",
        type="bus",
        responsibility="Asynchronous pub-sub telemetry distribution and internal agent event routing.",
        status="idle",
        implementation_type="full",
        layer="center"
    ),
    TopologyNode(
        id="api_gateway",
        name="API Gateway",
        type="gateway",
        responsibility="Ingress flow telemetry validation, CORS routing, and REST / WebSocket API termination.",
        status="idle",
        implementation_type="full",
        layer="outer"
    ),
    TopologyNode(
        id="policy_engine",
        name="Policy Engine",
        type="engine",
        responsibility="Deterministic rule-based policy validation and automated mitigation approval control.",
        status="idle",
        implementation_type="full",
        layer="outer"
    ),
    TopologyNode(
        id="data_intelligence",
        name="Data Intelligence Agent",
        type="agent",
        responsibility="Harmonized feature vector extraction, logging normalization, and dataset validation.",
        status="idle",
        implementation_type="full",
        layer="inner"
    ),
    TopologyNode(
        id="threat_analysis",
        name="Threat Analysis Agent",
        type="agent",
        responsibility="D1->D2 CORAL model inference, anomaly score generation, and attack probability scoring.",
        status="idle",
        implementation_type="full",
        layer="inner"
    ),
    TopologyNode(
        id="explainability",
        name="Explainability Agent",
        type="agent",
        responsibility="Shapley value attribution computation and feature impact ranking comparison.",
        status="idle",
        implementation_type="full",
        layer="inner"
    ),
    TopologyNode(
        id="risk_prediction",
        name="Risk Prediction Agent",
        type="agent",
        responsibility="Operational grid risk score calculation and asset criticality assessment.",
        status="idle",
        implementation_type="full",
        layer="inner"
    ),
    TopologyNode(
        id="decision_support",
        name="Decision Support Agent",
        type="agent",
        responsibility="Natural language decision summary generation and Ollama LLM integration with fallback.",
        status="idle",
        implementation_type="full",
        layer="inner"
    ),
    TopologyNode(
        id="knowledge_context",
        name="Knowledge Context Agent",
        type="agent",
        responsibility="RAG-assisted MITRE ATT&CK ICS technique lookup and historical context retrieval.",
        status="idle",
        implementation_type="full",
        layer="inner"
    )
]

TOPOLOGY_EDGES: List[TopologyEdge] = [
    TopologyEdge(source="api_gateway", target="message_bus", label="Flow Telemetry Ingress", event_types=["flow_ingested"]),
    TopologyEdge(source="message_bus", target="orchestrator", label="Event Dispatch", event_types=["task_routed"]),
    TopologyEdge(source="orchestrator", target="data_intelligence", label="Start Pipeline", event_types=["task_routed"]),
    TopologyEdge(source="data_intelligence", target="threat_analysis", label="Pass Features", event_types=["task_routed"]),
    TopologyEdge(source="threat_analysis", target="explainability", label="Pass Threat Data", event_types=["task_routed"]),
    TopologyEdge(source="explainability", target="knowledge_context", label="Pass Explainability Data", event_types=["task_routed"]),
    TopologyEdge(source="knowledge_context", target="risk_prediction", label="Pass Context", event_types=["task_routed"]),
    TopologyEdge(source="risk_prediction", target="decision_support", label="Pass Risk Score", event_types=["task_routed"])
]


# Connection manager for WS subscribers
class AgentStreamManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> bool:
        settings = get_settings()
        async with self._lock:
            if len(self.active_connections) >= settings.security.max_websocket_connections:
                return False
            self.active_connections.append(websocket)
            return True

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        dead_sockets = []
        async with self._lock:
            connections = list(self.active_connections)

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_sockets.append(connection)

        for ds in dead_sockets:
            await self.disconnect(ds)

agent_stream_manager = AgentStreamManager()


@router.get("/topology", response_model=TopologyResponse, tags=["agents"])
async def get_agent_topology(
    user: UserPrincipal = Depends(require_permission("read:agent-topology"))
):
    """Return dynamic 3D/2D agent network topology with nodes and edges."""
    return TopologyResponse(nodes=TOPOLOGY_NODES, edges=TOPOLOGY_EDGES)


from argus.schemas.api import PredictRequest
@router.post("/trace", response_model=TraceExecutionResponse, tags=["agents"])
async def trace_agent_execution(
    request: Optional[PredictRequest] = Body(None),
    req: Request = None,
    user: UserPrincipal = Depends(require_permission("execute:flow-simulation"))
) -> TraceExecutionResponse:
    """Trigger a end-to-end multi-step flow execution trace across the agent graph."""
    corr_id = f"flow-{uuid.uuid4().hex[:8]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Audit log trace execution with authenticated principal
    from argus.security.audit import AuditLogger, SecurityAuditEvent
    AuditLogger.log_event(SecurityAuditEvent(
        actor_id=user.sub,
        action="EXECUTE_AGENT_TRACE",
        resource="/api/v1/agents/trace",
        outcome="SUCCESS",
        source_ip=req.client.host if req and req.client else None,
        correlation_id=corr_id
    ))
    
    from argus.orchestrator.pipeline import execute_pipeline, pipeline_context_to_response
    if request is not None:
        features = request.features.model_dump()
        model_name = request.model_name
    else:
        # Default realistic flow features from CICIoT2023 / NF-ToN
        features = {
            "pkt_mean_to_max": 0.42,
            "tcp_flag_density": 0.15,
            "log_pkt_mean": 5.2,
            "log_pkt_max": 7.1,
        }
        model_name = "model_d2_coral"
    
    ctx = await execute_pipeline(features=features, model_name=model_name, correlation_id=corr_id)
    response = pipeline_context_to_response(ctx)
    
    events_sequence = []
    events_sequence.append(FlowEventItem(
        event_id=str(uuid.uuid4())[:8],
        correlation_id=corr_id,
        source_node="api_gateway",
        target_node="message_bus",
        event_type="api_trigger",
        timestamp=now_iso,
        summary="Received simulation request.",
        payload={}
    ))
    events_sequence.append(FlowEventItem(
        event_id=str(uuid.uuid4())[:8],
        correlation_id=corr_id,
        source_node="message_bus",
        target_node="orchestrator",
        event_type="orchestrate",
        timestamp=now_iso,
        summary="Orchestrator began execution.",
        payload={}
    ))

    last_node = "orchestrator"
    
    for step in response["trace"]["steps"]:
        current_node = step["agent"].lower()
        if current_node == "data_intelligence":
            last_node = "orchestrator"
            
        events_sequence.append(FlowEventItem(
            event_id=str(uuid.uuid4())[:8],
            correlation_id=corr_id,
            source_node=last_node,
            target_node=current_node,
            event_type="agent_executed",
            timestamp=step["started_at"] or now_iso,
            summary=f"{step['agent']}: {step['status']}" + (
                f" — {step['output_summary']}" if step.get("output_summary") else ""
            ) + (f" [ERROR: {step['error']}]" if step.get("error") else ""),
            payload={
                "stage": step["agent"],
                "status": step["status"],
                "duration_ms": step["duration"],
                "input": step.get("input_summary"),
                "output": step.get("output_summary"),
                "model_version": step.get("model_version"),
                "error": step.get("error"),
            }
        ))
        last_node = current_node

    asyncio.create_task(broadcast_flow_sequence(events_sequence))

    return TraceExecutionResponse(
        correlation_id=corr_id,
        flow_status=ctx.status,
        total_events=len(events_sequence),
        events=events_sequence
    )

async def broadcast_flow_sequence(events: List[FlowEventItem]):
    for evt in events:
        await agent_stream_manager.broadcast({
            "type": "flow_event",
            "event": evt.model_dump()
        })
        await asyncio.sleep(0.15)


@router.websocket("/stream")
async def websocket_agent_stream(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """WebSocket broadcasting live status updates and flow trace events with security controls."""
    settings = get_settings()

    # 1. Validate Origin
    origin = websocket.headers.get("origin")
    if origin and settings.is_production:
        origin_clean = origin.rstrip("/")
        allowed = any(
            o == "*" or o.rstrip("/") == origin_clean
            for o in settings.security.cors_origins
        )
        if not allowed:
            logger.warning("agent_websocket_origin_rejected", origin=origin)
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    # 2. Authenticate WebSocket Connection
    if settings.is_production or settings.security.oidc_enabled or token:
        if not token:
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header[7:].strip()

        if not token:
            logger.warning("agent_websocket_unauthenticated", path="/api/v1/agents/stream")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            user = await jwt_validator.validate_token(token)
            if not user.has_permission("read:agent-topology"):
                logger.warning("agent_websocket_forbidden", user=user.sub, perm="read:agent-topology")
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except Exception as e:
            logger.warning("agent_websocket_auth_failed", error=str(e))
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    # 3. Connect with connection bounds checking
    connected = await agent_stream_manager.connect(websocket)
    if not connected:
        logger.warning("agent_websocket_max_connections_reached")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    try:
        idle_timeout = settings.security.websocket_idle_timeout_seconds
        max_bytes = settings.security.websocket_max_message_bytes
        start_time = time.time()
        max_duration = settings.security.max_websocket_duration_seconds

        while True:
            if (time.time() - start_time) > max_duration:
                logger.info("agent_websocket_max_duration_exceeded")
                break

            # Read with idle timeout
            data = await asyncio.wait_for(websocket.receive_text(), timeout=idle_timeout)
            if len(data) > max_bytes:
                logger.warning("agent_websocket_message_oversized", size=len(data))
                break

            if data == "ping":
                await websocket.send_text("pong")

    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    except Exception as ex:
        logger.error("agent_websocket_error", error=str(ex))
    finally:
        await agent_stream_manager.disconnect(websocket)
        try:
            await websocket.close()
        except Exception:
            pass
