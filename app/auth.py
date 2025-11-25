"""OpenID Connect authentication for FastAPI."""

import logging
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class OIDCSettings(BaseSettings):
    """OIDC Configuration from environment variables."""
    provider_url: str
    audience: str
    issuer: str | None = None

    class Config:
        env_prefix = "OIDC_"

    def __init__(self, **data):
        super().__init__(**data)
        # Default issuer to provider_url if not specified
        if not self.issuer:
            self.issuer = self.provider_url.rstrip('/')
        self.well_known_url = f"{self.provider_url.rstrip('/')}/.well-known/openid-configuration"


# Global cache for JWKS
_jwks_cache: dict | None = None


async def get_jwks() -> dict:
    """Fetch and cache JWKS from the OIDC provider."""
    global _jwks_cache

    if _jwks_cache is not None:
        return _jwks_cache

    try:
        settings = OIDCSettings()
        
        async with httpx.AsyncClient() as client:
            # Get well-known configuration
            well_known_resp = await client.get(
                settings.well_known_url,
                timeout=10.0
            )
            well_known_resp.raise_for_status()
            well_known = well_known_resp.json()
            
            # Get JWKS
            jwks_uri = well_known.get("jwks_uri")
            if not jwks_uri:
                raise ValueError("JWKS URI not found in well-known configuration")
            
            jwks_resp = await client.get(jwks_uri, timeout=10.0)
            jwks_resp.raise_for_status()
            _jwks_cache = jwks_resp.json()
            return _jwks_cache
            
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OIDC provider unavailable"
        )


async def get_current_user(
    credentials: Annotated[HTTPAuthCredentials, Depends(security)]
) -> dict:
    """
    Validate the JWT token and return the user claims.
    
    This dependency can be used on any route that requires authentication.
    Use it as: `user: Annotated[dict, Depends(get_current_user)]`
    """
    try:
        settings = OIDCSettings()
        token = credentials.credentials
        
        # Get JWKS for verification
        jwks = await get_jwks()
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.audience,
            issuer=settings.issuer,
            options={"verify_signature": True}
        )
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
