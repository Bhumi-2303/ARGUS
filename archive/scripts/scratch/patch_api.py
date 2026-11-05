import re

with open('src/argus/api/main.py', 'r') as f:
    text = f.read()

start_stop = """
async def start_agent_chain():
    await agent_bus.start()
    dia = DataIntelligenceAgent(agent_id="agent_dia", name="DIA", version="1.0", description="DIA", capabilities=["data_normalization"], permissions=[], tools=[])
    taa = ThreatAnalysisAgent()
    rpa = RiskPredictionAgent()
    kca = KnowledgeContextAgent(agent_id="agent_kca", name="KCA", version="1.0", description="KCA", capabilities=["threat_enrichment"], permissions=[], tools=[])
    dsa = DecisionSupportAgent(agent_id="agent_dsa", name="DSA", version="1.0", description="DSA", capabilities=["action_recommendation"], permissions=[], tools=[])
    
    agents = [dia, taa, rpa, kca, dsa]
    for a in agents:
        await a.initialize()
        reg = AgentRegistration(agent_id=a.agent_id, name=a.name, version=a.version, description=a.description, capabilities=a.capabilities, permissions=a.permissions, tools=a.tools, status=AgentStatus.READY)
        await agent_registry.register(reg)

    await agent_orchestrator.start()
    logger.info("async_agent_orchestrator_started")

async def stop_agent_chain():
    await agent_orchestrator.stop()
    await agent_bus.stop()
"""

# Insert the functions right before `async def lifespan(app: FastAPI):`
text = re.sub(
    r'async def lifespan\(app: FastAPI\):',
    start_stop + '\n@asynccontextmanager\nasync def lifespan(app: FastAPI):',
    text
)

with open('src/argus/api/main.py', 'w') as f:
    f.write(text)
