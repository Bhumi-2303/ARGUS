"""Tests verifying that production configuration strictly fails closed on insecure defaults."""

import os
import pytest
from configs.settings import ArgusSettings, SecuritySettings


def test_production_fails_on_debug_true():
    """Production mode must reject debug=True."""
    with pytest.raises(RuntimeError, match="DEBUG mode must be False in production"):
        ArgusSettings(
            env="production",
            debug=True,
            security=SecuritySettings(
                oidc_enabled=True,
                oidc_issuer="https://auth.argus.enterprise",
                oidc_jwks_url="https://auth.argus.enterprise/.well-known/jwks.json",
                oidc_audience="argus-api-prod",
                secret_key="a" * 32,
                jwt_secret_key="b" * 32,
                cors_origins=["https://argus.enterprise"]
            )
        )


def test_production_fails_on_oidc_disabled():
    """Production mode must reject oidc_enabled=False."""
    with pytest.raises(RuntimeError, match="OIDC_ENABLED must be True in production"):
        ArgusSettings(
            env="production",
            debug=False,
            security=SecuritySettings(
                oidc_enabled=False,
                secret_key="a" * 32,
                jwt_secret_key="b" * 32,
                cors_origins=["https://argus.enterprise"]
            )
        )


def test_production_fails_on_placeholder_secret_key():
    """Production mode must reject default placeholder secret_key."""
    with pytest.raises(RuntimeError, match="SECRET_KEY contains insecure default placeholder"):
        ArgusSettings(
            env="production",
            debug=False,
            security=SecuritySettings(
                oidc_enabled=True,
                oidc_issuer="https://auth.argus.enterprise",
                oidc_jwks_url="https://auth.argus.enterprise/.well-known/jwks.json",
                oidc_audience="argus-api-prod",
                secret_key="change-this-to-a-random-secret-key-in-production",
                jwt_secret_key="b" * 32,
                cors_origins=["https://argus.enterprise"]
            )
        )


def test_production_fails_on_short_secret_key():
    """Production mode must reject secret_key shorter than 32 characters."""
    with pytest.raises(RuntimeError, match="SECRET_KEY must be at least 32 characters"):
        ArgusSettings(
            env="production",
            debug=False,
            security=SecuritySettings(
                oidc_enabled=True,
                oidc_issuer="https://auth.argus.enterprise",
                oidc_jwks_url="https://auth.argus.enterprise/.well-known/jwks.json",
                oidc_audience="argus-api-prod",
                secret_key="too-short-secret",
                jwt_secret_key="b" * 32,
                cors_origins=["https://argus.enterprise"]
            )
        )


def test_production_fails_on_example_com_issuer():
    """Production mode must reject placeholder example.com OIDC issuer."""
    with pytest.raises(RuntimeError, match="OIDC_ISSUER must be configured"):
        ArgusSettings(
            env="production",
            debug=False,
            security=SecuritySettings(
                oidc_enabled=True,
                oidc_issuer="https://example.com/issuer",
                oidc_jwks_url="https://auth.argus.enterprise/.well-known/jwks.json",
                oidc_audience="argus-api-prod",
                secret_key="a" * 32,
                jwt_secret_key="b" * 32,
                cors_origins=["https://argus.enterprise"]
            )
        )


def test_production_fails_on_symmetric_oidc_algorithm():
    """Production mode must reject symmetric or none algorithms in OIDC."""
    with pytest.raises(RuntimeError, match="Disallowed algorithm 'HS256' in OIDC_ALGORITHMS"):
        ArgusSettings(
            env="production",
            debug=False,
            security=SecuritySettings(
                oidc_enabled=True,
                oidc_issuer="https://auth.argus.enterprise",
                oidc_jwks_url="https://auth.argus.enterprise/.well-known/jwks.json",
                oidc_audience="argus-api-prod",
                oidc_algorithms=["HS256"],
                secret_key="a" * 32,
                jwt_secret_key="b" * 32,
                cors_origins=["https://argus.enterprise"]
            )
        )


def test_production_fails_on_wildcard_cors():
    """Production mode must reject wildcard CORS origin."""
    with pytest.raises(RuntimeError, match="Wildcard '\\*' origin is forbidden"):
        ArgusSettings(
            env="production",
            debug=False,
            security=SecuritySettings(
                oidc_enabled=True,
                oidc_issuer="https://auth.argus.enterprise",
                oidc_jwks_url="https://auth.argus.enterprise/.well-known/jwks.json",
                oidc_audience="argus-api-prod",
                secret_key="a" * 32,
                jwt_secret_key="b" * 32,
                cors_origins=["*"]
            )
        )


def test_production_fails_on_localhost_cors():
    """Production mode must reject localhost or loopback CORS origin."""
    with pytest.raises(RuntimeError, match="Localhost/loopback origin 'http://localhost:3000' is forbidden"):
        ArgusSettings(
            env="production",
            debug=False,
            security=SecuritySettings(
                oidc_enabled=True,
                oidc_issuer="https://auth.argus.enterprise",
                oidc_jwks_url="https://auth.argus.enterprise/.well-known/jwks.json",
                oidc_audience="argus-api-prod",
                secret_key="a" * 32,
                jwt_secret_key="b" * 32,
                cors_origins=["http://localhost:3000"]
            )
        )


def test_production_succeeds_with_valid_configuration():
    """Production mode initializes smoothly when all security parameters meet production standards."""
    settings = ArgusSettings(
        env="production",
        debug=False,
        security=SecuritySettings(
            oidc_enabled=True,
            oidc_issuer="https://auth.argus.enterprise",
            oidc_jwks_url="https://auth.argus.enterprise/.well-known/jwks.json",
            oidc_audience="argus-api-prod",
            oidc_algorithms=["RS256", "ES256"],
            secret_key="01234567890123456789012345678901",
            jwt_secret_key="98765432109876543210987654321098",
            cors_origins=["https://argus.enterprise", "https://app.argus.enterprise"]
        )
    )
    assert settings.is_production is True
    assert settings.security.oidc_enabled is True
