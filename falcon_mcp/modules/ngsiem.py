"""NG-SIEM module for Falcon MCP Server.

This module provides core functionality for executing LogScale/CQL queries against
CrowdStrike NG-SIEM with a modular, extensible architecture designed for future enhancements.

The module contains:
- NGSIEMConfig: Configuration management for query execution parameters
- NGSIEMQueryEngine: Core query execution engine with hook system for extensibility
- NGSIEMModule: MCP module for registering tools and handling query requests

Typical usage example:

  config = NGSIEMConfig()
  module = NGSIEMModule(client, config)
  result = module.execute_ngsiem_query("#event_simpleName=ProcessRollup2 | tail(3)")
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional

from mcp.server import FastMCP
from pydantic import Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)


class NGSIEMConfig:
    """Configuration for NGSIEM query engine designed for future extensibility.

    Provides configuration settings for query execution, resource management,
    and output formatting. Future features like query validation, result caching,
    and query templates are included but disabled by default.

    Attributes:
        timeout_seconds: Maximum time to wait for query completion in seconds.
        polling_interval: Time between status checks in seconds.
        max_attempts: Maximum number of polling attempts before timeout.
        enable_query_validation: Whether to enable query syntax validation.
        enable_result_caching: Whether to enable result caching.
        enable_query_templates: Whether to enable query templates.
        enable_data_analysis: Whether to enable data analysis tools.
        enable_field_search: Whether to enable field search helpers.
        cleanup_on_timeout: Whether to cleanup searches that timeout.
        cleanup_on_error: Whether to cleanup searches that error.
        track_active_searches: Whether to track active searches for management.
        default_limit: Default maximum number of results to return.
        default_export_behavior: Default export behavior for large results.
        default_sample_events: Default number of sample events for large results.
    """

    def __init__(self) -> None:
        """Initializes configuration with default values for all settings."""
        # Core query execution settings
        self.timeout_seconds = 180  # 3 minutes default
        self.polling_interval = 7.5  # seconds between status checks
        self.max_attempts = 24  # maximum polling attempts

        # Future extensibility - disabled by default for this PR
        self.enable_query_validation = False  # Future PR: query syntax validation
        self.enable_result_caching = False    # Future PR: result caching
        self.enable_query_templates = False   # Future PR: query templates
        self.enable_data_analysis = False     # Future PR: data analysis tools
        self.enable_field_search = False      # Future PR: field search helpers

        # Resource management
        self.cleanup_on_timeout = True
        self.cleanup_on_error = True
        self.track_active_searches = True

        # Output settings
        self.default_limit = 10000
        self.default_export_behavior = "smart"
        self.default_sample_events = 3

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'NGSIEMConfig':
        """Creates configuration from dictionary for future configuration file support.

        Args:
            config_dict: Dictionary containing configuration key-value pairs.

        Returns:
            NGSIEMConfig instance with values from the dictionary.
        """
        config = cls()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class NGSIEMQueryEngine:
    """Core NG-SIEM query functionality with extensible hook system.

    Provides the main query execution engine for LogScale/CQL queries against
    CrowdStrike NG-SIEM. Features an extensible hook system for future enhancements
    like query validation, result caching, and data analysis tools.

    The engine handles authentication, query submission, result polling, error
    handling, and resource cleanup with configurable timeout and retry behavior.

    Attributes:
        client: Falcon API client for NG-SIEM operations.
        config: Configuration settings for query execution.
        active_searches: Dictionary tracking active search operations.
    """

    def __init__(self, client: Any, config: Optional[NGSIEMConfig] = None) -> None:
        """Initialize with MCP Falcon client and configuration.

        Args:
            client: Falcon API client
            config: Configuration object (optional, uses defaults if not provided)
        """
        self.client = client
        self.config = config or NGSIEMConfig()

        # Hook system for future extensibility
        self._hooks: Dict[str, List[Callable]] = {
            'pre_search': [],      # Called before starting search
            'post_search': [],     # Called after successful search completion
            'search_timeout': [],  # Called when search times out
            'search_error': [],    # Called when search encounters error
            'search_cleanup': []   # Called during search cleanup
        }

        # Resource management for active searches
        self.active_searches: Dict[str, Dict[str, Any]] = {}

        logger.info("NGSIEMQueryEngine initialized with hook system and resource management")

    def add_hook(self, event: str, callback: Callable) -> None:
        """Adds a hook callback for the specified event.

        Enables future PRs to extend functionality without modifying core code.
        Supported events: pre_search, post_search, search_timeout, search_error,
        search_cleanup.

        Args:
            event: Hook event name for callback registration.
            callback: Function to call when event occurs.
        """
        if event in self._hooks:
            self._hooks[event].append(callback)
            logger.debug(f"Added hook for {event} event")
        else:
            logger.warning(f"Unknown hook event: {event}")

    def remove_hook(self, event: str, callback: Callable) -> None:
        """Removes a hook callback for the specified event.

        Args:
            event: Hook event name for callback removal.
            callback: Function to remove from the event hooks.
        """
        if event in self._hooks and callback in self._hooks[event]:
            self._hooks[event].remove(callback)
            logger.debug(f"Removed hook for {event} event")

    def _execute_hooks(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Executes all hooks for the specified event.

        Args:
            event: Hook event name to execute.
            *args: Positional arguments to pass to hook callbacks.
            **kwargs: Keyword arguments to pass to hook callbacks.
        """
        for hook in self._hooks.get(event, []):
            try:
                hook(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Hook execution failed for {event}: {e}")

    def parse_time_range(self, time_range: str) -> Dict[str, Any]:
        """Parses time range string into start/end timestamps.

        Supports multiple time range formats:
        - Relative: "15m", "24h", "7d", "2w" (minutes, hours, days, weeks)
        - Absolute start,end: "2024-01-01T00:00:00Z,2024-01-02T00:00:00Z"
        - Single timestamp: "2024-01-01T00:00:00Z" (start time, end is now)

        Args:
            time_range: Time range specification string.

        Returns:
            Dictionary with 'start' and 'end' keys containing timestamp values
            in milliseconds.
        """
        now = datetime.now(timezone.utc)

        if "," in time_range:
            # Start,End format
            start_str, end_str = time_range.split(",", 1)
            start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        elif time_range.endswith(("h", "d", "w", "m")):
            # Relative time format
            unit = time_range[-1]
            value = int(time_range[:-1])

            if unit == "h":
                delta = timedelta(hours=value)
            elif unit == "d":
                delta = timedelta(days=value)
            elif unit == "w":
                delta = timedelta(weeks=value)
            elif unit == "m":
                delta = timedelta(minutes=value)

            start_time = now - delta
            end_time = now
        else:
            # Assume single timestamp (start time)
            start_time = datetime.fromisoformat(time_range.replace("Z", "+00:00"))
            end_time = now

        return {
            # Convert to milliseconds
            "start": int(start_time.timestamp() * 1000),
            "end": int(end_time.timestamp() * 1000),
        }

    def _format_time_range_display(self, time_range: str, time_params: Dict[str, Any]) -> str:
        """Formats time range for display with human-readable timestamps.

        Args:
            time_range: Original time range string.
            time_params: Dictionary with 'start' and 'end' timestamp values.

        Returns:
            Formatted string showing time range with human-readable dates.
        """
        start_dt = datetime.fromtimestamp(time_params["start"] / 1000, tz=timezone.utc)
        end_dt = datetime.fromtimestamp(time_params["end"] / 1000, tz=timezone.utc)

        return (
            f"Searched time range: {time_range} "
            f"({start_dt.strftime('%Y-%m-%d %H:%M:%S UTC')} to "
            f"{end_dt.strftime('%Y-%m-%d %H:%M:%S UTC')})"
        )

    def _build_search_parameters(
        self, query: str, time_range: str, time_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Builds search parameters for NG-SIEM API calls using common utilities.

        Args:
            query: LogScale/CQL query string.
            time_range: Time range specification.
            time_params: Parsed time parameters with start/end timestamps.

        Returns:
            Dictionary containing API parameters for search request.
        """
        # Build raw parameters
        raw_params = {
            "queryString": query,
            "start": time_range
            if time_range.endswith(("h", "d", "w", "m"))
            else str(time_params["start"]),
            "isLive": False,
            "timeZoneOffsetMinutes": 0,
        }

        # Add end time for absolute time ranges
        if not time_range.endswith(("h", "d", "w", "m")):
            raw_params["end"] = str(time_params["end"])

        # Use common utility to filter None values and prepare for API
        return prepare_api_parameters(raw_params)

    def _extract_search_id(self, response: Dict[str, Any]) -> Optional[str]:
        """Extracts search ID from start_search response.

        Args:
            response: API response dictionary from start_search call.

        Returns:
            Search ID string if found, None otherwise.
        """
        if "body" in response and isinstance(response["body"], dict):
            return response["body"].get("id")
        elif "resources" in response and isinstance(response["resources"], dict):
            return response["resources"].get("id")
        elif "id" in response:
            return response.get("id")
        return None

    def _cleanup_search(self, search_id: str, repository: str, reason: str) -> None:
        """Cleans up a search with proper error handling and hooks.

        Args:
            search_id: Search ID to clean up.
            repository: Repository name where search was executed.
            reason: Reason for cleanup (timeout, error, etc.).
        """
        try:
            # Execute cleanup hooks (future extensibility)
            cleanup_info = {
                'search_id': search_id,
                'repository': repository,
                'reason': reason,
                'search_info': self.active_searches.get(search_id, {})
            }
            self._execute_hooks('search_cleanup', cleanup_info)

            # Stop the search
            self.client.command("StopSearchV1", repository=repository, id=search_id)
            logger.info(f"Successfully stopped search {search_id} (reason: {reason})")
        except Exception as e:
            logger.warning(f"Failed to stop search {search_id}: {e}")
        finally:
            # Always remove from active searches tracking
            self.active_searches.pop(search_id, None)

    def execute_query(
        self,
        query: str,
        time_range: str = "15m",
        repository: str = "search-all",
        limit: Optional[int] = None,  # Future parameter reference
        export_behavior: Optional[str] = None,
        output_format: str = "json",  # Future parameter reference
        sample_events: Optional[int] = None,  # Future parameter reference
    ) -> Dict[str, Any]:
        """Execute a LogScale query against CrowdStrike NG-SIEM.

        Args:
            query: LogScale/CQL query to execute
            time_range: Time range for the query (default: "15m")
            repository: Repository to search in (default: "search-all")
            limit: Maximum number of results (uses config default if None)
            export_behavior: Export behavior for large results (uses config default if None)
            output_format: Output format (always "json")
            sample_events: Number of sample events for large results (uses config default if None)

        Returns:
            Dict containing query results or error information
        """
        # Use configuration defaults for optional parameters
        limit = limit or self.config.default_limit
        export_behavior = export_behavior or self.config.default_export_behavior
        sample_events = sample_events or self.config.default_sample_events

        # Build parameters for hooks
        query_params = {
            'query': query,
            'time_range': time_range,
            'repository': repository,
            'limit': limit,
            'export_behavior': export_behavior,
            'output_format': output_format,
            'sample_events': sample_events
        }

        search_id = None
        try:
            logger.info(f"Starting NG-SIEM query execution: {query[:50]}...")

            # Execute pre-search hooks (future extensibility)
            self._execute_hooks('pre_search', query_params)

            # Check authentication status
            if not self.client.is_authenticated():
                error_response = handle_api_response(
                    {
                        "status_code": 401,
                        "body": {"errors": [{"message": "Authentication failed"}]},
                    },
                    operation="NG-SIEM Query",
                    error_message="Authentication failed for CrowdStrike Falcon API",
                )
                self._execute_hooks('search_error', error_response, query_params)
                return error_response

            # Parse time range and build search parameters
            time_params = self.parse_time_range(time_range)
            search_body = self._build_search_parameters(query, time_range, time_params)

            logger.info(f"Repository: {repository}")
            logger.info(f"Time range: {time_range} ({time_params})")

            # Start the search
            response = self.client.command("StartSearchV1", repository=repository, body=search_body)

            # Handle start_search response
            if response.get("status_code") != 200:
                error_response = handle_api_response(
                    response,
                    operation="NG-SIEM Query Start",
                    error_message="NG-SIEM API request failed",
                )
                self._execute_hooks('search_error', error_response, query_params)
                return error_response

            # Extract search ID
            search_id = self._extract_search_id(response)
            if not search_id:
                logger.error(f"Could not extract search ID from response: {response}")
                error_response = handle_api_response(
                    {
                        "status_code": 500,
                        "body": {"errors": [{"message": "Search ID not found in API response"}]},
                    },
                    operation="NG-SIEM Query Parse",
                    error_message="Failed to get search ID from API response",
                )
                self._execute_hooks('search_error', error_response, query_params)
                return error_response

            logger.info(f"Search initiated with ID: {search_id}")

            # Poll for results with resource management
            results = self._poll_for_results(search_id, repository, limit, query_params)

            # Check for errors or timeout
            if isinstance(results, dict) and "error" in results:
                self._execute_hooks('search_error', results, query_params)
                return results
            elif isinstance(results, dict) and (
                "polling_status" in results or "polling_timeout" in results
            ):
                return results  # Progress status or timeout

            # Build successful response
            full_response = {
                "search_id": search_id,
                "query": query,
                "time_range": time_range,
                "time_params": time_params,
                "time_range_display": self._format_time_range_display(time_range, time_params),
                "results": results,
                "result_count": len(results.get("events", [])),
                "execution_time": datetime.now(timezone.utc).isoformat(),
            }

            # Execute post-search hooks (future extensibility)
            self._execute_hooks('post_search', full_response, query_params)

            # Handle response formatting and export
            final_result = handle_api_response(
                full_response,
                operation=f"NG-SIEM Query ({query[:50]}...)",
            )

            logger.debug(f"handle_api_response returned type: {type(final_result)}")
            logger.debug(f"handle_api_response returned value: {final_result}")

            return final_result

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")

            # Cleanup search on error if configured
            if search_id and self.config.cleanup_on_error:
                self._cleanup_search(search_id, repository, "error")

            # Build detailed error response
            error_response = {
                "error": f"Query execution failed: {str(e)}",
                "exception_type": type(e).__name__,
                "query": query,
                "time_range": time_range,
                "repository": repository,
            }

            # Add authentication context if available
            try:
                if hasattr(self.client, "is_authenticated"):
                    error_response["authentication_status"] = (
                        "authenticated" if self.client.is_authenticated() else "not_authenticated"
                    )
                if hasattr(self.client.client, "token_valid"):
                    error_response["token_valid"] = self.client.client.token_valid
            except Exception:
                error_response["authentication_status"] = "unknown"

            self._execute_hooks('search_error', error_response, query_params)
            return error_response

    def _poll_for_results(
        self, search_id: str, repository: str, limit: int, query_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Polls for query results until completion with resource management and hooks.

        Args:
            search_id: Search ID to poll for results.
            repository: Repository name where search was executed.
            limit: Maximum number of results to return.
            query_params: Original query parameters for hook callbacks.

        Returns:
            Dictionary containing query results or status information.
        """
        max_attempts = self.config.max_attempts
        attempt = 0

        # Track this search
        if self.config.track_active_searches:
            self.active_searches[search_id] = {
                'repository': repository,
                'start_time': time.time(),
                'query_params': query_params,
                'status': 'polling'
            }

        logger.info(f"Starting to poll for query results (search_id: {search_id})")

        try:
            while attempt < max_attempts:
                try:
                    elapsed_seconds = attempt * self.config.polling_interval

                    # Update search status
                    if search_id in self.active_searches:
                        self.active_searches[search_id]['status'] = f'polling_attempt_{attempt + 1}'
                        self.active_searches[search_id]['elapsed_seconds'] = elapsed_seconds

                    # Use get_search_status method with proper error handling
                    response = self.client.command("GetSearchStatusV1", repository=repository, id=search_id)

                    if response.get("status_code") != 200:
                        return handle_api_response(
                            response,
                            operation="NG-SIEM Poll Status",
                            error_message="Failed to poll query results",
                        )

                    # Check if query is complete
                    body: Dict[str, Any] = response.get("body", {})
                    if body.get("done", False):
                        logger.info(f"Query completed successfully after {elapsed_seconds}s")

                        # Update final status
                        if search_id in self.active_searches:
                            self.active_searches[search_id]['status'] = 'completed'

                        return body

                    # Log progress for long-running queries
                    if attempt % 4 == 0 and attempt > 0:  # Every 30 seconds
                        logger.info(
                            f"Query still running after {elapsed_seconds}s - this is normal for large datasets"
                        )

                    # Provide user feedback for long-running queries at specific intervals
                    if attempt == 4:  # After 30 seconds
                        return {
                            "polling_status": "long_running_query",
                            "search_id": search_id,
                            "elapsed_time_seconds": elapsed_seconds,
                            "max_wait_seconds": max_attempts * self.config.polling_interval,
                            "message": f"Query is still processing after {elapsed_seconds}s. This indicates a complex query or large result set.",
                            "progress_message": f"Query running for {elapsed_seconds}s - continuing to poll (will wait up to {max_attempts * self.config.polling_interval}s total)",
                            "suggestions": [
                                "This is normal for large time ranges or complex queries",
                                "Large result sets are returned in JSON format",
                                "Query will continue processing in the background",
                                "You can try a smaller time range if you need faster results",
                            ],
                            "recommendation": "Please wait - legitimate large queries can take 1-3 minutes to complete.",
                        }
                    elif attempt == 12:  # After 90 seconds
                        return {
                            "polling_status": "very_long_running_query",
                            "search_id": search_id,
                            "elapsed_time_seconds": elapsed_seconds,
                            "max_wait_seconds": max_attempts * self.config.polling_interval,
                            "message": f"Query has been running for {elapsed_seconds}s. Still processing - this can be normal for very large datasets.",
                            "progress_message": f"Query running for {elapsed_seconds}s - will continue polling for up to {(max_attempts - attempt) * self.config.polling_interval}s more",
                            "suggestions": [
                                "Very large queries legitimately take 2-3 minutes",
                                "Result will be returned in JSON format",
                                "Query is still actively processing",
                                "Consider the query scope - 2000 events over 24h can be substantial",
                            ],
                            "recommendation": "Continuing to wait - query should complete soon and will provide results in JSON format.",
                        }

                    logger.info(
                        f"Query in progress... (attempt {attempt + 1}/"
                        f"{max_attempts}, {elapsed_seconds}s elapsed)"
                    )

                    # Sleep before next attempt
                    time.sleep(self.config.polling_interval)
                    attempt += 1

                except Exception as e:
                    logger.error(f"Polling failed with exception: {str(e)}")
                    return handle_api_response(
                        {
                            "status_code": 500,
                            "body": {"errors": [{"message": f"Polling exception: {str(e)}"}]},
                        },
                        operation="NG-SIEM Poll Exception",
                        error_message="Polling failed with exception",
                    )

            # Timeout reached - cleanup if configured
            total_elapsed = max_attempts * self.config.polling_interval
            logger.warning(
                f"Query polling timed out after {total_elapsed}s - this may indicate an exceptionally large result set"
            )

            # Execute timeout hooks
            timeout_info = {
                'search_id': search_id,
                'repository': repository,
                'elapsed_seconds': total_elapsed,
                'query_params': query_params
            }
            self._execute_hooks('search_timeout', timeout_info)

            # Cleanup search if configured
            if self.config.cleanup_on_timeout:
                self._cleanup_search(search_id, repository, "timeout")

            return handle_api_response(
                {
                    "status_code": 408,
                    "body": {
                        "errors": [
                            {"message": f"Query polling timed out after {total_elapsed} seconds"}
                        ]
                    },
                },
                operation="NG-SIEM Poll Timeout",
                error_message="Query polling timed out",
            )

        finally:
            # Always clean up tracking for completed/failed searches
            if search_id in self.active_searches and self.active_searches[search_id].get('status') != 'completed':
                self.active_searches.pop(search_id, None)


class NGSIEMModule(BaseModule):
    """Simplified NG-SIEM module focused on core query execution functionality.

    Provides MCP tool registration and integration for NG-SIEM query execution.
    This module focuses on core query functionality with a simplified architecture
    for reliable LogScale/CQL query execution against CrowdStrike NG-SIEM.

    Future PRs will add query templates, data analysis tools, field search helpers,
    and query validation capabilities.

    Attributes:
        config: Configuration settings for the module.
        query_engine: Core query execution engine instance.
    """

    def __init__(self, client: Any, config: Optional[NGSIEMConfig] = None) -> None:
        """Initialize the NG-SIEM module.

        Args:
            client: Falcon API client
            config: Configuration object (optional, uses defaults if not provided)
        """
        super().__init__(client)

        # Initialize integrated components with dependency injection
        self.config = config or NGSIEMConfig()
        self.query_engine = NGSIEMQueryEngine(client, self.config)

        logger.info("NGSIEMModule initialized with simplified architecture")

    def register_tools(self, server: FastMCP) -> None:
        """Registers core NG-SIEM tools with the MCP server.

        Currently registers only the core query execution tool. Future PRs will add:
        - Query templates and builders
        - Data analysis tools
        - Field search helpers
        - Query validation tools

        Args:
            server: FastMCP server instance for tool registration.
        """
        # Register core SIEM query execution tool
        self._add_tool(
            server=server,
            method=self.execute_ngsiem_query,
            name="execute_ngsiem_query",
        )


        logger.info("Registered NG-SIEM tools: query execution")

    def register_resources(self, server: FastMCP) -> None:
        """Registers minimal resources for this core functionality PR.

        Currently provides minimal resource registration. Future PRs will add
        comprehensive resource registration including:
        - Scraped LogScale documentation
        - Field mapping resources
        - Query pattern libraries
        - Use case examples

        Args:
            server: FastMCP server instance for resource registration.
        """
        # Minimal resources for this PR - future PRs will expand this
        logger.info("Minimal resource registration for core query execution")

    def execute_ngsiem_query(
        self,
        query: str = Field(description="LogScale/CQL query to execute"),
        time_range: str = Field(default="15m", description="Time range for the query"),
        repository: str = Field(
            default="search-all",
            description="Repository to search in (default is 'search-all')",
        ),
        output_format: str = Field(default="json", description="Output format (always 'json')"),  # Future parameter reference
        export_behavior: str = Field(
            default="smart",
            description="Export behavior: 'smart' (token-based), 'always', or 'never'",
        ),
        sample_events: int = Field(
            default=3,
            description="Number of sample events to include in response when data is auto-exported",  # Future parameter reference
        ),
    ) -> Dict[str, Any]:
        """Executes LogScale/CQL queries against CrowdStrike NG-SIEM.

        This is the core query execution tool focused on reliable search functionality.
        Future PRs will add query templates, validation, and analysis capabilities.

        Important: Always start queries with an event type filter like
        #event_simpleName=ProcessRollup2 for better performance and relevant results.

        Args:
            query: LogScale/CQL query to execute.
            time_range: Time range for the query (default: "15m").
            repository: Repository to search in (default: "search-all").
            output_format: Output format (always "json").
            export_behavior: Export behavior for large results.
            sample_events: Number of sample events for large results.

        Returns:
            Dictionary containing query results, metadata, and execution information.
        """
        logger.debug("execute_ngsiem_query called with parameters:")
        logger.debug("  query: %s", query)
        logger.debug("  time_range: %s", time_range)
        logger.debug("  repository: %s", repository)
        logger.debug("  output_format: %s", output_format)
        logger.debug("  export_behavior: %s", export_behavior)
        logger.debug("  sample_events: %s", sample_events)

        # Validate repository parameter
        valid_repositories = ["search-all", "detections", "base_sensor", "incidents", "idp"]
        if repository not in valid_repositories:
            logger.warning(
                f"Repository '{repository}' is not in standard list: {valid_repositories}"
            )

        try:
            # Execute the query using the engine with proper parameter mapping
            results = self.query_engine.execute_query(
                query=query,
                time_range=time_range,
                repository=repository,
                limit=self.config.default_limit,
                export_behavior=export_behavior,
                output_format=output_format,
                sample_events=sample_events,
            )

            logger.debug("Query engine returned results")
            logger.debug(f"Results type: {type(results)}")
            logger.debug(f"Results value: {results}")

            # Ensure we always return a dictionary for MCP tool validation
            if isinstance(results, list):
                logger.warning(f"Query engine returned list instead of dict: {results}")
                return {
                    "error": "Query engine returned unexpected list format",
                    "raw_results": results,
                    "query": query,
                    "time_range": time_range
                }

            return results

        except Exception as e:
            logger.error("Exception in execute_ngsiem_query: %s", str(e))

            # Return standardized error response
            return handle_api_response(
                {
                    "status_code": 500,
                    "body": {"errors": [{"message": f"Query execution failed: {str(e)}"}]},
                },
                operation="NG-SIEM Query Execution",
                error_message="Query execution failed",
            )


