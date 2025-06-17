"""
Tests for the Incidents module.
"""
from src.modules.incidents import IncidentsModule
from tests.modules.utils.test_modules import TestModules


class TestIncidentsModule(TestModules):
    """Test cases for the Incidents module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(IncidentsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "incidents_crowd_score",
            "incidents_get_incidents",
            "incidents_query_incidents",
            "incidents_get_behaviors",
            "incidents_query_behaviors",
        ]
        self.assert_tools_registered(expected_tools)
