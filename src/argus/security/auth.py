"""Authentication service using JWT."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from structlog import get_logger

from argus.schemas.security import TokenPayload
from config.settings import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = get_logger("argus.security.auth")


def create_access_token(subject: str, role: str) -> str:
    """Create a new JWT access token."""
    settings = get_settings().security
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry_minutes)
    to_encode = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> TokenPayload:
    """Verify a JWT token and extract payload."""
    settings = get_settings().security
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        role = payload.get("role")
        if sub is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenPayload(**payload)
    except JWTError as e:
        logger.warning("token_validation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """FastAPI dependency to get the current authenticated user/agent."""
    return verify_token(token)
