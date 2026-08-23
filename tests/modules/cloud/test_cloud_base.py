"""Tests for _CloudBase shared helpers."""

import unittest
from unittest.mock import patch

from falcon_mcp.modules.cloud.cloud import CloudModule
from falcon_mcp.modules.cloud.cloud_base import _CloudBase
from tests.modules.utils.test_modules import TestModules


class TestFetchPfmRules(TestModules):
    """Tests for _CloudBase._fetch_pfm_rules."""

    def setUp(self):
        self.setup_module(CloudModule)

    def _query_resp(self, uuids):
        return {"status_code": 200, "body": {"resources": uuids}}

    def _get_resp(self, rules):
        return {"status_code": 200, "body": {"resources": rules}}

    def test_returns_rules_for_matching_uuids(self):
        """Single page of UUIDs → single GetRule call → returns rules."""
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"]),
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
            self._query_resp(page1),
            self._query_resp(page2),
            *[self._get_resp(rules_p1[i:i+100]) for i in range(0, 500, 100)],
            self._get_resp(rules_p2),
        ]
        result = self.module._fetch_pfm_rules("f")
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("QueryRule"), 2)
        self.assertEqual(len(result), 501)

    def test_batches_get_rule_at_100(self):
        """More than 100 UUIDs are fetched in batches of 100."""
        uuids = [f"uuid-{i}" for i in range(150)]
        rules = [{"insight_id": f"id-{i}", "category": "N"} for i in range(150)]
        self.mock_client.command.side_effect = [
            self._query_resp(uuids),
            self._get_resp(rules[:100]),
            self._get_resp(rules[100:]),
        ]
        result = self.module._fetch_pfm_rules("f")
        ops = [c[0][0] for c in self.mock_client.command.call_args_list]
        self.assertEqual(ops.count("GetRule"), 2)
        self.assertEqual(len(result), 150)

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
            self._query_resp(["uuid-1"]),
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

    def _query_resp(self, uuids):
        return {"status_code": 200, "body": {"resources": uuids}}

    def _get_resp(self, rules):
        return {"status_code": 200, "body": {"resources": rules}}

    def test_second_call_within_ttl_uses_cache(self):
        """Second call with same filter within TTL does not hit the API again."""
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"]),
            self._get_resp(rules),
        ]

        result1 = self.module._fetch_pfm_rules("f")
        result2 = self.module._fetch_pfm_rules("f")

        self.assertEqual(self.mock_client.command.call_count, 2)  # QueryRule + GetRule, not 4
        self.assertEqual(result1, result2)

    def test_expired_cache_refetches(self):
        """After TTL expires, a fresh API call is made."""
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"]),
            self._get_resp(rules),
            self._query_resp(["uuid-1"]),
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

        self.assertEqual(self.mock_client.command.call_count, 4)  # both calls hit API

    def test_different_filters_cached_independently(self):
        """Each distinct filter string has its own cache entry."""
        rules_a = [{"insight_id": "a", "category": "Network"}]
        rules_b = [{"insight_id": "b", "category": "Identity"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-a"]),
            self._get_resp(rules_a),
            self._query_resp(["uuid-b"]),
            self._get_resp(rules_b),
        ]

        result_a = self.module._fetch_pfm_rules("filter_a")
        result_b = self.module._fetch_pfm_rules("filter_b")
        # Third call — should hit cache for filter_a
        result_a2 = self.module._fetch_pfm_rules("filter_a")

        self.assertEqual(self.mock_client.command.call_count, 4)  # only 2 API round-trips
        self.assertEqual(result_a, result_a2)
        self.assertNotEqual(result_a, result_b)

    def test_cache_disabled_when_ttl_zero(self):
        """Setting PFM_RULES_CACHE_TTL=0 disables caching — every call hits the API."""
        original_ttl = _CloudBase.PFM_RULES_CACHE_TTL
        _CloudBase.PFM_RULES_CACHE_TTL = 0
        try:
            rules = [{"insight_id": "iid1", "category": "Network"}]
            self.mock_client.command.side_effect = [
                self._query_resp(["uuid-1"]),
                self._get_resp(rules),
                self._query_resp(["uuid-1"]),
                self._get_resp(rules),
            ]
            self.module._fetch_pfm_rules("f")
            self.module._fetch_pfm_rules("f")
            self.assertEqual(self.mock_client.command.call_count, 4)
        finally:
            _CloudBase.PFM_RULES_CACHE_TTL = original_ttl

    def test_cache_is_per_instance(self):
        """Two module instances do not share a cache."""
        rules = [{"insight_id": "iid1", "category": "Network"}]
        self.mock_client.command.side_effect = [
            self._query_resp(["uuid-1"]),
            self._get_resp(rules),
            self._query_resp(["uuid-1"]),
            self._get_resp(rules),
        ]
        module2 = CloudModule(self.mock_client)

        self.module._fetch_pfm_rules("f")
        module2._fetch_pfm_rules("f")

        self.assertEqual(self.mock_client.command.call_count, 4)


if __name__ == "__main__":
    unittest.main()
