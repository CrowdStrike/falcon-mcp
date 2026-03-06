"""
Tests for the trailing slash stripping ASGI middleware.

These tests verify that strip_trailing_slash_middleware correctly normalizes
request paths to prevent Starlette's Router from issuing 307 redirects when
clients send requests with trailing slashes (e.g. /mcp/ instead of /mcp).
"""

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from falcon_mcp.common.auth import (
    ASGIApp,
    normalize_content_type_middleware,
    strip_trailing_slash_middleware,
)


def _echo_handler(request: Request) -> JSONResponse:
    """Echo handler that returns request details for verification."""
    return JSONResponse({
        "path": request.url.path,
        "method": request.method,
        "query": str(request.query_params),
    })


async def _async_echo_handler(request: Request) -> JSONResponse:
    """Async echo handler that reads and returns the POST body."""
    body = await request.body()
    return JSONResponse({
        "path": request.url.path,
        "body": body.decode("utf-8"),
        "content_type": request.headers.get("content-type", ""),
    })


def _make_app(use_middleware: bool = True) -> Starlette | ASGIApp:
    """Create a Starlette app with a /mcp route, optionally wrapped with middleware."""
    app = Starlette(
        routes=[
            Route("/mcp", _echo_handler, methods=["GET", "POST"]),
            Route("/mcp/post", _async_echo_handler, methods=["POST"]),
            Route("/", _echo_handler, methods=["GET"]),
        ],
    )
    if use_middleware:
        return strip_trailing_slash_middleware(app)
    return app


class TestTrailingSlashRedirectProblem:
    """Confirm the 307 redirect behavior without middleware."""

    def test_trailing_slash_redirects_without_middleware(self):
        """Without middleware, /mcp/ returns a 307 redirect to /mcp."""
        app = _make_app(use_middleware=False)
        client = TestClient(app, follow_redirects=False)
        response = client.get("/mcp/")
        assert response.status_code == 307

    def test_no_trailing_slash_works_without_middleware(self):
        """Without middleware, /mcp (no trailing slash) works normally."""
        app = _make_app(use_middleware=False)
        client = TestClient(app)
        response = client.get("/mcp")
        assert response.status_code == 200


