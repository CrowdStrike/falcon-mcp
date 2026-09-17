"""Integration tests for the IOC module."""

import pytest

from falcon_mcp.modules.ioc import IOCModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestIOCIntegration(BaseIntegrationTest):
    """Integration tests for IOC module with real API calls.

    Validates:
    - Correct FalconPy operation names (indicator_search_v1, indicator_get_v1,
      indicator_create_v1, indicator_delete_v1)
    - Two-step search pattern returns full details, not just IDs
    - GET query param usage for indicator_get_v1
    - Full CRUD lifecycle (create, search, delete)
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the IOC module with a real client."""
        self.module = IOCModule(falcon_client)

    @pytest.fixture(autouse=True, scope="class")
    @classmethod
    def create_test_ioc(cls, falcon_client):
        """Create a test IOC for the class and clean up after all tests.

        Creates a domain IOC with .invalid TLD (IANA-reserved, never resolves)
        and detect-only action for safety. Tagged with a unique source for
        easy identification and filter-based searching.

        Declared as a classmethod because a class-scoped fixture written as an
        instance method raises a pytest deprecation warning, and that warning
        subclasses UserWarning — under the `-W error::UserWarning` this suite is
        run with, it errors out every test in the file before any of them start.
        """
        module = IOCModule(falcon_client)

        # Create test IOC
        from tests.integration.utils.base_integration_test import resolve_field_defaults

        create_kwargs = resolve_field_defaults(module.add_ioc, {
            "type": "domain",
            "value": "falcon-mcp-integration-test.invalid",
            "action": "detect",
            "severity": "low",
            "source": "falcon-mcp-integration-test",
            "description": "Integration test IOC - safe to delete",
            "platforms": ["linux"],
            "applied_globally": True,
            "ignore_warnings": True,
        })
        result = module.add_ioc(**create_kwargs)

        # Validate creation succeeded
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                pytest.skip(
                    f"Cannot create test IOC (check IOC Management:write scope): {first}"
                )
            if isinstance(first, dict) and "id" in first:
                cls._test_ioc = first
                cls._test_ioc_id = first["id"]
            else:
                pytest.skip(f"Unexpected create response shape: {result}")
        else:
            pytest.skip(f"Unexpected create response: {result}")

        yield

        # Teardown: delete the test IOC
        try:
            delete_kwargs = resolve_field_defaults(module.remove_iocs, {
                "ids": [cls._test_ioc_id],
                "comment": "Integration test cleanup",
            })
            module.remove_iocs(**delete_kwargs)
        except Exception as e:
            import warnings
            warnings.warn(
                f"Failed to clean up test IOC {cls._test_ioc_id}: {e}",
                stacklevel=2,
            )

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong (e.g., 'indicator_search_v1' typo),
        the API call will fail with an error response.
        """
        result = self.call_method(self.module.search_iocs, limit=1)
        self.assert_no_error(result, context="operation name validation")

    def test_search_iocs_returns_details(self):
        """Test that search_iocs returns full IOC details, not just IDs.

        Validates the two-step search pattern:
        1. indicator_search_v1 returns IOC IDs
        2. indicator_get_v1 returns full details (GET with query params)
        """
        result = self.call_method(self.module.search_iocs, limit=5)

        self.assert_no_error(result, context="search_iocs")
        self.assert_valid_list_response(result, min_length=0, context="search_iocs")

        records = self.records(result, context="search_iocs")
        if len(records) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "type", "value"],
                context="search_iocs",
            )

    def test_search_iocs_with_filter(self):
        """Test search_iocs with FQL filter targeting the test IOC."""
        result = self.call_method(
            self.module.search_iocs,
            filter="source:'falcon-mcp-integration-test'",
            limit=5,
        )

        self.assert_no_error(result, context="search_iocs with filter")
        self.assert_valid_list_response(
            result, min_length=0, context="search_iocs with filter"
        )

    def test_search_iocs_with_sort(self):
        """Test search_iocs with sort parameter."""
        result = self.call_method(
            self.module.search_iocs,
            sort="modified_on.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_iocs with sort")
        self.assert_valid_list_response(
            result, min_length=0, context="search_iocs with sort"
        )

    def test_add_ioc_response_shape(self):
        """Test that the create response from the fixture has expected fields."""
        test_ioc = self.__class__._test_ioc

        assert isinstance(test_ioc, dict), (
            f"Expected dict for created IOC, got {type(test_ioc)}"
        )

        for field in ["id", "type", "value"]:
            assert field in test_ioc, (
                f"Expected '{field}' in created IOC. "
                f"Available fields: {list(test_ioc.keys())}"
            )

        assert test_ioc["type"] == "domain", (
            f"Expected type 'domain', got '{test_ioc['type']}'"
        )
        assert test_ioc["value"] == "falcon-mcp-integration-test.invalid", (
            f"Expected value 'falcon-mcp-integration-test.invalid', got '{test_ioc['value']}'"
        )

    def test_created_ioc_appears_in_search(self):
        """Round-trip: verify the created IOC is findable via search."""
        result = self.call_method(
            self.module.search_iocs,
            filter="source:'falcon-mcp-integration-test'+value:'falcon-mcp-integration-test.invalid'",
            limit=10,
        )

        self.assert_no_error(result, context="round-trip search")
        self.assert_valid_list_response(
            result, min_length=1, context="round-trip search"
        )

        # Verify the test IOC is in results
        records = self.records(result, context="round-trip search")
        found_ids = [
            item.get("id") for item in records if isinstance(item, dict)
        ]
        assert self.__class__._test_ioc_id in found_ids, (
            f"Created IOC {self.__class__._test_ioc_id} not found in search results. "
            f"Found IDs: {found_ids}"
        )

    def test_remove_ioc_by_id(self):
        """Test remove_iocs by ID using a dedicated IOC.

        Creates a separate IOC (not the shared fixture), deletes it by ID,
        and verifies the delete response has no errors.
        """
        # Create a disposable IOC for this test
        create_result = self.call_method(
            self.module.add_ioc,
            type="domain",
            value="falcon-mcp-delete-test.invalid",
            action="detect",
            severity="low",
            source="falcon-mcp-integration-test",
            description="Disposable IOC for delete test",
            platforms=["linux"],
            applied_globally=True,
            ignore_warnings=True,
        )

        self.assert_no_error(create_result, context="create disposable IOC")
        self.assert_valid_list_response(
            create_result, min_length=1, context="create disposable IOC"
        )

        disposable_id = self.get_first_id(create_result, id_field="id")
        if not disposable_id:
            self.skip_with_warning(
                "Could not extract ID from created IOC",
                context="test_remove_ioc_by_id",
            )

        # Delete it
        delete_result = self.call_method(
            self.module.remove_iocs,
            ids=[disposable_id],
            comment="Integration test delete verification",
        )

        self.assert_no_error(delete_result, context="remove_iocs by ID")

    # ------------------------------------------------------------------
    # Filter vocabularies
    #
    # indicator_combined_v1 answers an unknown filter field with an empty HTTP 200
    # (see tests/integration/test_filter_classification.py), so nothing here can be
    # settled by a clean response. Every value below is proved by rows, and the
    # non-members by rows on a sibling that shares the query.
    # ------------------------------------------------------------------

    def test_action_vocabulary(self):
        """Every filterable `action` value, including the two the hint used to omit.

        `action_query_v1` is not the source of truth for this: it reports `none`,
        but `action:'none'` matches nothing while `action:'no_action'` matches the
        records whose response `action` is `no_action`. The creation vocabulary and
        the filter vocabulary disagree on that one member, so this asserts the
        filter side.
        """
        for value in ("detect", "prevent", "no_action", "prevent_no_ui", "allow"):
            self.assert_filter_matches(
                self.module.search_iocs,
                f"action:'{value}'",
                predicate=lambda ioc, value=value: ioc.get("action") == value,
                predicate_desc=f"ioc.action == {value!r}",
                note="Every action value in the hint and the guide must match its own records.",
                limit=3,
            )

    def test_action_none_matches_nothing(self):
        """`none` is what action_query_v1 reports, and it filters nothing.

        Paired with the `no_action` case above, which runs against the same tenant:
        one of the two spellings returns records and the other does not, so this is
        a real divergence rather than an absence of data.
        """
        result = self.call_method(self.module.search_iocs, filter="action:'none'", limit=1)
        self.assert_envelope_ok(result, context="action:'none'")
        assert not self.records(result, "action:'none'"), (
            "action:'none' now returns records. The guide and hint document "
            "no_action because none matched nothing; if the API changed, both need "
            "updating and so does this test."
        )

    def test_type_vocabulary(self):
        """Every indicator type reported by ioc_type_query_v1 is filterable.

        Asserted as set equality against the vocabulary endpoint so the guide
        cannot drift in either direction — `all_subdomains` was missing from the
        hint, and `sha1` is not a member despite looking like it belongs.
        """
        response = self.module.client.command("ioc_type_query_v1")
        vocabulary = (response.get("body") or {}).get("resources")
        assert vocabulary, f"ioc_type_query_v1 returned no vocabulary: {response}"
        assert set(vocabulary) == {
            "sha256",
            "md5",
            "ipv4",
            "ipv6",
            "domain",
            "all_subdomains",
        }, (
            f"The indicator type vocabulary changed to {sorted(vocabulary)}. Update "
            "the guide's `type` row and the falcon_search_iocs filter hint to match."
        )

        for value in vocabulary:
            self.assert_filter_matches(
                self.module.search_iocs,
                f"type:'{value}'",
                predicate=lambda ioc, value=value: ioc.get("type") == value,
                predicate_desc=f"ioc.type == {value!r}",
                note="Each type reported by ioc_type_query_v1 must be filterable.",
                limit=3,
            )

    def test_severity_number_scale_is_not_one_to_five(self):
        """`severity_number` runs 0/10/30/50/70/90, mirroring the severity labels.

        The hint documented `1-5`. None of 1..5 matches a single record on a tenant
        holding IOCs at every severity, and the label cross-check below is what
        turns that absence into a mapping rather than a shrug: filtering on both
        the label and its number returns rows, so the pair is confirmed together.

        `0` is a real member, proved separately in
        test_severity_number_zero_is_reachable rather than here: it has no severity
        label to pair with, so it needs an IOC created without a severity at all.
        The 1..5 sweep below establishes that `severity_number` is honored — a
        dropped clause would return every record rather than none.
        """
        expected = {
            "informational": 10,
            "low": 30,
            "medium": 50,
            "high": 70,
            "critical": 90,
        }

        for label, number in expected.items():
            self.assert_filter_matches(
                self.module.search_iocs,
                f"severity:'{label}'+severity_number:{number}",
                predicate=lambda ioc, label=label: ioc.get("severity") == label,
                predicate_desc=f"ioc.severity == {label!r}",
                note=f"severity {label!r} is documented as severity_number {number}.",
                limit=3,
            )

        # The positive controls above establish the tenant holds every severity, so
        # a 1..5 probe finding nothing is the scale being wrong rather than the
        # tenant being bare.
        for number in range(1, 6):
            result = self.call_method(
                self.module.search_iocs, filter=f"severity_number:{number}", limit=1
            )
            self.assert_envelope_ok(result, context=f"severity_number:{number}")
            assert not self.records(result, f"severity_number:{number}"), (
                f"severity_number:{number} now matches records, so the scale is no "
                "longer 0/10/30/50/70/90. Update the guide and the filter hint."
            )

    def test_severity_number_zero_is_reachable(self):
        """Whether `severity_number:0` describes anything an IOC can actually be.

        0 sits outside the 10/30/50/70/90 label scale, so it can only mean "no
        severity". Nothing read-only settles that: this endpoint is silent, so zero
        rows at 0 cannot separate "no IOC is unscored" from "0 is not a member".
        `severity` is optional on the create call, so the decisive form is to create
        an IOC that omits it and read back what the API assigns.

        Swept across every action, because the API's rejection is conditional: it
        says severity "cannot be empty for this 'action' and 'mobile_action'
        combination", so one action refusing a severity-less IOC says nothing about
        the others. `allow` and `no_action` have no detection to rank.
        """
        outcomes: dict[str, str] = {}
        assigned: dict[str, object] = {}
        created_ids: list[str] = []

        try:
            for index, action in enumerate(
                ("detect", "prevent", "no_action", "prevent_no_ui", "allow")
            ):
                created = self.call_method(
                    self.module.add_ioc,
                    type="domain",
                    value=f"falcon-mcp-severityless-{index}.invalid",
                    action=action,
                    source="falcon-mcp-integration-test",
                    description="Severity-less IOC probe - safe to delete",
                    platforms=["linux"],
                    applied_globally=True,
                    ignore_warnings=True,
                )
                rejected = self.error_dicts(created)
                if rejected:
                    outcomes[action] = "rejected"
                    continue

                outcomes[action] = "accepted"
                records = self.records(created, context=f"severity-less {action}")
                if records:
                    assigned[action] = records[0].get("severity_number")
                    probe_id = records[0].get("id")
                    if probe_id:
                        created_ids.append(probe_id)

            print(f"\nseverity-less create by action: {outcomes}")
            print(f"severity_number on create response: {assigned}")

            if not assigned:
                self.skip_with_warning(
                    "No action accepts an IOC without a severity "
                    f"({outcomes}), so severity_number 0 is unreachable through "
                    "creation and stays unproven.",
                    context="severity_number 0",
                )

            # The create response omits severity fields, so read the stored record
            # back through search — that is the shape a filter actually sees.
            stored = self.call_method(
                self.module.search_iocs,
                filter=f"id:'{created_ids[0]}'",
                limit=1,
            )
            records = self.records(stored, context="stored severity-less IOC")
            assert records, (
                f"The severity-less IOC {created_ids[0]} is not findable by id, so "
                f"nothing can be read back off it: {stored}"
            )
            print(f"stored severity={records[0].get('severity')!r} "
                  f"severity_number={records[0].get('severity_number')!r}")

            stored_number = records[0].get("severity_number")
            probe = self.call_method(
                self.module.search_iocs,
                filter=f"id:'{created_ids[0]}'+severity_number:0",
                limit=1,
            )
            self.assert_envelope_ok(probe, context="severity_number:0 on an unscored IOC")
            matched = bool(self.records(probe, "severity_number:0 on an unscored IOC"))
            print(f"severity_number:0 matches the unscored IOC: {matched}")

            assert matched, (
                "An IOC created without a severity stores severity="
                f"{records[0].get('severity')!r} with severity_number "
                f"{stored_number!r}, and `severity_number:0` does not match it. "
                "Nothing an IOC can be is severity_number 0, so it belongs out of "
                f"the guide and hint. Record: {records[0]}"
            )
        finally:
            if created_ids:
                self.call_method(
                    self.module.remove_iocs,
                    ids=created_ids,
                    comment="Severity-less probe cleanup",
                )

