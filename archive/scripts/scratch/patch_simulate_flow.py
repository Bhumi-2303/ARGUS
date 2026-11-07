import re

with open("src/argus/api/routers/agents.py", "r") as f:
    code = f.read()

# Make simulate_agent_flow accept a payload
old_def = """@router.post("/simulate-flow", response_model=SimulateFlowResponse, tags=["agents"])
async def simulate_agent_flow():"""
new_def = """from argus.schemas.api import PredictRequest
@router.post("/simulate-flow", response_model=SimulateFlowResponse, tags=["agents"])
async def simulate_agent_flow(request: PredictRequest):"""
code = code.replace(old_def, new_def)

# Replace the fake payload with the actual input
old_payload = 'features = {"pkt_mean_to_max": 0.054, "tcp_flag_density": 0.0, "log_pkt_mean": 2.1, "log_pkt_max": 2.5}'
new_payload = 'features = request.features.model_dump()'
code = code.replace(old_payload, new_payload)

with open("src/argus/api/routers/agents.py", "w") as f:
    f.write(code)
