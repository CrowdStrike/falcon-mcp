"""
Query Component Detector utility class for analyzing and extracting components from CQL queries.

This utility helps detect various query patterns and extract components that can be used
for query validation, auto-correction, and intelligent query building.
"""

import re
from typing import Any, Dict, List, Optional

from falcon_mcp.common.logging import get_logger

logger = get_logger(__name__)


class QueryComponentDetector:
    """Utility class for detecting and extracting components from CQL queries."""

    def __init__(self) -> None:
        """Initialize the query component detector."""
        self.event_fields_needing_hash = {"event_simpleName", "Vendor", "type", "repo"}

    def detect_query_components(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Detect query components that can be used with the query builder.

        Args:
            query: The CQL query string to analyze

        Returns:
            Dictionary containing detected query components
        """
        components: Dict[str, Any] = {}

        # Handle simple aggregation patterns like "* groupby field" first
        simple_groupby = re.search(r"\*\s+(?:group\s*by|groupby)\s+([#\w]+)", query, re.IGNORECASE)
        if simple_groupby:
            components["group_by"] = [simple_groupby.group(1)]
            # Auto-add sorting and limiting for better UX
            components["sort_by"] = "_count"
            components["sort_order"] = "desc"
            components["limit"] = 20
            logger.info(f"Detected simple groupBy pattern: {simple_groupby.group(1)}")

        # Detect event type
        event_match = re.search(r"#?event_simpleName\s*=\s*(\w+)", query, re.IGNORECASE)
        if event_match:
            components["event_type"] = event_match.group(1)
        elif query.strip().startswith("*"):
            # Wildcard search - no specific event type
            pass

        # Detect platform
        platform_match = re.search(r"event_platform\s*=\s*(\w+)", query, re.IGNORECASE)
        if platform_match:
            components["platform"] = platform_match.group(1)

        # Detect groupBy fields
        groupby_matches = [
            re.search(
                r"groupby\s*\(\s*\[([^\]]+)\]\s*\)", query, re.IGNORECASE
            ),  # groupby([field1, field2])
            re.search(r"groupby\s*\(\s*([#\w]+)\s*\)", query, re.IGNORECASE),  # groupby(field)
            re.search(r"groupby\s+\[([^\]]+)\]", query, re.IGNORECASE),  # groupby [field1, field2]
            re.search(r"groupby\s+([#\w]+)", query, re.IGNORECASE),  # groupby field
        ]

        for match in groupby_matches:
            if match:
                group_fields = match.group(1)
                if "," in group_fields:
                    # Multiple fields
                    components["group_by"] = [f.strip() for f in group_fields.split(",")]
                else:
                    # Single field
                    components["group_by"] = [group_fields.strip()]
                break

        # Detect head/limit
        head_match = re.search(r"head\s*\(\s*(\d+)\s*\)", query, re.IGNORECASE)
        if head_match:
            components["limit"] = int(head_match.group(1))
        else:
            limit_match = re.search(r"limit\s+(\d+)", query, re.IGNORECASE)
            if limit_match:
                components["limit"] = int(limit_match.group(1))

        # Detect sort
        sort_matches = [
            re.search(r"sort\s*\(\s*([#\w]+)\s*,?\s*order\s*=\s*(\w+)\s*\)", query, re.IGNORECASE),
            re.search(r"sort\s*\(\s*([#\w]+)\s*\)", query, re.IGNORECASE),
            re.search(r"sort\s+([#\w]+)\s+(desc|asc)", query, re.IGNORECASE),
        ]

        for match in sort_matches:
            if match:
                components["sort_by"] = match.group(1)
                if len(match.groups()) > 1:
                    components["sort_order"] = match.group(2).lower()
                break

        # Detect basic filters (field=value patterns)
        filters = {}
        filter_patterns = [
            r'(\w+)\s*=\s*(["\']?)([^"\'\s\|]+)\2',  # field=value or field="value"
            r"(\w+)\s*([><=!]+)\s*(\d+)",  # field>123, field!=456
        ]

        for pattern in filter_patterns:
            for match in re.finditer(pattern, query):
                field = match.group(1)
                # Skip known CQL functions and event fields
                if field.lower() not in [
                    "groupby",
                    "sort",
                    "head",
                    "limit",
                    "select",
                    "event_simplename",
                ]:
                    if len(match.groups()) == 3 and match.group(2) in [
                        ">",
                        "<",
                        ">=",
                        "<=",
                        "!=",
                        "=",
                    ]:
                        # Comparison operator
                        filters[field] = f"{match.group(2)}{match.group(3)}"
                    else:
                        # Regular assignment
                        value = match.group(3) if len(match.groups()) > 2 else match.group(2)
                        filters[field] = value

        if filters:
            components["filters"] = filters

        logger.info(f"Detected components: {components}")
        return components if components else None

    def detect_query_intent(self, query: str) -> Optional[str]:
        """
        Detect the likely intent of a query based on patterns and keywords.

        Args:
            query: The CQL query string to analyze

        Returns:
            String representing the detected intent, or None if unclear
        """
        query_lower = query.lower()

        # Define intent patterns
        intent_patterns = {
            "event_distribution": ["groupby", "#event_simplename", "*"],
            "vendor_analysis": ["groupby", "#vendor", "*"],
            "audit_events": ["auditevent"],
            "fem_events": ["fem"],
            "api_activity": ["apiactivityaudit"],
            "auth_activity": ["authactivityaudit"],
            "user_activity": ["useractivityaudit"],
            "process_analysis": ["processrollup2", "commandline", "imagefile"],
            "network_analysis": ["networkconnectip4", "remoteaddress", "remoteport"],
            "threat_hunting": ["-enc", "bypass", "hidden", "malware"],
            "compliance_monitoring": ["admin", "privileged", "elevated"],
            "time_analysis": ["bucket", "timechart", "span"],
        }

        # Score each intent based on keyword matches
        best_intent = None
        best_score = 0

        for intent, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > best_score and score >= len(keywords) // 2:  # At least half keywords match
                best_intent = intent
                best_score = score

        return best_intent

    def detect_query_complexity(self, query: str) -> Dict[str, Any]:
        """
        Analyze query complexity and provide metrics.

        Args:
            query: The CQL query string to analyze

        Returns:
            Dictionary containing complexity metrics
        """
        complexity: Dict[str, Any] = {
            "character_count": len(query),
            "word_count": len(query.split()),
            "pipe_count": query.count("|"),
            "function_count": 0,
            "nested_function_count": 0,
            "complexity_level": "simple",
        }

        # Count functions (things with parentheses)
        function_pattern = r"\w+\s*\("
        functions = re.findall(function_pattern, query)
        complexity["function_count"] = len(functions)

        # Detect nested functions (functions within function parameters)
        nested_pattern = r"\([^()]*\([^()]*\)[^()]*\)"
        nested_matches = re.findall(nested_pattern, query)
        complexity["nested_function_count"] = len(nested_matches)

        # Determine complexity level
        if complexity["pipe_count"] == 0 and complexity["function_count"] <= 1:
            complexity["complexity_level"] = "simple"
        elif complexity["pipe_count"] <= 2 and complexity["function_count"] <= 3:
            complexity["complexity_level"] = "moderate"
        elif complexity["pipe_count"] <= 5 and complexity["function_count"] <= 7:
            complexity["complexity_level"] = "complex"
        else:
            complexity["complexity_level"] = "very_complex"

        return complexity

    def detect_syntax_patterns(self, query: str) -> Dict[str, List[str]]:
        """
        Detect various syntax patterns in the query.

        Args:
            query: The CQL query string to analyze

        Returns:
            Dictionary containing lists of detected patterns
        """
        patterns: Dict[str, List[str]] = {
            "field_filters": [],
            "regex_patterns": [],
            "time_functions": [],
            "aggregation_functions": [],
            "string_functions": [],
            "network_functions": [],
            "security_functions": [],
        }

        # Field filters (field=value, field!=value, etc.)
        field_filter_pattern = r"(\w+)\s*([!=<>]+)\s*([^|\s]+)"
        patterns["field_filters"] = re.findall(field_filter_pattern, query)

        # Regex patterns
        regex_pattern = r"/[^/]+/[gimsx]*"
        patterns["regex_patterns"] = re.findall(regex_pattern, query)

        # Function patterns
        function_patterns = {
            "time_functions": [
                r"bucket\s*\(",
                r"timeChart\s*\(",
                r"formatTime\s*\(",
                r"time:\w+\s*\(",
                r"now\s*\(",
            ],
            "aggregation_functions": [
                r"groupBy\s*\(",
                r"count\s*\(",
                r"sum\s*\(",
                r"avg\s*\(",
                r"max\s*\(",
                r"min\s*\(",
            ],
            "string_functions": [
                r"regex\s*\(",
                r"split\s*\(",
                r"length\s*\(",
                r"upper\s*\(",
                r"lower\s*\(",
            ],
            "network_functions": [
                r"ipLocation\s*\(",
                r"cidr\s*\(",
                r"rdns\s*\(",
            ],
            "security_functions": [
                r"crypto:\w+\s*\(",
                r"hash\s*\(",
                r"shannonEntropy\s*\(",
            ],
        }

        for category, function_list in function_patterns.items():
            detected = []
            for func_pattern in function_list:
                matches = re.findall(func_pattern, query, re.IGNORECASE)
                detected.extend(matches)
            patterns[category] = detected

        return patterns

    def detect_performance_issues(self, query: str) -> List[Dict[str, str]]:
        """
        Detect potential performance issues in the query.

        Args:
            query: The CQL query string to analyze

        Returns:
            List of dictionaries describing potential performance issues
        """
        issues = []

        # Check if query starts with wildcard without metadata field
        if query.strip().startswith("*") and not re.search(r"#\w+\s*=", query):
            issues.append(
                {
                    "type": "performance",
                    "severity": "high",
                    "message": "Query starts with wildcard without metadata field filter",
                    "suggestion": "Start with event type filter like #event_simpleName=ProcessRollup2",
                }
            )

        # Check for missing head/limit
        if "|" in query and not re.search(
            r"head\s*\(|limit\s*\(|limit\s+\d+", query, re.IGNORECASE
        ):
            issues.append(
                {
                    "type": "performance",
                    "severity": "medium",
                    "message": "Query lacks result limiting",
                    "suggestion": "Add | head(100) to limit results",
                }
            )

        # Check for complex regex without field filter
        regex_count = len(re.findall(r"/[^/]+/", query))
        if regex_count > 2 and not re.search(r"#event_simpleName\s*=", query):
            issues.append(
                {
                    "type": "performance",
                    "severity": "medium",
                    "message": "Multiple regex patterns without event type filter",
                    "suggestion": "Add event type filter before regex operations",
                }
            )

        # Check for groupBy without limit
        if re.search(r"groupby\s*\(", query, re.IGNORECASE) and not re.search(r"limit\s*=", query):
            issues.append(
                {
                    "type": "performance",
                    "severity": "low",
                    "message": "groupBy without limit may return many groups",
                    "suggestion": "Consider adding limit parameter to groupBy",
                }
            )

        return issues

    def normalize_field_name(self, field_name: str) -> str:
        """
        Add # prefix for known event fields that require it.

        Args:
            field_name: The field name to normalize

        Returns:
            Normalized field name with # prefix if needed
        """
        if field_name in self.event_fields_needing_hash and not field_name.startswith("#"):
            return f"#{field_name}"
        return field_name

    def extract_field_references(self, query: str) -> List[str]:
        """
        Extract all field references from the query.

        Args:
            query: The CQL query string to analyze

        Returns:
            List of unique field names referenced in the query
        """
        fields = set()

        # Pattern for field references (field=value, field!=value, etc.)
        field_patterns = [
            r"(\w+)\s*[!=<>]+\s*[^|\s]+",  # field=value patterns
            r"groupBy\s*\(\s*\[?([^\]]+)\]?\s*\)",  # groupBy field references
            r"select\s*\(\s*\[([^\]]+)\]\s*\)",  # select field references
            r"sort\s*\(\s*\[?([^\]]+)\]?\s*\)",  # sort field references
        ]

        for pattern in field_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""

                # Split comma-separated fields
                if "," in match:
                    field_list = [f.strip() for f in match.split(",")]
                    fields.update(field_list)
                else:
                    fields.add(match.strip())

        # Remove empty strings and common functions
        exclude_terms = {"", "count", "sum", "avg", "max", "min", "desc", "asc"}
        fields = {f for f in fields if f and f not in exclude_terms}

        return sorted(list(fields))

    def get_suggested_optimizations(self, query: str) -> List[Dict[str, str]]:
        """
        Get suggested optimizations for the query.

        Args:
            query: The CQL query string to analyze

        Returns:
            List of optimization suggestions
        """
        optimizations = []
        components = self.detect_query_components(query)
        issues = self.detect_performance_issues(query)

        # Convert performance issues to optimizations
        for issue in issues:
            optimizations.append(
                {
                    "type": "optimization",
                    "category": issue["type"],
                    "suggestion": issue["suggestion"],
                    "impact": issue["severity"],
                }
            )

        # Suggest event type if missing
        if not components or "event_type" not in components:
            optimizations.append(
                {
                    "type": "optimization",
                    "category": "performance",
                    "suggestion": "Add specific event type filter for better performance",
                    "impact": "high",
                    "example": "#event_simpleName=ProcessRollup2",
                }
            )

        # Suggest time range if not specified
        if not re.search(r"@timestamp|ProcessStartTime|time:", query):
            optimizations.append(
                {
                    "type": "optimization",
                    "category": "scope",
                    "suggestion": "Consider adding time constraints",
                    "impact": "medium",
                    "example": "Use time range parameters in the tool",
                }
            )

        return optimizations
