"""Integration tests for the Cases module."""

import time

import pytest

from falcon_mcp.modules.cases import CasesModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCasesIntegration(BaseIntegrationTest):
    """Integration tests for Cases module with real API calls.

    Validates:
    - Correct FalconPy operation names (queries_cases_get_v1, entities_cases_post_v2, etc.)
    - Two-step search pattern returns full details, not just IDs
    - POST body usage for get_cases
    - Create (PUT) and update (PATCH) body formats
    - Evidence attachment body format (alert objects, not strings)
    - Tag management asymmetry (POST body add vs DELETE query params remove)
    - Template listing with GET query params (use_params=True)
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the cases module with a real client."""
        self.module = CasesModule(falcon_client)

    # -------------------------------------------------------------------------
    # Operation Name Validation
    # -------------------------------------------------------------------------

    def test_operation_names_search(self):
        """Validate queries_cases_get_v1 and entities_cases_post_v2 are correct."""
        result = self.call_method(self.module.search_cases, limit=1)
        self.assert_no_error(result, context="search operation names")

    def test_operation_names_templates(self):
        """Validate queries_templates_get_v1 and entities_templates_get_v1 are correct."""
        result = self.call_method(self.module.list_case_templates, limit=1)
        self.assert_no_error(result, context="template operation names")

    # -------------------------------------------------------------------------
    # Search Tests
    # -------------------------------------------------------------------------

    def test_search_cases_returns_details(self):
        """Test that search_cases returns full case details, not just IDs.

        Validates the two-step search pattern:
        1. queries_cases_get_v1 returns case IDs
        2. entities_cases_post_v2 returns full details
        """
        result = self.call_method(self.module.search_cases, limit=5)

        self.assert_no_error(result, context="search_cases")
        self.assert_valid_list_response(result, min_length=0, context="search_cases")

        cases = self._unwrap_results(result)
        if len(cases) > 0:
            self.assert_search_returns_details(
                cases,
                expected_fields=["id", "name", "status", "severity"],
                context="search_cases full details",
            )

    def test_search_cases_with_filter(self):
        """Test search_cases with FQL filter."""
        result = self.call_method(
            self.module.search_cases,
            filter="status:'new'",
            limit=3,
        )

        self.assert_no_error(result, context="search_cases with filter")
        self.assert_valid_list_response(
            result, min_length=0, context="search_cases with filter"
        )

    def test_search_cases_with_sort(self):
        """Test search_cases with sort parameter."""
        result = self.call_method(
            self.module.search_cases,
            sort="created_timestamp.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_cases with sort")
        self.assert_valid_list_response(
            result, min_length=0, context="search_cases with sort"
        )

    def test_search_cases_sort_order_survives_hydration(self):
        """The requested sort order survives the query -> get-by-IDs hydration step.

        `entities_cases_post_v2` returns cases in an order unrelated to the query step's
        (measured: a different order on 6 of 6 trials), so this is the sort assertion with
        real teeth — `test_search_cases_with_sort` above only checks that the parameter is
        accepted, which stays green even if hydration scrambles every row.

        `created_timestamp` is the probe because it is strictly monotone in both directions
        on this endpoint. Reach for it rather than a plausible-looking alternative:
        `status`, `severity` and the other low-cardinality fields tie across rows here, and
        a tied key tie-breaks unstably, which makes for a flaky test instead of a real one.
        """
        key = "created_timestamp"
        ascending = self.call_method(self.module.search_cases, sort=f"{key}.asc", limit=20)
        descending = self.call_method(self.module.search_cases, sort=f"{key}.desc", limit=20)

        self.assert_no_error(ascending, context=f"search_cases {key}.asc")
        self.assert_no_error(descending, context=f"search_cases {key}.desc")

        self.assert_sort_orders_rows(
            [case[key] for case in self._unwrap_results(ascending)],
            [case[key] for case in self._unwrap_results(descending)],
            key,
            context="search_cases",
        )

    def test_search_cases_with_q(self):
        """Test search_cases with free-text search."""
        result = self.call_method(
            self.module.search_cases,
            q="test",
            limit=3,
        )

        self.assert_no_error(result, context="search_cases with q")
        self.assert_valid_list_response(
            result, min_length=0, context="search_cases with q"
        )

    # -------------------------------------------------------------------------
    # Get Tests
    # -------------------------------------------------------------------------

    def test_get_cases_with_valid_id(self):
        """Test get_cases with a valid case ID from search."""
        search_result = self._unwrap_results(
            self.call_method(self.module.search_cases, limit=1)
        )

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No cases available to test get_cases",
                context="test_get_cases_with_valid_id",
            )

        case_id = self.get_first_id(search_result, id_field="id")
        if not case_id:
            self.skip_with_warning(
                "Could not extract case ID from search results",
                context="test_get_cases_with_valid_id",
            )

        result = self.call_method(self.module.get_cases, ids=[case_id])

        self.assert_no_error(result, context="get_cases")
        self.assert_valid_list_response(result, min_length=1, context="get_cases")
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "status", "severity"],
            context="get_cases",
        )

    # -------------------------------------------------------------------------
    # Create / Update / Tag Round-trip
    # -------------------------------------------------------------------------

    def test_create_update_tag_roundtrip(self):
        """Full lifecycle: create a case, update it, add/remove tags, verify.

        Creates a unique test case, updates fields, manages tags, then
        verifies the final state. The case is left in 'closed' state as cleanup.
        """
        unique_name = f"falcon-mcp-test-{int(time.time())}"

        # Step 1: Create
        create_result = self.call_method(
            self.module.create_case,
            name=unique_name,
            severity=25,
            description="Integration test case - safe to delete",
            status="new",
        )

        self.assert_no_error(create_result, context="create_case")
        self.assert_valid_list_response(
            create_result, min_length=1, context="create_case"
        )

        case = create_result[0]
        assert isinstance(case, dict), f"Expected dict, got {type(case)}"
        assert "id" in case, f"Missing 'id' in created case. Fields: {list(case.keys())}"

        case_id = case["id"]
        case_version = case.get("version", 1)

        # Step 2: Update (change status and severity)
        update_result = self.call_method(
            self.module.update_case,
            id=case_id,
            status="in_progress",
            severity=50,
            expected_version=case_version,
        )

        self.assert_no_error(update_result, context="update_case")
        self.assert_valid_list_response(
            update_result, min_length=1, context="update_case"
        )

        updated_case = update_result[0]
        assert updated_case.get("status") == "in_progress", (
            f"Expected status 'in_progress', got '{updated_case.get('status')}'"
        )

        # Step 3: Add tags
        tag_add_result = self.call_method(
            self.module.manage_case_tags,
            id=case_id,
            action="add",
            tags=["mcp-test", "integration"],
        )

        self.assert_no_error(tag_add_result, context="add tags")

        # Step 4: Remove one tag
        tag_remove_result = self.call_method(
            self.module.manage_case_tags,
            id=case_id,
            action="remove",
            tags=["integration"],
        )

        self.assert_no_error(tag_remove_result, context="remove tags")

        # Step 5: Verify final state
        get_result = self.call_method(self.module.get_cases, ids=[case_id])

        self.assert_no_error(get_result, context="verify final state")
        self.assert_valid_list_response(
            get_result, min_length=1, context="verify final state"
        )

        final_case = get_result[0]
        assert final_case.get("status") == "in_progress"
        assert "mcp-test" in (final_case.get("tags") or [])
        assert "integration" not in (final_case.get("tags") or [])

        # Step 6: Close the case (cleanup)
        updated_version = final_case.get("version", case_version + 2)
        close_result = self.call_method(
            self.module.update_case,
            id=case_id,
            status="closed",
            expected_version=updated_version,
        )
        self.assert_no_error(close_result, context="close case cleanup")

    def test_description_format_roundtrip(self):
        """Create with a description_format, then change it, and verify each step.

        The PATCH body nests description_format inside 'fields'. Sending it at the
        body top level returns 200 and silently ignores it, so step 3 is the only
        assertion that catches that mistake. The case is left closed as cleanup.
        """
        unique_name = f"falcon-mcp-test-fmt-{int(time.time())}"

        # Step 1: Create with markdown format
        create_result = self.call_method(
            self.module.create_case,
            name=unique_name,
            severity=25,
            description="# Integration test case\n\nSafe to delete.",
            description_format="markdown",
            status="new",
        )

        self.assert_no_error(create_result, context="create_case with markdown")
        self.assert_valid_list_response(
            create_result, min_length=1, context="create_case with markdown"
        )

        case = create_result[0]
        case_id = case["id"]
        assert case.get("description_format") == "markdown", (
            "Created case did not report description_format 'markdown'. "
            f"Got '{case.get('description_format')}'. Fields: {list(case.keys())}"
        )

        # Step 2: Patch the description alone - the format must survive
        desc_result = self.call_method(
            self.module.update_case,
            id=case_id,
            description="## Updated body\n\nStill markdown.",
            expected_version=case.get("version", 1),
        )

        self.assert_no_error(desc_result, context="update description only")
        self.assert_valid_list_response(
            desc_result, min_length=1, context="update description only"
        )

        desc_case = desc_result[0]
        assert desc_case.get("description_format") == "markdown", (
            "Updating the description alone changed description_format. "
            f"Expected 'markdown', got '{desc_case.get('description_format')}'"
        )

        # Step 3: Flip the format to plaintext - the regression guard.
        # Pair it with a second field so 'fields' stays non-empty even if
        # description_format is misplaced, forcing the API to be the judge.
        fmt_result = self.call_method(
            self.module.update_case,
            id=case_id,
            description_format="plaintext",
            severity=50,
            expected_version=desc_case.get("version", 2),
        )

        self.assert_no_error(fmt_result, context="update description_format")
        self.assert_valid_list_response(
            fmt_result, min_length=1, context="update description_format"
        )

        fmt_case = fmt_result[0]
        assert fmt_case.get("description_format") == "plaintext", (
            "description_format did not change to 'plaintext'. Got "
            f"'{fmt_case.get('description_format')}'. The PATCH body most likely "
            "sent the field at the top level instead of inside 'fields', which "
            "the API accepts with 200 and ignores."
        )

        # Step 4: Close the case (cleanup)
        close_result = self.call_method(
            self.module.update_case,
            id=case_id,
            status="closed",
            expected_version=fmt_case.get("version", 3),
        )
        self.assert_no_error(close_result, context="close case cleanup")

    # -------------------------------------------------------------------------
    # Template Tests
    # -------------------------------------------------------------------------

    def test_list_case_templates(self):
        """Test that list_case_templates returns template details."""
        result = self.call_method(self.module.list_case_templates, limit=5)

        self.assert_no_error(result, context="list_case_templates")
        self.assert_valid_list_response(
            result, min_length=0, context="list_case_templates"
        )

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="list_case_templates details",
            )

    # -------------------------------------------------------------------------
    # FQL Filter Validation
    # -------------------------------------------------------------------------

    def test_fql_filter_by_severity(self):
        """Test FQL filter by severity range."""
        result = self.call_method(
            self.module.search_cases,
            filter="severity:>50",
            limit=3,
        )

        self.assert_no_error(result, context="FQL severity filter")

    def test_fql_filter_combined(self):
        """Test FQL combined filter."""
        result = self.call_method(
            self.module.search_cases,
            filter="status:'new'+severity:>50",
            limit=3,
        )

        self.assert_no_error(result, context="FQL combined filter")

    # -------------------------------------------------------------------------
    # Aggregate Tests
    # -------------------------------------------------------------------------

    AGGREGATE_METHODS = (
        ("aggregate_case_slas", "name"),
        ("aggregate_case_templates", "name"),
        ("aggregate_case_access_tags", "key"),
        ("aggregate_case_notification_groups", "name"),
    )

    def _aggregate(self, method_name, **kwargs):
        """Call an aggregate tool with every optional argument defaulted."""
        defaults = {
            "agg_type": "terms",
            "filter": None,
            "size": None,
            "from_": None,
            "date_ranges": None,
            "name": None,
        }
        if method_name == "aggregate_case_file_details":
            defaults["case_ids"] = None
        defaults.update(kwargs)
        return self.call_method(getattr(self.module, method_name), **defaults)

    def test_operation_names_aggregates(self):
        """Validate the four /casemgmt/aggregates operation names are correct."""
        for method_name, field in self.AGGREGATE_METHODS:
            result = self._aggregate(method_name, field=field)
            self.assert_no_error(result, context=f"{method_name} operation name")

    def test_operation_name_aggregate_file_details(self):
        """Validate aggregates_file_details_post_v1 is correct."""
        result = self._aggregate("aggregate_case_file_details", field="name")
        self.assert_no_error(
            result, context="aggregate_case_file_details operation name"
        )

    def test_aggregates_return_labeled_buckets(self):
        """Test that aggregates return buckets keyed on label and count."""
        for method_name, field in self.AGGREGATE_METHODS:
            result = self._aggregate(method_name, field=field, name="probe")

            self.assert_no_error(result, context=f"{method_name} buckets")
            assert isinstance(result, list), f"{method_name} should return a list"
            if not result:
                self.skip_with_warning(
                    f"No aggregate resources for {method_name}", "bucket shape"
                )
                continue

            assert result[0].get("name") == "probe", (
                f"{method_name} should echo the aggregation name back"
            )
            for bucket in result[0].get("buckets") or []:
                assert "label" in bucket, f"{method_name} bucket missing label"
                assert "count" in bucket, f"{method_name} bucket missing count"

    def test_aggregate_size_limits_buckets(self):
        """Test that size actually caps the number of buckets returned."""
        unbounded = self._aggregate("aggregate_case_templates", field="name")
        self.assert_no_error(unbounded, context="templates unbounded")

        if not unbounded or len(unbounded[0].get("buckets") or []) < 2:
            self.skip_with_warning("Fewer than 2 template buckets", "size limit")
            return

        limited = self._aggregate("aggregate_case_templates", field="name", size=1)
        self.assert_no_error(limited, context="templates size=1")
        assert len(limited[0]["buckets"]) == 1, "size=1 should return exactly 1 bucket"

    def test_aggregate_access_tags_supports_key_only(self):
        """Test the access-tags field set: key works, name is rejected.

        Access tags accept a narrower field set than the other case aggregates,
        so a shared field list would silently break this tool.
        """
        ok = self._aggregate("aggregate_case_access_tags", field="key")
        self.assert_no_error(ok, context="access tags field=key")

        rejected = self._aggregate("aggregate_case_access_tags", field="name")
        assert isinstance(rejected, list) and "error" in rejected[0], (
            "access tags should reject field=name with an error"
        )

    def test_aggregate_unsupported_field_returns_error(self):
        """Test that an unsupported aggregation field errors rather than returning empty.

        These endpoints validate the field server-side, so a typo is visible
        instead of silently producing zero buckets.
        """
        result = self._aggregate("aggregate_case_templates", field="not_a_real_field")

        assert isinstance(result, list), "unsupported field should return a list"
        assert "error" in result[0], "unsupported field should return an error"
        # The FQL guide documents the filter param, not the aggregation field.
        assert "fql_guide" not in result[0], (
            "a field error should not be reported as a filter problem"
        )

    def test_aggregate_bad_filter_returns_fql_guide(self):
        """Test that an unsupported filter field surfaces the FQL guide.

        Retried through `retry_on_transient` because the gateway intermittently returns an
        unparseable body, which arrives as a list-shaped error and fails the isinstance
        check below for a reason unrelated to filter handling.
        """
        result = self.retry_on_transient(
            lambda: self._aggregate(
                "aggregate_case_templates", field="name", filter="not_a_real_field:'x'"
            ),
            context="aggregate bad filter",
        )

        assert isinstance(result, dict), "filter error should return a dict"
        assert "fql_guide" in result, "filter error should attach the FQL guide"

    def test_aggregate_date_range_type(self):
        """Test that agg_type='date_range' returns range buckets."""
        result = self._aggregate(
            "aggregate_case_templates",
            field="created_timestamp",
            agg_type="date_range",
            date_ranges=[
                {"from": "2025-01-01T00:00:00Z", "to": "2030-01-01T00:00:00Z"}
            ],
        )

        self.assert_no_error(result, context="templates date_range")
        if not result:
            self.skip_with_warning("No date_range resources", "date_range shape")
            return
        buckets = result[0].get("buckets") or []
        assert buckets, "date_range should return at least one bucket"
        assert "count" in buckets[0], "date_range bucket missing count"

    def test_aggregate_fql_filter_narrows_results(self):
        """Test that a documented FQL filter genuinely reduces the aggregated count.

        Guards the FQL guide: an unsupported filter field or operator would leave
        the count unchanged or error, either of which fails here.
        """
        unfiltered = self._aggregate("aggregate_case_templates", field="name")
        self.assert_no_error(unfiltered, context="templates unfiltered")

        buckets = (unfiltered[0].get("buckets") or []) if unfiltered else []
        if len(buckets) < 2:
            self.skip_with_warning("Fewer than 2 template buckets", "FQL narrowing")
            return

        target = buckets[0]["label"]
        filtered = self._aggregate(
            "aggregate_case_templates", field="name", filter=f"name:'{target}'"
        )
        self.assert_no_error(filtered, context="templates name filter")
        assert filtered, "filter on a known name should return a resource"
        assert len(filtered[0].get("buckets") or []) < len(buckets), (
            "filtering on one known name should return fewer buckets than unfiltered"
        )

    def test_aggregate_substring_operator(self):
        """Test that the documented :* substring operator returns results.

        The guide documents `:*` rather than `~` or a quoted trailing wildcard;
        this asserts the documented form is the one that works.
        """
        unfiltered = self._aggregate("aggregate_case_templates", field="name")
        buckets = (unfiltered[0].get("buckets") or []) if unfiltered else []
        if not buckets:
            self.skip_with_warning("No template buckets", "substring operator")
            return

        fragment = str(buckets[0]["label"])[:3]
        result = self._aggregate(
            "aggregate_case_templates", field="name", filter=f"name:*'*{fragment}*'"
        )

        self.assert_no_error(result, context="templates :* substring")
        assert result and (result[0].get("buckets") or []), (
            f"substring filter name:*'*{fragment}*' should match at least one record"
        )

    def test_aggregate_file_details_case_ids_scopes_results(self):
        """Test that case_ids narrows file aggregation to the named cases.

        The endpoint's ids query param does not filter, so this asserts the
        case_id filter path that does.
        """
        unscoped = self._aggregate("aggregate_case_file_details", field="case_id")
        self.assert_no_error(unscoped, context="file details unscoped")

        buckets = (unscoped[0].get("buckets") or []) if unscoped else []
        if len(buckets) < 2:
            self.skip_with_warning(
                "Fewer than 2 cases with attached files", "case_ids scoping"
            )
            return

        target = buckets[0]["label"]
        scoped = self._aggregate(
            "aggregate_case_file_details", field="case_id", case_ids=[target]
        )

        self.assert_no_error(scoped, context="file details scoped")
        scoped_labels = [b["label"] for b in (scoped[0].get("buckets") or [])]
        assert scoped_labels == [target], (
            f"case_ids=[{target}] should return only that case, got {scoped_labels}"
        )

    def test_aggregate_file_details_file_size_is_filterable(self):
        """Test that file_size works as a filter, matched as a string not a number."""
        sizes = self._aggregate("aggregate_case_file_details", field="file_size")
        self.assert_no_error(sizes, context="file details file_size")

        buckets = (sizes[0].get("buckets") or []) if sizes else []
        if not buckets:
            self.skip_with_warning("No files with a size", "file_size filter")
            return

        target = buckets[0]["label"]
        filtered = self._aggregate(
            "aggregate_case_file_details",
            field="file_size",
            filter=f"file_size:'{target}'",
        )

        self.assert_no_error(filtered, context="file details file_size filter")
        assert filtered and (filtered[0].get("buckets") or []), (
            f"file_size:'{target}' should match at least one file"
        )
