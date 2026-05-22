"""
Tests for the Dynamic mode (two-tool pattern).
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from falcon_mcp import registry
from falcon_mcp.dynamic import DynamicMode, DynamicToolCatalog
from falcon_mcp.filter_hints import FILTER_HINTS
from falcon_mcp.modules.detections import DetectionsModule
from falcon_mcp.modules.hosts import HostsModule


def run_async(coro):
    return asyncio.run(coro)


class TestDynamicToolCatalog(unittest.TestCase):
    """Test cases for DynamicToolCatalog."""

    def setUp(self):
        self.mock_client = MagicMock()
        self.modules = {
            "detections": DetectionsModule(self.mock_client),
            "hosts": HostsModule(self.mock_client),
        }

    def test_catalog_builds_entries_from_modules(self):
        catalog = DynamicToolCatalog(self.modules)
        self.assertGreater(len(catalog.entries), 0)
        self.assertIn("falcon_search_detections", catalog.entries)
        self.assertIn("falcon_search_hosts", catalog.entries)

    def test_catalog_maps_tools_to_modules(self):
        catalog = DynamicToolCatalog(self.modules)
        self.assertEqual(catalog.entries["falcon_search_detections"].module, "detections")
        self.assertEqual(catalog.entries["falcon_search_hosts"].module, "hosts")

    def test_catalog_clears_module_tools_list(self):
        DynamicToolCatalog(self.modules)
        for module in self.modules.values():
            self.assertEqual(module.tools, [])

    def test_search_matches_keyword_in_name(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="search_detections")
        names = [r["name"] for r in results]
        self.assertIn("falcon_search_detections", names)

    def test_search_matches_keyword_in_description(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="severity")
        self.assertGreater(len(results), 0)

    def test_search_all_tokens_must_match(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="search detections")
        names = [r["name"] for r in results]
        self.assertIn("falcon_search_detections", names)

        results_no_match = catalog.search(query="search nonexistent_xyz_module")
        self.assertEqual(len(results_no_match), 0)

    def test_search_module_filter(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(module="detections")
        for r in results:
            self.assertEqual(r["module"], "detections")

    def test_search_respects_limit(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(limit=1)
        self.assertEqual(len(results), 1)

    def test_search_empty_query_returns_all_up_to_limit(self):
        catalog = DynamicToolCatalog(self.modules)
        total = len(catalog.entries)
        results = catalog.search(query="", limit=100)
        self.assertEqual(len(results), total)

    def test_summarize_parameters_flattens_schema(self):
        schema = {
            "properties": {
                "filter": {"type": "string", "description": "FQL filter"},
                "limit": {"type": "integer", "description": "Max results"},
            },
            "required": ["filter"],
        }
        summary = DynamicToolCatalog.summarize_parameters(schema)
        self.assertEqual(summary["filter"]["type"], "string")
        self.assertTrue(summary["filter"]["required"])
        self.assertFalse(summary["limit"]["required"])

    def test_format_entry_includes_annotations(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="search_detections")
        detection_result = next(r for r in results if r["name"] == "falcon_search_detections")
        self.assertTrue(detection_result["read_only"])
        self.assertFalse(detection_result["destructive"])

    def test_format_entry_appends_filter_hints(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="search_detections")
        detection_result = next(r for r in results if r["name"] == "falcon_search_detections")
        filter_desc = detection_result["parameters"]["filter"]["description"]
        self.assertIn("severity_name", filter_desc)
        self.assertIn("Common fields:", filter_desc)
        self.assertIn("falcon://detections/search/fql-guide", filter_desc)

    def test_format_entry_appends_host_filter_hints(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="search_hosts")
        host_result = next(r for r in results if r["name"] == "falcon_search_hosts")
        filter_desc = host_result["parameters"]["filter"]["description"]
        self.assertIn("hostname", filter_desc)
        self.assertIn("platform_name", filter_desc)
        self.assertIn("Common fields:", filter_desc)

    def test_format_entry_no_hint_for_tools_without_filter(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="get_detection_details")
        detail_result = next(r for r in results if r["name"] == "falcon_get_detection_details")
        for param in detail_result["parameters"].values():
            self.assertNotIn("Common fields:", param["description"])

    def test_format_entry_includes_examples_when_present(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="search_detections")
        detection_result = next(r for r in results if r["name"] == "falcon_search_detections")
        filter_param = detection_result["parameters"]["filter"]
        self.assertIn("examples", filter_param)
        self.assertIsInstance(filter_param["examples"], list)
        self.assertGreater(len(filter_param["examples"]), 0)

    def test_format_entry_omits_examples_when_absent(self):
        catalog = DynamicToolCatalog(self.modules)
        results = catalog.search(query="get_detection_details")
        detail_result = next(r for r in results if r["name"] == "falcon_get_detection_details")
        ids_param = detail_result["parameters"]["ids"]
        self.assertNotIn("examples", ids_param)

    def test_filter_hints_registry_covers_search_tools(self):
        """Verify that all tools with FQL filter params have hints registered."""
        from falcon_mcp.client import FalconClient

        mock_client = MagicMock(spec=FalconClient)
        all_modules = {
            name: cls(mock_client)
            for name, cls in registry.get_available_modules().items()
        }
        catalog = DynamicToolCatalog(all_modules)
        for name, entry in catalog.entries.items():
            properties = entry.tool.parameters.get("properties", {})
            filter_schema = properties.get("filter", {})
            if "fql-guide" in filter_schema.get("description", ""):
                self.assertIn(
                    name,
                    FILTER_HINTS,
                    f"Tool '{name}' has FQL filter but no hint in FILTER_HINTS",
                )


class TestExecuteFalconTool(unittest.TestCase):
    """Test cases for DynamicMode execute dispatch."""

    def setUp(self):
        self.mock_client = MagicMock()
        self.modules = {
            "detections": DetectionsModule(self.mock_client),
        }
        self.mock_server = MagicMock()
        self.dynamic = DynamicMode(self.modules, self.mock_server)

    def test_execute_dispatches_to_tool_run(self):
        entry = self.dynamic.catalog.get("falcon_get_detection_details")
        self.assertIsNotNone(entry)

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "det1", "severity": 5}]},
        }

        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_get_detection_details",
                parameters={"ids": ["det1"]},
            )
        )
        self.assertIsNotNone(result)

    def test_execute_unknown_tool_returns_error(self):
        result = run_async(
            self.dynamic._execute_tool(
                tool_name="nonexistent_tool",
                parameters={},
            )
        )
        self.assertIn("error", result)
        self.assertIn("Unknown tool", result["error"])
        self.assertIn("falcon_search_tools", result["error"])

    def test_execute_validation_error_returns_structured_error(self):
        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_get_detection_details",
                parameters={"ids": "not_a_list"},
            )
        )
        self.assertIn("error", result)
        self.assertIn("tool", result)
        self.assertEqual(result["tool"], "falcon_get_detection_details")

    def test_execute_full_format_returns_raw_result(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "det1"}]},
        }

        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_get_detection_details",
                parameters={"ids": ["det1"]},
                response_format="full",
            )
        )
        self.assertEqual(result, [{"id": "det1"}])

    def test_execute_summary_format_truncates_large_list(self):
        large_result = [{"id": f"det{i}"} for i in range(20)]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": large_result},
        }

        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_get_detection_details",
                parameters={"ids": [f"det{i}" for i in range(20)]},
                response_format="summary",
            )
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["total_count"], 20)
        self.assertEqual(result["showing"], 5)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["results"]), 5)

    def test_execute_summary_format_preserves_small_list(self):
        small_result = [{"id": "det1"}, {"id": "det2"}]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": small_result},
        }

        result = run_async(
            self.dynamic._execute_tool(
                tool_name="falcon_get_detection_details",
                parameters={"ids": ["det1", "det2"]},
                response_format="summary",
            )
        )
        self.assertEqual(result, small_result)

    def test_search_tools_no_results_returns_hint_with_available_modules(self):
        result = run_async(
            self.dynamic._search_tools(
                query="hosts nonexistent", module=None, limit=20
            )
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("hint", result)
        self.assertIn("detections", result["hint"])
        self.assertIn("No tools found", result["hint"])

    def test_search_tools_with_results_returns_list(self):
        result = run_async(
            self.dynamic._search_tools(
                query="search_detections", module=None, limit=20
            )
        )
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)


class TestDynamicServerIntegration(unittest.TestCase):
    """Test cases for dynamic mode server integration."""

    def setUp(self):
        registry.discover_modules()

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_dynamic_mode_registers_five_tools(self, mock_fastmcp, mock_client):
        from falcon_mcp.server import FalconMCPServer

        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        FalconMCPServer(
            enabled_modules={"detections"},
            dynamic=True,
        )

        tool_names = [
            call.kwargs["name"] for call in mock_server_instance.add_tool.call_args_list
        ]
        self.assertEqual(len(tool_names), 5)
        self.assertIn("falcon_check_connectivity", tool_names)
        self.assertIn("falcon_list_enabled_modules", tool_names)
        self.assertIn("falcon_list_modules", tool_names)
        self.assertIn("falcon_search_tools", tool_names)
        self.assertIn("falcon_execute_tool", tool_names)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_normal_mode_does_not_have_dynamic_tools(self, mock_fastmcp, mock_client):
        from falcon_mcp.server import FalconMCPServer

        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        FalconMCPServer(
            enabled_modules={"detections"},
            dynamic=False,
        )

        tool_names = [
            call.kwargs["name"] for call in mock_server_instance.add_tool.call_args_list
        ]
        self.assertNotIn("falcon_search_tools", tool_names)
        self.assertNotIn("falcon_execute_tool", tool_names)
        self.assertIn("falcon_search_detections", tool_names)

    @patch("falcon_mcp.server.FalconClient")
    @patch("falcon_mcp.server.FastMCP")
    def test_dynamic_mode_still_registers_resources(self, mock_fastmcp, mock_client):
        from falcon_mcp.server import FalconMCPServer

        mock_client_instance = MagicMock()
        mock_client_instance.authenticate.return_value = True
        mock_client.return_value = mock_client_instance

        mock_server_instance = MagicMock()
        mock_fastmcp.return_value = mock_server_instance

        FalconMCPServer(
            enabled_modules={"detections"},
            dynamic=True,
        )

        mock_server_instance.add_resource.assert_called()

    @patch("sys.argv", ["falcon-mcp", "--dynamic"])
    def test_parse_args_dynamic_flag(self):
        from falcon_mcp.server import parse_args

        args = parse_args()
        self.assertTrue(args.dynamic)

    @patch("sys.argv", ["falcon-mcp"])
    @patch.dict("os.environ", {"FALCON_MCP_DYNAMIC": "true"})
    def test_parse_args_dynamic_env_var(self):
        from falcon_mcp.server import parse_args

        args = parse_args()
        self.assertTrue(args.dynamic)

    @patch("sys.argv", ["falcon-mcp"])
    @patch.dict("os.environ", {}, clear=False)
    def test_parse_args_dynamic_defaults_false(self):
        import os

        os.environ.pop("FALCON_MCP_DYNAMIC", None)
        from falcon_mcp.server import parse_args

        args = parse_args()
        self.assertFalse(args.dynamic)


if __name__ == "__main__":
    unittest.main()
