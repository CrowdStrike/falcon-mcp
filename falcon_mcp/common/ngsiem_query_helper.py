"""
Enhanced NG-SIEM Query Helper with template matching and auto-correction capabilities.

This module provides comprehensive query template management, template matching,
and intelligent auto-correction features for LogScale/CQL queries.
"""

from typing import Any, Dict, List, Optional, cast

from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.query_component_detector import QueryComponentDetector

logger = get_logger(__name__)


class NGSIEMQueryHelper:
    """Enhanced helper for common SIEM queries and templates with intelligent matching."""

    def __init__(self) -> None:
        """Initialize the query helper with component detector."""
        self.component_detector = QueryComponentDetector()

        # Enhanced LogScale query templates with proper CQL syntax
        self.COMMON_QUERIES = {
            "event_distribution": {
                "query": "* | groupBy([#event_simpleName]) | sort(_count) | head(20)",
                "description": "Show top 20 event types by volume in your environment",
                "category": "analysis",
                "keywords": ["groupby", "event", "distribution", "*"],
                "splunk_equivalent": "* | stats count() by event_simpleName | sort count desc | head 20",
                "cql_features": [
                    "wildcard_search",
                    "hashtag_field_grouping",
                    "sorting",
                    "head_limit",
                ],
            },
            "vendor_analysis": {
                "query": "* | groupBy([#Vendor]) | sort(_count) | head(20)",
                "description": "Analyze vendor distribution across all events - shows top 20 vendors by event count",
                "category": "analysis",
                "keywords": ["vendor", "groupby", "*"],
                "splunk_equivalent": "* | stats count() by Vendor | sort count desc | head 20",
                "cql_features": [
                    "wildcard_search",
                    "hashtag_field_grouping",
                    "sorting",
                    "head_limit",
                ],
            },
            "audit_events": {
                "query": "#event_simpleName=/Event_.*AuditEvent/ | select([#event_simpleName, ComputerName, @timestamp, aid]) | head(100)",
                "description": "Find all audit events (API, Auth, User activity)",
                "category": "audit",
                "keywords": ["audit", "activity", "auditevent"],
                "splunk_equivalent": "event_simpleName=*AuditEvent* | table event_simpleName, ComputerName, timestamp, aid",
                "cql_features": [
                    "hashtag_field_regex",
                    "event_name_patterns",
                    "field_selection",
                    "head_limit",
                ],
            },
            "fem_events": {
                "query": "#event_simpleName=/FEM.*/ | groupBy([#event_simpleName]) | sort(_count) | head(20)",
                "description": "Find all Falcon Exposure Management events",
                "category": "vulnerability_management",
                "keywords": ["fem", "groupby"],
                "splunk_equivalent": "event_simpleName=FEM* | stats count by event_simpleName | sort count desc | head 20",
                "cql_features": ["hashtag_field_regex", "groupby", "sorting", "head_limit"],
            },
            "api_activity": {
                "query": "#event_simpleName=Event_APIActivityAuditEvent | select([@timestamp, ComputerName, aid]) | head(100)",
                "description": "API activity audit events",
                "category": "audit",
                "keywords": ["api", "apiactivityaudit", "audit"],
                "splunk_equivalent": "event_simpleName=Event_APIActivityAuditEvent | table timestamp, ComputerName, aid",
                "cql_features": ["event_filtering", "field_selection", "head_limit"],
            },
            "auth_activity": {
                "query": "#event_simpleName=Event_AuthActivityAuditEvent | select([@timestamp, ComputerName, aid]) | head(100)",
                "description": "Authentication activity audit events",
                "category": "authentication",
                "keywords": ["auth", "authactivityaudit", "authentication"],
                "splunk_equivalent": "event_simpleName=Event_AuthActivityAuditEvent | table timestamp, ComputerName, aid",
                "cql_features": ["event_filtering", "field_selection", "head_limit"],
            },
            "user_activity": {
                "query": "#event_simpleName=Event_UserActivityAuditEvent | select([@timestamp, ComputerName, aid]) | head(100)",
                "description": "User activity audit events",
                "category": "audit",
                "keywords": ["user", "useractivityaudit", "audit"],
                "splunk_equivalent": "event_simpleName=Event_UserActivityAuditEvent | table timestamp, ComputerName, aid",
                "cql_features": ["event_filtering", "field_selection", "head_limit"],
            },
            "process_analysis": {
                "query": "#event_simpleName=ProcessRollup2 | select([ComputerName, UserName, ImageFileName, CommandLine]) | head(100)",
                "description": "Basic process event analysis",
                "category": "process_monitoring",
                "keywords": ["process", "processrollup", "commandline"],
                "splunk_equivalent": "event_simpleName=ProcessRollup2 | table ComputerName, UserName, ImageFileName, CommandLine",
                "cql_features": ["event_filtering", "field_selection", "head_limit"],
            },
            "network_analysis": {
                "query": "#event_simpleName=NetworkConnectIP4 | select([ComputerName, RemoteAddressIP4, RemotePort, LocalPort]) | head(100)",
                "description": "Network connection analysis",
                "category": "network_monitoring",
                "keywords": ["network", "connection", "ip", "networkconnect"],
                "splunk_equivalent": "event_simpleName=NetworkConnectIP4 | table ComputerName, RemoteAddressIP4, RemotePort, LocalPort",
                "cql_features": ["event_filtering", "field_selection", "head_limit"],
            },
            "suspicious_powershell": {
                "query": "#event_simpleName=ProcessRollup2 FileName=*powershell* (CommandLine=*-enc* OR CommandLine=*bypass*) | select([ComputerName, UserName, CommandLine]) | head(50)",
                "description": "Detect suspicious PowerShell activity with encoding or execution policy bypass",
                "category": "threat_hunting",
                "keywords": ["powershell", "suspicious", "-enc", "bypass"],
                "splunk_equivalent": "event_simpleName=ProcessRollup2 FileName=*powershell* (CommandLine=*-enc* OR CommandLine=*bypass*)",
                "cql_features": [
                    "event_filtering",
                    "wildcard_matching",
                    "boolean_logic",
                    "field_selection",
                ],
            },
            "failed_logins": {
                "query": "#event_simpleName=UserLogon Status!=0 | select([ComputerName, UserName, LogonType, @timestamp]) | head(100)",
                "description": "Find failed login attempts",
                "category": "authentication",
                "keywords": ["login", "logon", "failed", "authentication"],
                "splunk_equivalent": "event_simpleName=UserLogon Status!=0 | table ComputerName, UserName, LogonType, timestamp",
                "cql_features": ["event_filtering", "status_filtering", "field_selection"],
            },
            "lateral_movement": {
                "query": "#event_simpleName=ProcessRollup2 (CommandLine=*wmic* OR CommandLine=*psexec* OR CommandLine=*powershell*) RemoteAddressIP4!=null | select([ComputerName, UserName, CommandLine, RemoteAddressIP4]) | head(50)",
                "description": "Detect potential lateral movement activities",
                "category": "threat_hunting",
                "keywords": ["lateral", "movement", "wmic", "psexec", "remote"],
                "splunk_equivalent": "event_simpleName=ProcessRollup2 (CommandLine=*wmic* OR CommandLine=*psexec*) RemoteAddressIP4!=null",
                "cql_features": [
                    "event_filtering",
                    "boolean_logic",
                    "field_existence",
                    "field_selection",
                ],
            },
        }

    def get_predefined_queries(self) -> Dict[str, Dict[str, Any]]:
        """Get all predefined query templates."""
        return cast(Dict[str, Dict[str, Any]], self.COMMON_QUERIES)

    def get_template_query(
        self, template_name: str, custom_filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get a specific template query, optionally with custom filters.

        Args:
            template_name: Name of the template to retrieve
            custom_filters: Optional custom filters to apply

        Returns:
            The template query string with any custom filters applied

        Raises:
            ValueError: If template name is not found
        """
        if template_name not in self.COMMON_QUERIES:
            raise ValueError(f"Unknown template '{template_name}'")

        base_query = cast(str, self.COMMON_QUERIES[template_name]["query"])

        # Apply custom filters if provided
        if custom_filters:
            # Simple filter application - could be enhanced
            for key, value in custom_filters.items():
                if isinstance(value, str):
                    base_query += f" {key}='{value}'"
                elif isinstance(value, list):
                    base_query += f" {key} in {value}"

        return base_query

    def find_matching_templates(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Find templates that match the intent of the given query.

        Args:
            query: Query string to match against templates
            max_results: Maximum number of results to return

        Returns:
            List of matching templates with relevance scores
        """
        query_lower = query.lower()
        matches = []

        # Get query intent and components for matching
        intent = self.component_detector.detect_query_intent(query)
        components = self.component_detector.detect_query_components(query)

        for template_name, template_info in self.COMMON_QUERIES.items():
            score = 0

            # Score based on keyword matching
            keywords = template_info.get("keywords", [])
            keyword_score = sum(1 for keyword in keywords if keyword in query_lower)
            score += keyword_score * 2  # Weight keyword matches heavily

            # Score based on intent matching
            if intent and intent in template_name:
                score += 5

            # Score based on component similarity
            component_similarity_score = 0
            if components:
                template_components = self.component_detector.detect_query_components(
                    cast(str, template_info["query"])
                )
                if template_components:
                    common_components = set(components.keys()) & set(template_components.keys())
                    component_similarity_score = len(common_components)
                    score += component_similarity_score

            # Score based on category relevance
            category_keywords = {
                "analysis": ["groupby", "count", "*"],
                "audit": ["audit", "activity"],
                "threat_hunting": ["suspicious", "malicious", "threat"],
                "authentication": ["login", "logon", "auth"],
                "process_monitoring": ["process", "commandline"],
                "network_monitoring": ["network", "connection", "ip"],
            }

            category = cast(str, template_info.get("category", ""))
            if category in category_keywords:
                category_score = sum(
                    1 for keyword in category_keywords[category] if keyword in query_lower
                )
                score += category_score

            if score > 0:
                matches.append(
                    {
                        "template_name": template_name,
                        "template_info": template_info,
                        "relevance_score": score,
                        "match_reasons": {
                            "keyword_matches": keyword_score,
                            "intent_match": intent == template_name if intent else False,
                            "component_similarity": component_similarity_score,
                        },
                    }
                )

        # Sort by relevance score and return top results
        matches.sort(key=lambda x: cast(int, x["relevance_score"]), reverse=True)
        return matches[:max_results]

    def suggest_template_for_failed_query(
        self, query: str, validation_errors: Optional[List[Dict[Any, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest a template for a query that failed validation.

        Args:
            query: The failed query string
            validation_errors: Optional list of validation errors

        Returns:
            Dictionary containing suggested template information, or None if no good match
        """
        matches = self.find_matching_templates(query, max_results=3)

        if not matches:
            return None

        best_match = matches[0]

        # Only suggest if the match is reasonably good
        if best_match["relevance_score"] >= 2:
            return {
                "suggested_template": best_match["template_name"],
                "template_query": best_match["template_info"]["query"],
                "description": best_match["template_info"]["description"],
                "category": best_match["template_info"]["category"],
                "relevance_score": best_match["relevance_score"],
                "match_reasons": best_match["match_reasons"],
                "original_query": query,
                "suggestion_reason": "Template matched based on query intent and keywords",
            }

        return None

    def get_auto_correction_suggestions(
        self, query: str, validation_result: Dict
    ) -> List[Dict[str, Any]]:
        """
        Get auto-correction suggestions based on validation results and template matching.

        Args:
            query: The original query string
            validation_result: Validation results from CQL validator

        Returns:
            List of auto-correction suggestions
        """
        suggestions = []

        # Try template matching first
        template_suggestion = self.suggest_template_for_failed_query(
            query, validation_result.get("syntax_errors", [])
        )
        if template_suggestion:
            suggestions.append(
                {
                    "type": "template_replacement",
                    "priority": "high",
                    "description": f"Replace with similar template: {template_suggestion['suggested_template']}",
                    "corrected_query": template_suggestion["template_query"],
                    "explanation": template_suggestion["description"],
                    "confidence": "high"
                    if template_suggestion["relevance_score"] >= 4
                    else "medium",
                }
            )

        # Try component-based reconstruction
        components = self.component_detector.detect_query_components(query)
        if components:
            reconstructed_query = self._reconstruct_query_from_components(components)
            if reconstructed_query and reconstructed_query != query:
                suggestions.append(
                    {
                        "type": "component_reconstruction",
                        "priority": "medium",
                        "description": "Reconstruct query using detected components with proper syntax",
                        "corrected_query": reconstructed_query,
                        "explanation": f"Built from detected components: {list(components.keys())}",
                        "confidence": "medium",
                    }
                )

        # Pattern-based corrections
        pattern_corrections = self._get_pattern_based_corrections(query, validation_result)
        suggestions.extend(pattern_corrections)

        return suggestions

    def _reconstruct_query_from_components(self, components: Dict[str, Any]) -> str:
        """
        Reconstruct a query from detected components using proper CQL syntax.

        Args:
            components: Dictionary of detected query components

        Returns:
            Reconstructed query string
        """
        query_parts = []

        # Start with event type or wildcard
        if "event_type" in components:
            query_parts.append(f"#event_simpleName={components['event_type']}")
        else:
            query_parts.append("*")

        # Add platform filter
        if "platform" in components:
            query_parts.append(f"event_platform={components['platform']}")

        # Add other filters
        if "filters" in components:
            for field, value in components["filters"].items():
                normalized_field = self.component_detector.normalize_field_name(field)
                if " " in str(value):
                    query_parts.append(f'{normalized_field}="{value}"')
                else:
                    query_parts.append(f"{normalized_field}={value}")

        # Build base query
        base_query = " ".join(query_parts)

        # Add functions
        functions = []

        # Add field selection
        if "select_fields" in components:
            functions.append(f"select([{', '.join(components['select_fields'])}])")

        # Add grouping
        if "group_by" in components:
            group_fields = components["group_by"]
            if len(group_fields) == 1:
                functions.append(f"groupBy([{group_fields[0]}])")
            else:
                functions.append(f"groupBy([{', '.join(group_fields)}])")

        # Add sorting
        if "sort_by" in components:
            sort_order = components.get("sort_order", "desc")
            if sort_order == "desc":
                functions.append(f"sort({components['sort_by']})")
            else:
                functions.append(f"sort({components['sort_by']}, order=asc)")

        # Add limiting
        if "limit" in components:
            functions.append(f"head({components['limit']})")
        elif "group_by" in components:
            # Add default limit for groupBy queries
            functions.append("head(20)")

        # Combine base query with functions
        if functions:
            return f"{base_query} | " + " | ".join(functions)
        else:
            return base_query

    def _get_pattern_based_corrections(
        self, query: str, validation_result: Dict
    ) -> List[Dict[str, Any]]:
        """
        Get pattern-based corrections for common syntax errors.

        Args:
            query: The original query string
            validation_result: Validation results from CQL validator

        Returns:
            List of pattern-based correction suggestions
        """
        corrections = []
        corrected_query = query

        # Common patterns to fix
        correction_patterns = [
            {
                "pattern": r"\*\s+groupby\s+([#\w]+)(?!\s*[\(\[])",
                "replacement": r"* | groupBy([\1])",
                "description": "Fix simple groupby syntax",
                "type": "syntax_fix",
            },
            {
                "pattern": r"groupby\s*\(\s*([#\w]+)\s*\)",
                "replacement": r"groupBy([\1])",
                "description": "Fix groupBy array syntax",
                "type": "syntax_fix",
            },
            {
                "pattern": r"\|\s*head\s+(\d+)",
                "replacement": r"| head(\1)",
                "description": "Fix head function syntax",
                "type": "syntax_fix",
            },
            {
                "pattern": r"\bgroupby\b",
                "replacement": "groupBy",
                "description": "Fix case sensitivity",
                "type": "case_fix",
            },
        ]

        changes_made = []
        for pattern_info in correction_patterns:
            import re

            if re.search(pattern_info["pattern"], corrected_query, re.IGNORECASE):
                old_query = corrected_query
                corrected_query = re.sub(
                    pattern_info["pattern"],
                    pattern_info["replacement"],
                    corrected_query,
                    flags=re.IGNORECASE,
                )
                if old_query != corrected_query:
                    changes_made.append(pattern_info["description"])

        if changes_made:
            corrections.append(
                {
                    "type": "pattern_based",
                    "priority": "medium",
                    "description": f"Applied pattern-based fixes: {', '.join(changes_made)}",
                    "corrected_query": corrected_query,
                    "explanation": "Fixed common CQL syntax patterns",
                    "confidence": "high",
                }
            )

        return corrections

    def get_query_enhancement_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """
        Get suggestions to enhance a valid query for better performance or functionality.

        Args:
            query: The query string to enhance

        Returns:
            List of enhancement suggestions
        """
        suggestions = []
        components = self.component_detector.detect_query_components(query)
        performance_issues = self.component_detector.detect_performance_issues(query)

        # Convert performance issues to enhancement suggestions
        for issue in performance_issues:
            suggestions.append(
                {
                    "type": "performance_enhancement",
                    "category": issue["type"],
                    "suggestion": issue["suggestion"],
                    "impact": issue["severity"],
                    "description": issue["message"],
                }
            )

        # Suggest field selection if not present
        if components and "select_fields" not in components and "| select(" not in query:
            suggestions.append(
                {
                    "type": "functionality_enhancement",
                    "category": "field_selection",
                    "suggestion": "Add field selection to focus on relevant data",
                    "impact": "medium",
                    "description": "Field selection improves query performance and output clarity",
                    "example": "| select([ComputerName, UserName, @timestamp])",
                }
            )

        # Suggest time constraints if not present
        if not any(
            time_field in query for time_field in ["@timestamp", "ProcessStartTime", "EventTime"]
        ):
            suggestions.append(
                {
                    "type": "functionality_enhancement",
                    "category": "time_filtering",
                    "suggestion": "Consider adding time constraints for better performance",
                    "impact": "high",
                    "description": "Time filtering significantly improves query performance",
                    "example": "Use time range parameters in the tool",
                }
            )

        return suggestions

    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all templates in a specific category.

        Args:
            category: Category name to filter by

        Returns:
            List of templates in the specified category
        """
        return [
            {"name": name, "info": info}
            for name, info in self.COMMON_QUERIES.items()
            if info.get("category") == category
        ]

    def get_available_categories(self) -> List[str]:
        """
        Get list of all available template categories.

        Returns:
            List of unique category names
        """
        categories = set()
        for template_info in self.COMMON_QUERIES.values():
            category = cast(str, template_info.get("category"))
            if category:
                categories.add(category)
        return sorted(list(categories))
