"""Tests for OIDC/JWKS JWT validation and prevention of algorithm confusion."""

import time
import json
import pytest
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException

from configs.settings import get_settings
from argus.auth.jwks import JWKSClient
from argus.auth.jwt import JWTValidator


@pytest.fixture(scope="module")
def rsa_keypair():
    """Generate RSA keypair and matching JWK for testing."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    jwk_dict = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(public_key))
    jwk_dict["kid"] = "argus-test-key-01"
    jwk_dict["alg"] = "RS256"

    return {
        "private_key": private_key,
        "public_key": public_key,
        "jwk": jwk_dict,
        "kid": "argus-test-key-01",
        "issuer": "https://auth.argus.enterprise",
        "audience": "argus-api-prod"
    }


@pytest.fixture
def mock_jwks_client(rsa_keypair):
    """JWKS client preloaded with test public key in cache."""
    client = JWKSClient(
        jwks_url="https://auth.argus.enterprise/.well-known/jwks.json",
        cache_ttl_seconds=3600
    )
    # Pre-populate cache directly with test public key
    client._keys[rsa_keypair["kid"]] = rsa_keypair["public_key"]
    client._last_fetch_time = time.time()
    return client


@pytest.fixture
def validator(mock_jwks_client, rsa_keypair, monkeypatch):
    """JWTValidator configured with mock JWKS client and test OIDC settings."""
    settings = get_settings()
    monkeypatch.setattr(settings.security, "oidc_enabled", True)
    monkeypatch.setattr(settings.security, "oidc_issuer", rsa_keypair["issuer"])
    monkeypatch.setattr(settings.security, "oidc_audience", rsa_keypair["audience"])
    monkeypatch.setattr(settings.security, "oidc_algorithms", ["RS256", "ES256"])

    val = JWTValidator(jwks_client=mock_jwks_client)
    val.settings = settings
    return val


@pytest.mark.asyncio
async def test_valid_oidc_jwt(validator, rsa_keypair):
    """Valid RSA token signed by trusted key is accepted and builds principal."""
    now = int(time.time())
    payload = {
        "sub": "sec-operator-01",
        "iss": rsa_keypair["issuer"],
        "aud": rsa_keypair["audience"],
        "exp": now + 3600,
        "nbf": now - 10,
        "iat": now,
        "roles": ["operator"],
        "permissions": ["run:prediction", "approve:response"]
    }
    token = jwt.encode(
        payload,
        rsa_keypair["private_key"],
        algorithm="RS256",
        headers={"kid": rsa_keypair["kid"]}
    )

    principal = await validator.validate_token(f"Bearer {token}")
    assert principal.sub == "sec-operator-01"
    assert principal.is_authenticated is True
    assert "operator" in principal.roles
    assert principal.has_permission("run:prediction") is True
    assert principal.has_permission("approve:response") is True


@pytest.mark.asyncio
async def test_missing_token_rejected(validator):
    """Empty or missing token must be rejected with 401."""
    with pytest.raises(HTTPException) as exc:
        await validator.validate_token("")
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_malformed_token_rejected(validator):
    """Malformed token string must be rejected with 401."""
    with pytest.raises(HTTPException) as exc:
        await validator.validate_token("Bearer not-a-valid-jwt-token")
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_expired_token_rejected(validator, rsa_keypair):
    """Expired token must be rejected with 401."""
    now = int(time.time())
    payload = {
        "sub": "user-expired",
        "iss": rsa_keypair["issuer"],
        "aud": rsa_keypair["audience"],
        "exp": now - 300,  # Expired 5 minutes ago
        "iat": now - 600
    }
    token = jwt.encode(
        payload,
        rsa_keypair["private_key"],
        algorithm="RS256",
        headers={"kid": rsa_keypair["kid"]}
    )

    with pytest.raises(HTTPException) as exc:
        await validator.validate_token(token)
    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_invalid_signature_rejected(validator, rsa_keypair):
    """Token signed by an untrusted key must be rejected with 401."""
    untrusted_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = int(time.time())
    payload = {
        "sub": "attacker",
        "iss": rsa_keypair["issuer"],
        "aud": rsa_keypair["audience"],
        "exp": now + 3600
    }
    token = jwt.encode(
        payload,
        untrusted_key,
        algorithm="RS256",
        headers={"kid": rsa_keypair["kid"]}  # Presenting valid kid with forged signature
    )

    with pytest.raises(HTTPException) as exc:
        await validator.validate_token(token)
    assert exc.value.status_code == 401
    assert "signature" in exc.value.detail.lower() or "validation failed" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_wrong_issuer_rejected(validator, rsa_keypair):
    """Token from wrong issuer must be rejected with 401."""
    now = int(time.time())
    payload = {
        "sub": "user-wrong-iss",
        "iss": "https://rogue-idp.example.com",
        "aud": rsa_keypair["audience"],
        "exp": now + 3600
    }
    token = jwt.encode(
        payload,
        rsa_keypair["private_key"],
        algorithm="RS256",
        headers={"kid": rsa_keypair["kid"]}
    )

    with pytest.raises(HTTPException) as exc:
        await validator.validate_token(token)
    assert exc.value.status_code == 401
    assert "issuer" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_wrong_audience_rejected(validator, rsa_keypair):
    """Token with wrong audience must be rejected with 401."""
    now = int(time.time())
    payload = {
        "sub": "user-wrong-aud",
        "iss": rsa_keypair["issuer"],
        "aud": "different-client-id",
        "exp": now + 3600
    }
    token = jwt.encode(
        payload,
        rsa_keypair["private_key"],
        algorithm="RS256",
        headers={"kid": rsa_keypair["kid"]}
    )

    with pytest.raises(HTTPException) as exc:
        await validator.validate_token(token)
    assert exc.value.status_code == 401
    assert "audience" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_algorithm_confusion_none_rejected(validator, rsa_keypair):
    """Token with algorithm 'none' must be rejected with 401."""
    now = int(time.time())
    payload = {
        "sub": "attacker",
        "iss": rsa_keypair["issuer"],
        "aud": rsa_keypair["audience"],
        "exp": now + 3600
    }
    token = jwt.encode(
        payload,
        key="",
        algorithm="none",
        headers={"kid": rsa_keypair["kid"]}
    )

    with pytest.raises(HTTPException) as exc:
        await validator.validate_token(token)
    assert exc.value.status_code == 401
    assert "unsupported" in exc.value.detail.lower() or "disallowed" in exc.value.detail.lower() or "algorithm" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_algorithm_confusion_hs256_rejected(validator, rsa_keypair):
    """Token attempting HMAC algorithm confusion with symmetric secret must be rejected."""
    now = int(time.time())
    payload = {
        "sub": "attacker",
        "iss": rsa_keypair["issuer"],
        "aud": rsa_keypair["audience"],
        "exp": now + 3600
    }
    # Attacker tries signing with HMAC using arbitrary secret
    token = jwt.encode(
        payload,
        key="attacker-arbitrary-symmetric-key",
        algorithm="HS256",
        headers={"kid": rsa_keypair["kid"]}
    )

    with pytest.raises(HTTPException) as exc:
        await validator.validate_token(token)
    assert exc.value.status_code == 401
    assert "unsupported" in exc.value.detail.lower() or "algorithm" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_missing_kid_rejected(validator, rsa_keypair):
    """Token missing 'kid' header must be rejected."""
    now = int(time.time())
    payload = {
        "sub": "user-no-kid",
        "iss": rsa_keypair["issuer"],
        "aud": rsa_keypair["audience"],
        "exp": now + 3600
    }
    token = jwt.encode(
        payload,
        rsa_keypair["private_key"],
        algorithm="RS256"
        # Omits kid header
    )

    with pytest.raises(HTTPException) as exc:
        await validator.validate_token(token)
    assert exc.value.status_code == 401
    assert "kid" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_unknown_kid_rejected(validator, rsa_keypair):
    """Token with an unknown kid not found in JWKS must be rejected."""
    now = int(time.time())
    payload = {
        "sub": "user-unknown-kid",
        "iss": rsa_keypair["issuer"],
        "aud": rsa_keypair["audience"],
        "exp": now + 3600
    }
    token = jwt.encode(
        payload,
        rsa_keypair["private_key"],
        algorithm="RS256",
        headers={"kid": "unknown-nonexistent-key-999"}
    )

    with pytest.raises(HTTPException) as exc:
        await validator.validate_token(token)
    assert exc.value.status_code == 401
    assert "signing key not found" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_jwks_outage_fails_closed():
    """When JWKS endpoint is unreachable and key is not cached, verification fails closed."""
    client = JWKSClient(
        jwks_url="https://unreachable.invalid:9999/.well-known/jwks.json",
        timeout_seconds=0.1
    )
    val = JWTValidator(jwks_client=client)

    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6InVua25vd24ifQ.eyJzdWIiOiIxMjMifQ.c2ln"
    with pytest.raises(HTTPException) as exc:
        await val.validate_token(token)
    assert exc.value.status_code == 401
