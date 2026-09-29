import pytest
import json
import asyncio
import os
import pandas as pd
from argus.orchestrator.state_machine import OrchestratorStateMachine
from argus.agents.explainability.agent import ExplainabilityAgent
from argus.utils.batch_replay import BatchReplay

# A mock agent that always raises an error
class ErrorAgent:
    async def validate(self, input_data):
        return True
    async def reason(self, context):
        return context
    async def plan(self, reasoning):
        return reasoning
    async def execute(self, plan):
        raise RuntimeError("Intentional error from agent")

class DummyAgent:
    async def initialize(self):
        pass
    async def validate(self, input_data):
        return True
    async def reason(self, context):
        return context
    async def plan(self, reasoning):
        return reasoning
    async def execute(self, plan):
        return {"dummy": "result"}

@pytest.mark.asyncio
async def test_end_to_end_pipeline():
    # 1. Ensure 1% sample data exists
    data_path = "tests/data/1_percent_sample.parquet"
    if not os.path.exists(data_path):
        import numpy as np
        df = pd.DataFrame({
            "f1": np.random.rand(100),
            "f2": np.random.rand(100),
            "f3": np.random.rand(100),
            "f4": np.random.rand(100),
        })
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df.to_parquet(data_path)

    explainability_agent = DummyAgent()
    await explainability_agent.initialize()
    
    agents = {
        "Explainability": explainability_agent,
        # Others left as None to test "not_implemented" listing
    }
    
    # 2. Run twice and compare JSON byte for byte
    async def run_pipeline():
        replay = BatchReplay(data_path, batch_size=100)
        all_results = []
        for batch_df in replay.iter_batches():
            orchestrator = OrchestratorStateMachine(agents)
            # Pass dictionary with 'features' as expected by ExplainabilityAgent
            result = await orchestrator.run({"features": batch_df})
            all_results.append(result)
        return all_results
        
    results_run1 = await run_pipeline()
    results_run2 = await run_pipeline()
    
    json1 = json.dumps(results_run1, sort_keys=True).encode("utf-8")
    json2 = json.dumps(results_run2, sort_keys=True).encode("utf-8")
    
    assert json1 == json2, "JSON output differs between runs!"
    
    # Verify "not_implemented" agents are in output
    for res in results_run1:
        assert "not_implemented_agents" in res
        # DataIntelligence, ThreatAnalysis, Fusion should be not implemented
        assert "DataIntelligence" in res["not_implemented_agents"]
        assert "ThreatAnalysis" in res["not_implemented_agents"]
        assert "Fusion" in res["not_implemented_agents"]
        
    # 3. Error path when an agent raises
    error_agents = {
        "Explainability": ErrorAgent()
    }
    orchestrator_err = OrchestratorStateMachine(error_agents)
    err_result = await orchestrator_err.run({"features": pd.DataFrame()})
    assert err_result["final_status"] == "error"
    assert "Intentional error" in err_result["error_message"]
