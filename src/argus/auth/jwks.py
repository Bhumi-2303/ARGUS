"""Resilient, non-blocking JWKS Client with caching and key rotation."""

import time
import asyncio
from typing import Dict, Any, Optional
import httpx
import jwt
from structlog import get_logger

logger = get_logger("argus.auth.jwks")


class JWKSClient:
    """Provider-neutral JWKS client with thread-safe caching and failure isolation."""

    def __init__(
        self,
        jwks_url: str,
        cache_ttl_seconds: int = 3600,
        timeout_seconds: float = 5.0,
        min_refresh_interval_seconds: float = 10.0
    ):
        self.jwks_url = jwks_url
        self.cache_ttl_seconds = cache_ttl_seconds
        self.timeout_seconds = timeout_seconds
        self.min_refresh_interval_seconds = min_refresh_interval_seconds

        self._keys: Dict[str, Any] = {}  # kid -> cryptography public key
        self._last_fetch_time: float = 0.0
        self._lock = asyncio.Lock()

    async def get_key_for_kid(self, kid: str) -> Optional[Any]:
        """Retrieve signing key by key ID (kid), refreshing cache if expired or missing."""
        now = time.time()

        # Check existing cache
        if kid in self._keys and (now - self._last_fetch_time) < self.cache_ttl_seconds:
            return self._keys[kid]

        # Acquire lock to refresh JWKS safely without duplicate network calls
        async with self._lock:
            # Recheck cache inside lock
            if kid in self._keys and (now - self._last_fetch_time) < self.cache_ttl_seconds:
                return self._keys[kid]

            # Enforce minimum refresh interval to prevent DoS from rotating unknown kids
            if (now - self._last_fetch_time) < self.min_refresh_interval_seconds and self._keys:
                logger.warning(
                    "jwks_refresh_rate_limited",
                    kid=kid,
                    elapsed=now - self._last_fetch_time,
                    min_interval=self.min_refresh_interval_seconds
                )
                return self._keys.get(kid)

            # Perform HTTP fetch
            await self._fetch_jwks()
            return self._keys.get(kid)

    async def _fetch_jwks(self) -> None:
        """Fetch JWKS keys from remote identity provider with timeout and failure isolation."""
        if not self.jwks_url:
            logger.error("jwks_url_empty")
            return

        try:
            logger.info("fetching_jwks_keys", url=self.jwks_url)
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(self.jwks_url)
                if response.status_code != 200:
                    logger.error(
                        "jwks_fetch_failed",
                        status_code=response.status_code,
                        url=self.jwks_url
                    )
                    return

                jwks_data = response.json()
                keys_data = jwks_data.get("keys", [])

                new_keys = {}
                for k in keys_data:
                    k_id = k.get("kid")
                    if not k_id:
                        continue
                    try:
                        pyjwk = jwt.PyJWK.from_dict(k)
                        new_keys[k_id] = pyjwk.key
                    except Exception as parse_err:
                        logger.warning("jwk_key_parse_failed", kid=k_id, error=str(parse_err))

                if new_keys:
                    self._keys = new_keys
                    self._last_fetch_time = time.time()
                    logger.info("jwks_keys_updated", total_keys=len(self._keys))
                else:
                    logger.warning("jwks_response_contained_no_valid_keys", url=self.jwks_url)

        except Exception as e:
            # Isolate failure: do not crash the application, fail closed on token verification
            logger.error("jwks_fetch_network_error", url=self.jwks_url, error=str(e))
