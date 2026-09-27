import re

def patch_file(filepath, replacements):
    with open(filepath, "r") as f:
        code = f.read()
    for old, new in replacements:
        code = code.replace(old, new)
    with open(filepath, "w") as f:
        f.write(code)

patch_file("src/argus/api/routers/agents.py", [
    ('@router.post("/simulate-flow"', '@router.post("/trace"'),
    ('async def simulate_agent_flow', 'async def trace_agent_execution'),
    ('SimulateFlowResponse', 'TraceExecutionResponse')
])

patch_file("src/argus/schemas/agents.py", [
    ('class SimulateFlowResponse', 'class TraceExecutionResponse')
])

patch_file("web/src/features/analysis/InputAnalysisPage.tsx", [
    ('agents/simulate-flow', 'agents/trace')
])

patch_file("web/src/features/topology/TopologyPage.tsx", [
    ('agents/simulate-flow', 'agents/trace')
])
