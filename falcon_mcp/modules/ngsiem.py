"""
NG-SIEM module for Falcon MCP Server

This module provides tools for executing LogScale/CQL queries against
CrowdStrike NG-SIEM, with query templates, data analysis capabilities,
and field reference documentation.
"""

import csv
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import FunctionResource
from pydantic import Field

from falcon_mcp.common.cql_validator import CQLSyntaxValidator
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.ngsiem_query_helper import NGSIEMQueryHelper
from falcon_mcp.common.query_component_detector import QueryComponentDetector
from falcon_mcp.common.response_handler import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)


class NGSIEMQueryEngine:
    """Core NG-SIEM query functionality integrated with MCP client."""

    def __init__(self, client: Any) -> None:
        """Initialize with MCP Falcon client."""
        self.client = client
        self.validator = CQLSyntaxValidator()
        self.component_detector = QueryComponentDetector()
        self.query_helper = NGSIEMQueryHelper()

    def parse_time_range(self, time_range: str) -> Dict[str, Any]:
        """Parse time range string into start/end timestamps."""
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
        """Format time range for display with human-readable timestamps."""
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
        """Build search parameters for NG-SIEM API calls using common utilities.

        Args:
            query: The LogScale query string
            time_range: Time range string
            time_params: Parsed time parameters

        Returns:
            Dict of prepared API parameters
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

    def execute_query(
        self,
        query: str,
        time_range: str = "15m",
        repository: str = "search-all",
        limit: int = 10000,
        export_behavior: str = "smart",
        output_format: str = "json",
        sample_events: int = 3,
    ) -> Dict[str, Any]:
        """Execute a LogScale query against CrowdStrike NG-SIEM."""

        try:
            # Log entry for debugging
            logger.info(f"NGSIEMQueryEngine.execute_query called with query: {query[:50]}...")

            # Check authentication status first
            if not self.client.is_authenticated():
                return handle_api_response(
                    {
                        "status_code": 401,
                        "body": {"errors": [{"message": "Authentication failed"}]},
                    },
                    operation="NG-SIEM Query",
                    error_message="Authentication failed for CrowdStrike Falcon API",
                )

            # Parse time range
            time_params = self.parse_time_range(time_range)

            logger.info(f"Executing query: {query[:100]}...")
            logger.info(f"Time range: {time_range} ({time_params})")
            logger.info(
                f"Start timestamp: {time_params['start']}, End timestamp: {time_params['end']}"
            )

            # Execute the query using NGSIEM client via FalconClient wrapper
            # The FalconClient.start_search expects repository and body parameters
            search_body = self._build_search_parameters(query, time_range, time_params)

            logger.info(f"Repository: {repository}")
            logger.info(f"Search body: {search_body}")

            # Add timeout protection for initial query submission
            try:
                response = self.client.start_search(repository=repository, body=search_body)
            except Exception as e:
                return handle_api_response(
                    {
                        "status_code": 500,
                        "body": {"errors": [{"message": f"Query submission failed: {str(e)}"}]},
                    },
                    operation="NG-SIEM Query Submission",
                    error_message="Query submission to CrowdStrike NG-SIEM failed",
                )

            # Debug: Log the full response
            logger.info(f"NG-SIEM API Response: {response}")

            # Handle the response using standard error handler
            if response.get("status_code") != 200:
                return handle_api_response(
                    response,
                    operation="NG-SIEM Query Start",
                    error_message="NG-SIEM API request failed",
                )

            # Get search ID from response using standard pattern
            search_id = None
            if "body" in response and isinstance(response["body"], dict):
                search_id = response["body"].get("id")
            elif "resources" in response and isinstance(response["resources"], dict):
                search_id = response["resources"].get("id")
            elif "id" in response:
                search_id = response.get("id")

            if not search_id:
                logger.error(f"Could not extract search ID from response: {response}")
                return handle_api_response(
                    {
                        "status_code": 500,
                        "body": {"errors": [{"message": "Search ID not found in API response"}]},
                    },
                    operation="NG-SIEM Query Parse",
                    error_message="Failed to get search ID from API response",
                )

            logger.info(f"Search initiated with ID: {search_id}")

            # Poll for results
            results = self._poll_for_results(search_id, repository, limit)

            # Check for polling errors, progress status, or timeout
            if isinstance(results, dict) and "error" in results:
                return results  # Return polling error directly
            elif isinstance(results, dict) and (
                "polling_status" in results or "polling_timeout" in results
            ):
                return results  # Return progress status or timeout directly

            # Construct the full response
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

            # Use handle_api_response to handle large datasets
            return handle_api_response(
                full_response,
                operation=f"NG-SIEM Query ({query[:50]}...)",
                export_behavior=export_behavior,
                export_format=output_format,
                sample_events=sample_events,
            )

        except Exception as e:
            detailed_error = {
                "error": f"Query execution failed: {str(e)}",
                "exception_type": type(e).__name__,
                "details": ("An unexpected error occurred while executing the NG-SIEM query."),
                "suggestions": [
                    "Check if the CrowdStrike Falcon API is accessible",
                    "Verify your network connectivity",
                    "Try a simpler query to test basic functionality",
                    "Check the MCP server logs for more detailed error information",
                ],
                "query": query,
                "time_range": time_range,
                "repository": repository,
            }

            # Add authentication context if available
            try:
                if hasattr(self.client, "is_authenticated"):
                    is_auth = self.client.is_authenticated()
                    detailed_error["authentication_status"] = (
                        "authenticated" if is_auth else "not_authenticated"
                    )
                if hasattr(self.client.client, "token_valid"):
                    detailed_error["token_valid"] = self.client.client.token_valid
            except Exception:
                detailed_error["authentication_status"] = "unknown"

            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {repr(e)}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return detailed_error

    def _poll_for_results(
        self, search_id: str, repository: str, limit: int = 10000
    ) -> Dict[str, Any]:
        """Poll for query results until completion using standardized error handling."""
        max_attempts = 24  # Maximum 3 minutes of polling (24 attempts × 7.5 seconds)
        attempt = 0

        logger.info(f"Starting to poll for query results (search_id: {search_id})")

        while attempt < max_attempts:
            try:
                elapsed_seconds = attempt * 7.5

                # Use get_search_status method with proper error handling
                response = self.client.get_search_status(repository=repository, id=search_id)

                if response.get("status_code") != 200:
                    return handle_api_response(
                        response,
                        operation="NG-SIEM Poll Status",
                        error_message="Failed to poll query results",
                    )

                # Check if query is complete
                body = response.get("body", {})
                if body.get("done", False):
                    logger.info(f"Query completed successfully after {elapsed_seconds}s")
                    return cast(Dict[str, Any], body)

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
                        "max_wait_seconds": max_attempts * 7.5,
                        "message": f"Query is still processing after {elapsed_seconds}s. This indicates a complex query or large result set.",
                        "progress_message": f"Query running for {elapsed_seconds}s - continuing to poll (will wait up to {max_attempts * 7.5}s total)",
                        "suggestions": [
                            "This is normal for large time ranges or complex queries",
                            "Large result sets often require CSV export when complete",
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
                        "max_wait_seconds": max_attempts * 7.5,
                        "message": f"Query has been running for {elapsed_seconds}s. Still processing - this can be normal for very large datasets.",
                        "progress_message": f"Query running for {elapsed_seconds}s - will continue polling for up to {(max_attempts - attempt) * 7.5}s more",
                        "suggestions": [
                            "Very large queries legitimately take 2-3 minutes",
                            "Result may require CSV export due to size",
                            "Query is still actively processing",
                            "Consider the query scope - 2000 events over 24h can be substantial",
                        ],
                        "recommendation": "Continuing to wait - query should complete soon or will provide results via CSV export.",
                    }

                logger.info(
                    f"Query in progress... (attempt {attempt + 1}/"
                    f"{max_attempts}, {elapsed_seconds}s elapsed)"
                )

                # Sleep before next attempt
                time.sleep(7.5)
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

        # Timeout reached after 3 minutes - use standard error handler
        total_elapsed = max_attempts * 7.5
        logger.warning(
            f"Query polling timed out after {total_elapsed}s - this may indicate an exceptionally large result set"
        )
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


class NGSIEMDataAnalyzer:
    """Data analysis utilities for NG-SIEM results."""

    def export_to_csv(self, results_data: Dict[str, Any]) -> str:
        """Export events to CSV format using native Python."""
        events = results_data.get("events", [])
        if not events:
            return ""

        # Get all unique fields across all events
        all_fields_set = set()
        for event in events:
            all_fields_set.update(event.keys())

        all_fields = sorted(list(all_fields_set))

        # Create CSV string
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=all_fields, extrasaction="ignore")
        writer.writeheader()

        for event in events:
            # Fill missing fields with empty strings
            row = {field: event.get(field, "") for field in all_fields}
            writer.writerow(row)

        return output.getvalue()

    def generate_summary(self, results_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary analysis."""
        events = results_data.get("events", [])
        if not events:
            return {"message": "No events found"}

        # Basic statistics
        total_events = len(events)

        # Field analysis
        field_counts: Counter[str] = Counter()
        all_fields = set()

        for event in events:
            for field in event.keys():
                all_fields.add(field)
                field_counts[field] += 1

        # Common values analysis for key fields
        key_fields = ["ComputerName", "UserName", "SourceIP", "DestinationIP", "FileName"]
        common_values = {}

        for field in key_fields:
            if field in all_fields:
                values: Counter[str] = Counter()
                for event in events:
                    if field in event and event[field]:
                        values[str(event[field])] += 1

                if values:
                    common_values[field] = values.most_common(10)

        # Time analysis
        timestamps = []
        for event in events:
            for time_field in ["timestamp", "@timestamp", "event_time"]:
                if time_field in event:
                    timestamps.append(event[time_field])
                    break

        time_span = "Unknown"
        if timestamps:
            try:
                # Convert to datetime if needed
                dt_stamps = []
                for ts in timestamps:
                    if isinstance(ts, (int, float)):
                        dt_stamps.append(datetime.fromtimestamp(ts))
                    else:
                        dt_stamps.append(datetime.fromisoformat(str(ts).replace("Z", "+00:00")))

                if dt_stamps:
                    min_time = min(dt_stamps)
                    max_time = max(dt_stamps)
                    time_span = f"{min_time.isoformat()} to {max_time.isoformat()}"
            except Exception:
                pass

        # Unique counts for key fields
        unique_hosts = len(
            set(event.get("ComputerName", "") for event in events if event.get("ComputerName"))
        )
        unique_users = len(
            set(event.get("UserName", "") for event in events if event.get("UserName"))
        )

        return {
            "total_events": total_events,
            "unique_fields": len(all_fields),
            "all_fields": sorted(list(all_fields)),
            "field_presence": dict(field_counts.most_common()),
            "common_values": common_values,
            "time_span": time_span,
            "unique_hosts": unique_hosts if unique_hosts > 0 else "N/A",
            "unique_users": unique_users if unique_users > 0 else "N/A",
            "time_range": results_data.get("time_range"),
            "execution_time": results_data.get("execution_time"),
        }

    def create_pivot_analysis(
        self, results_data: Dict[str, Any], pivot_fields: List[str]
    ) -> Dict[str, Any]:
        """Create pivot analysis using native Python collections."""
        events = results_data.get("events", [])
        if not events:
            return {"error": "No events to analyze"}

        # Group events by pivot fields
        grouped: defaultdict[str, int] = defaultdict(int)

        for event in events:
            # Create key from pivot fields
            key_parts = []
            for field in pivot_fields:
                value = event.get(field, "N/A")
                key_parts.append(str(value))

            key = " | ".join(key_parts)
            grouped[key] += 1

        # Sort by count descending
        sorted_groups = sorted(grouped.items(), key=lambda x: x[1], reverse=True)

        return {
            "pivot_fields": pivot_fields,
            "grouped_data": dict(sorted_groups),
            "total_groups": len(sorted_groups),
            "top_10": dict(sorted_groups[:10]),
        }

    def generate_statistical_analysis(self, results_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistical analysis."""
        events = results_data.get("events", [])
        if not events:
            return {"error": "No events to analyze"}

        # Field statistics
        field_stats: Dict[str, Dict[str, Any]] = {}
        numeric_fields = []

        for event in events:
            for field, value in event.items():
                if field not in field_stats:
                    field_stats[field] = {
                        "count": 0,
                        "unique_values": set(),
                        "is_numeric": True,
                        "numeric_values": [],
                    }

                field_stats[field]["count"] += 1
                field_stats[field]["unique_values"].add(str(value))

                # Check if numeric
                try:
                    numeric_val = float(value)
                    field_stats[field]["numeric_values"].append(numeric_val)
                except (ValueError, TypeError):
                    field_stats[field]["is_numeric"] = False

        # Calculate statistics for numeric fields
        for field, stats in field_stats.items():
            if stats["is_numeric"] and stats["numeric_values"]:
                values = stats["numeric_values"]
                stats["min"] = min(values)
                stats["max"] = max(values)
                stats["avg"] = sum(values) / len(values)
                numeric_fields.append(field)

            # Convert set to count for serialization
            stats["unique_count"] = len(stats["unique_values"])
            del stats["unique_values"]  # Remove set for JSON serialization
            del stats["numeric_values"]  # Remove list to save space

        return {
            "total_events": len(events),
            "field_statistics": field_stats,
            "numeric_fields": numeric_fields,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }


class NGSIEMModule(BaseModule):
    """Module for accessing CrowdStrike NG-SIEM with LogScale/CQL queries."""

    def __init__(self, client: Any) -> None:
        """Initialize the NG-SIEM module.

        Args:
            client: Falcon API client
        """
        super().__init__(client)

        # Initialize integrated components
        self.query_engine = NGSIEMQueryEngine(client)
        self.query_helper = NGSIEMQueryHelper()
        self.analyzer = NGSIEMDataAnalyzer()
        self.validator = CQLSyntaxValidator()
        self.component_detector = QueryComponentDetector()

    def register_tools(self, server: FastMCP) -> None:
        """Register NG-SIEM tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register core SIEM query tool
        self._add_tool(
            server=server,
            method=self.execute_ngsiem_query,
            name="execute_ngsiem_query",
        )

        # Register query helper with templates
        self._add_tool(
            server=server,
            method=self.ngsiem_query_templates,
            name="ngsiem_query_templates",
        )

        # Register data analysis tool
        self._add_tool(
            server=server,
            method=self.analyze_ngsiem_results,
            name="analyze_ngsiem_results",
        )

        # Register field search helper
        self._add_tool(
            server=server,
            method=self.search_ngsiem_fields,
            name="search_ngsiem_fields",
        )

        # Register query validation tool
        self._add_tool(
            server=server,
            method=self.validate_cql_syntax,
            name="validate_cql_syntax",
        )

        # Register interactive CQL builder
        self._add_tool(
            server=server,
            method=self.build_cql_query,
            name="build_cql_query",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register NG-SIEM resources with the MCP server.

        Args:
            server: MCP server instance
        """
        # Import the content from resources
        from falcon_mcp.resources.ngsiem import (
            NGSIEM_FIELD_MAPPINGS,
            NGSIEM_QUERY_PATTERNS,
            NGSIEM_USE_CASES,
        )

        # Use scraped docs from project resources directory
        project_root = Path(__file__).parent.parent.parent  # falcon-mcp/
        scraped_docs_path = project_root / "resources" / "ngsiem"

        # CrowdStrike-specific programmatic resources (from embedded content)

        # Scraped LogScale documentation categories
        scraped_categories = {
            "functions-reference": {
                "description": "Official LogScale function reference documentation",
                "patterns": ["*functions*.md", "*function*.md", "*()*.md"],
                "max_files": 50,
            },
            "query-examples": {
                "description": "Official LogScale query examples and patterns",
                "patterns": ["*Example*.md", "*examples*.md", "*Tutorial*.md"],
                "max_files": 35,
            },
            "syntax-guide": {
                "description": "LogScale syntax principles and concepts",
                "patterns": ["*principles*.md", "*syntax*.md", "*query*.md", "*Query*.md"],
                "max_files": 25,
            },
            "array-functions": {
                "description": "LogScale array manipulation functions",
                "patterns": ["*Array*.md", "*array*.md"],
                "max_files": 15,
            },
            "aggregate-functions": {
                "description": "LogScale aggregation and statistical functions",
                "patterns": ["*Aggregate*.md", "*aggregate*.md", "*Statistical*.md"],
                "max_files": 15,
            },
            "data-manipulation": {
                "description": "LogScale data processing and manipulation functions",
                "patterns": ["*Processing*.md", "*Manipulation*.md", "*Transform*.md"],
                "max_files": 20,
            },
        }

        # Register CrowdStrike-specific programmatic resources using the same pattern as scraped docs

        # Create individual programmatic resources using lambda with default parameters (like scraped docs)
        crowdstrike_resource_defs = [
            {
                "content": NGSIEM_FIELD_MAPPINGS,
                "uri": "falcon://ngsiem/field-mappings",
                "name": "falcon_ngsiem_field_mappings",
                "description": "CrowdStrike-specific field mappings for LogScale/CQL queries",
                "title": "CrowdStrike Field Mappings",
            },
            {
                "content": NGSIEM_QUERY_PATTERNS,
                "uri": "falcon://ngsiem/query-patterns",
                "name": "falcon_ngsiem_query_patterns",
                "description": "CQL query patterns optimized for CrowdStrike data",
                "title": "CrowdStrike Query Patterns",
            },
            {
                "content": NGSIEM_USE_CASES,
                "uri": "falcon://ngsiem/use-cases",
                "name": "falcon_ngsiem_use_cases",
                "description": "Security use cases with CrowdStrike data examples",
                "title": "CrowdStrike Use Cases",
            },
        ]

        for resource_def in crowdstrike_resource_defs:
            # Create resource using the same pattern as scraped docs with lambda default parameters
            resource = FunctionResource.from_function(
                fn=lambda content=resource_def["content"],
                title=resource_def["title"]: self._aggregate_crowdstrike_content(content, title),
                uri=resource_def["uri"],
                name=resource_def["name"],
                description=resource_def["description"],
                mime_type="text/markdown",
            )
            self._add_resource(server, resource)
            logger.info(f"Registered CrowdStrike resource: {resource_def['name']}")

        # Register scraped documentation categories
        if scraped_docs_path.exists():
            for category, config in scraped_categories.items():
                matching_files: List[Path] = []

                # Find files matching any of the patterns
                for pattern in config["patterns"]:
                    matching_files.extend(scraped_docs_path.glob(pattern))

                # Remove duplicates and limit results
                matching_files = list(set(matching_files))[: config["max_files"]]

                if matching_files:
                    # Create a function resource that aggregates matching files
                    resource = FunctionResource.from_function(
                        fn=lambda files=matching_files, cat=category: self._aggregate_scraped_docs(
                            files, cat
                        ),
                        uri=f"falcon://ngsiem/{category}",
                        name=f"falcon_ngsiem_{category.replace('-', '_')}",
                        description=config["description"],
                        mime_type="text/markdown",
                    )
                    self._add_resource(server, resource)
                    logger.info(f"Registered {category} with {len(matching_files)} files")
                else:
                    logger.warning(f"No files found for category: {category}")
        else:
            logger.warning(f"Scraped documentation path not found: {scraped_docs_path}")

    def _aggregate_scraped_docs(self, files: list, category: str) -> str:
        """Aggregate multiple scraped documentation files into a single resource."""
        content = f"# LogScale {category.replace('-', ' ').title()}\n\n"
        content += f"Official LogScale documentation aggregated from {len(files)} source files.\n\n"
        content += "---\n\n"

        for file_path in files[:20]:  # Limit to prevent huge responses
            try:
                file_content = file_path.read_text()
                # Clean up the title from filename
                title = file_path.stem.replace("___", " | ").replace("_", " ")

                content += f"## {title}\n\n"

                # Take first part of content (limit size)
                lines = file_content.split("\n")
                preview_lines = lines[:100] if len(lines) > 100 else lines
                content += "\n".join(preview_lines)

                if len(lines) > 100:
                    content += f"\n\n*[Content truncated - {len(lines) - 100} more lines available in original file]*"

                content += "\n\n---\n\n"

            except Exception as e:
                logger.warning(f"Error reading scraped file {file_path}: {e}")
                continue

        return content

    def _aggregate_crowdstrike_content(self, content: str, title: str) -> str:
        """Aggregate CrowdStrike-specific content into a formatted resource."""
        result = f"# {title}\n\n"
        result += "CrowdStrike-specific content for NG-SIEM queries.\n\n"
        result += "---\n\n"
        result += content
        return result

    def execute_ngsiem_query(
        self,
        query: str = Field(description="LogScale/CQL query to execute"),
        time_range: str = Field(default="15m", description="Time range for the query"),
        repository: str = Field(
            default="search-all",
            description="Repository to search in (e.g., 'search-all', 'detections', 'base_sensor')",
        ),
        output_format: str = Field(default="json", description="Output format: 'json' or 'csv'"),
        export_behavior: str = Field(
            default="smart",
            description="Export behavior: 'smart' (token-based), 'always', or 'never'",
        ),
        sample_events: int = Field(
            default=3,
            description="Number of sample events to include in response when data is auto-exported",
        ),
    ) -> Dict[str, Any]:
        """Execute LogScale/CQL queries against CrowdStrike NG-SIEM.

        This tool allows you to run LogScale queries against CrowdStrike's security data.
        Use the falcon://ngsiem/field-mappings resource to find available fields.
        Use the falcon://ngsiem/query-patterns resource for query syntax help.

        IMPORTANT: Always start queries with an event type filter like #event_simpleName=ProcessRollup2
        for better performance and relevant results.
        """

        # DEBUG: Log all parameters at the very start
        logger.debug("execute_ngsiem_query called with parameters:")
        logger.debug("  query: %s", query)
        logger.debug("  time_range: %s", time_range)
        logger.debug("  repository: %s", repository)
        logger.debug("  output_format: %s", output_format)
        logger.debug("  export_behavior: %s", export_behavior)
        logger.debug("  sample_events: %s", sample_events)

        logger.debug(
            "Executing NG-SIEM query: %s with time_range: %s, repository: %s, export_behavior: %s, sample_events: %s",
            query,
            time_range,
            repository,
            export_behavior,
            sample_events,
        )

        # Validate repository parameter
        valid_repositories = ["search-all", "detections", "base_sensor", "incidents", "idp"]
        if repository not in valid_repositories:
            logger.warning(
                f"Repository '{repository}' is not in standard list: {valid_repositories}"
            )

        try:
            # Pre-normalize common patterns before validation
            query = self._pre_normalize_query(query)

            # Enhanced validation and conversion with detailed error handling
            logger.info("Starting enhanced CQL validation...")
            validation_result = self.validator.validate_and_convert(query)

            # Check if validation found critical errors
            if not validation_result.get("is_valid_cql", True):
                # Check if the only issues are simple case corrections that were already fixed
                syntax_errors = validation_result.get("syntax_errors", [])
                corrections_made = validation_result.get("corrections_made", [])

                only_case_corrections = (
                    corrections_made
                    and all(
                        correction.get("type") == "case_correction"
                        for correction in corrections_made
                    )
                    and all(
                        error.get("error", "").startswith("Case sensitivity error")
                        for error in syntax_errors
                    )
                )

                if only_case_corrections:
                    # For simple case corrections, just use the corrected query without template matching
                    logger.info(
                        "Only case corrections needed, using corrected query without template matching"
                    )
                    final_query = validation_result["converted_query"]
                else:
                    # Try to auto-correct using query builder for common patterns
                    logger.info("Query validation failed, attempting auto-correction...")

                    corrected_query = self._attempt_query_auto_correction(query, validation_result)
                    if corrected_query:
                        logger.info(f"Auto-corrected query: {corrected_query}")
                        # Re-validate the corrected query
                        validation_result = self.validator.validate_and_convert(corrected_query)
                        if validation_result.get("is_valid_cql", True):
                            final_query = validation_result["converted_query"]
                            validation_result["auto_corrected"] = True
                            validation_result["original_query"] = query
                        else:
                            # Still invalid after correction attempt
                            return self._return_validation_error(query, validation_result)
                    else:
                        # Could not auto-correct
                        return self._return_validation_error(query, validation_result)
            else:
                # Use converted query if changes were made, but don't apply template matching
                # for queries that are already valid CQL
                final_query = validation_result["converted_query"]

            # Log validation results
            if validation_result.get("corrections_made"):
                logger.info(
                    f"Applied {len(validation_result['corrections_made'])} corrections to query"
                )
            if validation_result.get("suggestions"):
                logger.info(
                    f"Generated {len(validation_result['suggestions'])} suggestions for query optimization"
                )

            # Execute the query using integrated engine with proper repository parameter
            logger.info("About to call query engine...")
            results = self.query_engine.execute_query(
                final_query,
                time_range,
                repository,
                limit=10000,
                export_behavior=export_behavior,
                output_format=output_format,
                sample_events=sample_events,
            )
            logger.info("Query engine returned results")

        except Exception as e:
            logger.error("Exception in main execute_ngsiem_query function: %s", str(e))
            logger.error("Exception type: %s", type(e).__name__)
            import traceback

            logger.error("Traceback: %s", traceback.format_exc())

            # Return standardized error response
            return handle_api_response(
                {
                    "status_code": 500,
                    "body": {"errors": [{"message": f"Query execution failed: {str(e)}"}]},
                },
                operation="NG-SIEM Query Execution",
                error_message="Query execution failed",
            )

        # Debug: Log the results from execute_query (this code was previously unreachable)
        logger.info(f"Query execution results type: {type(results)}")
        logger.info(
            f"Query execution results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}"
        )

        # CRITICAL: Check for errors BEFORE processing
        if isinstance(results, dict) and "error" in results:
            # Surface the error immediately with enhanced context
            error_response = {
                "execution_failed": True,
                "user_message": f"❌ Query execution failed: {results.get('error', 'Unknown error')}\n\nTroubleshooting steps:\n1. Check your CrowdStrike API credentials\n2. Verify NG-SIEM access permissions\n3. Try a simpler query like: #event_simpleName=SensorHeartbeat | head(5)\n4. Check network connectivity",
                "error_details": results,
                "query": query,
                "final_query": final_query,
                "time_range": time_range,
            }

            # Add specific error context based on error type
            error_type = results.get("error", "").lower()
            if "authentication" in error_type:
                error_response["error_category"] = "authentication"
                error_response["user_message"] += (
                    "\n\n🔧 Action needed: Check FALCON_CLIENT_ID and FALCON_CLIENT_SECRET environment variables"
                )
            elif "timeout" in error_type:
                error_response["error_category"] = "timeout"
                error_response["user_message"] += (
                    "\n\n🔧 Action needed: Try a smaller time range or more specific query filters"
                )
            elif "permission" in error_type:
                error_response["error_category"] = "permissions"
                error_response["user_message"] += (
                    "\n\n🔧 Action needed: Contact your CrowdStrike administrator to grant NG-SIEM access"
                )

            return error_response

        # Check for polling status messages and convert them to user feedback
        if isinstance(results, dict) and "polling_status" in results:
            status_type = results.get("polling_status", "unknown")

            progress_response = {
                "query_status": "running",
                "polling_info": results,
                "query": query,
                "time_range": time_range,
            }

            if status_type == "long_running_query":
                progress_response["user_message"] = (
                    f"⏳ Query is taking longer than usual ({results.get('elapsed_time_seconds', 0)}s)\n\nThis indicates a complex query or large result set.\n✅ This is normal for large time ranges or complex queries\n⏱️  Continuing to poll (will wait up to {results.get('max_wait_seconds', 180)}s total)\n\n💡 Tip: Large result sets often require CSV export when complete"
                )
            elif status_type == "very_long_running_query":
                progress_response["user_message"] = (
                    f"⏰ Query has been running for {results.get('elapsed_time_seconds', 0)}s\n\n✅ Still processing - this can be normal for very large datasets\n⏱️  Will continue polling for up to {results.get('max_wait_seconds', 180) - results.get('elapsed_time_seconds', 0)}s more\n\n💡 Very large queries legitimately take 2-3 minutes\n📊 Result may require CSV export due to size"
                )
            else:
                progress_response["user_message"] = (
                    f"🔄 Query is still processing... ({results.get('elapsed_time_seconds', 'unknown')}s elapsed)\n\nPlease wait - query will complete soon."
                )

            return progress_response

        # Add success info to results
        if isinstance(results, dict) and "results" in results:
            result_count = results.get("result_count", 0)
            if result_count > 0:
                results["execution_status"] = (
                    f"✅ Query completed successfully! Found {result_count:,} results"
                )
            else:
                results["execution_status"] = (
                    "✅ Query completed successfully! No results found for this query"
                )

            # Add status info to successful results
            results["execution_status"] = {
                "query_status": "completed",
                "result_count": result_count,
                "message": results["execution_status"]
                if isinstance(results.get("execution_status"), str)
                else f"Found {result_count:,} results",
            }

        # Add validation info to successful results if syntax was corrected
        if validation_result["corrections_made"] or validation_result["warnings"]:
            results["query_validation"] = {
                "original_query": query,
                "corrected_query": final_query,
                "corrections_made": validation_result["corrections_made"],
                "warnings": validation_result["warnings"],
                "suggestions": validation_result["suggestions"],
            }

        # Handle large responses before processing output format
        if "results" in results and "events" in results.get("results", {}):
            events_data = results["results"]["events"]
            logger.debug(
                "About to handle response with export_behavior=%s, sample_events=%s, events_count=%d",
                export_behavior,
                sample_events,
                len(events_data),
            )
            print(
                f"[DEBUG] About to handle response with export_behavior={export_behavior}, sample_events={sample_events}, events_count={len(events_data)}"
            )

            # ALWAYS check for download requests, regardless of size
            # The response handler will handle explicit downloads properly
            handled_response = handle_api_response(
                response=events_data,
                operation="execute_ngsiem_query",
                export_format=output_format,
                export_behavior=export_behavior,
                sample_events=sample_events,
            )

            logger.debug("Response handled, type: %s", type(handled_response))
            print(f"[DEBUG] Response handled, type: {type(handled_response)}")
            if isinstance(handled_response, dict):
                logger.debug("Handled response keys: %s", list(handled_response.keys()))
                print(f"[DEBUG] Handled response keys: {list(handled_response.keys())}")

            # If response was handled (too large OR download requested), return the handled result
            if isinstance(handled_response, dict) and (
                # Check if response handler actually handled the response
                handled_response.get("handled")
                or
                # OR check for other response handling keys (legacy)
                any(
                    key in handled_response
                    for key in [
                        "response_summary",
                        "modify_query",
                        "operation_aborted",
                        "query_halted",
                    ]
                )
            ):
                logger.debug("Returning handled response")
                print("[DEBUG] Condition matched, returning handled response")
                # Add query metadata to the handled response
                handled_response["query_metadata"] = {
                    "query": query,
                    "time_range": time_range,
                    "total_results": len(events_data),
                }
                if "query_validation" in results:
                    handled_response["query_validation"] = results["query_validation"]
                return handled_response

            # If not handled or user chose to continue, use the returned data
            print("[DEBUG] Condition NOT matched, continuing with normal flow")
            if isinstance(handled_response, list):
                results["results"]["events"] = handled_response

        # Handle output format for normal-sized responses
        if (
            output_format == "csv"
            and "results" in results
            and "events" in results.get("results", {})
        ):
            event_count = len(results.get("results", {}).get("events", []))
            print(f"📊 Converting {event_count} results to CSV format...")
            csv_data = self.analyzer.export_to_csv(results["results"])
            print("✅ CSV conversion completed!")
            return {
                "format": "csv",
                "query": query,
                "time_range": time_range,
                "time_range_display": results.get("time_range_display", ""),
                "result_count": len(results.get("results", {}).get("events", [])),
                "csv_data": csv_data,
            }

        print(f"✅ Query execution completed! Found {results.get('result_count', 0)} results")

        return cast(Dict[str, Any], results)

    def ngsiem_query_templates(
        self,
        template_name: Optional[str] = Field(
            default=None,
            description="Specific template name to get, or None to list all available templates",
            examples=["failed_logins", "suspicious_powershell", "lateral_movement"],
        ),
        custom_filters: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Custom filter parameters to apply to the template query",
        ),
    ) -> Dict[str, Any]:
        """Get pre-built LogScale query templates for common security use cases.

        This tool provides access to curated query templates for threat hunting,
            incident response, and security monitoring. Templates can be customized
        with additional filters.
        """
        try:
            if template_name:
                # Get specific template
                query = self.query_helper.get_template_query(template_name, custom_filters or {})
                template_info = self.query_helper.COMMON_QUERIES[template_name]
                return {
                    "template": template_name,
                    "query": query,
                    "description": template_info.get("description", ""),
                    "category": template_info.get("category", ""),
                    "custom_filters": custom_filters,
                }
            else:
                # List all available templates
                templates = self.query_helper.get_predefined_queries()
                return {
                    "available_templates": list(templates.keys()),
                    "templates": {
                        name: {
                            "description": info.get("description", ""),
                            "category": info.get("category", "general"),
                        }
                        for name, info in templates.items()
                    },
                }

        except Exception as e:
            logger.error("Error getting query templates: %s", str(e))
            return {"error": f"Failed to get query templates: {str(e)}"}

    def analyze_ngsiem_results(
        self,
        results_data: Dict[str, Any] = Field(
            description="NG-SIEM query results to analyze (JSON format from execute_ngsiem_query)"
        ),
        analysis_type: str = Field(
            default="summary",
            description="Type of analysis to perform",
            examples=["summary", "pivot", "statistical"],
        ),
        pivot_fields: Optional[List[str]] = Field(
            default=None,
            description="Fields to pivot on for pivot analysis",
            examples=[["user", "host"], ["#event_simpleName", "severity"]],
        ),
    ) -> Dict[str, Any]:
        """Analyze NG-SIEM query results with statistical analysis and pivot tables.

        This tool processes query results to provide insights, summaries, and
        structured analysis of security events and patterns.
        """
        try:
            logger.debug("Analyzing NG-SIEM results with analysis_type: %s", analysis_type)

            # Validate input - handle both direct results and nested results structure
            events = []
            if isinstance(results_data, dict):
                if "events" in results_data:
                    events = results_data["events"]
                elif "results" in results_data and isinstance(results_data["results"], dict):
                    events = results_data["results"].get("events", [])

            if not events:
                return {"error": "Invalid results_data - no events found"}

            # Prepare results_data for analyzer (ensure events are at top level)
            analysis_data = results_data.copy()
            if "events" not in analysis_data:
                analysis_data["events"] = events

            if analysis_type == "summary":
                summary = self.analyzer.generate_summary(analysis_data)
                return {
                    "analysis_type": "summary",
                    "summary": summary,
                    "event_count": len(events),
                    "query_metadata": {
                        "query": results_data.get("query", ""),
                        "time_range": results_data.get("time_range", ""),
                        "execution_time": results_data.get("execution_time", ""),
                    },
                }

            elif analysis_type == "pivot":
                if not pivot_fields:
                    pivot_fields = ["#event_simpleName", "ComputerName"]  # Default pivot fields

                pivot_data = self.analyzer.create_pivot_analysis(analysis_data, pivot_fields)
                return {
                    "analysis_type": "pivot",
                    "pivot_fields": pivot_fields,
                    "pivot_data": pivot_data,
                    "event_count": len(events),
                }

            elif analysis_type == "statistical":
                stats = self.analyzer.generate_statistical_analysis(analysis_data)
                return {
                    "analysis_type": "statistical",
                    "statistics": stats,
                    "event_count": len(events),
                }

            else:
                return {
                    "error": f"Unknown analysis_type: {analysis_type}. Use: summary, pivot, or statistical"
                }

        except Exception as e:
            logger.error("Error analyzing NG-SIEM results: %s", str(e))
            return {"error": f"Failed to analyze results: {str(e)}"}

    def search_ngsiem_fields(
        self,
        search_term: str = Field(
            description="Search term to find relevant LogScale fields",
            examples=["process", "network", "user", "file", "registry"],
        ),
        field_type: Optional[str] = Field(
            default=None,
            description="Filter by field type if known",
            examples=["string", "number", "timestamp", "boolean"],
        ),
    ) -> Dict[str, Any]:
        """Search available LogScale fields by name or description.

        This tool helps you discover relevant fields for building LogScale queries
        by searching through the complete field reference documentation.
        """
        try:
            field_suggestions = self._get_field_suggestions(search_term)

            return {
                "search_term": search_term,
                "field_type": field_type,
                "matching_fields": field_suggestions,
                "recommendation": (
                    "Use falcon://ngsiem/field-mappings resource for complete field reference"
                ),
            }

        except Exception as e:
            logger.error("Error searching NG-SIEM fields: %s", str(e))
            return {"error": f"Failed to search fields: {str(e)}"}

    def validate_cql_syntax(
        self,
        query: str = Field(
            description="CQL query to validate and potentially convert from Splunk syntax",
            examples=["| stats count() by field", "#event_simpleName=ProcessRollup2 | head 100"],
        ),
    ) -> Dict[str, Any]:
        """Validate CQL syntax and convert Splunk patterns to proper CQL.

        This tool validates LogScale/CQL syntax, detects Splunk patterns, and provides
        corrections and suggestions for proper CQL syntax.
        """
        try:
            logger.debug("Validating CQL syntax for query: %s", query)

            # Run full validation and conversion
            validation_result = self.validator.validate_and_convert(query)

            # Add syntax guide reference
            validation_result["syntax_guide"] = (
                "Use falcon://ngsiem/query-patterns resource for complete CQL syntax reference"
            )

            return cast(Dict[str, Any], validation_result)

        except Exception as e:
            logger.error("Error validating CQL syntax: %s", str(e))
            return {"error": f"Failed to validate CQL syntax: {str(e)}"}

    def build_cql_query(
        self,
        event_type: Optional[str] = Field(
            default=None,
            description="Event type to filter on",
            examples=["ProcessRollup2", "NetworkConnectIP4", "UserLogon"],
        ),
        platform: Optional[str] = Field(
            default=None,
            description="Platform to filter on",
            examples=["Win", "Mac", "Lin"],
        ),
        filters: Optional[Dict[str, str]] = Field(
            default=None,
            description="Field filters as key-value pairs",
            examples=[{"UserName": "admin", "ProcessId": ">1000"}],
        ),
        regex_filters: Optional[Dict[str, str]] = Field(
            default=None,
            description="Regex filters as key-pattern pairs (will add /pattern/i for case-insensitive)",
            examples=[{"CommandLine": "powershell", "ImageFileName": "cmd\\.exe"}],
        ),
        wildcard_filters: Optional[Dict[str, str]] = Field(
            default=None,
            description="Wildcard filters as key-pattern pairs (will add *pattern* for simple matching)",
            examples=[{"CommandLine": "powershell", "UserName": "admin"}],
        ),
        group_by: Optional[List[str]] = Field(
            default=None,
            description="Fields to group by",
            examples=[["ComputerName"], ["UserName", "ComputerName"]],
        ),
        sort_by: Optional[str] = Field(
            default=None,
            description="Field to sort by",
            examples=["timestamp", "_count"],
        ),
        sort_order: str = Field(
            default="desc",
            description="Sort order",
            examples=["desc", "asc"],
        ),
        limit_type: str = Field(
            default="head",
            description="Type of limiting to apply",
            examples=["head", "groupby_limit"],
        ),
        limit: int = Field(
            default=1000,
            description="Number of results to limit to",
            ge=1,
            le=10000,
        ),
        select_fields: Optional[List[str]] = Field(
            default=None,
            description="Fields to select in output",
            examples=[["ComputerName", "UserName", "CommandLine"]],
        ),
    ) -> Dict[str, Any]:
        """Interactive CQL query builder with guided parameters.

        This tool helps construct proper LogScale/CQL queries by providing a guided
        interface for building queries step by step with proper syntax.
        """
        try:
            logger.debug("Building CQL query with parameters")

            query_parts = []
            explanations = []

            # Helper method to add # prefix for known event fields

            def normalize_field_name(field_name: str) -> str:
                """Add # prefix for known event fields that require it."""
                event_fields_needing_hash = {"event_simpleName", "Vendor", "type", "repo"}
                if field_name in event_fields_needing_hash and not field_name.startswith("#"):
                    return f"#{field_name}"
                return field_name

            # 1. Event type filtering (highly recommended)

            if event_type:
                query_parts.append(f"#event_simpleName={event_type}")
                explanations.append(f"Filter to {event_type} events for performance")
            else:
                query_parts.append("*")
                explanations.append(
                    "WARNING: Using wildcard search - consider specifying event_type for better performance"
                )

            # 2. Platform filtering
            if platform:
                query_parts.append(f"AND event_platform={platform}")
                explanations.append(f"Filter to {platform} platform events")

            # 3. Direct field filters
            if filters and isinstance(filters, dict):
                for field, value in filters.items():
                    normalized_field = normalize_field_name(field)
                    if value.startswith((">", "<", "!", "=")):
                        query_parts.append(f"AND {normalized_field}{value}")
                        explanations.append(f"Numeric/comparison filter on {normalized_field}")
                    elif " " in value:
                        query_parts.append(f'AND {normalized_field}="{value}"')
                        explanations.append(f"Quoted string filter on {normalized_field}")
                    else:
                        query_parts.append(f"AND {normalized_field}={value}")
                        explanations.append(f"Exact match filter on {normalized_field}")

            # 4. Regex filters
            if regex_filters and isinstance(regex_filters, dict):
                for field, pattern in regex_filters.items():
                    normalized_field = normalize_field_name(field)
                    query_parts.append(f"AND {normalized_field}=/{pattern}/i")
                    explanations.append(f"Case-insensitive regex filter on {normalized_field}")

            # 5. Wildcard filters
            if wildcard_filters and isinstance(wildcard_filters, dict):
                for field, pattern in wildcard_filters.items():
                    normalized_field = normalize_field_name(field)
                    query_parts.append(f"AND {normalized_field}=*{pattern}*")
                    explanations.append(f"Case-sensitive wildcard filter on {normalized_field}")

            # Build the base query
            base_query = " ".join(query_parts)

            # 6. Aggregations and functions
            functions = []

            # Field selection
            if select_fields and isinstance(select_fields, list):
                functions.append(f"select([{', '.join(select_fields)}])")
                explanations.append(f"Select specific fields: {', '.join(select_fields)}")

            # Grouping
            if group_by and isinstance(group_by, list):
                # Normalize field names in group_by
                normalized_group_by = [normalize_field_name(field) for field in group_by]

                if limit_type == "groupby_limit":
                    if len(normalized_group_by) == 1:
                        functions.append(f"groupBy({normalized_group_by[0]}, limit={limit})")
                        explanations.append(
                            f"Group by {normalized_group_by[0]} with limit of {limit} groups"
                        )
                    else:
                        functions.append(
                            f"groupBy([{', '.join(normalized_group_by)}], limit={limit})"
                        )
                        explanations.append(
                            f"Group by {', '.join(normalized_group_by)} with limit of {limit} groups"
                        )
                else:
                    if len(normalized_group_by) == 1:
                        functions.append(f"groupBy({normalized_group_by[0]})")
                    else:
                        functions.append(f"groupBy([{', '.join(normalized_group_by)}])")
                    explanations.append(f"Group by {', '.join(normalized_group_by)}")

                    # Sorting after groupBy
                    if sort_by:
                        normalized_sort_by = normalize_field_name(sort_by)
                        if sort_order == "desc":
                            functions.append(f"sort({normalized_sort_by})")
                            explanations.append(f"Sort by {normalized_sort_by} in descending order")
                        else:
                            functions.append(f"sort({normalized_sort_by}, order=asc)")
                            explanations.append(f"Sort by {normalized_sort_by} in ascending order")

                    # Head limit after groupBy and sort
                    if limit_type == "head":
                        functions.append(f"head({limit})")
                        explanations.append(f"Limit to {limit} results")

            else:
                # No grouping - just sorting and limiting
                if sort_by:
                    normalized_sort_by = normalize_field_name(sort_by)
                    if sort_order == "desc":
                        functions.append(f"sort({normalized_sort_by})")
                        explanations.append(f"Sort by {normalized_sort_by} in descending order")
                    else:
                        functions.append(f"sort({normalized_sort_by}, order=asc)")
                        explanations.append(f"Sort by {normalized_sort_by} in ascending order")

                if limit_type == "head":
                    functions.append(f"head({limit})")
                    explanations.append(f"Limit to {limit} results")

            # Combine base query with functions
            if functions:
                final_query = f"{base_query} | " + " | ".join(functions)
            else:
                final_query = base_query

            # Validate the built query
            validation_result = self.validator.validate_and_convert(final_query)

            return {
                "built_query": final_query,
                "query_explanation": explanations,
                "validation_result": validation_result,
                "cql_features_used": self._identify_cql_features(final_query),
                "suggested_improvements": validation_result.get("suggestions", []),
                "ready_to_execute": validation_result.get("is_valid_cql", True),
                "builder_parameters": {
                    "event_type": event_type,
                    "platform": platform,
                    "filters": filters,
                    "regex_filters": regex_filters,
                    "wildcard_filters": wildcard_filters,
                    "group_by": group_by,
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                    "limit_type": limit_type,
                    "limit": limit,
                    "select_fields": select_fields,
                },
            }

        except Exception as e:
            logger.error("Error building CQL query: %s", str(e))
            return {"error": f"Failed to build CQL query: {str(e)}"}

    def _attempt_query_auto_correction(self, query: str, validation_result: Dict) -> str:
        """Attempt to auto-correct common query syntax errors using intelligent workflow."""
        logger.info("Starting intelligent query auto-correction workflow")

        # Method 1: Try intelligent pattern detection and query builder
        corrected_query = self._attempt_intelligent_query_building(query)
        if corrected_query:
            logger.info("Successfully built query using intelligent pattern detection")
            return corrected_query

        # Method 2: Try template matching
        template_query = self._attempt_template_matching(query)
        if template_query:
            logger.info("Successfully matched query to template")
            return template_query

        # Method 3: Fall back to simple pattern fixes
        simple_fix = self._attempt_simple_pattern_fixes(query, validation_result)
        if simple_fix:
            logger.info("Applied simple pattern fixes")
            return simple_fix

        return None

    def _attempt_intelligent_query_building(self, query: str) -> Optional[str]:
        """Use the query builder to reconstruct queries from detected patterns."""
        try:
            logger.info(f"Analyzing query pattern: {query}")

            # Detect query components using the component detector
            components = self.component_detector.detect_query_components(query)
            if not components:
                return None

            logger.info(f"Detected components: {components}")

            # Use the query builder with detected components
            build_result = self.build_cql_query(**components)

            if build_result.get("ready_to_execute") and build_result.get("built_query"):
                built_query = build_result["built_query"]
                logger.info(f"Successfully built query: {built_query}")
                return built_query

        except Exception as e:
            logger.warning(f"Intelligent query building failed: {e}")

        return None

    def _attempt_template_matching(self, query: str) -> Optional[str]:
        """Try to match the query intent to a predefined template using the enhanced query helper."""
        try:
            # Use the enhanced query helper for template matching
            matches = self.query_helper.find_matching_templates(query, max_results=1)
            if matches:
                best_match = matches[0]
                if best_match["relevance_score"] >= 2:  # Minimum relevance threshold
                    logger.info(
                        f"Matched query to template: {best_match['template_name']} (score: {best_match['relevance_score']})"
                    )
                    return best_match["template_info"]["query"]

        except Exception as e:
            logger.warning(f"Template matching failed: {e}")

        return None

    def _attempt_simple_pattern_fixes(
        self, query: str, validation_result: Dict[str, Any]
    ) -> Optional[str]:
        """Apply simple pattern-based fixes as fallback."""
        corrected_query = query

        # Extract syntax errors and apply corrections
        for error in validation_result.get("syntax_errors", []):
            if error.get("corrected_field"):
                # Handle field corrections (like adding # prefix)
                field = error.get("corrected_field")
                old_field = field.lstrip("#")
                corrected_query = re.sub(rf"\b{old_field}\s*=", f"{field}=", corrected_query)
                logger.info(f"Auto-corrected field: {old_field} -> {field}")

        # Handle common Splunk-to-CQL patterns
        corrections = {
            # Fix groupBy syntax - most comprehensive patterns
            r"\*\s*\|\s*groupby\s+([#\w]+)(?!\s*[\(\[])": r"* | groupBy([\1])",  # * | groupby field -> * | groupBy([field])
            r"\*\s*\|\s*groupby\s*\(\s*([#\w]+)\s*\)": r"* | groupBy([\1])",  # * | groupby(field) -> * | groupBy([field])
            r"\*\s*\|\s*groupby\s*\[([^\]]+)\]": r"* | groupBy([\1])",  # * | groupby [field] -> * | groupBy([field])
            r"([*#\w\s=]+)\s+groupby\s+([#\w]+)(?!\s*[\(\[])": r"\1 | groupBy([\2])",  # query groupby field -> query | groupBy([field])
            r"([*#\w\s=]+)\s+groupby\s*\(\s*([#\w]+)\s*\)": r"\1 | groupBy([\2])",  # query groupby(field) -> query | groupBy([field])
            # Fix head/limit syntax
            r"\|\s*head\s+(\d+)": r"| head(\1)",
            r"\|\s*limit\s+(\d+)": r"| head(\1)",
            # Fix sort syntax
            r"\|\s*sort\s+([#\w]+)\s+desc": r"| sort(\1)",  # CQL default is desc
            r"\|\s*sort\s+([#\w]+)\s+asc": r"| sort(\1, order=asc)",
            r"\|\s*sort\s+([#\w]+)(?!\s*[\(,])": r"| sort(\1)",  # Add parentheses if missing
            # Fix case sensitivity
            r"\bgroupby\b": "groupBy",
        }

        for pattern, replacement in corrections.items():
            if re.search(pattern, corrected_query, re.IGNORECASE):
                old_query = corrected_query
                corrected_query = re.sub(pattern, replacement, corrected_query, flags=re.IGNORECASE)
                if old_query != corrected_query:
                    logger.info(f"Applied simple pattern fix: {pattern}")

        return corrected_query if corrected_query != query else None

    def _return_validation_error(self, query: str, validation_result: Dict) -> Dict:
        """Return a detailed validation error with intelligent suggestions."""
        error_response = {
            "execution_failed": True,
            "error_type": "validation_error",
            "user_message": f"❌ Query syntax validation failed\n\n**Original Query:** `{query}`\n\n**Issues Found:**",
            "validation_details": validation_result,
            "query": query,
        }

        # Add specific error descriptions
        for error in validation_result.get("syntax_errors", []):
            error_response["user_message"] += (
                f"\n• **{error.get('error', 'Syntax Error')}:** {error.get('message', 'Unknown error')}"
            )
            if error.get("suggestion"):
                error_response["user_message"] += f"\n  💡 *Suggestion:* {error['suggestion']}"

        # Add corrections that were attempted
        if validation_result.get("corrections_made"):
            error_response["user_message"] += "\n\n**Auto-corrections Applied:**"
            for correction in validation_result["corrections_made"]:
                error_response["user_message"] += f"\n• {correction.get('type', 'correction')}"

        # Add intelligent template suggestions based on query intent
        template_suggestion = self.query_helper.suggest_template_for_failed_query(query)
        if template_suggestion:
            error_response["user_message"] += "\n\n**🎯 Suggested Template (ready to use):**"
            error_response["user_message"] += (
                f"\n• **{template_suggestion['suggested_template']}**: {template_suggestion['description']}"
            )
            error_response["user_message"] += (
                f"\n  📝 *Query:* `{template_suggestion['template_query']}`"
            )
            error_response["user_message"] += (
                f"\n  🎯 *Relevance Score:* {template_suggestion['relevance_score']}"
            )

        # Add helpful suggestions
        error_response["user_message"] += "\n\n**🛠️ How to Fix:**"
        if validation_result.get("suggestions"):
            for suggestion in validation_result["suggestions"][:3]:  # Limit to top 3
                error_response["user_message"] += f"\n• {suggestion.get('message', 'No message')}"
                if suggestion.get("example"):
                    error_response["user_message"] += f"\n  📝 *Example:* `{suggestion['example']}`"

        # Add workflow suggestions
        error_response["user_message"] += "\n\n**🚀 Alternative Approaches:**"
        error_response["user_message"] += (
            "\n• **Use Query Builder**: Let the system build the query for you"
        )
        error_response["user_message"] += (
            "\n• **Try Templates**: Use pre-built queries for common tasks"
        )
        error_response["user_message"] += (
            "\n• **Start Simple**: Begin with `#event_simpleName=ProcessRollup2 | head(10)`"
        )

        # Add common CQL patterns
        error_response["user_message"] += "\n\n**📚 Common CQL Patterns:**"
        error_response["user_message"] += (
            "\n• Basic search: `#event_simpleName=ProcessRollup2 | head(100)`"
        )
        error_response["user_message"] += "\n• Grouping: `* | groupBy([#type]) | sort(_count)`"
        error_response["user_message"] += (
            "\n• Filtering: `ComputerName=*server* AND event_platform=Win`"
        )

        return error_response

    def _identify_cql_features(self, query: str) -> List[str]:
        """Identify which CQL features are used in a query."""
        features = []

        if "#event_simpleName=" in query:
            features.append("event_type_filtering")
        if "event_platform=" in query:
            features.append("platform_filtering")
        if re.search(r"/[^/]+/i?", query):
            features.append("regex_filtering")
        if "groupBy(" in query:
            features.append("grouping")
        if "sort(" in query:
            features.append("sorting")
        if "head(" in query:
            features.append("result_limiting")
        if "select(" in query:
            features.append("field_selection")
        if "limit=" in query:
            features.append("groupby_limiting")

        return features

    def _get_field_suggestions(self, search_term: str) -> List[Dict[str, str]]:
        """
        Get field suggestions based on search term.
        This uses the resources module for field mappings.
        """
        # Simple field suggestions based on common LogScale fields
        common_fields = [
            "ComputerName",
            "UserName",
            "ProcessId",
            "CommandLine",
            "FileName",
            "ImageFileName",
            "ParentProcessId",
            "SHA256HashData",
            "MD5HashData",
            "@timestamp",
            "event_simpleName",
            "aid",
            "cid",
            "LocalAddressIP4",
            "RemoteAddressIP4",
            "RemotePort",
            "LocalPort",
            "Protocol",
        ]

        search_lower = search_term.lower()
        matching_fields = [
            {"field": field, "description": f"LogScale field: {field}"}
            for field in common_fields
            if search_lower in field.lower()
        ]

        return (
            matching_fields[:10]
            if matching_fields
            else [
                {"field": "#event_simpleName", "description": "Event type filter (recommended)"},
                {"field": "#type", "description": "Data source type"},
                {"field": "ComputerName", "description": "Host/computer name"},
                {"field": "UserName", "description": "Username"},
                {"field": "@timestamp", "description": "Event timestamp"},
            ]
        )

    def _pre_normalize_query(self, query: str) -> str:
        """Aggressively normalize common query patterns before validation."""
        normalized = query.strip()

        # Handle missing pipes in groupBy
        normalized = re.sub(
            r"\*\s+groupby\s+([#\w]+)", r"* | groupBy([\1])", normalized, flags=re.IGNORECASE
        )
        normalized = re.sub(
            r"([^\|])\s+groupby\s+([#\w]+)", r"\1 | groupBy([\2])", normalized, flags=re.IGNORECASE
        )

        # Ensure proper groupBy array syntax
        normalized = re.sub(r"groupBy\(([#\w]+)\)", r"groupBy([\1])", normalized)

        # Fix case sensitivity immediately
        normalized = re.sub(r"\bgroupby\b", "groupBy", normalized, flags=re.IGNORECASE)

        # Add common enhancements for simple groupBy queries
        if re.match(r"\*\s*\|\s*groupBy\(\[[#\w]+\]\)\s*$", normalized):
            # For simple groupBy queries, add sorting and limiting for better UX
            normalized += " | sort(_count) | head(20)"

        logger.info(f"Pre-normalized query: '{query}' → '{normalized}'")
        return normalized
