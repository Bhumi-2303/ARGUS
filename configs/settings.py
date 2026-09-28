"""Configuration settings for ARGUS.

Provides production-ready configuration management, environment validation,
and fail-closed security enforcement.
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    sqlite_path: str = Field(default="data/argus.db")
    chromadb_path: str = Field(default="data/chromadb")
    pool_size: int = Field(default=5)


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    # Secrets (Must be overridden in production)
    secret_key: str = Field(default="change-this-to-a-random-secret-key-in-production")
    jwt_secret_key: str = Field(default="change-this-to-a-different-random-secret-key")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiry_minutes: int = Field(default=60)
    cors_origins: List[str] = Field(default=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"])
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100)
    rate_limit_window_seconds: int = Field(default=60)
    rate_limit_per_minute_public: int = Field(default=30)
    rate_limit_per_minute_authenticated: int = Field(default=120)
    rate_limit_per_minute_inference: int = Field(default=30)
    
    # OIDC / OAuth2 JWT Configuration
    oidc_enabled: bool = Field(default=False)
    oidc_issuer: str = Field(default="https://example.com/issuer")
    oidc_audience: str = Field(default="argus-api")
    oidc_algorithms: List[str] = Field(default=["RS256", "ES256"])
    oidc_jwks_url: str = Field(default="https://example.com/issuer/.well-known/jwks.json")
    oidc_jwks_cache_ttl_seconds: int = Field(default=3600)
    oidc_jwks_timeout_seconds: float = Field(default=5.0)
    
    # API Documentation & Network Controls
    enable_public_docs: bool = Field(default=False)
    trusted_proxies: List[str] = Field(default=["127.0.0.1", "::1"])
    
    # WebSocket & SSE Resource Limits
    max_websocket_connections: int = Field(default=50)
    max_websocket_duration_seconds: int = Field(default=3600)
    websocket_idle_timeout_seconds: int = Field(default=60)
    websocket_max_message_bytes: int = Field(default=65536)  # 64 KB
    max_sse_duration_seconds: int = Field(default=300)
    max_sse_row_count: int = Field(default=1000)
    
    # SIEM Configuration
    siem_enabled: bool = Field(default=False)
    siem_endpoint: str = Field(default="")
    siem_timeout_seconds: int = Field(default=3)


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
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    workers: int = Field(default=1)

    db: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    agent: AgentSettings = AgentSettings()
    observability: ObservabilitySettings = ObservabilitySettings()
    features: FeatureFlagSettings = FeatureFlagSettings()

    def model_post_init(self, __context) -> None:
        """Post-initialization hook to override settings from standard environment variables."""
        # Support standard ENVIRONMENT variable alongside ARGUS_ENV / ARGUS_MODE
        env_override = os.getenv("ENVIRONMENT") or os.getenv("ARGUS_MODE")
        if env_override:
            self.env = env_override.strip()

        # Support standard OIDC environment variables
        if "OIDC_ENABLED" in os.environ:
            self.security.oidc_enabled = os.environ["OIDC_ENABLED"].strip().lower() in ("true", "1", "yes")
        if "OIDC_ISSUER" in os.environ:
            self.security.oidc_issuer = os.environ["OIDC_ISSUER"].strip()
        if "OIDC_AUDIENCE" in os.environ:
            self.security.oidc_audience = os.environ["OIDC_AUDIENCE"].strip()
        if "OIDC_JWKS_URL" in os.environ:
            self.security.oidc_jwks_url = os.environ["OIDC_JWKS_URL"].strip()
        if "OIDC_ALGORITHMS" in os.environ:
            self.security.oidc_algorithms = [
                a.strip() for a in os.environ["OIDC_ALGORITHMS"].split(",") if a.strip()
            ]

        # Support standard secrets and CORS environment variables
        if "SECRET_KEY" in os.environ:
            self.security.secret_key = os.environ["SECRET_KEY"].strip()
        if "JWT_SECRET_KEY" in os.environ:
            self.security.jwt_secret_key = os.environ["JWT_SECRET_KEY"].strip()
        if "ALLOWED_ORIGINS" in os.environ:
            self.security.cors_origins = [
                o.strip() for o in os.environ["ALLOWED_ORIGINS"].split(",") if o.strip()
            ]
        elif "ARGUS_ALLOWED_ORIGINS" in os.environ:
            self.security.cors_origins = [
                o.strip() for o in os.environ["ARGUS_ALLOWED_ORIGINS"].split(",") if o.strip()
            ]

        # Enforce fail-closed validation for production environment
        if self.is_production:
            self.validate_production_configuration()

    @property
    def is_production(self) -> bool:
        """Check if application is running in production mode."""
        return self.env.strip().lower() in ("production", "prod")

    def validate_production_configuration(self) -> None:
        """Validate production configuration and fail closed if insecure defaults remain.
        
        Raises:
            RuntimeError: If any required production security control is missing or insecure.
        """
        errors = []

        # 1. Debug mode MUST be disabled in production
        if self.debug:
            errors.append("DEBUG mode must be False in production.")

        # 2. OIDC Authentication MUST be enabled in production
        if not self.security.oidc_enabled:
            errors.append("OIDC_ENABLED must be True in production. Development/mock authentication is forbidden.")

        # 3. OIDC Issuer & JWKS URL validation
        if not self.security.oidc_issuer or "example.com" in self.security.oidc_issuer:
            errors.append("OIDC_ISSUER must be configured with a valid identity provider URL (cannot contain 'example.com').")
        elif not self.security.oidc_issuer.startswith("https://"):
            errors.append("OIDC_ISSUER must use secure HTTPS protocol in production.")

        if not self.security.oidc_jwks_url or "example.com" in self.security.oidc_jwks_url:
            errors.append("OIDC_JWKS_URL must be configured with a valid JWKS endpoint (cannot contain 'example.com').")
        elif not self.security.oidc_jwks_url.startswith("https://"):
            errors.append("OIDC_JWKS_URL must use secure HTTPS protocol in production.")

        if not self.security.oidc_audience or self.security.oidc_audience in ("", "argus-api-placeholder"):
            errors.append("OIDC_AUDIENCE must be set to a valid audience identifier.")

        # 4. Asymmetric algorithm enforcement (Reject symmetric / none in OIDC)
        disallowed_algs = {"none", "hs256", "hs384", "hs512"}
        for alg in self.security.oidc_algorithms:
            if alg.lower() in disallowed_algs:
                errors.append(f"Disallowed algorithm '{alg}' in OIDC_ALGORITHMS. Production requires asymmetric algorithms (e.g. RS256, ES256).")

        # 5. Secrets must NOT be placeholder values
        insecure_placeholders = [
            "change-this",
            "random-secret",
            "default",
            "secret-key",
            "different-random-secret",
            "test-key"
        ]
        for token in insecure_placeholders:
            if token in self.security.secret_key.lower():
                errors.append("SECRET_KEY contains insecure default placeholder string.")
                break

        for token in insecure_placeholders:
            if token in self.security.jwt_secret_key.lower():
                errors.append("JWT_SECRET_KEY contains insecure default placeholder string.")
                break

        if len(self.security.secret_key) < 32:
            errors.append("SECRET_KEY must be at least 32 characters in production.")

        if len(self.security.jwt_secret_key) < 32:
            errors.append("JWT_SECRET_KEY must be at least 32 characters in production.")

        # 6. CORS hardening in production
        if not self.security.cors_origins:
            errors.append("ALLOWED_ORIGINS cannot be empty in production.")
        for origin in self.security.cors_origins:
            if origin == "*":
                errors.append("Wildcard '*' origin is forbidden in production CORS configuration.")
            if "localhost" in origin.lower() or "127.0.0.1" in origin:
                errors.append(f"Localhost/loopback origin '{origin}' is forbidden in production CORS configuration.")

        if errors:
            msg = "CRITICAL PRODUCTION CONFIGURATION FAILURE:\n" + "\n".join(f"  - {e}" for e in errors)
            raise RuntimeError(msg)


@lru_cache()
def get_settings() -> ArgusSettings:
    """Get the cached application settings."""
    return ArgusSettings()
