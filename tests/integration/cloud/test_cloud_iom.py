"""Integration tests for IOM findings and CSPM suppression rule tools."""

import time

import pytest

from falcon_mcp.modules.cloud.cloud import CloudModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCloudIomIntegration(BaseIntegrationTest):
    """Integration tests for IOM findings and CSPM suppression rule tools."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = CloudModule(falcon_client)

    def test_search_iom_findings_returns_details(self):
        """Validates cspm_evaluations_iom_queries and cspm_evaluations_iom_entities operation names."""
        result = self.call_method(self.module.search_iom_findings, limit=5)
        self.assert_no_error(result, context="search_iom_findings")
        self.skip_unless_tenant_has(result, "IOM findings", "search_iom_findings")

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "cid", "cloud", "evaluation", "resource"],
            context="search_iom_findings full details",
        )

    def test_search_iom_findings_with_severity_filter(self):
        result = self.call_method(
            self.module.search_iom_findings,
            filter="severity:'critical'",
            limit=3,
        )
        self.assert_valid_list_response(result, min_length=0, context="search_iom_findings severity filter")

    def test_search_iom_findings_with_cloud_provider_filter(self):
        result = self.call_method(
            self.module.search_iom_findings,
            filter="cloud_provider:'aws'",
            limit=3,
        )
        self.assert_no_error(result, context="search_iom_findings with cloud_provider filter")
        self.assert_valid_list_response(result, min_length=0, context="search_iom_findings cloud_provider filter")

    def test_search_iom_findings_with_sort(self):
        result = self.call_method(
            self.module.search_iom_findings,
            sort="severity|desc",
            limit=3,
        )
        self.assert_no_error(result, context="search_iom_findings with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_iom_findings with sort")

    def test_search_iom_findings_batching(self):
        """A limit above the 100-per-request detail batch size still returns every record.

        `len()` on the envelope counts its keys, so the old `len(result) > 100` guard was
        always false and this never exercised batching at all.
        """
        result = self.call_method(self.module.search_iom_findings, limit=200)
        self.assert_no_error(result, context="search_iom_findings batching")
        findings = self.skip_unless_tenant_has(result, "IOM findings", "search_iom_findings batching")

        total = result["pagination"]["total"]
        if total is not None and total <= 100:
            self.skip_with_warning(
                f"tenant has only {total} IOM findings, so batching is not exercised",
                context="search_iom_findings batching",
            )
            return

        assert len(findings) > 100, (
            f"Requested 200 findings from a tenant reporting {total}, but only "
            f"{len(findings)} came back — the 100-per-request detail batching is dropping records."
        )
        ids = [f.get("id") for f in findings]
        assert len(set(ids)) == len(ids), "Batching returned the same finding more than once"

    def test_search_suppression_rules(self):
        """Validates the override endpoint pattern for suppression rules."""
        result = self.call_method(self.module.search_cspm_suppression_rules, limit=5)
        self.assert_no_error(result, context="search_cspm_suppression_rules")
        rules = self.skip_unless_tenant_has(result, "CSPM suppression rules", "search_cspm_suppression_rules")

        first_rule = rules[0]
        assert isinstance(first_rule, dict), f"Expected dict items for suppression rules, got {type(first_rule)}"
        assert first_rule.get("id"), f"Expected 'id' on a suppression rule. Got: {sorted(first_rule.keys())}"

    def test_create_and_delete_suppression_rule_roundtrip(self):
        """Creates a narrowly-scoped suppression rule then deletes it."""
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

        rule_id = None
        if isinstance(create_result, list) and len(create_result) > 0:
            first = create_result[0]
            rule_id = first if isinstance(first, str) else first.get("id")
            print(f"✅ Created suppression rule: {rule_id}")
        elif isinstance(create_result, dict) and "id" in create_result:
            rule_id = create_result["id"]
            print(f"✅ Created suppression rule: {rule_id}")

        if rule_id:
            delete_result = self.call_method(
                self.module.delete_cspm_suppression_rules,
                ids=[rule_id],
            )
            self.assert_no_error(delete_result, context="delete_cspm_suppression_rules")
            print(f"✅ Deleted suppression rule: {rule_id}")
        else:
            print("⚠️  Could not extract rule ID from create response, skipping delete")
