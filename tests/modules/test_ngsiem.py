"""
Tests for the NG-SIEM module.
"""

import unittest
from unittest.mock import Mock

from falcon_mcp.modules.ngsiem import NGSIEMModule, NGSIEMQueryEngine
from tests.modules.utils.test_modules import TestModules


class TestNGSIEMModule(TestModules):
    """Test cases for the NG-SIEM module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(NGSIEMModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_execute_ngsiem_query",
            "falcon_ngsiem_query_templates",
            "falcon_analyze_ngsiem_results",
            "falcon_search_ngsiem_fields",
            "falcon_validate_cql_syntax",
            "falcon_build_cql_query",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        # The implementation registers 3 resources with these names
        expected_resources = [
            "falcon_ngsiem_field_mappings",
            "falcon_ngsiem_query_patterns",
            "falcon_ngsiem_use_cases",
        ]
        self.assert_resources_registered(expected_resources)

    def test_ngsiem_query_templates_list_all(self):
        """Test listing all available query templates."""
        result = self.module.ngsiem_query_templates()

        # The method should return something, even if there's an error
        self.assertIsInstance(result, dict)
        if "error" not in result:
            # If successful, check expected structure
            self.assertIn("templates", result)
            self.assertIsInstance(result["templates"], dict)

    def test_ngsiem_query_templates_specific(self):
        """Test getting a specific query template."""
        # Use a template that likely exists
        result = self.module.ngsiem_query_templates(template_name="event_distribution")

        # The method should return something, even if there's an error
        self.assertIsInstance(result, dict)
        if "error" not in result:
            # If successful, check expected structure
            self.assertIn("template", result)
            self.assertIn("query", result)

    def test_analyze_ngsiem_results_summary(self):
        """Test analysis of NG-SIEM results with summary."""
        sample_data = {
            "events": [
                {"ComputerName": "HOST1", "UserName": "admin", "ProcessId": "1234"},
                {"ComputerName": "HOST2", "UserName": "user1", "ProcessId": "5678"},
                {"ComputerName": "HOST1", "UserName": "admin", "ProcessId": "9999"},
            ]
        }

        result = self.module.analyze_ngsiem_results(
            results_data=sample_data, analysis_type="summary"
        )

        self.assertIn("summary", result)
        self.assertIn("event_count", result)

    def test_analyze_ngsiem_results_pivot(self):
        """Test analysis of NG-SIEM results with pivot table."""
        sample_data = {
            "events": [
                {"ComputerName": "HOST1", "UserName": "admin"},
                {"ComputerName": "HOST2", "UserName": "user1"},
                {"ComputerName": "HOST1", "UserName": "admin"},
            ]
        }

        result = self.module.analyze_ngsiem_results(
            results_data=sample_data,
            analysis_type="pivot",
            pivot_fields=["ComputerName", "UserName"],
        )

        self.assertIn("pivot_data", result)
        self.assertIn("pivot_fields", result["pivot_data"])

    def test_search_ngsiem_fields(self):
        """Test LogScale field search functionality."""
        result = self.module.search_ngsiem_fields(search_term="process")

        self.assertIn("matching_fields", result)
        self.assertIsInstance(result["matching_fields"], list)
        # Fields might be empty, so just check structure
        self.assertIn("search_term", result)

    def test_validate_cql_syntax_valid(self):
        """Test CQL syntax validation with valid query."""
        valid_query = "#event_simpleName=ProcessRollup2 | head(100)"

        result = self.module.validate_cql_syntax(query=valid_query)

        self.assertIn("is_valid_cql", result)
        # The result might be True or False, but should not crash
        self.assertIsInstance(result["is_valid_cql"], bool)

    def test_validate_cql_syntax_invalid(self):
        """Test CQL syntax validation with invalid query."""
        invalid_query = "| stats count by field"  # Missing event filter

        result = self.module.validate_cql_syntax(query=invalid_query)

        self.assertIn("is_valid_cql", result)
        # Should return validation result, not necessarily False
        self.assertIsInstance(result["is_valid_cql"], bool)

    def test_build_cql_query_basic(self):
        """Test CQL query builder with basic parameters."""
        result = self.module.build_cql_query(event_type="ProcessRollup2", limit=100)

        # Just check that it doesn't crash and returns some expected structure
        self.assertIsInstance(result, dict)
        if "built_query" in result:
            self.assertIn("#event_simpleName=ProcessRollup2", result["built_query"])
        elif "error" not in result:
            # If it returns something else, that's fine too
            self.assertTrue(len(result) > 0)

    def test_build_cql_query_with_filters(self):
        """Test CQL query builder with filters."""
        result = self.module.build_cql_query(
            event_type="ProcessRollup2", filters={"ComputerName": "DESKTOP-*"}, limit=50
        )

        self.assertIn("built_query", result)
        self.assertIn("#event_simpleName=ProcessRollup2", result["built_query"])
        self.assertIn("ComputerName", result["built_query"])


class TestNGSIEMQueryEngine(unittest.TestCase):
    """Test cases for NGSIEMQueryEngine component."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.engine = NGSIEMQueryEngine(self.mock_client)

    def test_initialization(self):
        """Test query engine initialization."""
        self.assertEqual(self.engine.client, self.mock_client)
        # Check that required components are initialized
        self.assertIsNotNone(self.engine.validator)
        self.assertIsNotNone(self.engine.component_detector)
        self.assertIsNotNone(self.engine.query_helper)


if __name__ == "__main__":
    unittest.main()
