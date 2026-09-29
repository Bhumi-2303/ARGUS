import pytest
from argus.orchestrator.pipeline import execute_pipeline, PipelineContext

@pytest.mark.asyncio
async def test_full_argus_agent_pipeline():
    features = {
        "pkt_mean_to_max": 0.5,
        "tcp_flag_density": 0.1,
        "log_pkt_mean": 5.0,
        "log_pkt_max": 7.0
    }
    
    ctx = await execute_pipeline(features=features, model_name="xgb_adapted")
    
    if ctx.status != "completed":
        print(f"Pipeline failed with error: {ctx.error}")
        print("Trace summary:")
        for t in ctx.trace:
            print(f"{t.agent}: {t.status} (error: {t.error})")
            
    assert ctx.status == "completed"

@pytest.mark.asyncio
async def test_full_argus_agent_pipeline_failure():
    """Verify that failure propagates and downstream agents are SKIPPED."""
    # Bad features that Data Intelligence Agent rejects
    features = {
        "flow_duration": 100.0,
        "fwd_pkts": 5.0,
        "bwd_pkts": 5.0,
        "tot_len_fwd_pkts": 500.0
    }
    
    ctx = await execute_pipeline(features=features, model_name="xgb_adapted")
    
    assert ctx.status == "failed"
    assert ctx.error is not None
    
    # 1 agent FAILED, 5 agents SKIPPED
    assert len(ctx.trace) == 6
    assert ctx.trace[0].agent == "DATA_INTELLIGENCE"
    assert ctx.trace[0].status == "FAILED"
    
    for i in range(1, 6):
        assert ctx.trace[i].status == "SKIPPED"
        assert "Dependency failed" in ctx.trace[i].error
