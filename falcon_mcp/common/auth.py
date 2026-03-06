"""ASGI middleware for Falcon MCP Server HTTP transports."""

import secrets
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from falcon_mcp.common.logging import get_logger

# ASGI type aliases - using MutableMapping for Starlette compatibility
Scope = MutableMapping[str, Any]
ASGIReceive = Callable[[], Awaitable[MutableMapping[str, Any]]]
ASGISend = Callable[[MutableMapping[str, Any]], Awaitable[None]]
ASGIApp = Callable[[Scope, ASGIReceive, ASGISend], Awaitable[None]]


def strip_trailing_slash_middleware(app: ASGIApp) -> ASGIApp:
    """Strip trailing slashes from HTTP request paths.

    Args:
        app: The ASGI application to wrap

    Returns:
        ASGI app that normalizes paths by removing trailing slashes
    """

    async def middleware(scope: Scope, receive: ASGIReceive, send: ASGISend) -> None:
        if scope["type"] == "http":
            path: str = scope["path"]
            if path != "/" and path.endswith("/"):
                scope["path"] = path.rstrip("/")
                if "raw_path" in scope and isinstance(scope["raw_path"], bytes):
                    raw = scope["raw_path"]
                    scope["raw_path"] = raw.rstrip(b"/") or b"/"
        await app(scope, receive, send)

    return middleware


def normalize_content_type_middleware(app: ASGIApp) -> ASGIApp:
    """Normalize ``application/json-rpc`` to ``application/json`` in HTTP request headers.

    Args:
        app: The ASGI application to wrap

    Returns:
        ASGI app that normalizes Content-Type headers
    """
    ct_logger = get_logger("falcon_mcp.content_type")

    async def middleware(scope: Scope, receive: ASGIReceive, send: ASGISend) -> None:
        if scope["type"] == "http":
            headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
            new_headers: list[tuple[bytes, bytes]] = []
            for name, value in headers:
                if name == b"content-type":
                    decoded = value.decode("utf-8")
                    if decoded.lower().startswith("application/json-rpc"):
                        # Replace only the media type, keep params (e.g. "; charset=utf-8")
                        rest = decoded[len("application/json-rpc"):]
                        new_value = f"application/json{rest}"
                        ct_logger.debug(
                            "Normalized Content-Type: %s -> %s", decoded, new_value
                        )
                        value = new_value.encode("utf-8")
                new_headers.append((name, value))
            scope["headers"] = new_headers
        await app(scope, receive, send)

    return middleware


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
