"""Tests for the Policies FQL resource documentation."""

import unittest

from falcon_mcp.resources.policies import SEARCH_POLICIES_FQL_DOCUMENTATION


class TestPoliciesResource(unittest.TestCase):
    """Validate the unified policies FQL guide content."""

    def test_documentation_is_non_empty_string(self):
        self.assertIsInstance(SEARCH_POLICIES_FQL_DOCUMENTATION, str)
        self.assertTrue(SEARCH_POLICIES_FQL_DOCUMENTATION.strip())

    def test_documents_core_fields_and_discriminator(self):
        # platform_name, enabled, and created_timestamp are real entries in the
        # FQL filter table (not just prose), so these assertions actually exercise
        # the documented-field content. policy_type appears in prose describing the
        # discriminator.
        for substring in (
            "platform_name",
            "enabled",
            "created_timestamp",
            "policy_type",
        ):
            self.assertIn(substring, SEARCH_POLICIES_FQL_DOCUMENTATION)

    def test_warns_platform_name_sort_returns_500(self):
        """The guide must warn that platform_name sort returns HTTP 500."""
        self.assertIn("HTTP 500", SEARCH_POLICIES_FQL_DOCUMENTATION)
        self.assertIn("platform_name", SEARCH_POLICIES_FQL_DOCUMENTATION)

    def test_does_not_recommend_platform_name_as_sort(self):
        """platform_name.asc must not appear as a recommended sort example."""
        self.assertNotIn("platform_name.asc", SEARCH_POLICIES_FQL_DOCUMENTATION)
        self.assertNotIn("platform_name.desc", SEARCH_POLICIES_FQL_DOCUMENTATION)


if __name__ == "__main__":
    unittest.main()
