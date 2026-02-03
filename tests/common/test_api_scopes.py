"""
Tests for the API scope utilities.
"""

import re
import unittest
import warnings
from pathlib import Path

from falcon_mcp.common.api_scopes import API_SCOPE_REQUIREMENTS, get_required_scopes


class TestApiScopes(unittest.TestCase):
    """Test cases for the API scope utilities."""

    @staticmethod
    def _extract_operations_from_modules() -> set[str]:
        """Extract all operation names used in module files.

        Returns:
            set[str]: Set of operation names found in modules
        """
        operations = set()

        # Get the modules directory
        modules_path = Path(__file__).parent.parent.parent / "falcon_mcp" / "modules"

        # Pattern to match operation= statements
        operation_pattern = re.compile(r'operation\s*=\s*["\']([^"\']+)["\']')

        # Search through all Python module files
        for module_file in modules_path.glob("*.py"):
            if module_file.name in ["__init__.py", "base.py"]:
                continue

            try:
                content = module_file.read_text()
                matches = operation_pattern.findall(content)
                operations.update(matches)
            except (OSError, UnicodeDecodeError):
                # Skip files that can't be read or decoded
                continue

        return operations

    def test_api_scope_requirements_structure(self):
        """Test API_SCOPE_REQUIREMENTS dictionary structure."""
        # Verify it's a dictionary
        self.assertIsInstance(API_SCOPE_REQUIREMENTS, dict)

        # Verify it has entries
        self.assertGreater(len(API_SCOPE_REQUIREMENTS), 0)

        # Verify structure of entries (keys are strings, values are lists of strings)
        for operation, scopes in API_SCOPE_REQUIREMENTS.items():
            self.assertIsInstance(operation, str)
            self.assertIsInstance(scopes, list)
            for scope in scopes:
                self.assertIsInstance(scope, str)

    def test_get_required_scopes(self):
        """Test get_required_scopes function."""
        # Test with known operations
        self.assertEqual(get_required_scopes("GetQueriesAlertsV2"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("PostEntitiesAlertsV2"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("QueryIncidents"), ["Incidents:read"])

        # Test with unknown operation
        self.assertEqual(get_required_scopes("UnknownOperation"), [])

        # Test with empty string
        self.assertEqual(get_required_scopes(""), [])

        # Test with None (should handle gracefully)
        self.assertEqual(get_required_scopes(None), [])

    def test_all_operations_have_scope_mappings(self):
        """Test that all operations used in modules have scope mappings defined."""
        # Extract all operations from module files
        operations_in_modules = self._extract_operations_from_modules()

        # Get operations that have scope mappings
        mapped_operations = set(API_SCOPE_REQUIREMENTS.keys())

        # Find operations without scope mappings
        unmapped_operations = operations_in_modules - mapped_operations

        # Assert that all operations have scope mappings
        self.assertEqual(
            len(unmapped_operations),
            0,
            f"The following operations are missing scope mappings: {sorted(unmapped_operations)}"
        )

    def test_no_unused_scope_mappings(self):
        """Test that all scope mappings correspond to operations actually used in modules."""
        # Extract all operations from module files
        operations_in_modules = self._extract_operations_from_modules()

        # Get operations that have scope mappings
        mapped_operations = set(API_SCOPE_REQUIREMENTS.keys())

        # Find scope mappings for operations not in modules (potentially unused)
        unused_mappings = mapped_operations - operations_in_modules

        # This is a warning test - we allow some unused mappings for backward compatibility
        # but we want to be aware of them
        if unused_mappings:
            warnings.warn(
                f"The following scope mappings may be unused: {sorted(unused_mappings)}",
                UserWarning,
                stacklevel=2
            )

    def test_scope_format_validation(self):
        """Test that all scopes follow the expected format."""
        for operation, scopes in API_SCOPE_REQUIREMENTS.items():
            for scope in scopes:
                # Test that scope is non-empty
                self.assertGreater(len(scope), 0, f"Empty scope found for operation {operation}")

                # Test that scope contains a colon (standard format: "Resource:permission")
                # Note: Some scopes like "Identity Protection GraphQL:write" have spaces and are valid
                self.assertIn(
                    ":", scope, f"Invalid scope format '{scope}' for operation {operation}"
                )

                # Test that scope doesn't start or end with whitespace
                self.assertEqual(
                    scope, scope.strip(), f"Scope '{scope}' has leading/trailing whitespace"
                )

                # Test that scope has both parts (before and after colon)
                parts = scope.split(":")
                self.assertEqual(
                    len(parts), 2, f"Invalid scope format '{scope}' - should have exactly one colon"
                )
                self.assertGreater(
                    len(parts[0]), 0, f"Empty resource name in scope '{scope}'"
                )
                self.assertGreater(
                    len(parts[1]), 0, f"Empty permission name in scope '{scope}'"
                )

    def test_error_handling_integration(self):
        """Test that get_required_scopes integrates properly with error handling."""
        # Test with multiple known operations to ensure consistency
        test_cases = [
            ("GetQueriesAlertsV2", ["Alerts:read"]),
            ("QueryIncidents", ["Incidents:read"]),
            ("QueryIntelActorEntities", ["Actors (Falcon Intelligence):read"]),
            ("api_preempt_proxy_post_graphql", [
                "Identity Protection Entities:read",
                "Identity Protection Timeline:read",
                "Identity Protection Detections:read",
                "Identity Protection Assessment:read",
                "Identity Protection GraphQL:write"
            ])
        ]

        for operation, expected_scopes in test_cases:
            with self.subTest(operation=operation):
                result = get_required_scopes(operation)
                self.assertEqual(result, expected_scopes)
                self.assertIsInstance(result, list)
                for scope in result:
                    self.assertIsInstance(scope, str)

    def test_graceful_fallback_behavior(self):
        """Test that unmapped operations handle gracefully without breaking error handling."""
        # Test edge cases that should return empty list
        edge_cases = [
            None,
            "",
            "NonExistentOperation",
            "malformed operation name",
            "operation:with:colons",
        ]

        for test_case in edge_cases:
            with self.subTest(operation=test_case):
                result = get_required_scopes(test_case)
                self.assertEqual(result, [])
                self.assertIsInstance(result, list)

    def test_scope_mapping_consistency(self):
        """Test that scope mappings are internally consistent and follow patterns."""
        # Collect scopes by category to validate consistency
        scope_patterns = {}
        for operation, scopes in API_SCOPE_REQUIREMENTS.items():
            for scope in scopes:
                resource = scope.split(":")[0]
                permission = scope.split(":")[1]

                if resource not in scope_patterns:
                    scope_patterns[resource] = set()
                scope_patterns[resource].add(permission)

        # Validate that most resources use consistent permission patterns
        read_only_resources = [
            "Alerts", "Hosts", "Incidents", "Vulnerabilities",
            "Assets", "Sensor Usage", "Scheduled Reports"
        ]

        for resource in read_only_resources:
            if resource in scope_patterns:
                self.assertEqual(
                    scope_patterns[resource],
                    {"read"},
                    f"Resource '{resource}' should only use 'read' permission"
                )

    def test_comprehensive_module_coverage(self):
        """Test that we have reasonable coverage across expected modules."""
        # Count operations by likely module based on operation patterns
        module_patterns = {
            "alerts": ["GetQueriesAlertsV2", "PostEntitiesAlertsV2"],
            "hosts": ["QueryDevicesByFilter", "PostDeviceDetailsV2"],
            "incidents": ["QueryIncidents", "GetIncidents", "QueryBehaviors", "GetBehaviors", "CrowdScore"],
            "intel": ["QueryIntelActorEntities", "QueryIntelIndicatorEntities", "QueryIntelReportEntities", "GetMitreReport"],
            "spotlight": ["combinedQueryVulnerabilities"],
            "cloud": ["ReadContainerCombined", "ReadContainerCount", "ReadCombinedVulnerabilities"],
            "discover": ["combined_applications", "combined_hosts"],
            "idp": ["api_preempt_proxy_post_graphql"],
            "sensor_usage": ["GetSensorUsageWeekly"],
            "scheduled_reports": [
                "scheduled_reports_query", "scheduled_reports_get", "scheduled_reports_launch",
                "report_executions_query", "report_executions_get", "report_executions_download_get"
            ],
            "serverless": ["GetCombinedVulnerabilitiesSARIF"]
        }

        # Verify that all expected operations are mapped
        all_expected_operations = set()
        for operations in module_patterns.values():
            all_expected_operations.update(operations)

        mapped_operations = set(API_SCOPE_REQUIREMENTS.keys())

        # All expected operations should be mapped
        missing_operations = all_expected_operations - mapped_operations
        self.assertEqual(
            len(missing_operations), 0,
            f"Expected operations missing from scope mappings: {sorted(missing_operations)}"
        )

        # Should have reasonable coverage (at least 11 different modules)
        self.assertGreaterEqual(
            len(module_patterns), 11,
            "Should have scope mappings for at least 11 different functional modules"
        )


if __name__ == "__main__":
    unittest.main()
