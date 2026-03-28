"""Integration tests for the ODS module."""

import pytest

from falcon_mcp.modules.ods import ODSModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestODSIntegration(BaseIntegrationTest):
    """Integration tests for the ODS module with real API calls.

    Validates:
    - Correct FalconPy operation names for ODS search and detail lookups
    - Two-step search patterns return full entity details, not just IDs
    - GET-with-params detail retrieval for ODS entities
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the ODS module with a real client."""
        self.module = ODSModule(falcon_client)

    def test_search_ods_scans_returns_details(self):
        """Test that ODS scan search returns full scan details."""
        result = self.call_method(self.module.search_ods_scans, limit=5)

        self.assert_no_error(result, context="search_ods_scans")
        self.assert_valid_list_response(result, min_length=0, context="search_ods_scans")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "status", "created_on"],
                context="search_ods_scans",
            )

    def test_get_ods_scan_details_with_valid_id(self):
        """Test ODS scan detail lookup using a valid scan ID."""
        search_result = self.call_method(self.module.search_ods_scans, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No ODS scans available to test get_ods_scan_details",
                context="test_get_ods_scan_details_with_valid_id",
            )

        scan_id = self.get_first_id(search_result)
        if not scan_id:
            self.skip_with_warning(
                "Could not extract ODS scan ID from search results",
                context="test_get_ods_scan_details_with_valid_id",
            )

        result = self.call_method(self.module.get_ods_scan_details, ids=[scan_id])

        self.assert_no_error(result, context="get_ods_scan_details")
        self.assert_valid_list_response(result, min_length=1, context="get_ods_scan_details")
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "status", "created_on"],
            context="get_ods_scan_details",
        )

    def test_search_ods_scan_hosts_returns_details(self):
        """Test that ODS scan-host search returns full host metadata."""
        result = self.call_method(self.module.search_ods_scan_hosts, limit=5)

        self.assert_no_error(result, context="search_ods_scan_hosts")
        self.assert_valid_list_response(result, min_length=0, context="search_ods_scan_hosts")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "scan_id", "host_id"],
                context="search_ods_scan_hosts",
            )

    def test_get_ods_scan_host_details_with_valid_id(self):
        """Test ODS scan-host detail lookup using a valid metadata ID."""
        search_result = self.call_method(self.module.search_ods_scan_hosts, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No ODS scan-host records available to test get_ods_scan_host_details",
                context="test_get_ods_scan_host_details_with_valid_id",
            )

        scan_host_id = self.get_first_id(search_result)
        if not scan_host_id:
            self.skip_with_warning(
                "Could not extract ODS scan-host ID from search results",
                context="test_get_ods_scan_host_details_with_valid_id",
            )

        result = self.call_method(self.module.get_ods_scan_host_details, ids=[scan_host_id])

        self.assert_no_error(result, context="get_ods_scan_host_details")
        self.assert_valid_list_response(
            result,
            min_length=1,
            context="get_ods_scan_host_details",
        )
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "scan_id", "host_id"],
            context="get_ods_scan_host_details",
        )

    def test_search_ods_scheduled_scans_returns_details(self):
        """Test that scheduled ODS scan search returns full schedule details."""
        result = self.call_method(self.module.search_ods_scheduled_scans, limit=5)

        self.assert_no_error(result, context="search_ods_scheduled_scans")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_ods_scheduled_scans",
        )

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "status", "description"],
                context="search_ods_scheduled_scans",
            )

    def test_get_ods_scheduled_scan_details_with_valid_id(self):
        """Test scheduled ODS scan detail lookup using a valid schedule ID."""
        search_result = self.call_method(self.module.search_ods_scheduled_scans, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No scheduled ODS scans available to test get_ods_scheduled_scan_details",
                context="test_get_ods_scheduled_scan_details_with_valid_id",
            )

        scheduled_scan_id = self.get_first_id(search_result)
        if not scheduled_scan_id:
            self.skip_with_warning(
                "Could not extract scheduled ODS scan ID from search results",
                context="test_get_ods_scheduled_scan_details_with_valid_id",
            )

        result = self.call_method(
            self.module.get_ods_scheduled_scan_details,
            ids=[scheduled_scan_id],
        )

        self.assert_no_error(result, context="get_ods_scheduled_scan_details")
        self.assert_valid_list_response(
            result,
            min_length=1,
            context="get_ods_scheduled_scan_details",
        )
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "status", "description"],
            context="get_ods_scheduled_scan_details",
        )

    def test_search_ods_malicious_files_returns_details(self):
        """Test that ODS malicious-file search returns full file details."""
        result = self.call_method(self.module.search_ods_malicious_files, limit=5)

        self.assert_no_error(result, context="search_ods_malicious_files")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_ods_malicious_files",
        )

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "scan_id", "hash"],
                context="search_ods_malicious_files",
            )

    def test_get_ods_malicious_file_details_with_valid_id(self):
        """Test malicious-file detail lookup using a valid file ID."""
        search_result = self.call_method(self.module.search_ods_malicious_files, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No ODS malicious files available to test get_ods_malicious_file_details",
                context="test_get_ods_malicious_file_details_with_valid_id",
            )

        malicious_file_id = self.get_first_id(search_result)
        if not malicious_file_id:
            self.skip_with_warning(
                "Could not extract malicious file ID from search results",
                context="test_get_ods_malicious_file_details_with_valid_id",
            )

        result = self.call_method(
            self.module.get_ods_malicious_file_details,
            ids=[malicious_file_id],
        )

        self.assert_no_error(result, context="get_ods_malicious_file_details")
        self.assert_valid_list_response(
            result,
            min_length=1,
            context="get_ods_malicious_file_details",
        )
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "scan_id", "hash"],
            context="get_ods_malicious_file_details",
        )
