"""Shared base class for all Cloud Security mixins."""

import time
from typing import Any

from mcp.server import FastMCP

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule


class _CloudBase(BaseModule):
    """Extends BaseModule with cloud-specific shared helpers."""

    # How long (seconds) a cached _fetch_pfm_rules result is considered fresh.
    # Set to 0 to disable caching entirely.
    PFM_RULES_CACHE_TTL: int = 600

    def __init__(self, client: Any) -> None:
        super().__init__(client)
        self._pfm_rules_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}

    def register_tools(self, server: FastMCP) -> None:
        pass

    def _batch_get_cspm_assets(self, asset_ids: list[str]) -> list[dict[str, Any]] | dict[str, Any]:
        """Fetch CSPM asset details in batches of 100 (API limit).

        The cloud_security_assets_entities_get API endpoint has a strict limit of 100 IDs
        per request (as confirmed by API validation). This helper splits large ID lists
        into chunks and aggregates the results.
        """
        BATCH_SIZE = 100
        all_assets: list[dict[str, Any]] = []

        for i in range(0, len(asset_ids), BATCH_SIZE):
            batch = asset_ids[i : i + BATCH_SIZE]
            result = self._base_get_by_ids(
                operation="cloud_security_assets_entities_get",
                ids=batch,
                id_key="ids",
                use_params=True,  # CRITICAL: GET method requires use_params
            )
            if self._is_error(result):
                return result
            if isinstance(result, list):
                all_assets.extend(result)

        return all_assets

    def _fetch_pfm_rules(self, filter: str) -> list[dict[str, Any]]:
        """Fetch PFM rules matching the given FQL filter, paginating as needed.

        Results are cached per instance per filter string for PFM_RULES_CACHE_TTL
        seconds. Set PFM_RULES_CACHE_TTL = 0 to disable caching.

        Args:
            filter: FQL filter string passed to QueryRule (e.g.
                    "rule_domain:'CSPM'+rule_subdomain:'Insight'").

        Returns:
            Flat list of raw rule dicts. Empty if none found.

        Raises:
            RuntimeError: If any API call returns an error.
        """
        if self.PFM_RULES_CACHE_TTL > 0:
            cached = self._pfm_rules_cache.get(filter)
            if cached is not None:
                cached_at, rules = cached
                if time.monotonic() - cached_at < self.PFM_RULES_CACHE_TTL:
                    return rules

        rules = self._fetch_pfm_rules_uncached(filter)

        if self.PFM_RULES_CACHE_TTL > 0:
            self._pfm_rules_cache[filter] = (time.monotonic(), rules)

        return rules

    def _fetch_pfm_rules_uncached(self, filter: str) -> list[dict[str, Any]]:
        """Fetch PFM rules from the API without consulting the cache."""
        uuids: list[str] = []
        offset = 0
        while True:
            params = prepare_api_parameters({"filter": filter, "limit": 500, "offset": offset})
            response = self.client.command("QueryRule", parameters=params)
            page = handle_api_response(
                response,
                operation="QueryRule",
                error_message="Failed to query PFM rules",
                default_result=[],
            )
            if self._is_error(page):
                raise RuntimeError(f"PFM QueryRule failed: {page}")
            if not isinstance(page, list) or not page:
                break
            uuids.extend(page)
            total = (
                (response.get("body") or {})
                .get("meta", {})
                .get("pagination", {})
                .get("total")
            )
            if total is not None:
                if len(uuids) >= total:
                    break
            elif len(page) < 500:
                break
            offset += len(page)

        if not uuids:
            return []

        rules: list[dict[str, Any]] = []
        for i in range(0, len(uuids), 100):
            batch = uuids[i : i + 100]
            result = self._base_get_by_ids(
                operation="GetRule",
                ids=batch,
                id_key="ids",
                use_params=True,
            )
            if self._is_error(result):
                raise RuntimeError(f"PFM GetRule failed: {result}")
            if isinstance(result, list):
                rules.extend(result)

        return rules
