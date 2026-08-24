"""
Base module for Falcon MCP Server

This module provides the base class for all Falcon MCP server modules.
"""

from abc import ABC, abstractmethod
from functools import partial, wraps
from inspect import iscoroutinefunction
from typing import Any, Callable

import anyio
from mcp import Resource
from mcp.server import FastMCP
from mcp.types import ToolAnnotations

from falcon_mcp.client import FalconClient
from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import filter_none_values, prepare_api_parameters

logger = get_logger(__name__)

# Default: read-only tool that talks to an external API
READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


def offload_to_thread(method: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap a sync tool handler so it runs on a worker thread, not the event loop.

    Falcon tool handlers are synchronous and call blocking, `requests`-based
    FalconPy. Run inline on the asyncio loop, one ~6s Falcon call freezes the loop
    and serializes every other in-flight request. Wrapping the handler in an
    `async def` that offloads via `anyio.to_thread.run_sync` lets a single
    server instance interleave concurrent Falcon calls.

    FastMCP builds each tool's arg schema with `inspect.signature` (which follows
    `functools.wraps`' `__wrapped__`), so the wrapper exposes the original
    handler's `Field(...)` parameters unchanged; but it detects async by
    inspecting the object directly (not `__wrapped__`), so the wrapper is awaited
    off-loop. Already-async handlers (e.g. ngsiem) are returned untouched.

    Two properties of the default anyio thread pool are load-bearing here:

    - **Concurrency caps at 40.** `anyio.to_thread.run_sync` shares one
      `CapacityLimiter` of 40 tokens per event loop, so calls 41+ queue until a
      worker frees up (60 concurrent callers of a 1s handler take ~2s, not ~1s).
      This is deliberate backpressure, not a bug: it bounds both thread count and
      the request rate we aim at the Falcon API. Raising it means passing an
      explicit `limiter=`.
    - **A cancelled request still occupies its worker.** We keep the default
      `abandon_on_cancel=False`, so when a client disconnects or the MCP 60s
      timeout fires, the thread is held until the blocking FalconPy call returns
      rather than being abandoned. Abandoning would free the slot sooner but leaks
      threads without bound under repeated timeouts, which is the worse failure.

    Args:
        method: The tool handler to wrap.

    Returns:
        The original method if it is already a coroutine function, otherwise an
        async wrapper that offloads the call to a thread.
    """
    if iscoroutinefunction(method):
        return method

    @wraps(method)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await anyio.to_thread.run_sync(partial(method, *args, **kwargs))

    return wrapper


class BaseModule(ABC):
    """Base class for all Falcon MCP server modules."""

    def __init__(self, client: FalconClient):
        """Initialize the module.

        Args:
            client: Falcon API client
        """
        self.client = client
        self.tools: list[str] = []  # List to track registered tools
        self.resources: list[str] = []  # List to track registered resources

    @abstractmethod
    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP Server.

        Args:
            server: MCP server instance
        """

    def _add_tool(
        self,
        server: FastMCP,
        method: Callable[..., Any],
        name: str,
        annotations: ToolAnnotations | None = None,
    ) -> None:
        """Add a tool to the MCP server and track it.

        Args:
            server: MCP server instance
            method: Method to register
            name: Tool name
            annotations: MCP tool annotations. Defaults to READ_ONLY_ANNOTATIONS.
        """
        prefixed_name = f"falcon_{name}"
        server.add_tool(
            offload_to_thread(method),
            name=prefixed_name,
            annotations=annotations or READ_ONLY_ANNOTATIONS,
            structured_output=False,
        )
        self.tools.append(prefixed_name)
        logger.debug("Added tool: %s", prefixed_name)

    def _add_resource(self, server: FastMCP, resource: Resource) -> None:
        """Add a resource to the MCP server and track it.

        Args:
            server: MCP server instance
            resource: Resource object
        """
        # FastMCP expects its own Resource type, cast accordingly
        server.add_resource(resource=resource)  # type: ignore[arg-type]

        resource_uri = resource.uri
        self.resources.append(str(resource_uri))
        logger.debug("Added resource: %s", resource_uri)

    def _base_get_by_ids(
        self,
        operation: str,
        ids: list[str],
        id_key: str = "ids",
        use_params: bool = False,
        parameters: dict[str, Any] | None = None,
        **additional_params: Any,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Helper method for API operations that retrieve entities by IDs.

        Whether a given option belongs in the body or the query string varies by
        operation; check the endpoint definition and pass it accordingly. An
        option sent in the wrong place is often ignored without an error.

        Args:
            operation: The API operation name
            ids: List of entity IDs
            id_key: The key name for IDs in the request (default: "ids")
            use_params: If True, send IDs as query parameters (GET).
                       If False, send as request body (POST). Default: False
            parameters: Query-string parameters, for operations that declare an
                option `in: query` even when the IDs travel in a POST body
            **additional_params: Additional parameters to include alongside the
                IDs, in the body or query string per `use_params`

        Returns:
            List of entity details or error dict
        """
        # Build the request params with dynamic ID key and additional parameters
        request_params = {id_key: ids}
        request_params.update(additional_params)

        prepared = prepare_api_parameters(request_params)
        query_params = prepare_api_parameters(parameters) if parameters else {}

        # Make the API request using either parameters (GET) or body (POST)
        if use_params:
            response = self.client.command(operation, parameters={**prepared, **query_params})
        elif query_params:
            response = self.client.command(operation, body=prepared, parameters=query_params)
        else:
            response = self.client.command(operation, body=prepared)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result=[],
        )

    def _reorder_by_ids(
        self,
        ordered_ids: list[str],
        entities: list[dict[str, Any]],
        id_field: str,
    ) -> list[dict[str, Any]]:
        """Reorder hydrated entities to match the sorted ID order from the query step.

        Search tools query entity IDs first (honoring the requested sort) and then
        hydrate full details by ID. Some "get entities by IDs" endpoints return
        resources in arbitrary order, discarding the sort. This restores the order
        of `ordered_ids`. It is a no-op for endpoints that already preserve order.

        Entities whose ID is not in `ordered_ids` are appended in their original
        order (never dropped); IDs with no matching entity are skipped.

        Args:
            ordered_ids: Entity IDs from the query step, in the desired order.
            entities: Hydrated entity dicts from the get-by-IDs step.
            id_field: The key inside each entity dict that holds its ID.

        Returns:
            The entities reordered to match ordered_ids.
        """
        by_id = {str(entity.get(id_field, "")): entity for entity in entities if isinstance(entity, dict)}

        result: list[dict[str, Any]] = []
        placed: set[str] = set()
        for entity_id in ordered_ids:
            key = str(entity_id)
            if key in by_id and key not in placed:
                result.append(by_id[key])
                placed.add(key)

        # Preserve entities not referenced by ordered_ids rather than dropping them
        result.extend(
            entity for entity in entities
            if isinstance(entity, dict) and str(entity.get(id_field, "")) not in placed
        )

        return result

    def _base_search_api_call(
        self,
        operation: str,
        search_params: dict[str, Any],
        error_message: str = "Search operation failed",
        default_result: Any = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Standardized API call for search operations with parameters.

        This method consolidates the common pattern of:
        1. Preparing parameters
        2. Making API request with parameters
        3. Handling the response
        4. Error checking

        Args:
            operation: The API operation name (e.g., "QueryDevicesByFilter")
            search_params: Dictionary of search parameters (filter, limit, offset, sort, etc.)
            error_message: Custom error message for failed operations
            default_result: Default value to return if no results found

        Returns:
            API response data or error dict
        """
        # Prepare parameters for the API request
        prepared_params = prepare_api_parameters(search_params)

        logger.debug("Executing %s with params: %s", operation, prepared_params)

        # Make the API request
        response = self.client.command(operation, parameters=prepared_params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=default_result if default_result is not None else [],
        )

    def _base_query_api_call(
        self,
        operation: str,
        query_params: dict[str, Any] | None = None,
        body_params: dict[str, Any] | None = None,
        error_message: str = "Query operation failed",
        default_result: Any = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Standardized API call for operations that can use both parameters and body.

        Args:
            operation: The API operation name
            query_params: Dictionary of query parameters (for parameters= argument)
            body_params: Dictionary of body parameters (for body= argument)
            error_message: Custom error message for failed operations
            default_result: Default value to return if no results found

        Returns:
            API response data or error dict
        """
        # Prepare the API call arguments
        call_args = {}

        if query_params:
            call_args["parameters"] = prepare_api_parameters(query_params)

        if body_params:
            call_args["body"] = prepare_api_parameters(body_params)

        logger.debug("Executing %s with args: %s", operation, call_args)

        # Make the API request
        response = self.client.command(operation, **call_args)

        # Handle GraphQL operations differently - they don't use "resources" structure
        if operation == "api_preempt_proxy_post_graphql":
            # For GraphQL, check status and return the full body on success
            if response.get("status_code") == 200:
                body: dict[str, Any] = response.get("body", {})
                return body
            else:
                # Use standard error handling for failed GraphQL requests
                return handle_api_response(
                    response,
                    operation=operation,
                    error_message=error_message,
                    default_result=default_result if default_result is not None else {},
                )

        # Handle the response using standard resource extraction
        return handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=default_result if default_result is not None else [],
        )

    def _base_get_api_call(
        self,
        operation: str,
        api_params: dict[str, Any],
        error_message: str = "GET operation failed",
        decode_binary: bool = True,
    ) -> list[dict[str, Any]] | dict[str, Any] | str:
        """Standardized API call for GET operations with optional binary response handling.

        This method handles various GET operations that may return:
        - Standard JSON responses (handled by handle_api_response)
        - Binary responses that need UTF-8 decoding (like MITRE reports)

        Args:
            operation: The API operation name (e.g., "GetMitreReport", "GetReportPdf")
            api_params: Dictionary of API parameters
            error_message: Custom error message for failed operations
            decode_binary: Whether to decode binary responses as UTF-8 (default: True)

        Returns:
            - For successful operations with binary responses: decoded string content
            - For successful operations with JSON responses: standard API response
            - For failed operations: error dict
        """
        # Prepare parameters for the API request
        prepared_params = prepare_api_parameters(api_params)

        logger.debug("Executing %s with params: %s", operation, prepared_params)

        # Make the API request
        command_response = self.client.command(operation, parameters=prepared_params)

        # FalconPy returns raw bytes for binary download endpoints (e.g., GetMitreReport)
        if isinstance(command_response, bytes):
            if decode_binary:
                return command_response.decode('utf-8')
            return command_response

        # Dict response - check status code and use standard error handling
        status_code = command_response.get("status_code")

        if status_code != 200:
            return handle_api_response(
                command_response,
                operation=operation,
                error_message=error_message,
                default_result=[],
            )

        # Standard response handling for dict responses
        return handle_api_response(
            command_response,
            operation=operation,
            error_message=error_message,
            default_result=[],
        )

    def _base_search_with_meta(
        self,
        operation: str,
        search_params: dict[str, Any],
        error_message: str = "Search operation failed",
    ) -> tuple[list[Any] | dict[str, Any], dict[str, Any] | None]:
        """Like _base_search_api_call but also returns the response's pagination metadata.

        Hydration (fetching full entity details by ID) discards `body.meta.pagination`
        from the query-step response, so callers that need `total`/`after` must capture
        it here, before calling `_base_get_by_ids`.

        Args:
            operation: The API operation name (e.g., "QueryDevicesByFilter")
            search_params: Dictionary of search parameters (filter, limit, offset, sort, etc.)
            error_message: Custom error message for failed operations

        Returns:
            Tuple of (resources or error dict, pagination dict or None)
        """
        prepared_params = prepare_api_parameters(search_params)

        logger.debug("Executing %s with params: %s", operation, prepared_params)

        response = self.client.command(operation, parameters=prepared_params)

        result = handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=[],
        )

        if self._is_error(result):
            return result, None

        pagination = self._extract_pagination(response)
        return result, pagination

    @staticmethod
    def _extract_pagination(response: dict[str, Any]) -> dict[str, Any] | None:
        """Pull the pagination cursor and counts out of a raw API response.

        The next-page cursor lives in one of three mutually-exclusive spots
        depending on the endpoint: nested `meta.pagination.next` (Shield), nested
        `meta.pagination.after` (IOC/Spotlight), or top-level `meta.next` (CSPM
        assets/IOM). The nested `meta.pagination` block also carries
        `total`/`offset`/`limit`. Fold the top-level `meta.next` into the nested
        dict — at lowest precedence — so the envelope builder sees one source.
        """
        meta = (response.get("body") or {}).get("meta") or {}
        pagination = meta.get("pagination")
        top_level_next = meta.get("next")

        if pagination is None and not top_level_next:
            return None

        result = dict(pagination) if pagination else {}
        # Top-level `meta.next` is the lowest-precedence cursor: only use it when
        # the nested block has no cursor of its own.
        if top_level_next and not result.get("next") and not result.get("after"):
            result["next"] = top_level_next
        return result

    def _build_pagination_envelope(
        self,
        results: list[dict[str, Any]],
        pagination: dict[str, Any] | None,
        filter_used: str | None = None,
    ) -> dict[str, Any]:
        """Assemble the standard search-tool response envelope.

        Args:
            results: The full entity details to return to the caller
            pagination: The raw `body.meta.pagination` dict from the API response, if any
            filter_used: The FQL filter string that was used, if applicable

        Returns:
            Dict with `results`, `pagination` (total/offset/limit/next), and
            optionally `filter_used`
        """
        pag: dict[str, Any] = {}
        if pagination:
            # `total` may be absent (some endpoints omit it) — report None rather
            # than inventing a count, so a caller can tell "unknown" from a real total.
            pag["total"] = pagination.get("total")
            if "offset" in pagination:
                pag["offset"] = pagination["offset"]
            if "limit" in pagination:
                pag["limit"] = pagination["limit"]
            # The next-page cursor may arrive as `next` (Shield, or a folded-in
            # top-level `meta.next` from CSPM) or as `after` (IOC/Spotlight);
            # `_extract_pagination` normalizes so `next` takes precedence.
            pag["next"] = pagination.get("next") or pagination.get("after") or None
        else:
            # No pagination metadata: the API gave us no count, so report None rather
            # than synthesizing one. A non-null `total` always means the API returned it.
            pag = {"total": None, "next": None}

        envelope: dict[str, Any] = {"results": results, "pagination": pag}
        if filter_used is not None:
            envelope["filter_used"] = filter_used
        return envelope

    def _is_error(self, response: Any) -> bool:
        return isinstance(response, dict) and "error" in response

    @staticmethod
    def _build_aggregate_spec(
        agg_type: str,
        field: str,
        filter: str | None = None,
        name: str | None = None,
        size: int | None = None,
        sort: str | None = None,
        interval: str | None = None,
        time_zone: str | None = None,
        from_: int | None = None,
        q: str | None = None,
        missing: str | None = None,
        include: str | None = None,
        exclude: str | None = None,
        date_ranges: list[dict[str, Any]] | None = None,
        ranges: list[dict[str, Any]] | None = None,
        percents: list[float] | None = None,
        filters_spec: dict[str, Any] | None = None,
        extended_bounds: dict[str, Any] | None = None,
        min_doc_count: int | None = None,
        max_doc_count: int | None = None,
        sub_aggregates: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Build one aggregation spec for a Falcon aggregate endpoint.

        Only `agg_type` and `field` are required. Unset keys are omitted, so
        passing a subset produces a body valid for the narrower dialects.

        Args:
            agg_type: Aggregation type, sent as the wire key `type`
            field: The document field to aggregate on
            filter: FQL filter narrowing the documents aggregated
            name: Label echoed back on the result, identifying it in a
                multi-spec response
            size: Max buckets to return
            sort: Bucket sort, e.g. "_count|desc". Accepted forms vary by
                endpoint; each tool documents what its own endpoint takes
            interval: Bucket width for `date_histogram`, as a bare unit name
                ("hour", "day", "week", "month", "quarter", "year")
            time_zone: Numeric UTC offset, e.g. "+00:00"
            from_: Bucket offset, sent as the wire key `from`
            q: Free-text query
            missing: Value substituted for documents missing `field`
            include: Bucket-key include pattern
            exclude: Bucket-key exclude pattern
            date_ranges: [{"from": ..., "to": ...}, ...] for `date_range`
            ranges: [{"From": ..., "To": ...}, ...] for `range`
            percents: Percentiles to compute, e.g. [50.0, 95.0]
            filters_spec: Named sub-filters for the `filters` type
            extended_bounds: Forces histogram bounds beyond the matched data
            min_doc_count: Drop buckets with fewer than this many documents
            max_doc_count: Drop buckets with more than this many documents
            sub_aggregates: Nested specs, each built with this same method

        Returns:
            The aggregation spec dict, with every unset key omitted
        """
        spec: dict[str, Any] = {
            "type": agg_type,
            "field": field,
            "from": from_,
            "filter": filter,
            "name": name,
            "size": size,
            "sort": sort,
            "interval": interval,
            "time_zone": time_zone,
            "q": q,
            "missing": missing,
            "include": include,
            "exclude": exclude,
            "date_ranges": date_ranges,
            "ranges": ranges,
            "percents": percents,
            "filters_spec": filters_spec,
            "extended_bounds": extended_bounds,
            "min_doc_count": min_doc_count,
            "max_doc_count": max_doc_count,
            "sub_aggregates": sub_aggregates,
        }
        return filter_none_values(spec)

    # Aggregation types that need a companion key in the same spec. The API answers a
    # spec missing its companion with an opaque 500 rather than a validation error.
    _AGGREGATE_REQUIRED_COMPANIONS: dict[str, str] = {
        "date_histogram": "interval",
        "date_range": "date_ranges",
        "range": "ranges",
    }

    @classmethod
    def _find_missing_aggregate_companion(
        cls, specs: list[dict[str, Any]]
    ) -> tuple[str, str] | None:
        """Find the first aggregation spec missing a required companion key.

        Recurses into `sub_aggregates`, which the API validates the same way.

        Args:
            specs: Aggregation specs to check

        Returns:
            A (type, missing key) pair, or None if every spec is complete
        """
        for spec in specs:
            if not isinstance(spec, dict):
                # Malformed input is the API's to reject, not this check's to crash on.
                continue

            agg_type = spec.get("type")
            if isinstance(agg_type, str):
                companion = cls._AGGREGATE_REQUIRED_COMPANIONS.get(agg_type)
                if companion and not spec.get(companion):
                    return agg_type, companion

            nested = spec.get("sub_aggregates")
            if isinstance(nested, list):
                found = cls._find_missing_aggregate_companion(nested)
                if found:
                    return found
        return None

    def _base_aggregate(
        self,
        operation: str,
        specs: list[dict[str, Any]] | None = None,
        error_message: str = "Aggregate operation failed",
        parameters: dict[str, Any] | None = None,
        **spec_kwargs: Any,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Run one or more aggregation specs against a Falcon aggregate endpoint.

        Pass either `specs` or the single-spec kwargs accepted by
        `_build_aggregate_spec`, not both.

        Args:
            operation: The API operation name (e.g. "PostAggregatesAlertsV2")
            specs: Pre-built aggregation specs, for batching several in one call
            error_message: Custom error message for failed operations
            parameters: Query-string parameters for endpoints that take them
                alongside the body (e.g. `include_hidden`)
            **spec_kwargs: Single-spec arguments forwarded to
                `_build_aggregate_spec`

        Returns:
            The API's resources list, one entry per aggregation, or an error dict.
            Each entry holds the aggregation `name` and its `buckets`, which key
            on `label` rather than `key`. Order does not track `specs`.

        Raises:
            ValueError: If both `specs` and single-spec kwargs are given, if
                neither is, or if `specs` is an empty list
        """
        if specs is not None and spec_kwargs:
            raise ValueError(
                "Pass either `specs` or the single-spec kwargs, not both: "
                f"got specs plus {sorted(spec_kwargs)}"
            )
        if specs is None:
            if not spec_kwargs:
                raise ValueError("Provide `specs` or the single-spec kwargs (agg_type, field)")
            specs = [self._build_aggregate_spec(**spec_kwargs)]
        elif not specs:
            # Falsy but not None, so it would otherwise reach the API as a
            # zero-spec POST.
            raise ValueError("`specs` is empty: provide at least one aggregation spec")

        missing = self._find_missing_aggregate_companion(specs)
        if missing:
            agg_type, companion = missing
            return _format_error_response(
                f"`{companion}` is required when type is `{agg_type}`",
                operation=operation,
            )

        logger.debug("Executing %s with %d aggregate spec(s)", operation, len(specs))

        # List-wrapped even for one spec; the API 400s on a bare object.
        command_kwargs: dict[str, Any] = {"body": specs}
        if parameters:
            command_kwargs["parameters"] = parameters
        response = self.client.command(operation, **command_kwargs)

        # A 2xx can still carry a body-level error, which handle_api_response would
        # read as success and discard. Only 2xx: a real 4xx/5xx also carries
        # `errors[]` and needs that function's 403 handling.
        status_code = response.get("status_code")
        body = response.get("body") or {}
        if status_code is not None and status_code < 300 and body.get("errors"):
            # Formatted here rather than via handle_api_response, which would
            # report a status the transport never returned.
            api_messages = [
                message
                for error in body["errors"]
                if (message := error.get("message"))
            ]
            detail = f" API said: {'; '.join(api_messages)}" if api_messages else ""
            return _format_error_response(
                f"{error_message}:{detail}" if detail else error_message,
                details=response,
                operation=operation,
            )

        return handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=[],
        )

    def _format_fql_error_response(
        self,
        errors: list[dict[str, Any]],
        filter_used: str | None,
        fql_documentation: str,
    ) -> dict[str, Any]:
        """Format response with FQL guide for API errors indicating filter problems.

        Use ONLY when the API returned an error (400+) that suggests the FQL
        filter syntax is incorrect. Do NOT use for empty results (200 with 0
        resources) — empty results use the standard pagination envelope, not
        this FQL-error shape.

        Args:
            errors: List containing the error dict from the API
            filter_used: The FQL filter string that was used (can be None)
            fql_documentation: Module-specific FQL documentation constant

        Returns:
            Dict with results, filter_used, fql_guide, and contextual hint
        """
        return {
            "results": errors,
            "filter_used": filter_used,
            "fql_guide": fql_documentation,
            "hint": "Filter error occurred. Review the FQL guide above to correct your query syntax.",
        }
