"""Input and output validation utilities."""
import re
from typing import Any, Dict
from fastapi import HTTPException, status
from argus.core.exceptions import ValidationError


def validate_payload_size(payload: bytes, max_bytes: int = 1048576) -> bool: # Default 1MB
    """Validate that a payload does not exceed the maximum allowed size."""
    if len(payload) > max_bytes:
        raise ValidationError(f"Payload size {len(payload)} exceeds maximum allowed {max_bytes} bytes")
    return True


def sanitize_input(text: str) -> str:
    """Basic sanitization of input text to prevent XSS/injection."""
    if not isinstance(text, str):
        return text
    # Remove null bytes
    text = text.replace("\x00", "")
    # Basic HTML tag stripping
    text = re.sub(r'<[^>]*>', '', text)
    return text


def validate_content_type(content_type: str, allowed_types: list[str]) -> bool:
    """Validate that the content type is allowed."""
    if not content_type:
        return False
        
    base_type = content_type.split(';')[0].strip().lower()
    if base_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported media type. Allowed types: {', '.join(allowed_types)}"
        )
    return True
