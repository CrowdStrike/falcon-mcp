"""Integration tests for the Exclusions module."""

import time
import warnings

import pytest

from falcon_mcp.modules.exclusions import ExclusionsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestExclusionsIntegration(BaseIntegrationTest):
    """Integration tests for the Exclusions module with real API calls.

    Validates against the live API:
    - Correct FalconPy operation names for all four exclusion types (IOA v2,
      ML v2, Sensor Visibility v1, Certificate-Based v1)
    - Two-step search pattern returns full details, not just IDs
    - Per-type create/delete body formats (wrapped vs flat, group key mapping)
    - Certificate metadata lookup

    Tests skip with a warning when the required exclusion scopes are absent.
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Exclusions module with a real client."""
        self.module = ExclusionsModule(falcon_client)

    # ---- Helpers ----------------------------------------------------------------

    def _scopes_available(self, exclusion_type: str) -> bool:
        """Return True if a search for the given type does not error on scope."""
        result = self.call_method(
            self.module.search_exclusions, exclusion_type=exclusion_type, limit=1
        )
        # A scope/permission failure surfaces as an error dict or error list.
        if isinstance(result, dict) and "error" in result:
            return False
        if isinstance(result, list) and result and isinstance(result[0], dict):
            if "error" in result[0]:
                return False
        return True

    def _first_host_group_id(self, falcon_client) -> str | None:
        """Fetch one real host group ID for scoping create roundtrips."""
        response = falcon_client.command("queryHostGroups", parameters={"limit": 1})
        if isinstance(response, dict) and response.get("status_code") == 200:
            resources = response.get("body", {}).get("resources", [])
            if resources:
                return resources[0]
        return None

    def _extract_id(self, result):
        """Extract an exclusion id from a create response (dict or bare string)."""
        if not isinstance(result, list) or not result:
            return None
        first = result[0]
        if isinstance(first, dict):
            return first.get("id")
        if isinstance(first, str):
            return first
        return None

    # ---- Operation name validation ----------------------------------------------

    def test_operation_names_are_correct(self):
        """Validate all per-type query+get operation names against the live API.

        A wrong operation name (typo) surfaces as an API error here even though
        mocked unit tests would pass.
        """
        for exclusion_type in ("ioa", "ml", "sensor_visibility", "certificate"):
            result = self.call_method(
                self.module.search_exclusions,
                exclusion_type=exclusion_type,
                limit=1,
            )
            # Empty results return the FQL guide dict (acceptable); only a true
            # error indicates a bad operation name or missing scope.
            if isinstance(result, list) and result and isinstance(result[0], dict):
                assert "error" not in result[0], (
                    f"Operation name validation failed for {exclusion_type}: {result[0]}"
                )

    # ---- Per-type full-detail searches ------------------------------------------

    def test_search_ioa_returns_details(self):
        """IOA search returns full details when results exist."""
        if not self._scopes_available("ioa"):
            self.skip_with_warning("IOA Exclusions scope not available", "search ioa")
            return
        result = self.call_method(
            self.module.search_exclusions, exclusion_type="ioa", limit=2
        )
        if not result or isinstance(result, dict):
            self.skip_with_warning("No IOA exclusions found", "search ioa details")
            return
        self.assert_search_returns_details(
            result, expected_fields=["id", "name", "pattern_id"], context="ioa"
        )

    def test_search_ml_returns_details(self):
        """ML search returns full details when results exist."""
        if not self._scopes_available("ml"):
            self.skip_with_warning("ML Exclusions scope not available", "search ml")
            return
        result = self.call_method(
            self.module.search_exclusions, exclusion_type="ml", limit=2
        )
        if not result or isinstance(result, dict):
            self.skip_with_warning("No ML exclusions found", "search ml details")
            return
        self.assert_search_returns_details(
            result, expected_fields=["id", "value"], context="ml"
        )

    def test_search_sensor_visibility_returns_details(self):
        """Sensor visibility search returns full details when results exist."""
        if not self._scopes_available("sensor_visibility"):
            self.skip_with_warning(
                "Sensor Visibility Exclusions scope not available", "search sv"
            )
            return
        result = self.call_method(
            self.module.search_exclusions,
            exclusion_type="sensor_visibility",
            limit=2,
        )
        if not result or isinstance(result, dict):
            self.skip_with_warning("No SV exclusions found", "search sv details")
            return
        self.assert_search_returns_details(
            result, expected_fields=["id", "value"], context="sensor_visibility"
        )

    def test_search_certificate_returns_details(self):
        """Certificate search returns full details when results exist."""
        if not self._scopes_available("certificate"):
            self.skip_with_warning(
                "Certificate exclusion scope not available", "search cert"
            )
            return
        result = self.call_method(
            self.module.search_exclusions, exclusion_type="certificate", limit=2
        )
        if not result or isinstance(result, dict):
            self.skip_with_warning("No certificate exclusions found", "search cert")
            return
        self.assert_search_returns_details(
            result, expected_fields=["id", "name", "certificate"], context="certificate"
        )

    # ---- Create / delete roundtrips ---------------------------------------------

    def test_ml_create_delete_roundtrip(self, falcon_client):
        """Create an ML exclusion (wrapped v2 body), verify, then delete it."""
        if not self._scopes_available("ml"):
            self.skip_with_warning("ML Exclusions scope not available", "ml roundtrip")
            return
        group_id = self._first_host_group_id(falcon_client)
        if not group_id:
            self.skip_with_warning("No host group available", "ml roundtrip")
            return

        ts = int(time.time())
        value = f"/tmp/falcon-mcp-test-{ts}.sh"
        create_result = self.call_method(
            self.module.create_exclusion,
            exclusion_type="ml",
            value=value,
            excluded_from=["blocking"],
            host_groups=[group_id],
            comment="falcon-mcp integration test",
        )
        self.assert_no_error(create_result, context="ml create")
        excl_id = self._extract_id(create_result)
        if not excl_id:
            self.skip_with_warning(
                f"Could not extract ML exclusion id from {create_result}", "ml roundtrip"
            )
            return

        try:
            delete_result = self.call_method(
                self.module.delete_exclusions,
                exclusion_type="ml",
                ids=[excl_id],
                comment="falcon-mcp integration cleanup",
            )
            self.assert_no_error(delete_result, context="ml delete")
        finally:
            # Best-effort safety net in case the assertion above raised.
            self._safe_cleanup("ml", excl_id)

    def test_sensor_visibility_create_delete_roundtrip(self, falcon_client):
        """Create a sensor visibility exclusion (flat body), verify, then delete it."""
        if not self._scopes_available("sensor_visibility"):
            self.skip_with_warning(
                "Sensor Visibility Exclusions scope not available", "sv roundtrip"
            )
            return
        group_id = self._first_host_group_id(falcon_client)
        if not group_id:
            self.skip_with_warning("No host group available", "sv roundtrip")
            return

        ts = int(time.time())
        value = f"/tmp/falcon-mcp-test-{ts}/**"
        create_result = self.call_method(
            self.module.create_exclusion,
            exclusion_type="sensor_visibility",
            value=value,
            host_groups=[group_id],
            comment="falcon-mcp integration test",
        )
        self.assert_no_error(create_result, context="sv create")
        excl_id = self._extract_id(create_result)
        if not excl_id:
            self.skip_with_warning(
                f"Could not extract SV exclusion id from {create_result}", "sv roundtrip"
            )
            return

        try:
            delete_result = self.call_method(
                self.module.delete_exclusions,
                exclusion_type="sensor_visibility",
                ids=[excl_id],
                comment="falcon-mcp integration cleanup",
            )
            self.assert_no_error(delete_result, context="sv delete")
        finally:
            self._safe_cleanup("sensor_visibility", excl_id)

    def test_ioa_create_delete_roundtrip(self, falcon_client):
        """Create an IOA exclusion (wrapped v2 body), verify, then delete it.

        Requires a real pattern_id, which is read from an existing IOA exclusion.
        """
        if not self._scopes_available("ioa"):
            self.skip_with_warning("IOA Exclusions scope not available", "ioa roundtrip")
            return

        existing = self.call_method(
            self.module.search_exclusions, exclusion_type="ioa", limit=1
        )
        if not existing or isinstance(existing, dict):
            self.skip_with_warning(
                "No existing IOA exclusion to source a real pattern_id", "ioa roundtrip"
            )
            return
        pattern_id = existing[0].get("pattern_id")
        if not pattern_id:
            self.skip_with_warning(
                "Existing IOA exclusion has no pattern_id", "ioa roundtrip"
            )
            return

        group_id = self._first_host_group_id(falcon_client)
        if not group_id:
            self.skip_with_warning("No host group available", "ioa roundtrip")
            return

        ts = int(time.time())
        create_result = self.call_method(
            self.module.create_exclusion,
            exclusion_type="ioa",
            name=f"falcon-mcp-test-{ts}",
            pattern_id=str(pattern_id),
            ifn_regex=f"/tmp/falcon-mcp-test-{ts}",
            cl_regex=f"/tmp/falcon-mcp-test-{ts}",
            host_groups=[group_id],
            description="falcon-mcp integration test",
            comment="falcon-mcp integration test",
        )
        self.assert_no_error(create_result, context="ioa create")
        excl_id = self._extract_id(create_result)
        if not excl_id:
            self.skip_with_warning(
                f"Could not extract IOA exclusion id from {create_result}", "ioa roundtrip"
            )
            return

        try:
            delete_result = self.call_method(
                self.module.delete_exclusions,
                exclusion_type="ioa",
                ids=[excl_id],
                comment="falcon-mcp integration cleanup",
            )
            self.assert_no_error(delete_result, context="ioa delete")
        finally:
            self._safe_cleanup("ioa", excl_id)

    def _safe_cleanup(self, exclusion_type: str, excl_id: str) -> None:
        """Best-effort delete that never raises (used in finally blocks)."""
        try:
            self.call_method(
                self.module.delete_exclusions,
                exclusion_type=exclusion_type,
                ids=[excl_id],
                comment="falcon-mcp integration cleanup",
            )
        except Exception as exc:  # noqa: BLE001 - cleanup must not mask test result
            warnings.warn(
                f"Failed to clean up {exclusion_type} exclusion {excl_id}: {exc}",
                stacklevel=2,
            )

    # ---- Certificate discovery --------------------------------------------------

    def test_search_certificates(self):
        """search_certificates calls the certificate exclusion operations."""
        if not self._scopes_available("certificate"):
            self.skip_with_warning(
                "Certificate exclusion scope not available", "search_certificates"
            )
            return
        result = self.call_method(self.module.search_certificates, limit=2)
        if isinstance(result, list) and result and isinstance(result[0], dict):
            assert "error" not in result[0], f"search_certificates error: {result[0]}"

    def test_get_certificate_details(self):
        """get_certificate_details returns without an API error for a dummy hash.

        A well-formed but nonexistent hash returns empty resources rather than an
        error, so this validates the certificates_get_v1 operation name is correct.
        """
        dummy_sha256 = "a" * 64
        result = self.call_method(
            self.module.get_certificate_details, sha256=dummy_sha256
        )
        if isinstance(result, list) and result and isinstance(result[0], dict):
            assert "error" not in result[0], (
                f"get_certificate_details error: {result[0]}"
            )
