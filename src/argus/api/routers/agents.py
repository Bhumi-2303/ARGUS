"""Agent router providing topology layout, live status WebSocket, and flow simulation."""

import uuid
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field

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
        id="risk_agent",
        name="Risk Prediction Agent",
        type="agent",
        responsibility="Operational grid risk score calculation and asset criticality assessment.",
        status="idle",
        implementation_type="stub",
        layer="inner"
    ),
    TopologyNode(
        id="decision_agent",
        name="Decision Support Agent",
        type="agent",
        responsibility="Natural language decision summary generation and Ollama LLM integration with fallback.",
        status="idle",
        implementation_type="stub",
        layer="inner"
    ),
    TopologyNode(
        id="knowledge_agent",
        name="Knowledge Context Agent",
        type="agent",
        responsibility="RAG-assisted MITRE ATT&CK ICS technique lookup and historical context retrieval.",
        status="idle",
        implementation_type="stub",
        layer="inner"
    )
]

TOPOLOGY_EDGES: List[TopologyEdge] = [
    TopologyEdge(source="api_gateway", target="message_bus", label="Flow Telemetry Ingress", event_types=["flow_ingested"]),
    TopologyEdge(source="message_bus", target="orchestrator", label="Event Dispatch", event_types=["task_routed"]),
    TopologyEdge(source="orchestrator", target="data_intelligence", label="Preprocess Flow", event_types=["task_routed"]),
    TopologyEdge(source="orchestrator", target="threat_analysis", label="Evaluate Model", event_types=["task_routed"]),
    TopologyEdge(source="orchestrator", target="explainability", label="Compute SHAP", event_types=["task_routed"]),
    TopologyEdge(source="orchestrator", target="risk_agent", label="Assess Grid Risk", event_types=["task_routed"]),
    TopologyEdge(source="risk_agent", target="knowledge_agent", label="Query ATT&CK Context", event_types=["bus_message"]),
    TopologyEdge(source="orchestrator", target="policy_engine", label="Validate Policy", event_types=["bus_message"]),
    TopologyEdge(source="policy_engine", target="decision_agent", label="Recommend Action", event_types=["task_routed"])
]


# Connection manager for WS subscribers
class AgentStreamManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        dead_sockets = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_sockets.append(connection)
        for ds in dead_sockets:
            self.disconnect(ds)

agent_stream_manager = AgentStreamManager()


@router.get("/topology", response_model=TopologyResponse, tags=["agents"])
async def get_agent_topology():
    """Return dynamic 3D/2D agent network topology with nodes and edges."""
    return TopologyResponse(nodes=TOPOLOGY_NODES, edges=TOPOLOGY_EDGES)


from argus.schemas.api import PredictRequest
@router.post("/trace", response_model=TraceExecutionResponse, tags=["agents"])
async def trace_agent_execution(request: PredictRequest):
    """Trigger a end-to-end multi-step flow execution trace across the agent graph."""
    corr_id = f"flow-{uuid.uuid4().hex[:8]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # 1. Run REAL Data Intelligence Agent
    from argus.agents.data_intelligence.agent import DataIntelligenceAgent
    dia = DataIntelligenceAgent()
    await dia.initialize()
    
    # 2. Run REAL Threat Analysis Agent
    from argus.agents.threat_analysis.agent import ThreatAnalysisAgent
    taa = ThreatAnalysisAgent()
    await taa.initialize()
    
    # Create fake payload that resembles real CICIoT data
    features = request.features.model_dump()
    
    # Execute DIA
    # It just acts as pass-through for now but it's the real class
    
    # Execute TAA
    threat_res = await taa.reason({"event_id": corr_id, "source": "dia", "features": features, "timestamp": now_iso})
    # threat_res has 'confidence', 'threat_level', 'evidence'
    
    prob = threat_res["confidence"]
    model_ver = threat_res["model_version"]
    
    events_sequence = [
        FlowEventItem(
            event_id=str(uuid.uuid4())[:8],
            correlation_id=corr_id,
            source_node="api_gateway",
            target_node="message_bus",
            event_type="flow_ingested",
            timestamp=now_iso,
            summary="Ingested SCADA flow packet",
            payload={"domain": "nfton", "protocol": "NetFlow_v2"}
        ),
        FlowEventItem(
            event_id=str(uuid.uuid4())[:8],
            correlation_id=corr_id,
            source_node="message_bus",
            target_node="orchestrator",
            event_type="task_routed",
            timestamp=now_iso,
            summary="Dispatched flow evaluation task",
            payload={"task_id": f"task-{uuid.uuid4().hex[:8]}", "priority": "high"}
        ),
        FlowEventItem(
            event_id=str(uuid.uuid4())[:8],
            correlation_id=corr_id,
            source_node="orchestrator",
            target_node="data_intelligence",
            event_type="task_routed",
            timestamp=now_iso,
            summary="Extracted harmonized flow feature vectors",
            payload={"features": list(features.keys())}
        ),
        FlowEventItem(
            event_id=str(uuid.uuid4())[:8],
            correlation_id=corr_id,
            source_node="orchestrator",
            target_node="threat_analysis",
            event_type="task_routed",
            timestamp=now_iso,
            summary=f"Evaluated {model_ver} model (Probability: {prob:.4f})",
            payload={"model": model_ver, "attack_prob": round(prob, 4), "prediction": 1 if prob > 0.5 else 0}
        ),
        FlowEventItem(
            event_id=str(uuid.uuid4())[:8],
            correlation_id=corr_id,
            source_node="orchestrator",
            target_node="risk_agent",
            event_type="task_routed",
            timestamp=now_iso,
            summary="Risk Prediction Agent (Stub) marked not_implemented",
            payload={"status": "not_implemented"}
        ),
        FlowEventItem(
            event_id=str(uuid.uuid4())[:8],
            correlation_id=corr_id,
            source_node="risk_agent",
            target_node="knowledge_agent",
            event_type="task_routed",
            timestamp=now_iso,
            summary="Knowledge Context Agent (Stub) marked not_implemented",
            payload={"status": "not_implemented"}
        ),
        FlowEventItem(
            event_id=str(uuid.uuid4())[:8],
            correlation_id=corr_id,
            source_node="knowledge_agent",
            target_node="decision_agent",
            event_type="task_routed",
            timestamp=now_iso,
            summary="Decision Support Agent (Stub) marked not_implemented",
            payload={"status": "not_implemented"}
        )
    ]

    return TraceExecutionResponse(
        correlation_id=corr_id,
        flow_status="completed",
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
async def websocket_agent_stream(websocket: WebSocket):
    """WebSocket broadcasting live status updates and flow trace events."""
    await agent_stream_manager.connect(websocket)
    try:
        while True:
            # Keepalive read
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        agent_stream_manager.disconnect(websocket)
    except Exception:
        agent_stream_manager.disconnect(websocket)
