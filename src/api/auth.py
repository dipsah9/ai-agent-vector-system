"""
JWT authentication middleware for the RAG service.

Verifies tokens issued by the EvoFarm Go API. The JWT_SECRET must
match the one used by the EvoFarm API for tokens to validate.
"""
import logging
from typing import Optional

import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import settings

logger = logging.getLogger(__name__)

# Endpoints that don't require authentication
PUBLIC_PATHS = (
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/metrics",
)


class JWTMiddleware(BaseHTTPMiddleware):
    """
    Middleware that verifies the Authorization header on protected routes.

    Adds the decoded JWT claims to `request.state.user` for downstream use.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow public paths
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        # Extract token
        auth_header: Optional[str] = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing authentication token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header[len("Bearer "):].strip()

        # Verify token
        if not settings.jwt_secret:
            logger.error("JWT_SECRET is not set — cannot verify tokens")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Server misconfigured: JWT_SECRET not set"},
            )

        try:
            claims = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=["HS256"],
            )
            # Attach claims to request state for routes that want them
            request.state.user = claims
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token expired"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)