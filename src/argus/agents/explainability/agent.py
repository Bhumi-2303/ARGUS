import numpy as np
import pandas as pd
from typing import Any, Dict, List
import structlog
import xgboost as xgb
from scipy.stats import spearmanr
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

from argus.core.base_agent import BaseAgent
from argus.core.enums import AgentStatus

class ExplainabilityAgent(BaseAgent):
    """
    Explainability Agent
    Calculates feature attributions (TreeSHAP or xgboost pred_contribs)
    and explanation stability between source and adapted models.
    """
    
    def __init__(self, source_model=None, adapted_model=None, **kwargs):
        kwargs.setdefault("agent_id", "agent_explainability")
        kwargs.setdefault("name", "Explainability Agent")
        kwargs.setdefault("version", "1.0.0")
        kwargs.setdefault("description", "Feature attribution using SHAP")
        kwargs.setdefault("capabilities", ["explainability", "shap"])
        kwargs.setdefault("permissions", ["compute:inference"])
        kwargs.setdefault("tools", [])
        
        super().__init__(**kwargs)
        self.logger = structlog.get_logger("argus.agent.explainability")
        self.status = AgentStatus.INITIALIZING
        self.source_model = source_model
        self.adapted_model = adapted_model
        
    async def initialize(self) -> None:
        self.logger.info("initializing_explainability_agent")
        if self.source_model is None:
            # Mock model for tests
            self.source_model = xgb.XGBClassifier(n_estimators=10, max_depth=3)
            # Create dummy data to fit
            X_dummy = np.random.rand(10, 4)
            y_dummy = np.random.randint(0, 2, 10)
            self.source_model.fit(X_dummy, y_dummy)
            
        if self.adapted_model is None:
            self.adapted_model = xgb.XGBClassifier(n_estimators=10, max_depth=3)
            X_dummy = np.random.rand(10, 4)
            y_dummy = np.random.randint(0, 2, 10)
            self.adapted_model.fit(X_dummy, y_dummy)
            
        self.status = AgentStatus.READY
        
    async def validate(self, input_data: Any) -> bool:
        if not isinstance(input_data, dict):
            return False
        if "features" not in input_data and "data" not in input_data:
            return False
        return True
        
    async def reason(self, context: Any) -> Any:
        return context
        
    async def plan(self, reasoning: Any) -> Any:
        return reasoning
        
    async def execute(self, plan: Any) -> Any:
        # Assuming plan contains 'features' which is a numpy array or DataFrame
        features = plan.get("features", plan.get("data"))
        if isinstance(features, list):
            features = pd.DataFrame(features)
            
        # Per-flow attributions
        if HAS_SHAP:
            explainer_source = shap.TreeExplainer(self.source_model)
            explainer_adapted = shap.TreeExplainer(self.adapted_model)
            shap_source = explainer_source.shap_values(features)
            shap_adapted = explainer_adapted.shap_values(features)
        else:
            # Fallback to xgboost pred_contribs
            booster_source = self.source_model.get_booster()
            booster_adapted = self.adapted_model.get_booster()
            dmatrix = xgb.DMatrix(features)
            shap_source = booster_source.predict(dmatrix, pred_contribs=True)[:, :-1]
            shap_adapted = booster_adapted.predict(dmatrix, pred_contribs=True)[:, :-1]
            
        # Global mean |attribution|
        mean_abs_source = np.abs(shap_source).mean(axis=0)
        mean_abs_adapted = np.abs(shap_adapted).mean(axis=0)
        
        # Rank features
        rank_source = np.argsort(-mean_abs_source)
        rank_adapted = np.argsort(-mean_abs_adapted)
        
        # Explanation stability (Spearman correlation)
        # Note: With only four features, this is coarse. Do not assume ranks agree.
        rho, pval = spearmanr(rank_source, rank_adapted)
        
        return {
            "per_flow_attributions_source": shap_source.tolist() if isinstance(shap_source, np.ndarray) else shap_source,
            "per_flow_attributions_adapted": shap_adapted.tolist() if isinstance(shap_adapted, np.ndarray) else shap_adapted,
            "global_mean_abs_source": mean_abs_source.tolist(),
            "global_mean_abs_adapted": mean_abs_adapted.tolist(),
            "explanation_stability_rho": rho if not np.isnan(rho) else 0.0,
            "note": "With only four features, Spearman correlation is coarse."
        }
        
    async def call_tools(self, tool_requests: List[Any]) -> List[Any]:
        return []
        
    async def update_memory(self, result: Any) -> None:
        pass
        
    async def publish(self, result: Any) -> None:
        pass
        
    async def health(self) -> Any:
        return {"status": self.status.value}
        
    async def shutdown(self) -> None:
        self.status = AgentStatus.SHUTDOWN