class TestMiddlewareFixesRedirect:
    """Verify the middleware prevents 307 redirects."""

    def test_trailing_slash_returns_200_with_middleware(self):
        """/mcp/ returns 200 with middleware (no redirect)."""
        app = _make_app(use_middleware=True)
        client = TestClient(app)
        response = client.get("/mcp/")
        assert response.status_code == 200
        assert response.json()["path"] == "/mcp"

    def test_no_trailing_slash_still_works(self):
        """/mcp (no trailing slash) continues to work."""
        app = _make_app(use_middleware=True)
        client = TestClient(app)
        response = client.get("/mcp")
        assert response.status_code == 200
        assert response.json()["path"] == "/mcp"

    def test_post_body_preserved(self):
        """POST body is preserved through the middleware."""
        app = _make_app(use_middleware=True)
        client = TestClient(app)
        response = client.post(
            "/mcp/post/",
            content='{"jsonrpc":"2.0","method":"initialize","id":1}',
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["body"] == '{"jsonrpc":"2.0","method":"initialize","id":1}'
        assert data["content_type"] == "application/json"


class TestEdgeCases:
    """Test edge cases for the middleware."""

    def test_root_path_not_modified(self):
        """Root path / is not stripped."""
        app = _make_app(use_middleware=True)
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["path"] == "/"

    def test_multiple_trailing_slashes(self):
        """Multiple trailing slashes are all stripped."""
        app = _make_app(use_middleware=True)
        client = TestClient(app)
        response = client.get("/mcp///")
        assert response.status_code == 200
        assert response.json()["path"] == "/mcp"

    def test_query_params_preserved(self):
        """Query parameters are preserved through the middleware."""
        app = _make_app(use_middleware=True)
        client = TestClient(app)
        response = client.get("/mcp/?foo=bar&baz=1")
        assert response.status_code == 200
        data = response.json()
        assert data["path"] == "/mcp"
        assert "foo=bar" in data["query"]

    def test_non_http_scope_passthrough(self):
        """Non-HTTP scopes (e.g. lifespan) are passed through unchanged."""

        async def inner_app(scope, receive, send):
            """Track that the inner app was called."""
            inner_app.called = True
            inner_app.scope_type = scope["type"]

        inner_app.called = False
        inner_app.scope_type = None

        wrapped = strip_trailing_slash_middleware(inner_app)

        import asyncio

        scope = {"type": "lifespan", "path": "/should-not-be-touched/"}

        asyncio.run(wrapped(scope, None, None))

        assert inner_app.called is True
        # Path should not be modified for non-http scopes
        assert scope["path"] == "/should-not-be-touched/"

    def test_post_to_trailing_slash_returns_200(self):
        """POST to /mcp/ returns 200 (not 307 redirect losing the body)."""
        app = _make_app(use_middleware=True)
        client = TestClient(app, follow_redirects=False)
        response = client.post(
            "/mcp/",
            content='{"test": true}',
            headers={"Content-Type": "application/json"},
        )
        # Should be 200 (handled), not 307 (redirect)
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Content-Type normalization middleware tests
# ---------------------------------------------------------------------------


def _make_content_type_app() -> ASGIApp:
    """Create a Starlette app wrapped with content-type normalization middleware."""
    base_app = Starlette(
        routes=[
            Route("/mcp", _async_echo_handler, methods=["POST"]),
        ],
    )
    return normalize_content_type_middleware(base_app)


class TestContentTypeNormalization:
    """Verify that application/json-rpc is rewritten to application/json."""

    def test_json_rpc_rewritten_to_json(self):
        """application/json-rpc is rewritten to application/json."""
        app = _make_content_type_app()
        client = TestClient(app)
        response = client.post(
            "/mcp",
            content='{"method":"tools/call"}',
            headers={"Content-Type": "application/json-rpc"},
        )
        assert response.status_code == 200
        assert response.json()["content_type"] == "application/json"

    def test_json_rpc_with_charset_preserves_params(self):
        """application/json-rpc; charset=utf-8 becomes application/json; charset=utf-8."""
        app = _make_content_type_app()
        client = TestClient(app)
        response = client.post(
            "/mcp",
            content='{"method":"tools/call"}',
            headers={"Content-Type": "application/json-rpc; charset=utf-8"},
        )
        assert response.status_code == 200
        assert response.json()["content_type"] == "application/json; charset=utf-8"

    def test_plain_json_left_untouched(self):
        """application/json is left unchanged."""
        app = _make_content_type_app()
        client = TestClient(app)
        response = client.post(
            "/mcp",
            content='{"method":"initialize"}',
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200
        assert response.json()["content_type"] == "application/json"

    def test_missing_content_type_left_alone(self):
        """Requests without Content-Type header are passed through."""
        app = _make_content_type_app()
        client = TestClient(app)
        # Send a POST without explicitly setting Content-Type
        response = client.post("/mcp", content=b"raw-body")
        # The app should still receive the request (may get a default content-type
        # from the test client, but the middleware should not error)
        assert response.status_code == 200

    def test_non_http_scope_passthrough(self):
        """Non-HTTP scopes (e.g. lifespan) are passed through unchanged."""

        async def inner_app(scope, receive, send):
            inner_app.called = True
            inner_app.scope_type = scope["type"]

        inner_app.called = False
        inner_app.scope_type = None

        wrapped = normalize_content_type_middleware(inner_app)

        import asyncio

        scope = {"type": "lifespan"}

        asyncio.run(wrapped(scope, None, None))

        assert inner_app.called is True
        assert scope["type"] == "lifespan"
