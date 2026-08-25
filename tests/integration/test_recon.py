"""Integration tests for the Recon module."""

import pytest

from falcon_mcp.modules.recon import ReconModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestReconIntegration(BaseIntegrationTest):
    """Integration tests for the Recon module with real API calls.

    Validates:
    - Correct FalconPy operation names (QueryNotificationsV1, GetNotificationsDetailedV1, etc.)
    - GET-with-params pattern for all three Get* operations (use_params=True)
    - Two-step search pattern returns full details, not just IDs
    - FQL filter fields accepted by the live API

    Requires Falcon Intelligence Recon, Counter Adversary, or Adversary Intelligence
    subscription. Tests skip gracefully if no data is present.
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Recon module with a real client."""
        self.module = ReconModule(falcon_client)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def test_search_recon_notifications_operation_names(self):
        """Validate QueryNotificationsV1 and GetNotificationsDetailedV1 operation names."""
        result = self.call_method(self.module.search_recon_notifications, limit=1)
        self.assert_no_error(result, context="QueryNotificationsV1 / GetNotificationsDetailedV1 validation")

    def test_search_recon_notifications_returns_list(self):
        """Test that search returns a list or empty-response dict (never an error)."""
        result = self.call_method(self.module.search_recon_notifications, limit=5)

        self.assert_no_error(result, context="search_recon_notifications")
        self.assert_valid_list_response(
            result, min_length=0, context="search_recon_notifications"
        )

    def test_search_recon_notifications_returns_full_details(self):
        """Test that results contain full notification detail, not just IDs."""
        result = self.call_method(self.module.search_recon_notifications, limit=3)

        self.assert_no_error(result, context="search_recon_notifications details")

        records = result["results"] if isinstance(result, dict) else result
        if not records:
            self.skip_with_warning(
                "No recon notifications available — skipping details field validation",
                context="search_recon_notifications full details",
            )
            return

        # Full details should have more than just an id field
        first = records[0]
        assert isinstance(first, dict), "Expected dict entity"
        assert "id" in first, f"Missing 'id' field; got keys: {list(first.keys())}"
        # A detailed notification has status and rule metadata at minimum
        assert len(first.keys()) > 1, (
            f"Result looks like ID-only response; got keys: {list(first.keys())}"
        )

    def test_search_recon_notifications_with_filter(self):
        """Test search with a simple FQL filter."""
        result = self.call_method(
            self.module.search_recon_notifications,
            filter="status:'new'",
            limit=3,
        )
        self.assert_no_error(result, context="search_recon_notifications filter=status:'new'")

    def test_search_recon_notifications_with_sort(self):
        """Test sort parameter accepted by the API."""
        result = self.call_method(
            self.module.search_recon_notifications,
            sort="created_date|desc",
            limit=3,
        )
        self.assert_no_error(result, context="search_recon_notifications sort=created_date|desc")

    def test_notification_sort_keys_are_nested_under_notification(self):
        """Both documented sort fields read back from `notification.<field>`, not the root.

        `sort="created_date.desc"` is valid, but a notification record's root holds only
        `id` and `notification`. A consumer that sorts by a documented key and then reads
        that key off the record gets `None`, silently.

        Pinned because the mapping is a schema fact the `sort` description has to state
        correctly, and because it is why this tool gets no sort-order test: the obvious
        `[r["created_date"] for r in rows]` raises KeyError instead of comparing anything.
        """
        result = self.call_method(
            self.module.search_recon_notifications, sort="created_date.desc", limit=3
        )
        self.assert_no_error(result, context="search_recon_notifications created_date.desc")
        records = self.skip_unless_tenant_has(
            result, "recon notifications", "notification sort key nesting"
        )
        first = records[0]

        notification = first.get("notification")
        assert isinstance(notification, dict), (
            f"Expected a `notification` dict to hold the sort keys; got {type(notification)}. "
            f"Root keys: {sorted(first.keys())}"
        )

        for sort_field in ("created_date", "updated_date"):
            assert sort_field not in first, (
                f"`{sort_field}` is now a root-level field, so the sort description's "
                f"nesting note is stale for it. Root keys: {sorted(first.keys())}"
            )
            assert sort_field in notification, (
                f"Sort field `{sort_field}` is documented as reading from "
                f"`notification.{sort_field}`, but that key is absent. notification keys: "
                f"{sorted(notification.keys())}"
            )

    def test_search_recon_notifications_with_q(self):
        """Test free-text q parameter."""
        result = self.call_method(
            self.module.search_recon_notifications,
            q="domain",
            limit=3,
        )
        self.assert_no_error(result, context="search_recon_notifications q=domain")

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------

    def test_search_recon_rules_operation_names(self):
        """Validate QueryRulesV1 and GetRulesV1 operation names."""
        result = self.call_method(self.module.search_recon_rules, limit=1)
        self.assert_no_error(result, context="QueryRulesV1 / GetRulesV1 validation")

    def test_search_recon_rules_returns_list(self):
        """Test that rule search returns a list or empty-response dict."""
        result = self.call_method(self.module.search_recon_rules, limit=5)

        self.assert_no_error(result, context="search_recon_rules")
        self.assert_valid_list_response(result, min_length=0, context="search_recon_rules")

    def test_search_recon_rules_returns_full_details(self):
        """Test that rule results contain full rule definition, not just IDs."""
        result = self.call_method(self.module.search_recon_rules, limit=3)

        self.assert_no_error(result, context="search_recon_rules details")

        records = result["results"] if isinstance(result, dict) else result
        if not records:
            self.skip_with_warning(
                "No recon rules available — skipping details field validation",
                context="search_recon_rules full details",
            )
            return

        first = records[0]
        assert isinstance(first, dict), "Expected dict entity"
        assert "id" in first, f"Missing 'id' field; got keys: {list(first.keys())}"
        assert len(first.keys()) > 1, (
            f"Result looks like ID-only response; got keys: {list(first.keys())}"
        )

    def test_search_recon_rules_with_filter(self):
        """Test rule search with status filter."""
        result = self.call_method(
            self.module.search_recon_rules,
            filter="status:'active'",
            limit=3,
        )
        self.assert_no_error(result, context="search_recon_rules filter=status:'active'")

    def test_search_recon_rules_sort_order_survives_hydration(self):
        """The requested sort order survives the QueryRulesV1 -> GetRulesV1 hydration step.

        `GetRulesV1` returns rules in an order unrelated to the query step's (measured: a
        different order on 6 of 6 trials), so without this the sort could be scrambled on
        every call and the rest of this file would still pass.

        `created_timestamp` is the probe because it is strictly monotone in both directions
        here. `priority` and `topic` — the other documented sort keys — tie across rows on
        this tenant, and a tied key tie-breaks unstably, so they would flake. The limit is
        deliberately 8 rather than 20: the tenant holds few rules, and asking for more than
        exist gives no extra coverage.
        """
        key = "created_timestamp"
        ascending = self.call_method(self.module.search_recon_rules, sort=f"{key}.asc", limit=8)
        descending = self.call_method(self.module.search_recon_rules, sort=f"{key}.desc", limit=8)

        self.assert_no_error(ascending, context=f"search_recon_rules {key}.asc")
        self.assert_no_error(descending, context=f"search_recon_rules {key}.desc")

        self.assert_sort_orders_rows(
            [rule[key] for rule in self._unwrap_results(ascending)],
            [rule[key] for rule in self._unwrap_results(descending)],
            key,
            context="search_recon_rules",
        )

    # ------------------------------------------------------------------
    # Exposed-data records
    # ------------------------------------------------------------------

    def test_search_recon_exposed_data_records_operation_names(self):
        """Validate QueryNotificationsExposedDataRecordsV1 and GetNotificationsExposedDataRecordsV1 names."""
        result = self.call_method(self.module.search_recon_exposed_data_records, limit=1)
        self.assert_no_error(
            result,
            context="QueryNotificationsExposedDataRecordsV1 / GetNotificationsExposedDataRecordsV1 validation",
        )

    def test_search_recon_exposed_data_records_returns_list(self):
        """Test that exposed-data search returns a list or empty-response dict."""
        result = self.call_method(self.module.search_recon_exposed_data_records, limit=5)

        self.assert_no_error(result, context="search_recon_exposed_data_records")
        self.assert_valid_list_response(
            result, min_length=0, context="search_recon_exposed_data_records"
        )

    def test_search_recon_exposed_data_records_returns_full_details(self):
        """Test that exposed-data results contain full record detail, not just IDs."""
        result = self.call_method(self.module.search_recon_exposed_data_records, limit=3)

        self.assert_no_error(result, context="search_recon_exposed_data_records details")

        records = result["results"] if isinstance(result, dict) else result
        if not records:
            self.skip_with_warning(
                "No exposed-data records available — skipping details field validation",
                context="search_recon_exposed_data_records full details",
            )
            return

        first = records[0]
        assert isinstance(first, dict), "Expected dict entity"
        assert "id" in first, f"Missing 'id' field; got keys: {list(first.keys())}"
        assert len(first.keys()) > 1, (
            f"Result looks like ID-only response; got keys: {list(first.keys())}"
        )

    def test_search_recon_exposed_data_records_with_sort(self):
        """Test sort parameter accepted by the API."""
        result = self.call_method(
            self.module.search_recon_exposed_data_records,
            sort="created_date|desc",
            limit=3,
        )
        self.assert_no_error(
            result, context="search_recon_exposed_data_records sort=created_date|desc"
        )

    def test_search_recon_exposed_data_records_rows_in_query_step_order(self):
        """Hydrated records come back in the order the query step reported them.

        A reorder-contract test rather than a monotonicity one: this endpoint has no
        strictly monotone sort field on this tenant. Exposed-data records are created in
        bulk per notification, so `created_date` and `exposure_date` both repeat heavily
        (measured: 3 distinct `created_date` values across 8 rows, and 1 distinct
        `exposure_date`), and a tied key tie-breaks unstably. Asserting the reorder contract
        instead keeps the guard without the flakiness.

        The contract is load-bearing here: `GetNotificationsExposedDataRecordsV1` returned a
        different order than it was handed on 5 of 6 measured trials.
        """
        self.assert_rows_in_query_step_order(
            self.module.search_recon_exposed_data_records,
            id_field="id",
            context="search_recon_exposed_data_records reorder contract",
            limit=8,
        )

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------

    def test_aggregate_recon_notifications_operation_name(self):
        """Validate the AggregateNotificationsV1 operation name and terms buckets."""
        result = self.call_method(
            self.module.aggregate_recon_notifications,
            field="status",
            aggregate_type="terms",
            name="by_status",
            size=5,
        )

        self.assert_no_error(result, context="AggregateNotificationsV1 validation")
        assert isinstance(result, list), f"Expected list of aggregations; got {type(result)}"

        if not result:
            self.skip_with_warning(
                "No notification aggregations returned",
                context="aggregate_recon_notifications",
            )
            return

        agg = result[0]
        assert agg.get("name") == "by_status", f"Aggregation name not echoed back: {agg}"
        for bucket in agg.get("buckets") or []:
            # Buckets key on `label`, not the Elasticsearch-style `key`.
            assert "label" in bucket, f"Bucket missing 'label': {bucket}"
            assert "count" in bucket, f"Bucket missing 'count': {bucket}"

    def test_aggregate_recon_notifications_supported_types(self):
        """Every aggregate_type the tool exposes must be accepted by the live API."""
        cases = {
            "terms": {"field": "rule_topic", "size": 3},
            "date_histogram": {"field": "created_date", "interval": "day"},
            "cardinality": {"field": "rule_id"},
            "max": {"field": "created_date"},
            "min": {"field": "created_date"},
            "date_range": {
                "field": "created_date",
                "date_ranges": [{"from": "now-30d", "to": "now"}],
            },
            "range": {
                "field": "created_date",
                "ranges": [{"From": 0, "To": 9999999999999}],
            },
        }
        for agg_type, kwargs in cases.items():
            result = self.call_method(
                self.module.aggregate_recon_notifications,
                aggregate_type=agg_type,
                name=f"probe_{agg_type}",
                **kwargs,
            )
            self.assert_no_error(result, context=f"notifications aggregate_type={agg_type}")

    def test_aggregate_recon_notifications_filter_narrows_results(self):
        """A documented FQL filter must be honored, not silently ignored."""
        unfiltered = self.call_method(
            self.module.aggregate_recon_notifications,
            field="rule_topic",
            aggregate_type="terms",
            name="all",
            size=50,
        )
        filtered = self.call_method(
            self.module.aggregate_recon_notifications,
            field="rule_topic",
            aggregate_type="terms",
            filter="rule_topic:'SA_TYPOSQUATTING'",
            name="filtered",
            size=50,
        )

        self.assert_no_error(unfiltered, context="aggregate notifications unfiltered")
        self.assert_no_error(filtered, context="aggregate notifications filtered")

        all_buckets = (unfiltered[0].get("buckets") or []) if unfiltered else []
        filtered_buckets = (filtered[0].get("buckets") or []) if filtered else []

        if len(all_buckets) < 2 or not filtered_buckets:
            self.skip_with_warning(
                "Not enough topic diversity to prove the filter narrowed results",
                context="aggregate_recon_notifications filter",
            )
            return

        labels = {bucket["label"] for bucket in filtered_buckets}
        assert labels == {"SA_TYPOSQUATTING"}, (
            f"Filter did not narrow to the requested topic; got labels {labels}"
        )

    def test_aggregate_recon_exposed_data_records_operation_name(self):
        """Validate the AggregateNotificationsExposedDataRecordsV1 operation name."""
        result = self.call_method(
            self.module.aggregate_recon_exposed_data_records,
            field="credential_status",
            aggregate_type="terms",
            name="by_credential_status",
            size=5,
        )

        self.assert_no_error(
            result, context="AggregateNotificationsExposedDataRecordsV1 validation"
        )
        assert isinstance(result, list), f"Expected list of aggregations; got {type(result)}"

    def test_aggregate_recon_exposed_data_records_supported_types(self):
        """Every aggregate_type the tool exposes must be accepted by this endpoint too.

        Both aggregate tools share one `ReconAggregateType`, so the exposed-data
        endpoint needs the same live coverage as the notifications one.
        """
        cases = {
            "terms": {"field": "rule.topic", "size": 3},
            "date_histogram": {"field": "created_date", "interval": "day"},
            "cardinality": {"field": "rule.id"},
            "max": {"field": "created_date"},
            "min": {"field": "created_date"},
            "date_range": {
                "field": "created_date",
                "date_ranges": [{"from": "now-30d", "to": "now"}],
            },
            "range": {
                "field": "created_date",
                "ranges": [{"From": 0, "To": 9999999999999}],
            },
        }
        for agg_type, kwargs in cases.items():
            result = self.call_method(
                self.module.aggregate_recon_exposed_data_records,
                aggregate_type=agg_type,
                name=f"probe_{agg_type}",
                **kwargs,
            )
            self.assert_no_error(result, context=f"exposed-data aggregate_type={agg_type}")

    def test_aggregate_recon_exposed_data_records_documented_fields(self):
        """Every field the aggregate guide documents must be accepted by the live API.

        This endpoint rejects unlisted fields with a 400, so the guide's list is a
        hard contract rather than a suggestion.
        """
        documented = [
            "cid",
            "notification_id",
            "notification_group_id",
            "created_date",
            "rule.id",
            "rule.name",
            "rule.topic",
            "source_category",
            "site",
            "author",
            "file.name",
            "credential_status",
            "bot.operating_system.hardware_id",
            "bot.bot_id",
        ]
        for field in documented:
            result = self.call_method(
                self.module.aggregate_recon_exposed_data_records,
                field=field,
                aggregate_type="terms",
                name="probe",
                size=1,
            )
            self.assert_no_error(result, context=f"exposed-data aggregate field={field}")

    def test_aggregate_recon_exposed_data_records_sub_aggregates(self):
        """Nested sub-aggregations must come back inside the parent buckets."""
        result = self.call_method(
            self.module.aggregate_recon_exposed_data_records,
            field="rule.topic",
            aggregate_type="terms",
            name="by_topic",
            size=2,
            sub_aggregates=[
                {
                    "type": "terms",
                    "field": "credential_status",
                    "name": "by_status",
                    "size": 2,
                }
            ],
        )

        self.assert_no_error(result, context="exposed-data sub_aggregates")

        buckets = (result[0].get("buckets") or []) if result else []
        if not buckets:
            self.skip_with_warning(
                "No exposed-data records to nest aggregations over",
                context="aggregate_recon_exposed_data_records sub_aggregates",
            )
            return

        assert "sub_aggregates" in buckets[0], (
            f"Sub-aggregation missing from bucket: {buckets[0]}"
        )

    # ------------------------------------------------------------------
    # Rule preview
    # ------------------------------------------------------------------

    def test_preview_recon_rule_operation_name(self):
        """Validate PreviewRuleV1 and its fixed channel/count/site breakdown."""
        result = self.call_method(
            self.module.preview_recon_rule,
            topic="SA_DOMAIN",
            filter="(domain:'example.com')",
            lookback_days=30,
        )

        self.assert_no_error(result, context="PreviewRuleV1 validation")
        assert isinstance(result, list), f"Expected list of aggregations; got {type(result)}"

        names = {agg.get("name") for agg in result}
        assert "count" in names, f"Preview response missing the 'count' aggregation: {names}"
        assert names <= {"channel", "count", "site"}, (
            f"Preview returned unexpected aggregations: {names}"
        )

    def test_preview_recon_rule_accepts_documented_lookback_values(self):
        """lookback_days is an enum; every value the tool exposes must be accepted."""
        for lookback in (7, 30, 180, 365):
            result = self.call_method(
                self.module.preview_recon_rule,
                topic="SA_DOMAIN",
                filter="(domain:'example.com')",
                lookback_days=lookback,
            )
            self.assert_no_error(result, context=f"PreviewRuleV1 lookback_days={lookback}")

    def test_preview_recon_rule_omitted_lookback(self):
        """Omitting lookback_days must still be a valid request."""
        result = self.call_method(
            self.module.preview_recon_rule,
            topic="SA_EMAIL",
            filter="(email:'user@example.com')",
        )
        self.assert_no_error(result, context="PreviewRuleV1 without lookback_days")

    def test_preview_recon_rule_documented_topic_filters(self):
        """Each topic/condition-word pair shown in the preview guide must parse."""
        cases = [
            ("SA_DOMAIN", "(domain:'example.com')"),
            ("SA_EMAIL", "(email:'user@example.com')"),
            ("SA_IP", "(ip:'1.2.3.4')"),
            ("SA_AUTHOR", "(author:'handle')"),
            ("SA_BRAND_PRODUCT", "(phrase:'Acme')+(keyword:'Acme')"),
            ("SA_THIRD_PARTY", "(phrase:'Acme')"),
            ("SA_CUSTOM", "(keyword:'term')"),
            ("SA_VIP", "(keyword:'term')"),
            ("SA_CVE", "(keyword:'term')"),
            ("SA_ALIAS", "(keyword:'term')"),
        ]
        for topic, rule_filter in cases:
            result = self.call_method(
                self.module.preview_recon_rule,
                topic=topic,
                filter=rule_filter,
                lookback_days=30,
            )
            self.assert_no_error(result, context=f"PreviewRuleV1 topic={topic}")

    def test_preview_recon_rule_invalid_filter_returns_guide(self):
        """A bare (non-FQL) filter is rejected and the guide is returned for self-correction."""
        result = self.call_method(
            self.module.preview_recon_rule,
            topic="SA_DOMAIN",
            filter="example.com",
        )

        assert isinstance(result, dict), f"Expected the FQL-error dict; got {type(result)}"
        assert "fql_guide" in result, f"Rejected filter did not return a guide: {result}"
