import asyncio
import uuid
import structlog
import logging
from argus.orchestrator.orchestrator import Orchestrator
from argus.registry.registry import AgentRegistry
from argus.bus.message_bus import MessageBus
from argus.schemas.tasks import TaskDefinition
from argus.core.enums import TaskPriority, TaskStatus
from argus.schemas.agents import AgentRegistration
from argus.core.enums import AgentStatus

from argus.agents.data_intelligence.agent import DataIntelligenceAgent
from argus.agents.threat_analysis.agent import ThreatAnalysisAgent
from argus.agents.risk_prediction.agent import RiskPredictionAgent
from argus.agents.knowledge_context.agent import KnowledgeContextAgent
from argus.agents.decision_support.agent import DecisionSupportAgent

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

async def main():
    registry = AgentRegistry()
    bus = MessageBus()
    await bus.start()
    orch = Orchestrator(registry=registry, message_bus=bus)
    
    dia = DataIntelligenceAgent(agent_id="agent_dia", name="DIA", version="1.0", description="DIA", capabilities=["data_normalization"], permissions=[], tools=[])
    taa = ThreatAnalysisAgent()
    rpa = RiskPredictionAgent()
    kca = KnowledgeContextAgent(agent_id="agent_kca", name="KCA", version="1.0", description="KCA", capabilities=["threat_enrichment"], permissions=[], tools=[])
    dsa = DecisionSupportAgent(agent_id="agent_dsa", name="DSA", version="1.0", description="DSA", capabilities=["action_recommendation"], permissions=[], tools=[])
    
    agents = [dia, taa, rpa, kca, dsa]
    for a in agents:
        await a.initialize()
        reg = AgentRegistration(
            agent_id=a.agent_id,
            name=a.name,
            version=a.version,
            description=a.description,
            capabilities=a.capabilities,
            permissions=a.permissions,
            tools=a.tools,
            status=AgentStatus.READY
        )
        await registry.register(reg)

    await orch.start()
    
    trace_id = str(uuid.uuid4())
    print(f"\n--- STARTING TRACE {trace_id} ---")
    
    t1 = TaskDefinition(task_type="preprocess", required_capabilities=["data_normalization"], payload={"file_path": "dummy.csv", "config": {}, "trace_id": trace_id}, priority=TaskPriority.HIGH)
    t1_id = await orch.submit_task(t1)
    
    t2 = TaskDefinition(task_type="analyze", required_capabilities=["anomaly_detection"], payload={"event_id": trace_id, "source": "dia", "features": {"pkt_mean_to_max": 0.5, "tcp_flag_density": 0.1, "log_pkt_mean": 2.0, "log_pkt_max": 3.0}, "timestamp": "2026-09-26T00:00:00Z"}, dependencies=[t1_id], priority=TaskPriority.HIGH)
    t2_id = await orch.submit_task(t2)
    
    t3 = TaskDefinition(task_type="predict", required_capabilities=["risk_scoring"], payload={"threat_event": {"source_event_id": trace_id, "attack_type": "ddos", "severity": 0.9, "description": "test"}, "knowledge_event": {"source_event_id": trace_id, "attack_context": {}, "mitre_techniques": [], "cves": [], "cisa_advisories": [], "recommended_mitigations": [], "references": [], "confidence": 0.9, "processing_metadata": {}, "affected_assets": ["pump1"], "asset_types": {"pump1": "ics_controller"}}}, dependencies=[t2_id], priority=TaskPriority.HIGH)
    t3_id = await orch.submit_task(t3)
    
    t4 = TaskDefinition(task_type="knowledge", required_capabilities=["threat_enrichment"], payload={"threat_data": {"attack_type": "ddos"}}, dependencies=[t2_id], priority=TaskPriority.HIGH)
    t4_id = await orch.submit_task(t4)
    
    t5 = TaskDefinition(task_type="decision", required_capabilities=["action_recommendation"], payload={"risk_event": {"source_event_id": trace_id, "risk_score": 80, "severity": "high", "confidence": 0.8, "asset_priority": "critical", "impact_estimation": {"reasoning": "", "asset_priority": "critical", "safety_impact": "high", "operational_impact": "high", "environmental_impact": "high", "financial_impact": "high"}, "reasoning": "", "metadata": {}}, "knowledge_event": {"source_event_id": trace_id, "attack_context": {}, "mitre_techniques": [], "cves": [], "cisa_advisories": [], "recommended_mitigations": [], "references": [], "confidence": 0.9, "processing_metadata": {}}}, dependencies=[t3_id, t4_id], priority=TaskPriority.HIGH)
    t5_id = await orch.submit_task(t5)
    
    # We simulate agents completing tasks so orchestrator chains them
    await asyncio.sleep(1.0)
    # Orchestrator routed t1 to DIA. Simulate completion:
    from argus.schemas.tasks import TaskCompletion
    await orch._handle_task_result(TaskCompletion(task_id=t1_id, status=TaskStatus.COMPLETED, result={}, error=None, duration=0.1))
    await asyncio.sleep(1.0)
    # Now t2 is scheduled and routed.
    await orch._handle_task_result(TaskCompletion(task_id=t2_id, status=TaskStatus.COMPLETED, result={}, error=None, duration=0.1))
    await asyncio.sleep(1.0)
    # t3 and t4 scheduled
    await orch._handle_task_result(TaskCompletion(task_id=t3_id, status=TaskStatus.COMPLETED, result={}, error=None, duration=0.1))
    await orch._handle_task_result(TaskCompletion(task_id=t4_id, status=TaskStatus.COMPLETED, result={}, error=None, duration=0.1))
    await asyncio.sleep(1.0)
    # t5 scheduled
    await orch._handle_task_result(TaskCompletion(task_id=t5_id, status=TaskStatus.COMPLETED, result={}, error=None, duration=0.1))
    await asyncio.sleep(1.0)
    
    await orch.stop()
    await bus.stop()

if __name__ == "__main__":
    asyncio.run(main())
