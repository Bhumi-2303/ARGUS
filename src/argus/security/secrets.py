"""Secret management utility."""
import os
from typing import Optional
import structlog
from argus.core.exceptions import SecurityError

logger = structlog.get_logger("argus.security.secrets")

class SecretManager:
    """Manages secure access to secrets and keys."""
    
    @staticmethod
    def get_secret(name: str) -> Optional[str]:
        """Get a secret by name."""
        return os.environ.get(name)
        
    @staticmethod
    def validate_secrets(required_secrets: list[str]) -> bool:
        """Validate that all required secrets are present."""
        missing = [secret for secret in required_secrets if not os.environ.get(secret)]
        if missing:
            logger.error("missing_required_secrets", missing=missing)
            return False
        return True
        
    @staticmethod
    def mask_secret(value: str) -> str:
        """Mask a secret value for logging."""
        if not value:
            return ""
        if len(value) <= 4:
            return "****"
        return f"{value[:2]}****{value[-2:]}"
