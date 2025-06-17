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
            "falcon_show_crowd_score",
            "falcon_get_incident_details",
            "falcon_search_incidents",
            "falcon_get_behavior_details",
            "falcon_search_behaviors",
        ]
        self.assert_tools_registered(expected_tools)
