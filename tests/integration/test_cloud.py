"""Integration tests for the Cloud module."""

import time
from typing import Any

import pytest

from falcon_mcp.modules.cloud import CloudModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCloudIntegration(BaseIntegrationTest):
    """Integration tests for Cloud module with real API calls.

    Validates:
    - Correct FalconPy operation names (ReadContainerCombined, ReadContainerCount, ReadCombinedVulnerabilities)
    - Combined query endpoints return full details
    - API response schema consistency
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the cloud module with a real client."""
        self.module = CloudModule(falcon_client)

    def test_search_kubernetes_containers_returns_details(self):
        """Test that search_kubernetes_containers returns full container details.

        Validates the ReadContainerCombined operation name is correct.
        """
        result = self.call_method(self.module.search_kubernetes_containers, limit=5)

        self.assert_no_error(result, context="search_kubernetes_containers")
        self.assert_valid_list_response(result, min_length=0, context="search_kubernetes_containers")

        if len(result) > 0:
            # Verify we get full details
            self.assert_search_returns_details(
                result,
                expected_fields=["container_id", "container_name"],
                context="search_kubernetes_containers",
            )

    def test_search_kubernetes_containers_with_filter(self):
        """Test search_kubernetes_containers with FQL filter."""
        result = self.call_method(
            self.module.search_kubernetes_containers,
            filter="running_status:true",
            limit=3,
        )

        self.assert_no_error(result, context="search_kubernetes_containers with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_kubernetes_containers with filter")

    def test_search_kubernetes_containers_with_sort(self):
        """Test search_kubernetes_containers with sort parameter."""
        result = self.call_method(
            self.module.search_kubernetes_containers,
            sort="last_seen.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_kubernetes_containers with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_kubernetes_containers with sort")

    def test_count_kubernetes_containers(self):
        """Test that count_kubernetes_containers returns a count.

        Validates the ReadContainerCount operation name is correct.
        """
        result = self.call_method(self.module.count_kubernetes_containers)

        # Result should be an integer or a list with error
        if isinstance(result, list):
            self.assert_no_error(result, context="count_kubernetes_containers")
        else:
            # Should be a valid count (integer >= 0)
            assert isinstance(result, int), f"Expected int, got {type(result)}"
            assert result >= 0, f"Expected non-negative count, got {result}"

    def test_count_kubernetes_containers_with_filter(self):
        """Test count_kubernetes_containers with FQL filter."""
        result = self.call_method(
            self.module.count_kubernetes_containers,
            filter="running_status:true",
        )

        if isinstance(result, list):
            self.assert_no_error(result, context="count_kubernetes_containers with filter")
        else:
            assert isinstance(result, int), f"Expected int, got {type(result)}"
            assert result >= 0, f"Expected non-negative count, got {result}"

    def test_search_images_vulnerabilities_returns_details(self):
        """Test that search_images_vulnerabilities returns full vulnerability details.

        Validates the ReadCombinedVulnerabilities operation name is correct.
        """
        result = self.call_method(self.module.search_images_vulnerabilities, limit=5)

        self.assert_no_error(result, context="search_images_vulnerabilities")
        self.assert_valid_list_response(result, min_length=0, context="search_images_vulnerabilities")

    def test_search_images_vulnerabilities_with_filter(self):
        """Test search_images_vulnerabilities with FQL filter."""
        result = self.call_method(
            self.module.search_images_vulnerabilities,
            filter="cvss_score:>5",
            limit=3,
        )

        self.assert_no_error(result, context="search_images_vulnerabilities with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_images_vulnerabilities with filter")

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        """
        # Test ReadContainerCombined
        result = self.call_method(self.module.search_kubernetes_containers, limit=1)
        self.assert_no_error(result, context="ReadContainerCombined operation name")

        # Test ReadCombinedVulnerabilities
        result = self.call_method(self.module.search_images_vulnerabilities, limit=1)
        self.assert_no_error(result, context="ReadCombinedVulnerabilities operation name")

        # Test cloud_security_assets_queries and cloud_security_assets_entities_get
        result = self.call_method(self.module.search_cspm_assets, limit=1)
        self.assert_no_error(result, context="CSPM asset operation names")

        # Test cspm_evaluations_iom_queries and cspm_evaluations_iom_entities
        result = self.call_method(self.module.search_iom_findings, limit=1)
        self.assert_no_error(result, context="IOM operation names")

        # Test suppression rules override endpoints
        result = self.call_method(self.module.search_cspm_suppression_rules, limit=1)
        self.assert_no_error(result, context="Suppression rules override operation names")

    def test_search_cspm_assets_returns_details(self):
        """Test that search_cspm_assets returns full asset details using two-step pattern.

        Validates:
        - cloud_security_assets_queries operation name is correct
        - cloud_security_assets_entities_get operation name is correct
        - Two-step pattern (query IDs -> get details) works correctly
        - Returns full asset records, not just IDs
        """
        result = self.call_method(self.module.search_cspm_assets, limit=5)

        self.assert_no_error(result, context="search_cspm_assets")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets")

        if len(result) > 0:
            # Verify we get full details, not just IDs
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "cloud_provider", "resource_type"],
                context="search_cspm_assets",
            )

    def test_search_cspm_assets_with_cloud_provider_filter(self):
        """Test search_cspm_assets with cloud provider FQL filter."""
        result = self.call_method(
            self.module.search_cspm_assets,
            filter="cloud_provider:'AWS'",
            limit=3,
        )

        self.assert_no_error(result, context="search_cspm_assets with cloud_provider filter")
        self.assert_valid_list_response(
            result, min_length=0, context="search_cspm_assets with cloud_provider filter"
        )

        # If results exist, verify they match the filter
        if len(result) > 0:
            for asset in result:
                assert "cloud_provider" in asset, "Asset should have cloud_provider field"
                # Note: Filter may return AWS and aws, be flexible
                assert asset["cloud_provider"].upper() == "AWS", (
                    f"Expected cloud_provider AWS, got {asset['cloud_provider']}"
                )

    def test_search_cspm_assets_with_tag_filter(self):
        """Test search_cspm_assets with tag FQL filter syntax.

        Validates the tag_key FQL syntax is accepted by the API.
        May return empty results if no assets have this tag.
        """
        result = self.call_method(
            self.module.search_cspm_assets,
            filter="tag_key:'Environment'",
            limit=10,
        )

        self.assert_no_error(result, context="search_cspm_assets with tag filter")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets with tag filter")

    def test_search_cspm_assets_with_sort(self):
        """Test search_cspm_assets with sort parameter."""
        result = self.call_method(
            self.module.search_cspm_assets,
            sort="updated_at.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_cspm_assets with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets with sort")

    def test_search_cspm_assets_batching_large_result(self):
        """Test search_cspm_assets with large limit to verify batching works.

        If the environment has >100 assets, this tests the batching logic.
        """
        result = self.call_method(self.module.search_cspm_assets, limit=500)

        self.assert_no_error(result, context="search_cspm_assets with large limit")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_assets large result")

        # If we got >100 results, batching was tested successfully
        if len(result) > 100:
            print(f"✅ Batching tested successfully with {len(result)} assets")

    # --- IOM Findings Integration Tests ---

    def test_search_iom_findings_returns_details(self):
        """Test that search_iom_findings returns full IOM entity details.

        Validates:
        - cspm_evaluations_iom_queries operation name is correct
        - cspm_evaluations_iom_entities operation name is correct
        - Two-step pattern returns full details, not just IDs
        """
        result = self.call_method(self.module.search_iom_findings, limit=5)

        self.assert_no_error(result, context="search_iom_findings")
        self.assert_valid_list_response(result, min_length=0, context="search_iom_findings")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "cid", "cloud", "evaluation", "resource"],
                context="search_iom_findings full details",
            )

    def test_search_iom_findings_with_severity_filter(self):
        """Test search_iom_findings with severity FQL filter."""
        result = self.call_method(
            self.module.search_iom_findings,
            filter="severity:'critical'",
            limit=3,
        )

        # May return list of results or FQL guide dict if no critical findings exist
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="search_iom_findings with severity filter"
            )
        else:
            # FQL guide response on empty results is valid
            assert isinstance(result, dict), "Expected dict or list response"

    def test_search_iom_findings_with_cloud_provider_filter(self):
        """Test search_iom_findings filtering by cloud provider."""
        result = self.call_method(
            self.module.search_iom_findings,
            filter="cloud_provider:'aws'",
            limit=3,
        )

        self.assert_no_error(result, context="search_iom_findings with cloud_provider filter")
        self.assert_valid_list_response(
            result, min_length=0, context="search_iom_findings cloud_provider filter"
        )

    def test_search_iom_findings_with_sort(self):
        """Test search_iom_findings with sort parameter."""
        result = self.call_method(
            self.module.search_iom_findings,
            sort="severity|desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_iom_findings with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_iom_findings with sort")

    def test_search_iom_findings_batching(self):
        """Test search_iom_findings with larger limit to verify batching."""
        result = self.call_method(self.module.search_iom_findings, limit=200)

        self.assert_no_error(result, context="search_iom_findings batching")
        self.assert_valid_list_response(result, min_length=0, context="search_iom_findings batching")

        if len(result) > 100:
            print(f"✅ IOM batching tested successfully with {len(result)} findings")

    # --- Suppression Rules Integration Tests ---

    def test_search_suppression_rules(self):
        """Test search_cspm_suppression_rules returns rule details.

        Validates the override endpoint pattern works correctly.
        May return empty if no suppression rules exist in the environment.
        """
        result = self.call_method(self.module.search_cspm_suppression_rules, limit=5)

        self.assert_no_error(result, context="search_cspm_suppression_rules")
        self.assert_valid_list_response(result, min_length=0, context="search_cspm_suppression_rules")

        if len(result) > 0:
            first_rule = result[0]
            assert isinstance(first_rule, dict), "Expected dict items for suppression rules"
            print(f"✅ Found {len(result)} suppression rule(s). Fields: {list(first_rule.keys())}")

    def test_create_and_delete_suppression_rule_roundtrip(self):
        """Test creating and deleting a suppression rule (full roundtrip).

        Creates a narrowly-scoped suppression rule with a short expiration,
        verifies it was created, then deletes it to clean up.
        """
        # Create a narrowly-scoped test rule with unique name
        rule_name = f"falcon-mcp-test-{int(time.time())}"
        create_result = self.call_method(
            self.module.create_cspm_suppression_rule,
            name=rule_name,
            suppression_reason="false-positive",
            rule_names=["integration-test-nonexistent-rule"],
            rule_ids=None,
            rule_severities=None,
            cloud_providers=["aws"],
            account_ids=None,
            regions=["us-east-1"],
            resource_ids=None,
            resource_types=None,
            expiration_date="2027-01-01T00:00:00Z",
        )

        self.assert_no_error(create_result, context="create_cspm_suppression_rule")

        # Extract the created rule ID for cleanup
        # API returns IDs as strings in a list: ["uuid-here"]
        rule_id = None
        if isinstance(create_result, list) and len(create_result) > 0:
            first = create_result[0]
            if isinstance(first, str):
                rule_id = first
            elif isinstance(first, dict):
                rule_id = first.get("id")
            print(f"✅ Created suppression rule: {rule_id}")
        elif isinstance(create_result, dict) and "id" in create_result:
            rule_id = create_result["id"]
            print(f"✅ Created suppression rule: {rule_id}")

        # Clean up: delete the rule we just created
        if rule_id:
            delete_result = self.call_method(
                self.module.delete_cspm_suppression_rules,
                ids=[rule_id],
            )
            self.assert_no_error(delete_result, context="delete_cspm_suppression_rules")
            print(f"✅ Deleted suppression rule: {rule_id}")
        else:
            print("⚠️  Could not extract rule ID from create response, skipping delete")


@pytest.mark.integration
class TestCloudRisksIntegration(BaseIntegrationTest):
    """Integration tests for cloud risks and cloud groups tools.

    Validates correct operation names, combined endpoint response shape,
    and that the API returns data we can assert on.
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = CloudModule(falcon_client)

    def test_search_cloud_risks_operation_name_correct(self):
        """Validate combined_cloud_risks operation name is correct (not a typo)."""
        result = self.call_method(self.module.search_cloud_risks, limit=1)
        self.assert_no_error(result, context="combined_cloud_risks operation name")
        self.assert_valid_list_response(result, min_length=0, context="search_cloud_risks")

    def test_search_cloud_risks_returns_full_details(self):
        """Test that search_cloud_risks returns full entity details, not IDs."""
        result = self.call_method(self.module.search_cloud_risks, limit=3)
        self.assert_no_error(result, context="search_cloud_risks full details")
        if not result:
            self.skip_with_warning("No cloud risks found in environment", "search_cloud_risks details")
            return
        first = result[0]
        assert isinstance(first, dict), f"Expected dict, got {type(first)}"
        print(f"\nCloud risk entity keys: {sorted(first.keys())}")
        for field in ["id", "severity", "status"]:
            assert field in first, f"Expected '{field}' in risk entity. Got: {sorted(first.keys())}"

    def test_search_cloud_risks_with_severity_filter(self):
        """Test severity FQL filter returns results (validates operator support)."""
        result = self.call_method(
            self.module.search_cloud_risks,
            filter="severity:'critical'",
            limit=3,
        )
        self.assert_no_error(result, context="search_cloud_risks severity filter")
        self.assert_valid_list_response(result, min_length=0, context="severity filter")

    def test_search_cloud_risks_with_status_filter(self):
        """Test status FQL filter (validates operator support)."""
        result = self.call_method(
            self.module.search_cloud_risks,
            filter="status:'open'",
            limit=3,
        )
        self.assert_no_error(result, context="search_cloud_risks status filter")
        self.assert_valid_list_response(result, min_length=0, context="status filter")

    def test_search_cloud_risks_with_cloud_provider_filter(self):
        """Test cloud_provider FQL filter (validates operator support)."""
        result = self.call_method(
            self.module.search_cloud_risks,
            filter="cloud_provider:'aws'",
            limit=3,
        )
        self.assert_no_error(result, context="search_cloud_risks cloud_provider filter")
        self.assert_valid_list_response(result, min_length=0, context="cloud_provider filter")

    def test_search_cloud_risks_with_sort(self):
        """Test sort parameter is accepted by the API."""
        result = self.call_method(
            self.module.search_cloud_risks,
            sort="severity|desc",
            limit=3,
        )
        self.assert_no_error(result, context="search_cloud_risks with sort")
        self.assert_valid_list_response(result, min_length=0, context="sort")

    @staticmethod
    def _is_403_error(result: Any) -> bool:
        """Return True if result signals a 403 / scope-not-permitted error."""
        if isinstance(result, dict) and "error" in result:
            error_msg = str(result)
            if (
                "403" in error_msg
                or "access denied" in error_msg.lower()
                or "forbidden" in error_msg.lower()
                or "scope not permitted" in error_msg.lower()
            ):
                return True
        if isinstance(result, list) and result and isinstance(result[0], dict) and "error" in result[0]:
            error_msg = str(result[0])
            if (
                "403" in error_msg
                or "access denied" in error_msg.lower()
                or "forbidden" in error_msg.lower()
                or "scope not permitted" in error_msg.lower()
            ):
                return True
        return False

    def test_search_cloud_groups_operation_name_correct(self):
        """Validate ListCloudGroupsExternal operation name is correct."""
        result = self.call_method(self.module.search_cloud_groups, limit=5)
        if self._is_403_error(result):
            self.skip_with_warning("Cloud groups scope not available on this key", "search_cloud_groups")
            return
        self.assert_no_error(result, context="ListCloudGroupsExternal operation name")
        self.assert_valid_list_response(result, min_length=0, context="search_cloud_groups")

    def test_search_cloud_groups_returns_full_details(self):
        """Test that search_cloud_groups returns full group entities."""
        result = self.call_method(self.module.search_cloud_groups, limit=3)
        if self._is_403_error(result):
            self.skip_with_warning("Cloud groups scope not available on this key", "search_cloud_groups details")
            return
        self.assert_no_error(result, context="search_cloud_groups full details")
        if not result:
            self.skip_with_warning("No cloud groups found in environment", "search_cloud_groups details")
            return
        first = result[0]
        assert isinstance(first, dict), f"Expected dict, got {type(first)}"
        print(f"\nCloud group entity keys: {sorted(first.keys())}")
        assert "id" in first, f"Expected 'id' in group entity. Got: {sorted(first.keys())}"

    def test_get_cloud_groups_operation_name_correct(self):
        """Validate ListCloudGroupsByIDExternal operation name is correct."""
        groups = self.call_method(self.module.search_cloud_groups, limit=1)
        if self._is_403_error(groups):
            self.skip_with_warning("Cloud groups scope not available on this key", "get_cloud_groups by ID")
            return
        self.assert_no_error(groups, context="get groups for ID lookup")
        if not groups:
            self.skip_with_warning("No cloud groups found", "get_cloud_groups by ID")
            return
        group_id = groups[0].get("id")
        assert group_id, "Expected 'id' field in group"
        result = self.call_method(self.module.get_cloud_groups, ids=[group_id])
        self.assert_no_error(result, context="ListCloudGroupsByIDExternal operation name")
        self.assert_valid_list_response(result, min_length=1, context="get_cloud_groups by ID")
        assert result[0]["id"] == group_id

