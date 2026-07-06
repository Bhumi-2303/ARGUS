import pytest
from argus.agents.decision_support.tools.playbook_selector import PlaybookSelector
from argus.agents.decision_support.tools.recommendation_engine import RecommendationEngine
from argus.agents.decision_support.tools.action_prioritizer import ActionPrioritizer

@pytest.mark.asyncio
async def test_playbook_selection(decision_input_model):
    selector = PlaybookSelector()
    await selector.initialize()
    
    playbooks = await selector.execute(decision_input_model)
    
    # CRITICAL severity with vulnerabilities should trigger CONTAIN and PATCH
    ids = [p.playbook_id for p in playbooks]
    assert "SOP-CONTAIN-01" in ids
    assert "SOP-PATCH-02" in ids

@pytest.mark.asyncio
async def test_recommendation_and_priority(decision_input_model):
    selector = PlaybookSelector()
    playbooks = await selector.execute(decision_input_model)
    
    engine = RecommendationEngine()
    recs = await engine.execute(decision_input_model, playbooks)
    
    prioritizer = ActionPrioritizer()
    action_plan = await prioritizer.execute(decision_input_model, recs)
    
    # Check prioritization
    assert len(action_plan.recommendations) > 0
    top_rec = action_plan.recommendations[0]
    
    assert top_rec.priority == 1
    assert top_rec.urgency == "immediate"
    assert top_rec.action_type == "isolate_network"
