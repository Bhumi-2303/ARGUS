"""Configuration settings for Threat Analysis Agent."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from argus.agents.threat_analysis.models.schemas import ModelType


class ThreatAnalysisConfig(BaseSettings):
    """Agent-specific configuration."""
    model_config = SettingsConfigDict(env_prefix="ARGUS_TA_")

    model_dir: str = "/tmp/argus_models"
    default_model_type: ModelType = ModelType.XGBOOST
    confidence_threshold: float = 0.7
    gemini_enabled: bool = True
    max_concurrent_inferences: int = 10


config = ThreatAnalysisConfig()
