"""Tests for _CloudBase shared helpers."""

import unittest
from typing import Any
from unittest.mock import patch

from falcon_mcp.modules.cloud.cloud import CloudModule
from falcon_mcp.modules.cloud.cloud_base import _CloudBase
from tests.modules.utils.test_modules import TestModules


class TestFetchPfmRules(TestModules):
    """Tests for _CloudBase._fetch_pfm_rules."""

    def setUp(self):
        self.setup_module(CloudModule)

    def _query_resp(self, uuids, total: int | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"resources": uuids}
        if total is not None:
            body["meta"] = {"pagination": {"total": total, "offset": 0, "limit": 500}}
        return {"status_code": 200, "body": body}

    def _get_resp(self, rules):
        return {"status_code": 200, "body": {"resources": rules}}

    def test_returns_rules_for_matching_uuids(self):
        """Single page of UUIDs → single GetRule call → returns rules."""
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"], total=1),
            self._get_resp(rules),
        ]
        result = self.module._fetch_pfm_rules("rule_domain:'CSPM'")
        self.assertEqual(result, rules)

    def test_returns_empty_when_query_returns_no_uuids(self):
        """QueryRule returns empty → no GetRule call → returns []."""
        self.mock_client.command.return_value = self._query_resp([])
        result = self.module._fetch_pfm_rules("rule_domain:'CSPM'")
        self.assertEqual(result, [])
        self.assertEqual(self.mock_client.command.call_count, 1)

    def test_filter_forwarded_to_query_rule(self):
        """The filter arg is passed verbatim to QueryRule."""
        self.mock_client.command.return_value = self._query_resp([])
        self.module._fetch_pfm_rules("rule_domain:'X'+rule_subdomain:'Y'")
        params = self.mock_client.command.call_args[1]["parameters"]
        self.assertEqual(params["filter"], "rule_domain:'X'+rule_subdomain:'Y'")

    def test_paginates_query_rule(self):
        """QueryRule returning 500 results triggers a second page request."""
        page1 = [f"uuid-{i}" for i in range(500)]
        page2 = ["uuid-extra"]
        rules_p1 = [{"insight_id": f"id-{i}", "category": "N"} for i in range(500)]
        rules_p2 = [{"insight_id": "id-extra", "category": "N"}]
        self.mock_client.command.side_effect = [
            self._query_resp(page1, total=501),
            self._query_resp(page2, total=501),
            *[self._get_resp(rules_p1[i:i+100]) for i in range(0, 500, 100)],
            self._get_resp(rules_p2),
        ]
        result = self.module._fetch_pfm_rules("f")
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("QueryRule"), 2)
        self.assertEqual(len(result), 501)

    def test_terminates_at_total_without_extra_request(self):
        """When total is known and all IDs fetched, no extra QueryRule is made."""
        uuids = [f"uuid-{i}" for i in range(500)]
        rules = [{"insight_id": f"id-{i}", "category": "N"} for i in range(500)]
        # total=500 means exactly one page — should NOT make a second QueryRule call
        self.mock_client.command.side_effect = [
            self._query_resp(uuids, total=500),
            *[self._get_resp(rules[i:i+100]) for i in range(0, 500, 100)],
        ]
        result = self.module._fetch_pfm_rules("f")
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("QueryRule"), 1)
        self.assertEqual(len(result), 500)

    def test_batches_get_rule_at_100(self):
        """More than 100 UUIDs are fetched in batches of 100."""
        uuids = [f"uuid-{i}" for i in range(150)]
        rules = [{"insight_id": f"id-{i}", "category": "N"} for i in range(150)]
        self.mock_client.command.side_effect = [
            self._query_resp(uuids, total=150),
            self._get_resp(rules[:100]),
            self._get_resp(rules[100:]),
        ]
        result = self.module._fetch_pfm_rules("f")
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("GetRule"), 2)
        self.assertEqual(len(result), 150)

    def test_short_page_terminates_without_extra_request(self):
        """A page shorter than the page size is the last page, even with no `total`.

        Short-page detection is the primary termination condition: it does not depend on
        the API reporting `meta.pagination.total`, so it holds even if `total` is absent
        or wrong.
        """
        rules = [{"insight_id": "id-1", "category": "N"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"]),  # no total, 1 < 500 → last page
            self._get_resp(rules),
        ]
        result = self.module._fetch_pfm_rules("f")
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops, ["QueryRule", "GetRule"])
        self.assertEqual(result, rules)

    def test_under_reporting_total_does_not_truncate(self):
        """A full page must never terminate the loop, even if `total` under-reports.

        Regression guard: terminating on `len(uuids) >= total` while the page was full
        silently drops every rule after page 1 when `total` is wrong. Short-page
        detection must be checked first.
        """
        page1 = [f"uuid-{i}" for i in range(500)]
        page2 = ["uuid-extra"]
        rules_p1 = [{"insight_id": f"id-{i}", "category": "N"} for i in range(500)]
        rules_p2 = [{"insight_id": "id-extra", "category": "N"}]
        self.mock_client.command.side_effect = [
            self._query_resp(page1, total=100),  # total lies: says 100, page is full
            self._query_resp(page2, total=100),
            *[self._get_resp(rules_p1[i:i + 100]) for i in range(0, 500, 100)],
            self._get_resp(rules_p2),
        ]
        result = self.module._fetch_pfm_rules("f")
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("QueryRule"), 2)
        self.assertEqual(len(result), 501)

    def test_paginates_when_total_is_absent(self):
        """Multi-page walk works with no `total` at all — driven by page length alone."""
        page1 = [f"uuid-{i}" for i in range(500)]
        page2 = ["uuid-extra"]
        rules_p1 = [{"insight_id": f"id-{i}", "category": "N"} for i in range(500)]
        rules_p2 = [{"insight_id": "id-extra", "category": "N"}]
        self.mock_client.command.side_effect = [
            self._query_resp(page1),  # no meta at all
            self._query_resp(page2),
            *[self._get_resp(rules_p1[i:i + 100]) for i in range(0, 500, 100)],
            self._get_resp(rules_p2),
        ]
        result = self.module._fetch_pfm_rules("f")
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("QueryRule"), 2)
        self.assertEqual(len(result), 501)

    def test_duplicate_uuids_across_pages_are_deduped(self):
        """A UUID repeated across pages is fetched once, not twice."""
        page1 = [f"uuid-{i}" for i in range(500)]
        page2 = ["uuid-499", "uuid-new"]  # uuid-499 repeats from page 1
        self.mock_client.command.side_effect = [
            self._query_resp(page1),
            self._query_resp(page2),
            *[self._get_resp([]) for _ in range(6)],
        ]
        self.module._fetch_pfm_rules("f")
        get_calls = [
            c[1]["parameters"]["ids"]
            for c in self.mock_client.command.call_args_list
            if c[0][0] == "GetRule"
        ]
        requested = [uuid for batch in get_calls for uuid in batch]
        self.assertEqual(len(requested), len(set(requested)))
        self.assertEqual(len(requested), 501)  # 500 unique + uuid-new

    def test_hard_cap_stops_runaway_pagination(self):
        """An API that never returns a short page is bounded by _PFM_MAX_RULES."""
        full_page = [f"uuid-{i}" for i in range(500)]

        def endless(operation, **kwargs):
            if operation == "QueryRule":
                offset = kwargs["parameters"]["offset"]
                return self._query_resp([f"uuid-{offset + i}" for i in range(500)])
            return self._get_resp([])

        self.mock_client.command.side_effect = endless
        with patch("falcon_mcp.modules.cloud.cloud_base._PFM_MAX_RULES", len(full_page) * 3):
            self.module._fetch_pfm_rules("f")
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("QueryRule"), 3)

    def test_repeated_identical_page_stops_instead_of_looping(self):
        """A server that keeps returning the same full page must not spin forever.

        The dedupe means an all-duplicate page adds nothing to `uuids`, so a cap measured
        against the deduped count can never be reached — progress has to be judged by
        whether the page contributed anything new. The mock aborts after a small number of
        calls so this fails loudly rather than hanging the suite.
        """
        page = [f"uuid-{i}" for i in range(500)]  # identical every time, ignores offset
        calls = {"n": 0}

        def stuck(operation, **kwargs):
            if operation == "QueryRule":
                calls["n"] += 1
                if calls["n"] > 10:
                    raise AssertionError(
                        f"QueryRule called {calls['n']} times on a repeating page — "
                        "pagination is not terminating"
                    )
                return self._query_resp(page)
            return self._get_resp([])

        self.mock_client.command.side_effect = stuck
        self.module._fetch_pfm_rules("f")

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("QueryRule"), 2)  # first page, then one no-progress page
        self.assertEqual(ops.count("GetRule"), 5)  # the 500 unique UUIDs, batched at 100

    def test_cap_is_reached_even_when_every_page_is_a_duplicate(self):
        """The cap must be measured against something that always advances.

        Distinct from the test above: here the pages alternate between two full pages, so
        each individual page does contribute new UUIDs on its first appearance but the walk
        never converges. Keyed on the deduped count the cap would never fire.
        """
        page_a = [f"a-{i}" for i in range(500)]
        page_b = [f"b-{i}" for i in range(500)]
        calls = {"n": 0}

        def alternating(operation, **kwargs):
            if operation == "QueryRule":
                calls["n"] += 1
                if calls["n"] > 20:
                    raise AssertionError(
                        f"QueryRule called {calls['n']} times — cap never fired"
                    )
                return self._query_resp(page_a if calls["n"] % 2 else page_b)
            return self._get_resp([])

        self.mock_client.command.side_effect = alternating
        with patch("falcon_mcp.modules.cloud.cloud_base._PFM_MAX_RULES", 1500):
            self.module._fetch_pfm_rules("f")

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertLessEqual(ops.count("QueryRule"), 4)

    def test_query_rule_error_raises_runtime_error(self):
        """QueryRule API error raises RuntimeError."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "forbidden"}]},
        }
        with self.assertRaises(RuntimeError):
            self.module._fetch_pfm_rules("f")

    def test_get_rule_error_raises_runtime_error(self):
        """GetRule API error raises RuntimeError."""
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"], total=1),
            {"status_code": 500, "body": {"errors": [{"message": "boom"}]}},
        ]
        with self.assertRaises(RuntimeError):
            self.module._fetch_pfm_rules("f")


class TestBatchGetCspmAssets(TestModules):
    """Tests for _CloudBase._batch_get_cspm_assets."""

    def setUp(self):
        self.setup_module(CloudModule)

    def _get_resp(self, assets):
        return {"status_code": 200, "body": {"resources": assets}}

    def test_fetches_single_batch(self):
        """Up to 100 IDs sent in a single request."""
        assets = [{"id": f"a{i}"} for i in range(10)]
        self.mock_client.command.return_value = self._get_resp(assets)
        result = self.module._batch_get_cspm_assets([f"a{i}" for i in range(10)])
        self.assertEqual(self.mock_client.command.call_count, 1)
        self.assertEqual(len(result), 10)

    def test_splits_into_batches_of_100(self):
        """150 IDs result in two entity-get calls."""
        ids = [f"a{i}" for i in range(150)]
        assets = [{"id": iid} for iid in ids]
        self.mock_client.command.side_effect = [
            self._get_resp(assets[:100]),
            self._get_resp(assets[100:]),
        ]
        result = self.module._batch_get_cspm_assets(ids)
        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(len(result), 150)
        # First batch IDs forwarded correctly
        first_ids = self.mock_client.command.call_args_list[0][1]["parameters"]["ids"]
        self.assertEqual(first_ids, ids[:100])

    def test_returns_error_on_first_batch_failure(self):
        """Error in the first batch is returned immediately."""
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "boom"}]},
        }
        result = self.module._batch_get_cspm_assets(["a1"])
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_short_circuits_on_second_batch_error(self):
        """Error in the second batch stops processing and returns the error."""
        ids = [f"a{i}" for i in range(150)]
        batch1_ok = {"status_code": 200, "body": {"resources": [{"id": iid} for iid in ids[:100]]}}
        batch2_err = {"status_code": 500, "body": {"errors": [{"message": "boom"}]}}
        self.mock_client.command.side_effect = [batch1_ok, batch2_err]
        result = self.module._batch_get_cspm_assets(ids)
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(self.mock_client.command.call_count, 2)

    def test_uses_get_method_via_params(self):
        """cloud_security_assets_entities_get is called with use_params (GET method)."""
        self.mock_client.command.return_value = self._get_resp([{"id": "a1"}])
        self.module._batch_get_cspm_assets(["a1"])
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "cloud_security_assets_entities_get")
        self.assertIn("parameters", call[1])


class TestFetchPfmRulesCache(TestModules):
    """Tests for _CloudBase._fetch_pfm_rules per-instance caching."""

    def setUp(self):
        self.setup_module(CloudModule)

    def _query_resp(self, uuids, total: int | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"resources": uuids}
        if total is not None:
            body["meta"] = {"pagination": {"total": total, "offset": 0, "limit": 500}}
        return {"status_code": 200, "body": body}

    def _get_resp(self, rules):
        return {"status_code": 200, "body": {"resources": rules}}

    def test_second_call_within_ttl_uses_cache(self):
        """Second call with same filter within TTL makes no further API calls.

        Asserts the operation sequence rather than a bare call count, so this test
        fails if the second call reaches the API at all.
        """
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"], total=1),
            self._get_resp(rules),
        ]

        result1 = self.module._fetch_pfm_rules("f")
        ops_after_first = [c[0][0] for c in self.mock_client.command.call_args_list]
        result2 = self.module._fetch_pfm_rules("f")
        ops_after_second = [c[0][0] for c in self.mock_client.command.call_args_list]

        self.assertEqual(ops_after_first, ["QueryRule", "GetRule"])
        self.assertEqual(ops_after_second, ops_after_first)  # nothing new was called
        self.assertEqual(result1, result2)

    def test_cached_result_is_not_aliased(self):
        """The cache hands back a copy, so a caller mutating the result cannot poison it."""
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"], total=1),
            self._get_resp(rules),
        ]

        first = self.module._fetch_pfm_rules("f")
        first.append({"insight_id": "injected", "category": "Bogus"})
        first.clear()

        second = self.module._fetch_pfm_rules("f")
        self.assertEqual(second, rules)

    def test_expired_cache_refetches(self):
        """After TTL expires, a fresh API call is made."""
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"], total=1),
            self._get_resp(rules),
            self._query_resp(["uuid-1"], total=1),
            self._get_resp(rules),
        ]

        ttl = _CloudBase.PFM_RULES_CACHE_TTL
        expired_t = float(ttl + 100)
        with patch("falcon_mcp.modules.cloud.cloud_base.time") as mock_time:
            mock_time.monotonic.side_effect = [
                0.0,        # call 1: write timestamp
                expired_t,  # call 2: read timestamp (expired_t - 0 > TTL → expired)
                expired_t,  # call 2: write timestamp
            ]
            self.module._fetch_pfm_rules("f")
            self.module._fetch_pfm_rules("f")

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops, ["QueryRule", "GetRule", "QueryRule", "GetRule"])

    def test_fresh_cache_within_ttl_does_not_refetch(self):
        """Discriminates the TTL comparison itself: just inside the TTL is still a hit.

        Paired with test_expired_cache_refetches, this pins the boundary — a helper that
        ignored the timestamp entirely, or one that always treated entries as stale,
        fails one of the two.
        """
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"], total=1),
            self._get_resp(rules),
        ]

        fresh_t = float(_CloudBase.PFM_RULES_CACHE_TTL - 1)
        with patch("falcon_mcp.modules.cloud.cloud_base.time") as mock_time:
            mock_time.monotonic.side_effect = [0.0, fresh_t]
            self.module._fetch_pfm_rules("f")
            self.module._fetch_pfm_rules("f")

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops, ["QueryRule", "GetRule"])

    def test_different_filters_cached_independently(self):
        """Each distinct filter string has its own cache entry.

        Asserts the filters actually sent to the API, so a cache keyed on something
        other than the filter string (or not keyed at all) fails here.
        """
        rules_a = [{"insight_id": "a", "category": "Network"}]
        rules_b = [{"insight_id": "b", "category": "Identity"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-a"], total=1),
            self._get_resp(rules_a),
            self._query_resp(["uuid-b"], total=1),
            self._get_resp(rules_b),
        ]

        result_a = self.module._fetch_pfm_rules("filter_a")
        result_b = self.module._fetch_pfm_rules("filter_b")
        # Third call — should hit cache for filter_a
        result_a2 = self.module._fetch_pfm_rules("filter_a")

        queried_filters = [
            c[1]["parameters"]["filter"]
            for c in self.mock_client.command.call_args_list
            if c[0][0] == "QueryRule"
        ]
        self.assertEqual(queried_filters, ["filter_a", "filter_b"])  # filter_a queried once
        self.assertEqual(result_a, result_a2)
        self.assertNotEqual(result_a, result_b)

    def test_cache_disabled_when_ttl_zero(self):
        """Setting PFM_RULES_CACHE_TTL=0 disables caching — every call hits the API."""
        original_ttl = _CloudBase.PFM_RULES_CACHE_TTL
        _CloudBase.PFM_RULES_CACHE_TTL = 0
        try:
            rules = [{"insight_id": "iid1", "category": "Network"}]
            self.mock_client.command.side_effect = [
                self._query_resp(["uuid-1"], total=1),
                self._get_resp(rules),
                self._query_resp(["uuid-1"], total=1),
                self._get_resp(rules),
            ]
            self.module._fetch_pfm_rules("f")
            self.module._fetch_pfm_rules("f")
            ops = [c[0][0] for c in self.mock_client.command.call_args_list]
            self.assertEqual(ops, ["QueryRule", "GetRule", "QueryRule", "GetRule"])
            self.assertEqual(self.module._pfm_rules_cache, {})  # nothing was stored
        finally:
            _CloudBase.PFM_RULES_CACHE_TTL = original_ttl

    def test_cache_is_per_instance(self):
        """Two module instances do not share a cache."""
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"], total=1),
            self._get_resp(rules),
            self._query_resp(["uuid-1"], total=1),
            self._get_resp(rules),
        ]
        module2 = CloudModule(self.mock_client)

        self.module._fetch_pfm_rules("f")
        module2._fetch_pfm_rules("f")

        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops, ["QueryRule", "GetRule", "QueryRule", "GetRule"])
        self.assertIsNot(self.module._pfm_rules_cache, module2._pfm_rules_cache)


if __name__ == "__main__":
    unittest.main()
