from src.modules.intel import IntelModule
from tests.modules.utils.test_modules import TestModules


class TestIntelModule(TestModules):
    """Test cases for the Intel module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(IntelModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "intel_query_intel_actor_entities",
            "intel_query_intel_indicator_entities",
            "intel_query_intel_report_entities",
            "intel_query_intel_rule_entities",
            "intel_get_intel_actor_entities",
            "intel_get_intel_indicator_entities",
            "intel_get_intel_report_pdf",
            "intel_get_intel_report_entities",
            "intel_get_intel_rule_entities",
            "intel_get_intel_rule_file",
            "intel_get_latest_intel_indicator_timestamp",
            "intel_get_mitre_report",
            "intel_get_rule_details",
            "intel_get_rules_details",
            "intel_get_rule_preview",
            "intel_get_vulnerabilities",
        ]
        self.assert_tools_registered(expected_tools)
