"""
JWT authentication middleware for the RAG service.

Verifies tokens issued by the EvoFarm Go API. The JWT_SECRET must
match the one used by the EvoFarm API for tokens to validate.

Implemented as a pure ASGI middleware so it composes correctly with
CORSMiddleware (BaseHTTPMiddleware can swallow preflight responses).
"""
import logging
from typing import Optional

import jwt
from fastapi import Request, status
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

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


class JWTMiddleware:
    """
    Pure ASGI middleware that verifies the Authorization header
    on protected routes.

    Adds the decoded JWT claims to the ASGI scope for downstream use.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = request.url.path

        # Allow public paths
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            await self.app(scope, receive, send)
            return

        # Allow CORS preflight (OPTIONS requests never carry Authorization)
        if request.method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        # Extract token
        auth_header: Optional[str] = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing authentication token"},
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return

        token = auth_header[len("Bearer "):].strip()

        # Verify token
        if not settings.jwt_secret:
            logger.error("JWT_SECRET is not set — cannot verify tokens")
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Server misconfigured: JWT_SECRET not set"},
            )
            await response(scope, receive, send)
            return

        try:
            claims = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=["HS256"],
            )
            # Attach claims to scope for downstream routes
            scope["state"] = scope.get("state", {})
            scope["state"]["user"] = claims
        except jwt.ExpiredSignatureError:
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token expired"},
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT: {e}")
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)