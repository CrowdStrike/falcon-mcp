"""
Centralized constants for Falcon MCP.
"""

# Common error codes and their meanings
ERROR_CODE_DESCRIPTIONS = {
    403: "Permission denied. The API credentials don't have the required access.",
    401: "Authentication failed. The API credentials are invalid or expired.",
    404: "Resource not found. The requested resource does not exist.",
    429: "Rate limit exceeded. Too many requests in a short period.",
    500: "Server error. An unexpected error occurred on the server.",
    503: "Service unavailable. The service is temporarily unavailable.",
}


class SearchLimits:
    """Constants for search and pagination limits."""
    DEFAULT = 10
    DEFAULT_DISCOVER = 100
    MAX_DETECTIONS = 9999
    MAX_HOSTS = 5000
    MAX_INCIDENTS = 500
    MAX_CLOUD_SCORE = 2500
    MAX_DISCOVER_APPS = 1000
    MAX_INTEL = 5000
    MAX_SPOTLIGHT = 5000
    MAX_IDP_RESULTS = 200
    MAX_IDP_RELATIONSHIPS = 3
    DEFAULT_IDP_RELATIONSHIPS = 2


class GraphQLDefaults:
    """Default values for GraphQL query parameters."""
    FIRST_INCIDENTS = 10
    FIRST_ENTITIES_BATCH = 50
    DEFAULT_TIMELINE_LIMIT = 50
    DEFAULT_RELATIONSHIP_LIMIT = 50


class ServerDefaults:
    """Server-level configuration constants."""
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 8000
    DEFAULT_TRANSPORT = "stdio"
    CORE_TOOLS_COUNT = 3


class TransportTypes:
    """Transport protocol identifiers."""
    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable-http"
