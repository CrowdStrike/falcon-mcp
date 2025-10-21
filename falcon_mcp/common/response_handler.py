"""
Universal response handler for large datasets in Falcon MCP Server

This module provides functionality to handle large API responses by:
1. Detecting when responses exceed size thresholds
2. Automatically triggering standalone data analysis scripts
3. Saving data in JSON or CSV formats
4. Returning summaries instead of full data to preserve context
5. Integrating with standalone CrowdStrike query tools
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from falcon_mcp.common.logging import get_logger

logger = get_logger(__name__)


class ResponseSizeConfig:
    """Configuration for response size thresholds - purely token-based."""

    # Token-based thresholds (only limits that matter)
    MCP_SAFE_TOKEN_THRESHOLD = 25_000  # Safe for direct MCP response
    MCP_WARNING_TOKEN_THRESHOLD = 50_000  # Return with warning message
    MCP_MAX_TOKEN_THRESHOLD = 200_000  # Force export to prevent MCP errors

    # Character estimation (rough approximation: 4 chars per token)
    TOKEN_RATIO = 4

    @classmethod
    def estimate_tokens(cls, text_size: int) -> int:
        """Estimate token count from character count."""
        return text_size // cls.TOKEN_RATIO

    @classmethod
    def get_export_action(cls, token_count: int) -> str:
        """Determine export action based purely on token count.

        Returns:
            "direct_return" | "return_with_warning" | "force_export"
        """
        if token_count <= cls.MCP_SAFE_TOKEN_THRESHOLD:
            return "direct_return"
        elif token_count <= cls.MCP_WARNING_TOKEN_THRESHOLD:
            return "return_with_warning"
        else:
            return "force_export"

    @classmethod
    def is_mcp_safe_tokens(cls, token_count: int) -> bool:
        """Check if token count is safe for MCP protocol."""
        return token_count <= cls.MCP_SAFE_TOKEN_THRESHOLD

    @classmethod
    def exceeds_mcp_warning(cls, token_count: int) -> bool:
        """Check if token count exceeds warning threshold."""
        return token_count > cls.MCP_WARNING_TOKEN_THRESHOLD

    @classmethod
    def exceeds_mcp_max(cls, token_count: int) -> bool:
        """Check if token count exceeds maximum allowed for MCP."""
        return token_count > cls.MCP_MAX_TOKEN_THRESHOLD


class LargeResponseHandler:
    """Handles large API responses with automatic data saving and analysis."""

    def __init__(self, output_dir: str = "falcon_exports"):
        """Initialize handler with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.config = ResponseSizeConfig()
        self._current_export_format: Optional[str] = None

        # Find standalone scripts
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.siem_analyzer_script = self.project_root / "siem_data_analyzer.py"

        logger.info("Initialized LargeResponseHandler with output directory: %s", self.output_dir)
        logger.info("Project root: %s", self.project_root)
        logger.info("SIEM analyzer script: %s", self.siem_analyzer_script)

    def analyze_response_size(self, data: Any) -> Tuple[int, int]:
        """Analyze response size and estimate tokens.

        Returns:
            Tuple of (character_count, estimated_tokens)
        """
        logger.debug("Analyzing response size for data type: %s", type(data).__name__)

        if isinstance(data, (list, dict)):
            json_str = json.dumps(data, default=str)
            char_count = len(json_str)
        else:
            char_count = len(str(data))

        estimated_tokens = self.config.estimate_tokens(char_count)

        logger.debug(
            "Response analysis: %d characters, ~%d estimated tokens", char_count, estimated_tokens
        )

        return char_count, estimated_tokens

    def analyze_event_count(self, data: Any) -> int:
        """Analyze data to count events/records.

        Returns:
            Number of events/records in the data
        """
        event_count = 0

        if isinstance(data, list):
            event_count = len(data)
        elif isinstance(data, dict):
            # Check for common patterns in API responses
            if "events" in data:
                events = data["events"]
                if isinstance(events, list):
                    event_count = len(events)
            elif "results" in data and isinstance(data["results"], dict):
                if "events" in data["results"]:
                    events = data["results"]["events"]
                    if isinstance(events, list):
                        event_count = len(events)
                elif isinstance(data["results"], list):
                    event_count = len(data["results"])
            elif "resources" in data and isinstance(data["resources"], list):
                event_count = len(data["resources"])

        logger.debug("Analyzed event count: %d events", event_count)
        return event_count

    def should_auto_export(
        self, data: Any, export_behavior: str = "smart"
    ) -> Tuple[bool, int, str]:
        """Check if data should be automatically exported based on token size and behavior.

        Args:
            data: The response data to analyze
            export_behavior: "smart" (token-based), "always", or "never"

        Returns:
            Tuple of (should_export, token_count, reason)
        """
        char_count, token_count = self.analyze_response_size(data)

        if export_behavior == "never":
            return (False, token_count, "Export disabled by export_behavior='never'")
        elif export_behavior == "always":
            return (True, token_count, "Export forced by export_behavior='always'")
        elif export_behavior == "smart":
            action = self.config.get_export_action(token_count)

            if action == "direct_return":
                return (
                    False,
                    token_count,
                    f"Small response ({token_count:,} tokens < "
                    f"{self.config.MCP_SAFE_TOKEN_THRESHOLD:,} threshold)",
                )
            elif action == "return_with_warning":
                return (
                    False,
                    token_count,
                    f"Medium response ({token_count:,} tokens, will warn user)",
                )
            else:  # force_export
                return (
                    True,
                    token_count,
                    f"Large response ({token_count:,} tokens > "
                    f"{self.config.MCP_WARNING_TOKEN_THRESHOLD:,} threshold)",
                )
        else:
            # Fallback to smart behavior
            return self.should_auto_export(data, "smart")

    def check_mcp_token_limit(self, data: Any) -> Tuple[bool, int, str]:
        """Check if response exceeds MCP token limits.

        Returns:
            Tuple of (exceeds_limit, token_count, action_required)
        """
        char_count, token_count = self.analyze_response_size(data)

        if self.config.exceeds_mcp_max(token_count):
            return (True, token_count, "force_export")
        elif self.config.exceeds_mcp_warning(token_count):
            return (True, token_count, "warn_and_truncate")
        elif not self.config.is_mcp_safe_tokens(token_count):
            return (True, token_count, "warn_user")
        else:
            return (False, token_count, "safe")

    def create_token_safe_response(
        self, data: Any, operation: str, sample_events: int = 5
    ) -> Dict[str, Any]:
        """Create a response that's guaranteed to be within token limits.

        Args:
            data: The original response data
            operation: Operation name for context
            sample_events: Number of events to include in safe response

        Returns:
            Token-safe response with metadata
        """
        exceeds_limit, token_count, action = self.check_mcp_token_limit(data)

        if not exceeds_limit:
            return {"data": data, "token_safe": True, "token_count": token_count}

        logger.warning(
            "Response exceeds MCP token limits: %d tokens (max: %d), action: %s",
            token_count,
            self.config.MCP_MAX_TOKEN_THRESHOLD,
            action,
        )

        # Force export for very large responses
        if action == "force_export":
            # Auto-export to file and return minimal response
            # Use export_format from original handle_api_response call
            if hasattr(self, "_current_export_format") and self._current_export_format == "csv":
                filepath = self.save_to_csv(data, f"{operation}_auto_export_large")
            else:
                filepath = self.save_to_json(data, f"{operation}_auto_export_large")

            sample_response = self.create_sample_response(data, sample_events)

            return {
                "token_safe": True,
                "action_taken": "auto_exported",
                "original_token_count": token_count,
                "max_allowed_tokens": self.config.MCP_MAX_TOKEN_THRESHOLD,
                "export_file": filepath,
                "data": sample_response["sample_data"],
                "total_events": sample_response["total_events"],
                "sample_events_count": sample_response["sample_events_count"],
                "message": (
                    f"⚠️ Response too large for MCP protocol ({token_count:,} tokens > "
                    f"{self.config.MCP_MAX_TOKEN_THRESHOLD:,} limit).\n"
                    f"📁 Full data exported to: {filepath}\n"
                    f"📊 {sample_response['sample_note']}"
                ),
                "warning": f"Original response ({token_count:,} tokens) exceeded MCP limits and was auto-exported",
            }

        # For warning-level responses, truncate and warn
        elif action in ["warn_and_truncate", "warn_user"]:
            sample_response = self.create_sample_response(data, sample_events)

            return {
                "token_safe": True,
                "action_taken": "truncated",
                "original_token_count": token_count,
                "safe_token_threshold": self.config.MCP_SAFE_TOKEN_THRESHOLD,
                "data": sample_response["sample_data"],
                "total_events": sample_response["total_events"],
                "sample_events_count": sample_response["sample_events_count"],
                "message": (
                    f"⚠️ Large response ({token_count:,} tokens) truncated to prevent MCP errors.\n"
                    f"📊 {sample_response['sample_note']}\n"
                    f"💡 For full data, use download=True or export to file"
                ),
                "warning": f"Response truncated from {token_count:,} to ~{self.config.estimate_tokens(len(json.dumps(sample_response['sample_data'], default=str))):,} tokens",
            }

        # Fallback - should not reach here
        return {"data": data, "token_safe": False, "token_count": token_count}

    def should_handle_large_response(self, data: Any) -> bool:
        """Check if response should be handled as large based on token count."""
        char_count, estimated_tokens = self.analyze_response_size(data)
        action = self.config.get_export_action(estimated_tokens)
        is_large = action != "direct_return"

        if is_large:
            logger.info(
                "Large response detected: %d characters, ~%d tokens (action: %s)",
                char_count,
                estimated_tokens,
                action,
            )
        else:
            logger.debug(
                "Normal response size: %d characters, ~%d tokens", char_count, estimated_tokens
            )

        return is_large

    def generate_summary(self, data: Any, operation: str) -> Dict[str, Any]:
        """Generate a summary of the large response."""
        logger.debug("Generating summary for operation: %s", operation)
        char_count, estimated_tokens = self.analyze_response_size(data)

        summary: Dict[str, Any] = {
            "operation": operation,
            "response_size": {
                "characters": char_count,
                "estimated_tokens": estimated_tokens,
                "size_category": self._get_size_category(char_count),
            },
            "timestamp": datetime.now().isoformat(),
            "data_type": type(data).__name__,
        }

        # Add type-specific summary information
        if isinstance(data, list):
            summary["record_count"] = len(data)
            logger.debug("List data: %d records", len(data))
            if data and isinstance(data[0], dict):
                sample_fields = list(data[0].keys())[:10]
                summary["sample_fields"] = sample_fields
                logger.debug("Sample fields from first record: %s", sample_fields)
        elif isinstance(data, dict):
            summary["field_count"] = len(data.keys())
            top_fields = list(data.keys())[:10]
            summary["top_level_fields"] = top_fields
            logger.debug("Dict data: %d fields, top fields: %s", len(data.keys()), top_fields)

        logger.info(
            "Generated summary for %s: %s category, %d chars, ~%d tokens",
            operation,
            summary["response_size"]["size_category"],
            char_count,
            estimated_tokens,
        )

        return summary

    def _get_size_category(self, char_count: int) -> str:
        """Categorize response size based on token count."""
        token_count = self.config.estimate_tokens(char_count)
        action = self.config.get_export_action(token_count)

        if action == "force_export":
            return "critical"
        elif action == "return_with_warning":
            return "warning"
        else:
            return "normal"

    def save_to_json(self, data: Any, operation: str, filename: Optional[str] = None) -> str:
        """Save data to JSON file."""
        logger.debug("Preparing to save data to JSON for operation: %s", operation)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{operation}_{timestamp}.json"

        filepath = self.output_dir / filename
        logger.info("Saving JSON data to: %s", filepath)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)

        json_size = len(json.dumps(data, default=str))
        logger.info("Saved %d characters to %s", json_size, filepath)
        return str(filepath)

    def save_to_csv(self, data: Any, operation: str, filename: Optional[str] = None) -> str:
        """Save data to CSV file with optional metadata header for NG-SIEM queries."""
        logger.debug("Preparing to save data to CSV for operation: %s", operation)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{operation}_{timestamp}.csv"

        filepath = self.output_dir / filename
        logger.info("Saving CSV data to: %s", filepath)

        # Check if this is NG-SIEM query data with metadata
        has_query_metadata = isinstance(data, dict) and any(
            key in data for key in ["query", "time_range", "search_id", "results"]
        )

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            # Write metadata header for NG-SIEM queries
            if has_query_metadata:
                logger.debug("Adding NG-SIEM query metadata header to CSV")

                # Extract metadata for header
                query_info = {
                    "query": data.get("query", ""),
                    "time_range": data.get("time_range", ""),
                    "time_params": json.dumps(data.get("time_params", {}), default=str),
                    "time_range_display": data.get("time_range_display", ""),
                    "result_count": data.get("result_count", 0),
                    "execution_time": data.get("execution_time", ""),
                }

                # Write metadata header
                f.write("# Query Metadata\n")
                writer = csv.DictWriter(f, fieldnames=query_info.keys())
                writer.writeheader()
                writer.writerow(query_info)
                f.write("\n# Event Data\n")

                # Extract events for CSV data section
                events_data = []
                if "results" in data and isinstance(data["results"], dict):
                    if "events" in data["results"] and isinstance(data["results"]["events"], list):
                        events_data = data["results"]["events"]
                elif "events" in data and isinstance(data["events"], list):
                    events_data = data["events"]

                if events_data and isinstance(events_data[0], dict):
                    # Write events as CSV
                    fieldnames = set()
                    for record in events_data:
                        fieldnames.update(record.keys())

                    writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                    writer.writeheader()
                    for record in events_data:
                        # Flatten complex fields to strings
                        flat_record = {}
                        for key, value in record.items():
                            if isinstance(value, (dict, list)):
                                flat_record[key] = json.dumps(value, default=str)
                            else:
                                flat_record[key] = value
                        writer.writerow(flat_record)
                else:
                    # No events found, write a note
                    f.write("# No event data found in response\n")

            elif isinstance(data, list) and data and isinstance(data[0], dict):
                # List of dictionaries - standard CSV export
                logger.debug("Processing list of %d dictionaries for CSV export", len(data))
                fieldnames = set()
                for record in data:
                    fieldnames.update(record.keys())

                logger.debug(
                    "CSV will have %d columns: %s", len(fieldnames), sorted(list(fieldnames))[:10]
                )

                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                for record in data:
                    # Flatten complex fields to strings
                    flat_record = {}
                    for key, value in record.items():
                        if isinstance(value, (dict, list)):
                            flat_record[key] = json.dumps(value, default=str)
                        else:
                            flat_record[key] = value
                    writer.writerow(flat_record)

            elif isinstance(data, dict):
                # Single dictionary - transpose to key-value CSV
                logger.debug("Processing single dictionary with %d keys for CSV export", len(data))
                csv_writer = csv.writer(f)
                csv_writer.writerow(["Field", "Value"])
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, default=str)
                    csv_writer.writerow([key, value])

            else:
                # Fallback - convert to string and save as single column
                logger.debug("Processing fallback data type %s for CSV export", type(data).__name__)
                csv_writer = csv.writer(f)
                csv_writer.writerow(["Data"])
                csv_writer.writerow([str(data)])

        logger.info("Saved data to CSV: %s", filepath)
        return str(filepath)

    def extract_events_for_export(self, data: Any) -> List[Dict[str, Any]]:
        """Extract events/records from data structure for export.

        Returns:
            List of dictionaries suitable for export
        """
        events = []

        if isinstance(data, list):
            # Direct list of events
            events = data
        elif isinstance(data, dict):
            # Check for common patterns in API responses
            if "events" in data and isinstance(data["events"], list):
                events = data["events"]
            elif "results" in data:
                results = data["results"]
                if (
                    isinstance(results, dict)
                    and "events" in results
                    and isinstance(results["events"], list)
                ):
                    events = results["events"]
                elif isinstance(results, list):
                    events = results
            elif "resources" in data and isinstance(data["resources"], list):
                events = data["resources"]

        logger.debug("Extracted %d events for export", len(events))
        return events

    def create_sample_response(self, data: Any, sample_events: int = 3) -> Dict[str, Any]:
        """Create a sampled version of the response data for Claude processing.

        Args:
            data: The full response data
            sample_events: Number of events to include in sample

        Returns:
            Dictionary with sampled data and metadata
        """
        logger.debug("Creating sample response with %d events", sample_events)

        if sample_events <= 0:
            # Return summary only, no sample data
            return {
                "sample_data": None,
                "total_events": self.analyze_event_count(data),
                "sample_note": "No sample events requested (sample_events=0)",
            }

        sample_data: Optional[Any] = None
        total_events = 0

        if isinstance(data, list):
            total_events = len(data)
            sample_data = data[:sample_events] if data else []
        elif isinstance(data, dict):
            # Extract events from common API response patterns
            events = self.extract_events_for_export(data)
            total_events = len(events)

            if events:
                sample_events_data = events[:sample_events]
                # Reconstruct the data structure with sample events
                sample_data_dict = data.copy()

                if "events" in data:
                    sample_data_dict["events"] = sample_events_data
                elif "results" in data:
                    if isinstance(data["results"], dict) and "events" in data["results"]:
                        sample_data_dict["results"] = data["results"].copy()
                        sample_data_dict["results"]["events"] = sample_events_data
                    elif isinstance(data["results"], list):
                        sample_data_dict["results"] = sample_events_data
                elif "resources" in data:
                    sample_data_dict["resources"] = sample_events_data

                sample_data = sample_data_dict
            else:
                # No events found, return first few key-value pairs
                sample_data = dict(list(data.items())[:sample_events])

        sample_note = (
            f"Showing {min(sample_events, total_events)} sample events out of {total_events} total"
        )
        if total_events == 0:
            sample_note = "No events found in response"
        elif total_events <= sample_events:
            sample_note = f"Showing all {total_events} events (within sample limit)"

        logger.debug(
            "Sample created: %d events sampled from %d total",
            min(sample_events, total_events),
            total_events,
        )

        return {
            "sample_data": sample_data,
            "total_events": total_events,
            "sample_events_count": min(sample_events, total_events),
            "sample_note": sample_note,
        }

    def auto_export_large_dataset(
        self, data: Any, operation: str, export_format: str = "csv", export_behavior: str = "smart"
    ) -> Optional[Dict[str, Any]]:
        """Automatically export datasets based on token size and behavior.

        Args:
            data: The data to potentially export
            operation: Operation name for file naming
            export_format: Format to export to ("json" or "csv")
            export_behavior: "smart" (token-based), "always", or "never"

        Returns:
            Dictionary with export results if auto-export was triggered,
            None otherwise
        """
        should_export, token_count, reason = self.should_auto_export(data, export_behavior)

        if not should_export:
            logger.debug("Auto-export not triggered: %s", reason)
            return None

        logger.info("Auto-export triggered: %s", reason)

        # Extract events for export
        events = self.extract_events_for_export(data)
        export_data = events if events else data

        # Save data in the specified format
        if export_format.lower() == "csv":
            filepath = self.save_to_csv(export_data, f"{operation}_auto_export")
            file_type = "CSV"
        else:
            filepath = self.save_to_json(export_data, f"{operation}_auto_export")
            file_type = "JSON"

        # Create a summary to return instead of full data
        summary = {
            "auto_export_triggered": True,
            "reason": reason,
            "token_count": token_count,
            "export_file": filepath,
            "export_format": export_format.upper(),
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "message": (
                f"🚀 Large dataset auto-exported to {file_type} to save "
                f"tokens! {token_count:,} tokens saved to "
                f"{Path(filepath).name}"
            ),
            "token_savings": (f"Estimated token savings: ~{token_count:,} tokens"),
        }

        # Add sample of first few events for reference
        if export_data:
            sample_response = self.create_sample_response(
                export_data, 3
            )  # Always show 3 for auto-export
            summary["sample_events"] = sample_response["sample_data"]
            summary["sample_note"] = sample_response["sample_note"]

        logger.info("Auto-export completed: %s", filepath)
        return summary

    def handle_large_response(
        self,
        data: Any,
        operation: str,
        export_format: str = "json",
        export_behavior: str = "smart",
        sample_events: int = 3,
    ) -> Dict[str, Any]:
        """Handle a response based on export behavior.

        Args:
            data: The response data
            operation: Operation name for context
            export_format: Format for export ("json" or "csv")
            export_behavior: "smart" (token-based), "always", or "never"
            sample_events: Number of sample events to return to Claude (default: 3)

        Returns:
            Dictionary with either full data or summary + file path
        """
        logger.info(
            "Starting response handling for operation: %s, export_behavior: %s",
            operation,
            export_behavior,
        )

        # Handle explicit export request
        if export_behavior == "always":
            logger.info(
                "Export behavior 'always': automatically saving to falcon_exports directory"
            )
            if export_format.lower() == "csv":
                filepath = self.save_to_csv(data, operation)
            else:
                filepath = self.save_to_json(data, operation)

            # Create sample response for Claude
            sample_response = self.create_sample_response(data, sample_events)

            return {
                "handled": True,
                "action": "forced_export",
                "file_path": filepath,
                "data": sample_response["sample_data"],  # Only sample data for Claude
                "total_events": sample_response["total_events"],
                "sample_events_count": sample_response["sample_events_count"],
                "sample_note": sample_response["sample_note"],
                "message": (
                    f"Results saved to falcon_exports: {Path(filepath).name}. "
                    f"{sample_response['sample_note']} shown below."
                ),
            }

        # Handle never export
        if export_behavior == "never":
            logger.debug("Export behavior 'never': returning data as-is")
            return {"data": data, "handled": False}

        # Handle smart behavior (token-based)
        if not self.should_handle_large_response(data):
            logger.debug("Response size is normal, returning data as-is")
            return {"data": data, "handled": False}

        summary = self.generate_summary(data, operation)
        logger.info(
            "Generated summary for large response: %s category, %d chars",
            summary["response_size"]["size_category"],
            summary["response_size"]["characters"],
        )

        # Auto-save based on export format for smart behavior
        if export_format.lower() == "csv":
            logger.info("Auto-saving as CSV")
            filepath = self.save_to_csv(data, operation)
            logger.info("Auto-saved large response to: %s", filepath)
            return {
                "handled": True,
                "action": "auto_save_csv",
                "summary": summary,
                "file_path": filepath,
                "message": (f"Large response automatically saved to {Path(filepath).name}"),
            }
        else:
            logger.info("Auto-saving as JSON")
            filepath = self.save_to_json(data, operation)
            logger.info("Auto-saved large response to: %s", filepath)
            return {
                "handled": True,
                "action": "auto_save_json",
                "summary": summary,
                "file_path": filepath,
                "message": (f"Large response automatically saved to {Path(filepath).name}"),
            }


