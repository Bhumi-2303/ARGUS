"""Enterprise OIDC/OAuth2 JWT Validator.

Enforces signature verification, claim validation, asymmetric algorithm allowlists,
and prevention of algorithm confusion.
"""

from typing import List, Set, Optional, Dict, Any
import jwt
from jwt.exceptions import (
    PyJWTError,
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidIssuerError,
    InvalidAudienceError,
    InvalidAlgorithmError,
)
from fastapi import HTTPException, status
from structlog import get_logger

from configs.settings import get_settings
from argus.auth.models import UserPrincipal
from argus.auth.jwks import JWKSClient

logger = get_logger("argus.auth.jwt")

# Default role -> permissions mapping
DEFAULT_ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "admin": {
        "read:domains",
        "read:models",
        "read:results",
        "run:prediction",
        "run:explanation",
        "run:onboarding",
        "read:telemetry",
        "read:agent-topology",
        "run:agent-trace",
        "read:monitoring",
        "read:incidents",
        "write:incidents",
        "approve:response",
        "admin:system",
    },
    "operator": {
        "read:domains",
        "read:models",
        "read:results",
        "run:prediction",
        "run:explanation",
        "run:onboarding",
        "read:telemetry",
        "read:agent-topology",
        "run:agent-trace",
        "read:monitoring",
        "read:incidents",
        "write:incidents",
        "approve:response",
    },
    "analyst": {
        "read:domains",
        "read:models",
        "read:results",
        "run:prediction",
        "run:explanation",
        "read:telemetry",
        "read:agent-topology",
        "run:agent-trace",
        "read:monitoring",
        "read:incidents",
    },
    "viewer": {
        "read:domains",
        "read:models",
        "read:results",
        "read:telemetry",
        "read:agent-topology",
        "read:monitoring",
        "read:incidents",
    },
}


class JWTValidator:
    """Validator for incoming bearer tokens via OIDC/JWKS or development signatures."""

    def __init__(self, jwks_client: Optional[JWKSClient] = None):
        self.settings = get_settings()
        self.jwks_client = jwks_client or JWKSClient(
            jwks_url=self.settings.security.oidc_jwks_url,
            cache_ttl_seconds=self.settings.security.oidc_jwks_cache_ttl_seconds,
            timeout_seconds=self.settings.security.oidc_jwks_timeout_seconds,
        )

    async def validate_token(self, token: str) -> UserPrincipal:
        """Validate JWT signature and claims, returning authenticated UserPrincipal.
        
        Raises:
            HTTPException: 401 Unauthorized on invalid, expired, or untrusted token.
        """
        if not token or not token.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token is missing.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = token.strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        # In production mode: MUST use real OIDC/JWKS asymmetric validation
        if self.settings.is_production or self.settings.security.oidc_enabled:
            return await self._validate_oidc_jwt(token)

        # In development mode without OIDC: support dev tokens or fallback
        return self._validate_dev_jwt(token)

    async def _validate_oidc_jwt(self, token: str) -> UserPrincipal:
        """Asymmetric OIDC JWT validation against remote JWKS."""
        try:
            # 1. Inspect unverified headers to extract kid and alg
            unverified_headers = jwt.get_unverified_header(token)
            alg = unverified_headers.get("alg")
            kid = unverified_headers.get("kid")

            if not alg:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token header: 'alg' header missing.",
                    headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
                )

            # 2. Prevent algorithm confusion: strictly verify against allowed asymmetric algorithms
            allowed_algs = [a.upper() for a in self.settings.security.oidc_algorithms]
            if alg.upper() not in allowed_algs or alg.lower() in ("none", "hs256", "hs384", "hs512"):
                logger.warning("unsupported_jwt_algorithm_attempted", algorithm=alg, allowed=allowed_algs)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Unsupported token algorithm '{alg}'.",
                    headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
                )

            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token header: 'kid' (key ID) missing.",
                    headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
                )

            # 3. Lookup signing key in JWKS cache / refresh
            key = await self.jwks_client.get_key_for_kid(kid)
            if not key:
                logger.warning("jwks_key_not_found", kid=kid)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Signing key not found in identity provider JWKS.",
                    headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
                )

            # 4. Decode and verify signature, issuer, audience, and exp
            payload = jwt.decode(
                token,
                key=key,
                algorithms=[alg],
                issuer=self.settings.security.oidc_issuer,
                audience=self.settings.security.oidc_audience,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "verify_aud": True,
                    "require": ["exp", "iss", "sub"],
                },
            )

            # 5. Extract principal identity, roles, and permissions
            return self._build_principal_from_claims(payload)

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\", error_description=\"Token expired\""},
            )
        except InvalidIssuerError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token issuer does not match expected identity provider.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
            )
        except InvalidAudienceError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token audience does not match ARGUS API audience.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
            )
        except InvalidSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token signature verification failed.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
            )
        except InvalidAlgorithmError as iae:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Disallowed algorithm: {str(iae)}",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
            )
        except HTTPException:
            raise
        except PyJWTError as e:
            logger.warning("jwt_validation_error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
            )

    def _validate_dev_jwt(self, token: str) -> UserPrincipal:
        """Validate development token signed with dev secret or return parsed claims."""
        try:
            # First try symmetric validation with dev secret
            payload = jwt.decode(
                token,
                key=self.settings.security.jwt_secret_key,
                algorithms=[self.settings.security.jwt_algorithm],
                options={"verify_exp": True},
            )
            return self._build_principal_from_claims(payload)
        except Exception as e:
            logger.debug("dev_jwt_validation_failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid development token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _build_principal_from_claims(self, claims: Dict[str, Any]) -> UserPrincipal:
        """Extract roles and permissions from standard claims mapping."""
        sub = str(claims.get("sub", "unknown"))
        iss = str(claims.get("iss", "unknown"))
        email = claims.get("email")
        client_id = claims.get("client_id") or claims.get("azp")

        # Extract roles from standard JWT claim locations
        roles: List[str] = []
        if isinstance(claims.get("roles"), list):
            roles.extend([str(r).lower() for r in claims["roles"]])
        if isinstance(claims.get("groups"), list):
            roles.extend([str(g).lower() for g in claims["groups"]])
        if isinstance(claims.get("realm_access", {}).get("roles"), list):
            roles.extend([str(r).lower() for r in claims["realm_access"]["roles"]])

        # Extract permissions
        permissions: Set[str] = set()
        if isinstance(claims.get("permissions"), list):
            permissions.update([str(p) for p in claims["permissions"]])
        if isinstance(claims.get("scope"), str):
            permissions.update(claims["scope"].split())
        elif isinstance(claims.get("scp"), list):
            permissions.update([str(p) for p in claims["scp"]])

        # Map assigned roles to permissions
        for role in roles:
            if role in DEFAULT_ROLE_PERMISSIONS:
                permissions.update(DEFAULT_ROLE_PERMISSIONS[role])

        return UserPrincipal(
            sub=sub,
            issuer=iss,
            roles=roles,
            permissions=permissions,
            email=email,
            client_id=client_id,
            claims=claims,
            is_authenticated=True,
        )


# Global validator instance
jwt_validator = JWTValidator()
