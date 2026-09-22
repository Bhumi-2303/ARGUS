import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from argus.security.jwks import JWKSCache
from argus.security.sink import AuditSink
from argus.security.audit import SecurityAuditEvent

@pytest.mark.asyncio
async def test_jwks_cache_hit_and_miss():
    jwks = JWKSCache(jwks_url="http://fake-jwks", cache_ttl_seconds=3600)
    
    # Mock httpx response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "keys": [{"kid": "test-kid", "kty": "RSA"}]
    }
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        
        # 1. Miss, triggers refresh
        key1 = await jwks.get_key("test-kid")
        assert key1 == {"kid": "test-kid", "kty": "RSA"}
        assert mock_get.call_count == 1
        
        # 2. Hit, no refresh
        key2 = await jwks.get_key("test-kid")
        assert key2 == {"kid": "test-kid", "kty": "RSA"}
        assert mock_get.call_count == 1

@pytest.mark.asyncio
async def test_jwks_refresh_on_unknown_kid():
    jwks = JWKSCache(jwks_url="http://fake-jwks", cache_ttl_seconds=3600)
    
    # Pre-populate cache
    jwks._cache = {"old-kid": {"kid": "old-kid"}}
    jwks._last_fetch_time = __import__("time").time()
    
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "keys": [{"kid": "old-kid"}, {"kid": "new-kid"}]
    }
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        
        # Requesting unknown kid forces a refresh despite valid TTL
        key = await jwks.get_key("new-kid")
        assert key == {"kid": "new-kid"}
        assert mock_get.call_count == 1

@pytest.mark.asyncio
async def test_jwks_failure_semantics():
    jwks = JWKSCache(jwks_url="http://fake-jwks", cache_ttl_seconds=3600)
    
    # Network failure
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Network down")
        key = await jwks.get_key("test-kid")
        assert key is None # Should not crash, just returns None causing auth failure

@pytest.mark.asyncio
async def test_siem_reliable_delivery():
    event = SecurityAuditEvent(actor_id="test", action="TEST", resource="test", outcome="SUCCESS")
    
    # Simulate SIEM 500 then 200
    mock_response_500 = MagicMock()
    mock_response_500.status_code = 500
    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = [mock_response_500, mock_response_200]
        
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await AuditSink._reliable_send_to_siem(event.model_dump(), "http://siem", 3)
            
            assert mock_post.call_count == 2
            assert mock_sleep.call_count == 1 # Slept once between retries