# Global handler instance
_response_handler = None


def get_response_handler(output_dir: str = "falcon_exports") -> LargeResponseHandler:
    """Get or create global response handler instance."""
    global _response_handler
    if _response_handler is None:
        logger.debug("Creating new global response handler instance")
        _response_handler = LargeResponseHandler(output_dir)
    else:
        logger.debug("Using existing global response handler instance")
    return _response_handler


def handle_api_response(
    response: Dict[str, Any],
    operation: str = "api_operation",
    error_message: str = "API operation failed",
    export_behavior: str = "smart",
    export_format: str = "json",
    sample_events: int = 3,
) -> Dict[str, Any]:
    """Handle API response with token-safe processing and flexible export behavior.

    This is a convenience function that modules can use to automatically
    handle responses based on token size and export preferences.

    Args:
        response: The API response data
        operation: Operation name for file naming
        error_message: Error message if the operation failed
        export_behavior: "smart" (token-based), "always", or "never"
        export_format: Format for export ("json" or "csv")
        sample_events: Number of sample events to return to Claude (default: 3)

    Returns:
        Token-safe response, export summary, or full data based on behavior
    """
    logger.debug(
        "Handling API response for operation: %s with export_behavior: %s",
        operation,
        export_behavior,
    )

    # Check for API errors first
    if isinstance(response, dict):
        status_code = response.get("status_code", 200)
        if status_code != 200:
            error_data = response.get("body", {})
            if isinstance(error_data, dict) and "errors" in error_data:
                errors = error_data["errors"]
                if errors:
                    error_msg = errors[0].get("message", "Unknown error")
                    logger.error("API error: %s", error_msg)
                    return {
                        "error": f"{error_message}: {error_msg}",
                        "status_code": status_code,
                        "details": response,
                    }

    # Get handler instance
    handler = get_response_handler()

    # Store export format for use in create_token_safe_response
    handler._current_export_format = export_format

    # Handle explicit export requests FIRST - export_behavior="always" overrides token limits
    if export_behavior == "always":
        logger.info("Export behavior 'always': saving response to falcon_exports directory")
        return handler.handle_large_response(
            response,
            operation,
            export_format=export_format,
            export_behavior="always",
            sample_events=sample_events,
        )

    # CRITICAL: Check MCP token limits for responses that aren't being force-exported
    exceeds_limit, token_count, action = handler.check_mcp_token_limit(response)

    if exceeds_limit:
        logger.warning(
            "Response exceeds MCP token limits (%d tokens), using token-safe handling", token_count
        )
        # Return token-safe response immediately - this prevents MCP API errors
        return handler.create_token_safe_response(response, operation, sample_events)

    # Handle never export
    if export_behavior == "never":
        logger.debug("Export behavior 'never': returning response as-is")
        return response

    # Handle smart behavior - try auto-export for large datasets
    auto_export_result = handler.auto_export_large_dataset(
        response, operation, export_format, export_behavior
    )

    if auto_export_result:
        logger.info("Large dataset auto-exported for %s", operation)
        return auto_export_result
    else:
        logger.debug("No auto-export needed for %s", operation)
        return response
