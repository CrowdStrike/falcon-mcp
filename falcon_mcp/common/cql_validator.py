"""
CQL Syntax Validation and Conversion Utilities

This module provides utilities to validate LogScale/CQL syntax and convert
common Splunk syntax patterns to proper CQL equivalents.
"""

import re
from typing import Any, Dict, cast


class CQLSyntaxValidator:
    """Validates and converts query syntax to proper LogScale/CQL format."""

    def __init__(self) -> None:
        """Initialize the validator with conversion patterns."""
        # Splunk to CQL conversion patterns
        self.splunk_to_cql_patterns = {
            # Stats aggregations
            r"\|\s*stats\s+count\(\)\s+by\s+(\w+)": r"| groupBy(\1)",
            r"\|\s*stats\s+count\(\)\s+by\s+(\w+),\s*(\w+)": r"| groupBy([\1, \2])",
            r"\|\s*stats\s+count\(\)\s+by\s+(.+)": r"| groupBy(\1)",
            # Head/limit
            r"\|\s*head\s+(\d+)": r"| head(\1)",
            r"\|\s*limit\s+(\d+)": r"| head(\1)",
            # Sort patterns
            r"\|\s*sort\s+(\w+)\s+desc": r"| sort(\1, order=desc)",
            r"\|\s*sort\s+(\w+)\s+asc": r"| sort(\1, order=asc)",
            r"\|\s*sort\s+(\w+)": r"| sort(\1)",
            r"\|\s*sort\s+-(\w+)": r"| sort(\1, order=desc)",
            r"\|\s*sort\s+\+?(\w+)": r"| sort(\1, order=asc)",
            # Table to select
            r"\|\s*table\s+(.+)": r"| select([\1])",
            # WHERE CLAUSE - Convert Splunk where to CQL direct filtering
            r'\|\s*where\s+(\w+)\s*=\s*(["\']?)([^"\']+)\2': r'AND \1="\3"',
            r'\|\s*where\s+(\w+)\s*!=\s*(["\']?)([^"\']+)\2': r'AND \1!="\3"',
            r"\|\s*where\s+(\w+)\s*>\s*(\d+)": r"AND \1>\2",
            r"\|\s*where\s+(\w+)\s*<\s*(\d+)": r"AND \1<\2",
            r"\|\s*where\s+(\w+)\s*>=\s*(\d+)": r"AND \1>=\2",
            r"\|\s*where\s+(\w+)\s*<=\s*(\d+)": r"AND \1<=\2",
            # Regex patterns - Convert Splunk regex to CQL format
            r'\|\s*rex\s+field=(\w+)\s+["\']([^"\']+)["\']': r"AND \1=/\2/",
            r'(\w+)\s*=\s*["\'][*]([^*"\']+)[*]["\']': r"\1=/\2/i",
            # Rename (LogScale uses different syntax)
            r"\|\s*rename\s+(\w+)\s+AS\s+(\w+)": r"| eval \2 = \1",
        }

        # Common CQL syntax errors and corrections
        self.common_errors = {
            "stats count() by": "Use groupBy() instead of stats count() by",
            "head ": "Use head() with parentheses: head(100)",
            "sort field desc": "Use sort(field, order=desc)",
            "sort field asc": "Use sort(field, order=asc)",
            "| table": "Use | select([field1, field2]) instead of | table",
            "| where": "CQL uses direct filtering: field=value (no where clause)",
            "| grep": "Use field regex instead: field_name=/pattern/i (not grep function)",
            "rename": "Use | eval new_field = old_field instead of rename",
        }

    def validate_and_convert(self, query: str) -> Dict[str, Any]:
        """
        Validate CQL syntax and convert Splunk patterns if found.

        Args:
            query: The query string to validate and convert

        Returns:
            Dict with validation results, converted query, and suggestions
        """
        result = {
            "original_query": query,
            "converted_query": query,
            "is_valid_cql": True,
            "splunk_patterns_found": [],
            "corrections_made": [],
            "warnings": [],
            "suggestions": [],
            "syntax_errors": [],
        }

        # Check for Splunk patterns and convert
        converted_query = self._convert_splunk_to_cql(query, result)
        result["converted_query"] = converted_query

        # Validate CQL syntax
        self._validate_cql_syntax(converted_query, result)

        # Check for common errors
        self._check_common_errors(query, result)

        # Provide CQL best practices suggestions
        self._suggest_improvements(converted_query, result)

        return result

    def _convert_splunk_to_cql(self, query: str, result: Dict) -> str:
        """Convert Splunk syntax patterns to CQL."""
        converted = query

        for splunk_pattern, cql_replacement in self.splunk_to_cql_patterns.items():
            matches = re.findall(splunk_pattern, query, re.IGNORECASE)
            if matches:
                # Record what was found
                result["splunk_patterns_found"].append(
                    {"pattern": splunk_pattern, "matches": matches, "replacement": cql_replacement}
                )

                # Apply conversion
                old_converted = converted
                converted = re.sub(splunk_pattern, cql_replacement, converted, flags=re.IGNORECASE)

                if old_converted != converted:
                    result["corrections_made"].append(
                        {"from": old_converted, "to": converted, "type": "splunk_to_cql_conversion"}
                    )

        return converted

    def _validate_cql_syntax(self, query: str, result: Dict) -> None:
        """Validate CQL-specific syntax patterns."""

        # Check for lowercase function names (CQL is case-sensitive)
        lowercase_functions = ["groupby", "groupby(", "selectfrom", "orderby"]
        for func in lowercase_functions:
            if func in query.lower() and func in query:
                if func == "groupby":
                    result["syntax_errors"].append(
                        {
                            "error": f'Case sensitivity error: "{func}" should be "groupBy"',
                            "message": 'CQL function names are case-sensitive. Use "groupBy" not "groupby"',
                            "severity": "error",
                            "suggestion": "Change groupby to groupBy (camelCase)",
                        }
                    )
                    result["is_valid_cql"] = False

                    # Auto-correct the case
                    corrected = re.sub(r"\bgroupby\b", "groupBy", query, flags=re.IGNORECASE)
                    if corrected != query:
                        result["converted_query"] = corrected
                        result["corrections_made"].append(
                            {
                                "from": query,
                                "to": corrected,
                                "type": "case_correction",
                                "field": "groupby -> groupBy",
                            }
                        )

        # Check for proper function syntax
        function_patterns = [
            (r"\|\s*groupBy\s*\([^)]+\)", "groupBy function syntax looks correct"),
            (r"\|\s*sort\s*\([^)]+\)", "sort function syntax looks correct"),
            (r"\|\s*head\s*\(\s*\d+\s*\)", "head function syntax looks correct"),
        ]

        for pattern, message in function_patterns:
            if re.search(pattern, query):
                result["suggestions"].append(
                    {"type": "syntax_validation", "message": message, "severity": "info"}
                )

        # Check for missing pipe operator before groupBy
        if re.search(r"\*\s+groupby\s+", query, re.IGNORECASE):
            result["syntax_errors"].append(
                {
                    "error": "Missing pipe operator before groupBy",
                    "message": "Use * | groupBy() syntax with proper pipes",
                    "severity": "error",
                    "suggestion": "Add | before groupBy and use proper syntax",
                }
            )
            result["is_valid_cql"] = False

            # Auto-correct: * groupby field → * | groupBy([field])
            corrected = re.sub(
                r"\*\s+groupby\s+([#\w]+)", r"* | groupBy([\1])", query, flags=re.IGNORECASE
            )
            if corrected != query:
                result["converted_query"] = corrected
                result["corrections_made"].append(
                    {"from": query, "to": corrected, "type": "pipe_and_groupby_correction"}
                )

        # Check for missing pipe operator in other groupBy patterns
        if re.search(r"([^\|])\s+groupby\s+([#\w]+)", query, re.IGNORECASE):
            result["syntax_errors"].append(
                {
                    "error": "Missing pipe operator before groupBy",
                    "message": "groupBy requires pipe operator: | groupBy()",
                    "severity": "error",
                    "suggestion": "Add | before groupBy",
                }
            )
            result["is_valid_cql"] = False

            # Auto-correct: query groupby field → query | groupBy([field])
            corrected = re.sub(
                r"([^\|])\s+groupby\s+([#\w]+)", r"\1 | groupBy([\2])", query, flags=re.IGNORECASE
            )
            if corrected != query:
                result["converted_query"] = corrected
                result["corrections_made"].append(
                    {"from": query, "to": corrected, "type": "pipe_and_groupby_correction"}
                )

        # Check for proper groupBy syntax
        if re.search(r"groupBy\s*\[", query) and not re.search(r"groupBy\s*\(\[", query):
            result["syntax_errors"].append(
                {
                    "error": "Invalid groupBy syntax - missing parentheses",
                    "message": "groupBy with arrays requires parentheses: groupBy([field1, field2])",
                    "severity": "error",
                    "suggestion": "Use groupBy([field]) for arrays or groupBy(field) for single fields",
                }
            )
            result["is_valid_cql"] = False

            # Auto-correct by adding parentheses
            corrected = re.sub(r"groupBy\s*\[([^]]+)\]", r"groupBy([\1])", query)
            if corrected != query:
                result["converted_query"] = corrected
                result["corrections_made"].append(
                    {"from": query, "to": corrected, "type": "groupby_parentheses_correction"}
                )

        # Ensure single fields in groupBy use array syntax for consistency
        if re.search(r"groupBy\s*\(\s*([#\w]+)\s*\)", query) and not re.search(
            r"groupBy\s*\(\s*\[", query
        ):
            corrected = re.sub(r"groupBy\s*\(\s*([#\w]+)\s*\)", r"groupBy([\1])", query)
            if corrected != query:
                result["converted_query"] = corrected
                result["corrections_made"].append(
                    {"from": query, "to": corrected, "type": "groupby_array_normalization"}
                )

        # Check for groupBy without parentheses at all
        if re.search(r"groupBy\s+([#\w]+)(?!\s*[\(\[])", query):
            result["syntax_errors"].append(
                {
                    "error": "Invalid groupBy syntax - missing parentheses",
                    "message": "groupBy requires parentheses around field names",
                    "severity": "error",
                    "suggestion": "Use groupBy(field) instead of groupBy field",
                }
            )
            result["is_valid_cql"] = False

            # Auto-correct by adding parentheses
            corrected = re.sub(r"groupBy\s+([#\w]+)(?!\s*[\(\[])", r"groupBy(\1)", query)
            if corrected != query:
                result["converted_query"] = corrected
                result["corrections_made"].append(
                    {"from": query, "to": corrected, "type": "groupby_parentheses_correction"}
                )

        # Check for old LogScale sort syntax (LogScale now uses different syntax)
        if re.search(r"sort\([^,)]+,\s*order\s*=\s*(asc|desc)\)", query):
            result["syntax_errors"].append(
                {
                    "error": "Outdated sort syntax detected",
                    "message": "LogScale sort syntax has changed. Use sort(field) for ascending or sort(field, order=desc) for descending",
                    "severity": "warning",
                    "suggestion": "Use sort(field) or sort(field, order=desc) syntax",
                }
            )

        # More comprehensive validation for sort function
        if re.search(r"sort\s*\([^)]*order\s*=", query):
            # Check if the syntax matches the expected pattern exactly
            if not re.search(r"sort\s*\(\s*[#\w\[\],\s]+,\s*order\s*=\s*(asc|desc)\s*\)", query):
                result["syntax_errors"].append(
                    {
                        "error": "Invalid sort syntax",
                        "message": "Sort with order parameter syntax: sort(field, order=desc)",
                        "severity": "error",
                        "suggestion": "Use sort(field, order=desc) or sort(field, order=asc)",
                    }
                )
                result["is_valid_cql"] = False

        # Check for invalid CQL patterns
        if "| where " in query:
            result["syntax_errors"].append(
                {
                    "error": "Invalid where clause detected",
                    "message": "CQL uses direct filtering (field=value), not | where clauses",
                    "severity": "error",
                    "suggestion": "Use direct filtering: field=value or field=/regex/i",
                }
            )
            result["is_valid_cql"] = False

        if "| grep" in query:
            result["syntax_errors"].append(
                {
                    "error": "Invalid grep function detected",
                    "message": "CQL does not use grep functions for filtering",
                    "severity": "error",
                    "suggestion": "Use field regex: field_name=/pattern/i instead of | grep(/pattern/)",
                }
            )
            result["is_valid_cql"] = False

        if "| stats " in query and "groupBy" not in query:
            result["syntax_errors"].append(
                {
                    "error": "Splunk stats syntax detected",
                    "message": "Use groupBy() instead of stats for aggregations in CQL",
                    "severity": "error",
                }
            )
            result["is_valid_cql"] = False

        # Check for proper regex syntax
        if re.search(r"=.*\*.*\*", query) and not re.search(r"=/.*/", query):
            result["suggestions"].append(
                {
                    "pattern": "wildcard_usage",
                    "message": "Wildcards (*pattern*) are valid. You can also use regex (/pattern/i) for case-insensitive matching",
                    "severity": "info",
                }
            )

        # Check for missing # prefix on event fields
        event_fields_without_hash = ["event_simpleName", "Vendor", "type", "repo"]

        for field in event_fields_without_hash:
            # Look for the field without # prefix but exclude cases where it's already correct
            if re.search(rf"\b{field}\s*=", query) and not re.search(rf"#{field}\s*=", query):
                result["syntax_errors"].append(
                    {
                        "error": f"Missing # prefix on {field} field",
                        "message": f'Field "{field}" should be "#{field}" for proper event filtering',
                        "severity": "error",
                        "suggestion": f"Use #{field} instead of {field}",
                        "corrected_field": f"#{field}",
                    }
                )
                result["is_valid_cql"] = False

                # Auto-correct the query
                corrected_query = re.sub(rf"\b{field}\s*=", f"#{field}=", query)
                if corrected_query != query:
                    result["converted_query"] = corrected_query
                    result["corrections_made"].append(
                        {
                            "from": query,
                            "to": corrected_query,
                            "type": "hash_prefix_correction",
                            "field": field,
                        }
                    )

        # Check for proper field references
        if re.search(r"#event_simpleName\s*=\s*\w+", query):
            result["suggestions"].append(
                {
                    "type": "best_practice",
                    "message": "Good! Starting with event type filter",
                    "severity": "info",
                }
            )

    def _check_common_errors(self, query: str, result: Dict) -> None:
        """Check for common syntax errors."""

        for error_pattern, correction in self.common_errors.items():
            if error_pattern in query.lower():
                result["warnings"].append(
                    {"pattern": error_pattern, "message": correction, "severity": "warning"}
                )

    def _suggest_improvements(self, query: str, result: Dict) -> None:
        """Suggest CQL best practices and improvements."""

        suggestions = []

        # Check if query starts with event type
        if not re.search(r"#event_simpleName\s*=", query):
            suggestions.append(
                {
                    "type": "performance",
                    "message": "Consider starting with #event_simpleName=EventType for better performance",
                    "severity": "warning",
                    "example": "#event_simpleName=ProcessRollup2",
                }
            )

        # Check for result limiting
        if not re.search(r"\|\s*head\s*\(", query):
            suggestions.append(
                {
                    "type": "performance",
                    "message": "Consider adding result limit to prevent large result sets",
                    "severity": "info",
                    "example": "| head(1000)",
                }
            )

        # Check for platform filtering
        if "event_platform" not in query and "#event_simpleName" in query:
            suggestions.append(
                {
                    "type": "optimization",
                    "message": "Consider adding platform filter for more targeted results",
                    "severity": "info",
                    "example": "AND event_platform=Win",
                }
            )

        result["suggestions"].extend(suggestions)

    def get_cql_syntax_guide(self) -> Dict[str, Dict[str, str]]:
        """Get a quick reference for CQL syntax."""
        return {
            "aggregation": {
                "splunk": "| stats count() by field",
                "cql": "| groupBy(field)",
                "example": "#event_simpleName=ProcessRollup2 | groupBy(ComputerName)",
            },
            "sorting": {
                "splunk": "| sort field desc",
                "cql": "| sort(field, order=desc)",
                "example": "| sort(timestamp, order=desc)",
            },
            "limiting": {"splunk": "| head 100", "cql": "| head(100)", "example": "| head(1000)"},
            "field_selection": {
                "splunk": "| table field1, field2",
                "cql": "| select([field1, field2])",
                "example": "| select([ComputerName, UserName, CommandLine])",
            },
            "filtering": {
                "splunk": "| where field=value",
                "cql": "field=value (direct filtering)",
                "example": "ProcessId>1000 AND event_platform=Win",
            },
            "wildcard_filtering": {
                "splunk": "field=*value*",
                "cql": "field=*value* (wildcards work in CQL too)",
                "example": "CommandLine=*powershell* (simple pattern matching)",
            },
            "regex_filtering": {
                "splunk": '| rex field=CommandLine "pattern"',
                "cql": "CommandLine=/pattern/i",
                "example": "CommandLine=/powershell/i (case-insensitive regex)",
            },
            "pattern_comparison": {
                "wildcards": "CommandLine=*powershell* (simple, case-sensitive)",
                "regex": "CommandLine=/powershell/i (powerful, case-insensitive)",
                "example": "Both are valid CQL - choose based on your needs",
            },
            "pattern_search": {
                "splunk": '| rex field=field "pattern" | search extracted_field=value',
                "cql": "field_name=/pattern/i (direct field regex)",
                "example": "CommandLine=/threat|malicious|suspicious/i",
            },
            "content_filtering": {
                "wrong": "| grep(/pattern/) (does not work in CQL)",
                "correct": "field_name=/pattern/i (field-specific regex)",
                "example": "ImageFileName=/malware|trojan|virus/i",
            },
            "event_filtering": {
                "splunk": "sourcetype=event_type",
                "cql": "#event_simpleName=EventType",
                "example": "#event_simpleName=ProcessRollup2",
            },
        }


# Convenience function for quick validation
def validate_cql_query(query: str) -> Dict[str, Any]:
    """Quick validation function for CQL queries."""
    validator = CQLSyntaxValidator()
    return validator.validate_and_convert(query)


# Convenience function for quick conversion
def convert_splunk_to_cql(query: str) -> str:
    """Quick conversion from Splunk to CQL syntax."""
    validator = CQLSyntaxValidator()
    result = validator.validate_and_convert(query)
    return cast(str, result["converted_query"])
