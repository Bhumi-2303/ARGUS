import pytest
from datetime import datetime, timedelta
from argus.core.trace import ExecutionTrace, TraceStep

def test_trace_step_success():
    start = datetime.utcnow()
    end = start + timedelta(milliseconds=150)
    step = TraceStep(
        stage="DETECTED",
        component="Detector Agent",
        status="SUCCESS",
        start_time=start,
        end_time=end,
        duration_ms=150.0,
        model_version="1.0.0"
    )
    trace = ExecutionTrace(event_id="evt-1")
    trace.add_step(step)
    
    assert len(trace.steps) == 1
    assert trace.steps[0].status == "SUCCESS"

def test_trace_step_failure():
    step = TraceStep(
        stage="RISK_ASSESSED",
        component="Risk Agent",
        status="FAILED",
        error="Dependency timeout"
    )
    assert step.status == "FAILED"
    assert step.error == "Dependency timeout"
