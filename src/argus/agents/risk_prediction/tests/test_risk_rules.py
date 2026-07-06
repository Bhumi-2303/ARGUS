import pytest
from argus.agents.risk_prediction.tools.critical_asset_analyzer import CriticalAssetAnalyzer
from argus.agents.risk_prediction.tools.risk_scorer import RiskScorer
from argus.agents.risk_prediction.models.schemas import (
    AssetPriority, ImpactResult, EscalationResult, ImpactSeverity, CriticalityResult
)

@pytest.mark.asyncio
async def test_critical_asset_analyzer(risk_input_model):
    analyzer = CriticalAssetAnalyzer()
    await analyzer.initialize()
    
    result = await analyzer.execute(risk_input_model)
    
    assert result.asset_priority == AssetPriority.CRITICAL
    assert "scada_server_1" in result.critical_assets

@pytest.mark.asyncio
async def test_risk_scorer():
    scorer = RiskScorer()
    await scorer.initialize()
    
    crit = CriticalityResult(asset_priority=AssetPriority.CRITICAL, critical_assets=["x"], reasoning="")
    imp = ImpactResult(severity=ImpactSeverity.SEVERE, estimated_downtime_hours=12.0, impacted_services=["x"], reasoning="")
    esc = EscalationResult(escalation_factor=1.5, historical_context="", reasoning="")
    
    # Base for SEVERE is 60. Criticality multiplier is 1.2. Escalation is 1.5.
    # Score = 60 * 1.2 * 1.5 = 108. Clamped to 100.
    result = await scorer.execute(crit, imp, esc)
    
    assert result.score == 100
    assert result.severity == "CRITICAL"
