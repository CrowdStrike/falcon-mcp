"""
Authentication middleware for Falcon MCP Server HTTP transports.

This module provides API key authentication middleware for HTTP-based
transports (SSE, streamable-http).
"""

from starlette.requests import Request
from starlette.responses import JSONResponse


def auth_middleware(app, api_key: str):
    """Wrap an ASGI app with API key authentication.

    Args:
        app: The ASGI application to wrap
        api_key: The expected API key value

    Returns:
        ASGI app that validates x-api-key header before passing to wrapped app
    """

    async def middleware(scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope)
            if request.headers.get("x-api-key") != api_key:
                response = JSONResponse({"error": "Unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return
        await app(scope, receive, send)

    return middleware
