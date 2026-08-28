"""Base class for integration tests with real API calls."""

import asyncio
import inspect
import warnings
from typing import Any, Callable, Optional
from unittest.mock import patch

import pytest
from pydantic.fields import FieldInfo


def resolve_field_defaults(method: Callable, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Resolve Pydantic Field defaults for method parameters.

    When calling module methods directly (not through FastMCP), Field()
    default values are not resolved automatically. This helper inspects
    the method signature and resolves any Field() defaults for parameters
    not explicitly provided.

    Args:
        method: The method to call
        kwargs: The keyword arguments provided

    Returns:
        Updated kwargs with Field defaults resolved
    """
    sig = inspect.signature(method)
    resolved_kwargs = dict(kwargs)

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        # Skip if already provided
        if param_name in resolved_kwargs:
            continue

        # Check if default is a Pydantic FieldInfo
        if isinstance(param.default, FieldInfo):
            resolved_kwargs[param_name] = param.default.default
        elif param.default is not inspect.Parameter.empty:
            resolved_kwargs[param_name] = param.default

    return resolved_kwargs


#: Error messages that mean the request never really reached the endpoint. FalconPy raises
#: the bytes/get one when the gateway hands back a binary or truncated body instead of JSON;
#: it surfaces as a 500-shaped error dict on any endpoint, has nothing to do with the request
#: that triggered it, and clears on retry. Observed on ~1 in 8 long runs.
TRANSIENT_API_ERROR_MARKERS = (
    "'bytes' object has no attribute 'get'",
    "Connection aborted",
    "Connection reset by peer",
)


class BaseIntegrationTest:
    """Base class providing common assertions for integration tests.

    Integration tests validate that modules work correctly against the real
    CrowdStrike Falcon API, catching issues that mocked tests cannot detect:
    - Incorrect FalconPy operation names (typos)
    - HTTP method mismatches (POST body vs GET query parameters)
    - Two-step search patterns not returning full details
    - API response schema changes
    """

    def assert_no_error(
        self,
        result: Any,
        context: str = "",
    ) -> None:
        """Assert that the result is not an API error response.

        Args:
            result: The API response to check
            context: Optional context string for the error message
        """
        error_msg = f"API error{f' ({context})' if context else ''}: {result}"

        # Check for error dict format
        if isinstance(result, dict):
            assert "error" not in result, error_msg
            assert result.get("status_code", 200) < 400, error_msg

        # Check for list containing error dict. Unwrap first: a search tool reports
        # failure as an error dict inside the envelope's `results`, where neither the
        # top-level key check above nor a bare `isinstance(result, list)` can see it.
        records = self._unwrap_results(result)
        if isinstance(records, list) and len(records) > 0:
            first_item = records[0]
            if isinstance(first_item, dict):
                assert "error" not in first_item, error_msg

    def _unwrap_results(self, result: Any) -> Any:
        """Unwrap the `{"results": [...], "pagination": {...}}` envelope if present.

        Search tools now return a paginated envelope dict instead of a bare list.
        Non-search results (plain lists, error dicts without a "results" key) pass
        through unchanged.
        """
        if isinstance(result, dict) and "results" in result:
            return result["results"]
        return result

    def assert_valid_list_response(
        self,
        result: Any,
        min_length: int = 0,
        context: str = "",
    ) -> None:
        """Assert that the result is a valid list response.

        Accepts either a bare list or the `{"results": [...], "pagination": {...}}`
        envelope now returned by search tools; also sanity-checks `pagination.total`
        when the envelope is present.

        Args:
            result: The API response to check
            min_length: Minimum expected length of the list
            context: Optional context string for the error message
        """
        ctx = f" ({context})" if context else ""

        if isinstance(result, dict) and "results" in result:
            pagination = result.get("pagination")
            if pagination is not None:
                # `total` is always present but may be None when the API reports
                # no count (see _build_pagination_envelope); only sanity-check a
                # real number so the honest-None case doesn't raise TypeError.
                total = pagination.get("total")
                assert (
                    total is None or total >= 0
                ), f"Expected pagination.total >= 0{ctx}, got {total}"
            result = result["results"]

        assert isinstance(result, list), f"Expected list response{ctx}, got {type(result)}"
        assert (
            len(result) >= min_length
        ), f"Expected at least {min_length} items{ctx}, got {len(result)}"

    def is_transient_api_error(self, result: Any) -> bool:
        """True if `result` is a gateway/transport failure rather than a real API answer.

        Tests that assert on a *specific* error (a 400 naming a bad parameter, say) need to
        tell that apart from the gateway intermittently returning an unparseable body — the
        latter arrives shaped like an error dict and would otherwise read as "the API gave
        me the wrong error", failing the test for a reason that has nothing to do with the
        behavior under test.
        """
        candidates = result if isinstance(result, list) else [result]
        if isinstance(result, dict) and isinstance(result.get("results"), list):
            candidates = result["results"]

        for item in candidates:
            if not isinstance(item, dict):
                continue
            blob = str(item.get("error", "")) + str(item.get("details", ""))
            if any(marker in blob for marker in TRANSIENT_API_ERROR_MARKERS):
                return True
        return False

    def retry_on_transient(
        self,
        call: Callable[[], Any],
        attempts: int = 3,
        context: str = "",
    ) -> Any:
        """Call `call`, retrying while the result is a transient gateway failure.

        Fails rather than skips if every attempt is transient: the behavior under test went
        unverified, and reporting that as a pass is how a real regression hides behind
        infrastructure noise.
        """
        result = None
        for attempt in range(1, attempts + 1):
            result = call()
            if not self.is_transient_api_error(result):
                return result
            # Reported via print rather than warnings.warn on purpose: skip_with_warning
            # uses UserWarning, and suites run with `-W error::UserWarning` to prove no test
            # went green by skipping. Routing retries through the same channel would make a
            # retry indistinguishable from a skip.
            print(
                f"Transient API error on attempt {attempt}/{attempts}"
                f"{f' ({context})' if context else ''}; retrying."
            )

        pytest.fail(
            f"Every one of {attempts} attempts hit a transient gateway error"
            f"{f' ({context})' if context else ''}, so the behavior under test could not be "
            f"verified. Last result: {result}"
        )

    def assert_sort_orders_rows(
        self,
        asc: list[Any],
        desc: list[Any],
        key: str,
        context: str = "",
        allow_ties: bool = False,
    ) -> None:
        """Assert an ascending/descending sort really ordered the rows.

        This is the assertion that gives a two-step search tool's sort handling teeth. A
        tool that forwards `sort` but then loses the order during hydration (the bug
        `BaseModule._reorder_by_ids` exists to fix) still returns rows and still passes
        `assert_no_error` — only comparing the actual key sequence catches it.

        Both directions must be *strictly* monotone by default. Ties are treated as a
        failure rather than tolerated, because a tied key tie-breaks unstably and would
        make the test flaky; if this starts failing on ties, the field is no longer a valid
        probe and the test should move to a different one rather than relax the assertion.

        `allow_ties=True` is for endpoints where no documented sort key is tie-free and the
        strict default would mean no ordering coverage at all — a severity enum, say, where
        a page of 50 rows holds one or two distinct values. What tie-breaks unstably is
        *which rows* come back in a tied run, not the key sequence, and the sequence is all
        this compares, so ties do not make these assertions flaky. The one thing they would
        break is the `asc != desc` check, since an all-tied page looks identical in both
        directions; that is replaced by requiring at least two distinct values across the
        two pages and asserting the pages start at opposite ends.

        Args:
            asc: The sort key's value for each row, from the ascending call.
            desc: The same, from the descending call.
            key: The sort field name, for error messages.
            context: Optional context string for the error messages.
            allow_ties: Accept repeated values, for keys with no tie-free alternative.
        """
        ctx = f" ({context})" if context else ""

        # Too little data is a failure, not a skip: silently passing on one row is how a
        # regression in the reorder path stays green forever.
        assert len(asc) > 1, (
            f"Need more than one row to test {key} ordering{ctx}, got {len(asc)}. "
            "Either the tenant has no data for this query or the filter is too narrow."
        )
        assert len(desc) > 1, (
            f"Need more than one row to test {key} ordering{ctx}, got {len(desc)}"
        )

        if not allow_ties:
            assert len(set(map(str, asc))) == len(asc), (
                f"{key} has tied values{ctx}, so sort order is not deterministic and this "
                f"test cannot distinguish a real ordering from a tie-break: {asc}"
            )
            assert len(set(map(str, desc))) == len(desc), (
                f"{key} has tied values{ctx}: {desc}"
            )

        assert asc == sorted(asc), f"{key}.asc is not ascending{ctx}: {asc}"
        assert desc == sorted(desc, reverse=True), f"{key}.desc is not descending{ctx}: {desc}"

        if not allow_ties:
            assert asc != desc, (
                f"{key}.asc and {key}.desc returned the same order{ctx}, so the sort "
                f"direction was ignored: {asc}"
            )
            return

        assert len(set(map(str, asc)) | set(map(str, desc))) > 1, (
            f"Every row in both {key} pages holds the same value{ctx}, so nothing here "
            f"could tell an ordering from an arbitrary one: {asc}"
        )
        assert desc[0] > asc[0], (
            f"{key}.asc and {key}.desc both start at {asc[0]!r}{ctx}. With more than one "
            f"distinct value present the two directions have to land on opposite ends of "
            f"the same ordering — this is what an ignored sort parameter looks like."
        )

    def assert_rows_in_query_step_order(
        self,
        method: Callable[..., Any],
        id_field: str = "id",
        context: str = "",
        **kwargs: Any,
    ) -> Any:
        """Assert a two-step search returns rows in the order its query step reported.

        This is the alternative to `assert_sort_orders_rows` for endpoints with no strictly
        monotone sort field, where an asc/desc comparison would tie-break unstably. Rather
        than checking a sort direction, it asserts `BaseModule._reorder_by_ids`' documented
        contract directly: whatever order the query step returned IDs in, the hydrated
        output preserves it. No monotonicity means no tie flakiness.

        Spies on `_base_get_by_ids` because the query step's ID order is only observable
        from inside a single tool invocation — by the time the tool returns, the reorder has
        already happened (or failed to).

        Args:
            method: The bound search method to drive (e.g. `self.module.search_hosts`).
            id_field: Key holding each row's ID in the response.
            context: Optional context string for the error messages.
            **kwargs: Passed to the search method; keep the limit at or under the tool's
                detail batch size so the query step is captured in one request.

        Returns:
            The raw tool result, for further assertions.
        """
        ctx = f" ({context})" if context else ""
        captured_id_batches: list[list[str]] = []
        real_get_by_ids = self.module._base_get_by_ids

        def spy(*args: Any, **spy_kwargs: Any) -> Any:
            ids = spy_kwargs.get("ids")
            captured_id_batches.append(list(ids) if ids is not None else [])
            return real_get_by_ids(*args, **spy_kwargs)

        with patch.object(self.module, "_base_get_by_ids", side_effect=spy):
            result = self.call_method(method, **kwargs)

        self.assert_no_error(result, context=context)
        rows = self.skip_unless_tenant_has(result, "records", context)

        assert len(captured_id_batches) == 1, (
            f"Expected exactly one detail request{ctx}, got {len(captured_id_batches)}. "
            "Lower the limit below the tool's batch size, or reassemble the query-step "
            "order across batches before comparing."
        )
        query_order = captured_id_batches[0]
        assert len(query_order) > 1, (
            f"Need more than one ID to test ordering{ctx}, got {len(query_order)}"
        )

        returned_order = [row[id_field] for row in rows]
        # IDs that did not hydrate are skipped rather than reordered, per the helper's
        # contract, so compare against the query order restricted to what came back.
        returned_set = set(returned_order)
        expected_order = [
            entity_id for entity_id in query_order if entity_id in returned_set
        ]

        # Guard on the *intersection*, not the query count. If hydration only returned one
        # row out of many queried, `expected_order` collapses to a single element and the
        # comparison below is trivially true — a pass that checked nothing.
        assert len(expected_order) > 1, (
            f"Only {len(expected_order)} of {len(query_order)} queried IDs came back from "
            f"hydration{ctx}, which is too few to verify ordering. The comparison would be "
            "vacuous, so this fails rather than reporting success."
        )

        assert returned_order == expected_order, (
            f"Rows came back in an order that does not match the query step{ctx}. The "
            "_reorder_by_ids call is missing, or reorders against the wrong list.\n"
            f"query step: {query_order}\n"
            f"returned:   {returned_order}"
        )
        return result

    def assert_search_returns_details(
        self,
        result: list[dict[str, Any]],
        expected_fields: list[str],
        context: str = "",
    ) -> None:
        """Assert that search results contain full entity details, not just IDs.

        This validates the two-step search pattern:
        1. Search returns entity IDs
        2. Get details returns full entity objects

        Accepts either a bare list or the `{"results": [...], "pagination": {...}}`
        envelope now returned by search tools.

        Args:
            result: The search results to check
            expected_fields: List of field names expected in each result
            context: Optional context string for the error message
        """
        ctx = f" ({context})" if context else ""

        result = self._unwrap_results(result)

        assert isinstance(result, list), f"Expected list of results{ctx}"
        assert len(result) > 0, f"Expected at least one result to validate{ctx}"

        first_item = result[0]
        assert isinstance(first_item, dict), (
            f"Expected dict items (full details), got {type(first_item)}{ctx}. "
            "This may indicate the search is returning IDs only instead of full details."
        )

        for field in expected_fields:
            assert field in first_item, (
                f"Expected field '{field}' in result{ctx}. "
                f"Available fields: {list(first_item.keys())}"
            )

    def records(self, result: Any, context: str = "") -> list[Any]:
        """Pull the entity list out of a search tool's pagination envelope.

        Search tools return `{"results": [...], "pagination": {...}}`. Indexing that dict
        directly raises `KeyError`, and `len()` on it counts keys rather than records — so
        both `result[0]` and `len(result) > 100` silently misread it. Unwrap once here, then
        assert against the list. Get-by-IDs tools return a bare list and pass through
        unchanged.
        """
        ctx = f" ({context})" if context else ""
        records = self._unwrap_results(result)
        assert isinstance(records, list), f"Expected a list of records{ctx}, got {type(records)}"
        return records

    def skip_unless_tenant_has(self, result: Any, thing: str, context: str = "") -> list[Any]:
        """Return the records, or skip only once the API confirms the tenant has none.

        `pagination.total == 0` is the API stating there is nothing to find, which is a
        legitimate reason to skip. An empty page alongside a non-zero total means the query
        step found records the detail step did not return — a bug, not a bare tenant — so
        that fails instead.
        """
        records = self.records(result, context)
        if records:
            return records

        total = (result.get("pagination") or {}).get("total") if isinstance(result, dict) else None
        assert not total, (
            f"No {thing} returned but pagination.total is {total} — the query step found "
            f"records the detail step did not return{f' ({context})' if context else ''}."
        )
        self.skip_with_warning(f"tenant has no {thing}", context=context)
        return []

    def assert_filter_matches(
        self,
        search: Any,
        filter: str,
        predicate: Optional[Any] = None,
        predicate_desc: str = "",
        note: str = "",
        limit: int = 5,
        **search_kwargs: Any,
    ) -> Any:
        """Assert a documented FQL filter returns rows, and that every row satisfies it.

        Query APIs report an unsupported field or operator as an empty HTTP 200 as often
        as they do a 400, so a test that tolerates zero rows cannot tell "the guide is
        wrong" from "the tenant has no such data". Only a non-empty result proves the
        documented construction works, and only a per-record check proves the filter
        selected on what it claims to.

        Args:
            search: The search callable, invoked as ``search(filter=..., limit=...)``.
            filter: The FQL filter under test.
            predicate: Optional ``record -> bool`` applied to every returned record.
            predicate_desc: Human-readable description of the predicate, for failures.
            note: Extra context appended to the zero-rows failure message.
            limit: Row limit for the query.
            **search_kwargs: Extra keyword arguments forwarded to ``search``.

        Returns:
            The full search result (envelope or list), so callers can assert further.
        """
        result = self.call_method(search, filter=filter, limit=limit, **search_kwargs)
        self.assert_no_error(result, context=f"filter {filter!r}")

        records = self._unwrap_results(result)
        assert isinstance(records, list), f"Expected a list of records for {filter!r}, got {type(records)}"
        assert records, (
            f"Documented filter returned zero rows: {filter}. {note} "
            "Either the guide is wrong or the tenant has no matching data — "
            "an unsupported field or operator can come back as an empty 200 here."
        )

        if predicate is not None:
            failures = [record for record in records if not predicate(record)]
            assert not failures, (
                f"{len(failures)} of {len(records)} records returned by {filter!r} do not "
                f"satisfy [{predicate_desc or 'the caller predicate'}]. "
                f"Offending records: {failures[:3]}"
            )

        return result

    def assert_result_has_id(
        self,
        result: list[dict[str, Any]],
        id_field: str = "id",
        context: str = "",
    ) -> None:
        """Assert that each result item has an ID field.

        Accepts either a bare list or the `{"results": [...], "pagination": {...}}`
        envelope now returned by search tools.

        Args:
            result: The results to check
            id_field: The name of the ID field to check for
            context: Optional context string for the error message
        """
        ctx = f" ({context})" if context else ""

        result = self._unwrap_results(result)

        assert isinstance(result, list), f"Expected list of results{ctx}"

        for i, item in enumerate(result):
            assert isinstance(item, dict), f"Expected dict at index {i}{ctx}"
            assert id_field in item, f"Missing '{id_field}' field at index {i}{ctx}"

    def get_first_id(
        self,
        result: list[dict[str, Any]],
        id_field: str = "id",
    ) -> Optional[str]:
        """Extract the first ID from a list of results.

        Accepts either a bare list or the `{"results": [...], "pagination": {...}}`
        envelope now returned by search tools.

        Args:
            result: The results to extract from
            id_field: The name of the ID field

        Returns:
            The first ID value, or None if not found
        """
        result = self._unwrap_results(result)

        if not result or not isinstance(result, list):
            return None

        first_item = result[0]
        if isinstance(first_item, dict):
            return first_item.get(id_field)

        return None

    def call_method(self, method: Callable[..., Any], **kwargs: Any) -> Any:
        """Call a module method with resolved Pydantic Field defaults.

        When calling module methods directly (not through FastMCP), Field()
        default values are not resolved automatically. This helper ensures
        Field defaults are properly resolved before calling the method.

        Handles both sync and async methods - if the method returns a
        coroutine, it will be executed with asyncio.run().

        Args:
            method: The module method to call
            **kwargs: Keyword arguments to pass to the method

        Returns:
            The result of calling the method
        """
        resolved_kwargs = resolve_field_defaults(method, kwargs)
        result = method(**resolved_kwargs)

        # If result is a coroutine, run it to completion
        if inspect.iscoroutine(result):
            return asyncio.run(result)

        return result

    def skip_with_warning(self, reason: str, context: str = "") -> None:
        """Skip a test with a warning to make it visible in CI output.

        This method emits a warning before skipping to ensure skipped tests
        are visible in CI logs and test reports. Silent skips can mask issues
        where tests never actually run.

        Args:
            reason: The reason for skipping the test
            context: Optional context about the test being skipped
        """
        full_reason = f"{reason}" if not context else f"{reason} ({context})"
        warnings.warn(f"INTEGRATION TEST SKIPPED: {full_reason}", stacklevel=2)
        pytest.skip(full_reason)
