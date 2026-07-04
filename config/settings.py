"""Configuration settings for ARGUS."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    sqlite_path: str = Field(default="data/argus.db")
    chromadb_path: str = Field(default="data/chromadb")
    pool_size: int = Field(default=5)


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    secret_key: str = Field(default="change-this-to-a-random-secret-key-in-production")
    jwt_secret_key: str = Field(default="change-this-to-a-different-random-secret-key")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiry_minutes: int = Field(default=60)
    cors_origins: List[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])
    rate_limit_requests: int = Field(default=100)
    rate_limit_window_seconds: int = Field(default=60)


class AgentSettings(BaseSettings):
    """Agent configuration settings."""
    heartbeat_interval: int = Field(default=30)
    task_timeout: int = Field(default=300)
    max_retries: int = Field(default=3)


class ObservabilitySettings(BaseSettings):
    """Observability configuration settings."""
    log_level: str = Field(default="INFO")
    metrics_enabled: bool = Field(default=True)
    trace_sampling_rate: float = Field(default=1.0)


class FeatureFlagSettings(BaseSettings):
    """Feature flag configuration settings."""
    adk_planning: bool = Field(default=False)
    vector_memory: bool = Field(default=True)
    audit_logging: bool = Field(default=True)
    rate_limiting: bool = Field(default=True)


class ArgusSettings(BaseSettings):
    """Root configuration settings for ARGUS."""
    model_config = SettingsConfigDict(
        env_prefix="ARGUS_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    env: str = Field(default="development")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=1)

    db: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    agent: AgentSettings = AgentSettings()
    observability: ObservabilitySettings = ObservabilitySettings()
    features: FeatureFlagSettings = FeatureFlagSettings()


@lru_cache()
def get_settings() -> ArgusSettings:
    """Get the cached application settings."""
    return ArgusSettings()
