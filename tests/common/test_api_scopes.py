"""
Tests for the API scope utilities.
"""

import unittest

from falcon_mcp.common.api_scopes import API_SCOPE_REQUIREMENTS, get_required_scopes


class TestApiScopes(unittest.TestCase):
    """Test cases for the API scope utilities."""

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
        self.assertEqual(get_required_scopes("GetQueriesAlertsV2"), ["alerts:read"])
        self.assertEqual(get_required_scopes("PostEntitiesAlertsV2"), ["alerts:read"])
        self.assertEqual(get_required_scopes("QueryIncidents"), ["incidents:read"])

        # Test with unknown operation
        self.assertEqual(get_required_scopes("UnknownOperation"), [])

        # Test with empty string
        self.assertEqual(get_required_scopes(""), [])

        # Test with None (should handle gracefully)
        self.assertEqual(get_required_scopes(None), [])


if __name__ == "__main__":
    unittest.main()
