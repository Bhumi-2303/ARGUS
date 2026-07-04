"""Message signing utilities."""
import hmac
import hashlib
from typing import Optional
from argus.core.exceptions import SecurityError

def sign_message(message: str, key: str) -> str:
    """Sign a message using HMAC-SHA256."""
    if not message or not key:
        raise ValueError("Message and key must be provided")
        
    hmac_obj = hmac.new(
        key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    )
    return hmac_obj.hexdigest()

def verify_signature(message: str, signature: str, key: str) -> bool:
    """Verify a HMAC-SHA256 signature."""
    try:
        expected_signature = sign_message(message, key)
        return hmac.compare_digest(expected_signature, signature)
    except Exception:
        return False
