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
        """`severity` filters on the value nested at `evaluation.severity`.

        The filter is flat and the response is not, so a test written from the filter name
        alone would look for a top-level `severity` that never exists.
        """
        self.assert_filter_matches(
            self.module.search_iom_findings,
            "severity:'critical'",
            predicate=lambda finding: finding.get("evaluation", {}).get("severity") == "critical",
            predicate_desc="finding.evaluation.severity == 'critical'",
            note="Every guide and example in this repo uses these lowercase severity names.",
            limit=5,
        )

    def test_search_iom_findings_with_cloud_provider_filter(self):
        """`cloud_provider` filters on the value the response nests at `cloud.provider`.

        Lowercase is the only spelling this operation accepts — uppercase comes back as an
        empty HTTP 200 rather than an error, which
        `test_cloud_provider_casing_differs_across_cloud_endpoints` pins from the other side.
        """
        self.assert_filter_matches(
            self.module.search_iom_findings,
            "cloud_provider:'aws'",
            predicate=lambda finding: finding.get("cloud", {}).get("provider") == "aws",
            predicate_desc="finding.cloud.provider == 'aws'",
            note="The filter is cloud_provider; the response calls it cloud.provider.",
            limit=5,
        )

    def test_search_iom_findings_sort_orders_by_last_detected(self):
        """`last_detected` orders findings, and the order survives entity hydration.

        `last_detected` is the probe because it is the documented key with the most distinct
        values per page, which is what lets this catch `_reorder_by_ids` losing the order
        during hydration. `severity` and `status` hold a handful of values across half a
        million findings, so a page of either is almost entirely tied; `first_detected`
        returns a descending page that is genuinely out of order (3 of 3 trials).

        Comparison is truncated to milliseconds because that is the precision the endpoint
        actually orders on. The response carries nanoseconds, and findings written inside the
        same millisecond come back in arbitrary sub-millisecond order — measured on 6 of 6
        descending trials during a write burst, while every truncated comparison held. The
        full-precision value looks tie-free and is not, which is the flake this avoids; it
        also means the truncated values tie, hence `allow_ties`.

        The window filter is not cosmetic: unfiltered, the ascending page is entirely
        records with no `last_detected` at all, and null sort values cannot be compared.
        Read the value from `evaluation`, not the root — see
        `test_iom_sort_keys_are_never_at_the_record_root`.
        """
        key = "last_detected"
        window = f"{key}:>'now-3650d'"

        def to_millis(finding):
            """'YYYY-MM-DDTHH:MM:SS.mmm' — everything the endpoint's ordering respects."""
            return finding["evaluation"][key][:23]

        ascending = self.call_method(
            self.module.search_iom_findings, filter=window, sort=f"{key}.asc", limit=20
        )
        descending = self.call_method(
            self.module.search_iom_findings, filter=window, sort=f"{key}.desc", limit=20
        )
        self.assert_no_error(ascending, context=f"search_iom_findings {key}.asc")
        self.assert_no_error(descending, context=f"search_iom_findings {key}.desc")

        desc_millis = [
            to_millis(f) for f in self.skip_unless_tenant_has(descending, "IOM findings")
        ]
        self.assert_sort_orders_rows(
            [to_millis(f) for f in self.skip_unless_tenant_has(ascending, "IOM findings")],
            desc_millis,
            key,
            context="search_iom_findings",
            allow_ties=True,
        )

        piped = self.call_method(
            self.module.search_iom_findings, filter=window, sort=f"{key}|desc", limit=20
        )
        self.assert_no_error(piped, context=f"search_iom_findings {key}|desc")
        assert [
            to_millis(f) for f in self.skip_unless_tenant_has(piped, "IOM findings")
        ] == desc_millis, (
            f"'{key}|desc' and '{key}.desc' disagree. The tool documents the dot form and "
            "the pipe form is the API's own; both have to reach the same ordering. Only the "
            "millisecond-truncated sequence is compared: two runs seconds apart can legally "
            "return different rows within a tied millisecond."
        )

    def test_iom_severity_sort_puts_the_most_severe_first_in_ascending_order(self):
        """`severity.asc` returns critical findings; `severity.desc` returns informational.

        The endpoint sorts the underlying severity code, and critical is its lowest value,
        so the direction reads backwards from the word. An agent asking for the worst
        findings needs `severity.asc`, which is why the `sort` description says so and why
        this pins it — the failure is silent, and 'fixing' the tool to invert it would give
        the opposite of what was asked with no error to show for it.
        """
        severity_code = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}

        def leading_severity(direction):
            result = self.call_method(
                self.module.search_iom_findings, sort=f"severity.{direction}", limit=20
            )
            self.assert_no_error(result, context=f"search_iom_findings severity.{direction}")
            findings = self.skip_unless_tenant_has(result, "IOM findings", f"severity.{direction}")
            codes = [severity_code[f["evaluation"]["severity"]] for f in findings]
            assert codes == sorted(codes, reverse=direction == "desc"), (
                f"severity.{direction} did not order findings by severity code: {codes}"
            )
            return findings[0]["evaluation"]["severity"]

        assert leading_severity("asc") == "critical", (
            "severity.asc no longer leads with critical findings. If the endpoint now sorts "
            "severity by rank rather than by its numeric code, the note in the sort "
            "description is backwards and has to change with it."
        )
        assert leading_severity("desc") == "informational", (
            "severity.desc no longer leads with informational findings."
        )

    def test_iom_sort_keys_are_never_at_the_record_root(self):
        """Every documented sort field reads back from a nested key, not the root.

        `sort="severity.desc"` is valid, but the returned record's root holds only
        id/cid/cloud/cloud_groups/cloud_labels/evaluation/resource. A consumer that sorts by
        a documented key and then reads that key off the record gets `None`, silently.

        Pinned because the mapping is a schema fact the `sort` description has to state
        correctly, and because it is the trap a sort-order test here would fall into: the
        obvious `[r["severity"] for r in rows]` raises KeyError rather than comparing
        anything. The expected locations below are live-validated.
        """
        expected_location = {
            "severity": ("evaluation", "severity"),
            "status": ("evaluation", "status"),
            "first_detected": ("evaluation", "first_detected"),
            "last_detected": ("evaluation", "last_detected"),
            "cloud_provider": ("cloud", "provider"),
            "service": ("resource", "service"),
        }

        result = self.call_method(self.module.search_iom_findings, sort="severity.desc", limit=3)
        self.assert_no_error(result, context="search_iom_findings severity.desc")
        findings = self.skip_unless_tenant_has(result, "IOM findings", "iom sort key nesting")
        first = findings[0]

        for sort_field, (parent, key) in expected_location.items():
            assert sort_field not in first, (
                f"`{sort_field}` is now a root-level IOM field, so the sort description's "
                f"nesting note is stale for it. Root keys: {sorted(first.keys())}"
            )
            block = first.get(parent)
            assert isinstance(block, dict), (
                f"Expected a `{parent}` dict to hold `{sort_field}`; got {type(block)}. "
                f"Root keys: {sorted(first.keys())}"
            )
            assert key in block, (
                f"Sort field `{sort_field}` is documented as reading from "
                f"`{parent}.{key}`, but that key is absent. {parent} keys: "
                f"{sorted(block.keys())}"
            )

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
