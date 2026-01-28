"""
Authentication middleware for Falcon MCP Server HTTP transports.

This module provides API key authentication middleware for HTTP-based
transports (SSE, streamable-http).
"""

import secrets
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

# ASGI type aliases - using MutableMapping for Starlette compatibility
Scope = MutableMapping[str, Any]
ASGIReceive = Callable[[], Awaitable[MutableMapping[str, Any]]]
ASGISend = Callable[[MutableMapping[str, Any]], Awaitable[None]]
ASGIApp = Callable[[Scope, ASGIReceive, ASGISend], Awaitable[None]]


def auth_middleware(app: ASGIApp, api_key: str) -> ASGIApp:
    """Wrap an ASGI app with API key authentication.

    Args:
        app: The ASGI application to wrap
        api_key: The expected API key value

    Returns:
        ASGI app that validates x-api-key header before passing to wrapped app
    """

    async def middleware(scope: Scope, receive: ASGIReceive, send: ASGISend) -> None:
        if scope["type"] == "http":
            request = Request(scope)
            provided_key = request.headers.get("x-api-key", "")
            if not secrets.compare_digest(provided_key, api_key):
                response = JSONResponse({"error": "Unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return
        await app(scope, receive, send)

    return middleware
