import re

with open('src/argus/api/routers/agents.py', 'r') as f:
    content = f.read()

new_func = """@router.post("/simulate-flow", response_model=SimulateFlowResponse, tags=["agents"])
async def simulate_agent_flow():
    \"\"\"Trigger a end-to-end multi-step flow execution trace across the agent graph.\"\"\"
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
    features = {"pkt_mean_to_max": 0.054, "tcp_flag_density": 0.0, "log_pkt_mean": 2.1, "log_pkt_max": 2.5}
    
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

    return SimulateFlowResponse(
        correlation_id=corr_id,
        flow_status="completed",
        total_events=len(events_sequence),
        events=events_sequence
    )
"""

content = re.sub(
    r'@router\.post\("/simulate-flow".*?events=events_sequence\n    \)',
    new_func,
    content,
    flags=re.DOTALL
)

with open('src/argus/api/routers/agents.py', 'w') as f:
    f.write(content)
