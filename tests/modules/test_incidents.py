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
            "show_crowd_score",
            "get_incident_details",
            "search_incidents",
            "get_behavior_details",
            "search_behaviors",
        ]
        self.assert_tools_registered(expected_tools)
