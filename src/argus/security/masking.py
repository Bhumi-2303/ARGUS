"""Data masking utility."""
import re
from typing import Any, Dict

# Default patterns to mask (passwords, tokens, API keys)
DEFAULT_PATTERNS = [
    r"(?i)password[=:]\s*([^\s,]+)",
    r"(?i)token[=:]\s*([^\s,]+)",
    r"(?i)api_?key[=:]\s*([^\s,]+)",
    r"(?i)secret[=:]\s*([^\s,]+)",
    r"Bearer\s+([A-Za-z0-9\-\._~\+\/]+=*)"
]

def mask_sensitive_data(data: str, patterns: list[str] = DEFAULT_PATTERNS) -> str:
    """Mask sensitive information in a string using regex patterns."""
    masked_data = str(data)
    for pattern in patterns:
        def replace(match):
            full_match = match.group(0)
            secret = match.group(1)
            return full_match.replace(secret, "****")
            
        masked_data = re.sub(pattern, replace, masked_data)
        
    return masked_data
