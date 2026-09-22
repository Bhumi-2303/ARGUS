import asyncio
import json
import enum
from typing import Dict, Any, List

class State(enum.Enum):
    VALIDATE = "validate"
    DATA_INTELLIGENCE = "data_intelligence"
    THREAT_ANALYSIS = "threat_analysis"
    EXPLAINABILITY = "explainability"
    FUSION = "fusion"
    FINAL_REPORT = "final_report"
    ERROR = "error"
    DONE = "done"

class OrchestratorStateMachine:
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.state = State.VALIDATE
        self.context = {}
        self.report = {
            "not_implemented_agents": [],
            "results": {}
        }
        
    async def run(self, input_data: Any) -> Dict[str, Any]:
        self.context["input_data"] = input_data
        
        while self.state not in (State.DONE, State.ERROR):
            try:
                if self.state == State.VALIDATE:
                    # In a real scenario, we might call a specific validate function
                    if not isinstance(input_data, dict):
                        raise ValueError("Input data must be a dictionary")
                    self.state = State.DATA_INTELLIGENCE
                    
                elif self.state == State.DATA_INTELLIGENCE:
                    await self._run_agent("DataIntelligence", State.THREAT_ANALYSIS)
                    
                elif self.state == State.THREAT_ANALYSIS:
                    await self._run_agent("ThreatAnalysis", State.EXPLAINABILITY)
                    
                elif self.state == State.EXPLAINABILITY:
                    await self._run_agent("Explainability", State.FUSION)
                    
                elif self.state == State.FUSION:
                    await self._run_agent("Fusion", State.FINAL_REPORT)
                    
                elif self.state == State.FINAL_REPORT:
                    self.report["final_status"] = "success"
                    self.state = State.DONE
                    
            except Exception as e:
                self.report["final_status"] = "error"
                self.report["error_message"] = str(e)
                self.state = State.ERROR
                
        return self.report
        
    async def _run_agent(self, agent_name: str, next_state: State):
        agent = self.agents.get(agent_name)
        if agent is None:
            self.report["not_implemented_agents"].append(agent_name)
            self.report["results"][agent_name] = {"status": "not_implemented"}
            self.state = next_state
            return
            
        is_valid = await agent.validate(self.context["input_data"])
        if not is_valid:
            raise ValueError(f"{agent_name} validation failed on input data.")
            
        reasoning = await agent.reason(self.context["input_data"])
        plan = await agent.plan(reasoning)
        result = await agent.execute(plan)
        
        self.report["results"][agent_name] = {
            "status": "completed",
            "output": result
        }
        self.state = next_state
