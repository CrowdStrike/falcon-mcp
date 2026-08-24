"""Shared base class for all Cloud Security mixins."""

import time
from typing import Any

from mcp.server import FastMCP

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)

_PFM_QUERY_PAGE_SIZE = 500

# Upper bound on rules accumulated from QueryRule pagination. The live CSPM catalog is
# ~3.5k rules in total, so this leaves ample headroom while bounding the loop if the
# API ever stops returning a short final page.
_PFM_MAX_RULES = 10_000


class _CloudBase(BaseModule):
    """Extends BaseModule with cloud-specific shared helpers."""

    # How long (seconds) a cached _fetch_pfm_rules result is considered fresh.
    # Set to 0 to disable caching entirely.
    PFM_RULES_CACHE_TTL: int = 600

    def __init__(self, client: Any) -> None:
        super().__init__(client)
        self._pfm_rules_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}

    def register_tools(self, server: FastMCP) -> None:
        """Terminate the cooperative ``super().register_tools()`` chain.

        Each cloud mixin registers its own tools and then delegates to ``super()``;
        this no-op is the end of that chain, not a forgotten override. Registration is
        covered end to end by ``tests/modules/cloud/test_cloud.py``, which asserts the
        exact set of tools ``CloudModule`` exposes — a mixin dropped from the chain
        fails there.
        """
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
            Flat list of raw rule dicts. Empty if none found. The list itself is a copy,
            so appending or clearing it cannot disturb the cache, but the dicts inside
            are shared with the cached entry — treat them as read-only.

        Raises:
            RuntimeError: If any API call returns an error.
        """
        if self.PFM_RULES_CACHE_TTL > 0:
            cached = self._pfm_rules_cache.get(filter)
            if cached is not None:
                cached_at, rules = cached
                if time.monotonic() - cached_at < self.PFM_RULES_CACHE_TTL:
                    return list(rules)

        rules = self._fetch_pfm_rules_uncached(filter)

        if self.PFM_RULES_CACHE_TTL > 0:
            self._pfm_rules_cache[filter] = (time.monotonic(), list(rules))

        return rules

    def _fetch_pfm_rules_uncached(self, filter: str) -> list[dict[str, Any]]:
        """Fetch PFM rules from the API without consulting the cache."""
        uuids: list[str] = []
        seen: set[str] = set()
        offset = 0
        while True:
            params = prepare_api_parameters({"filter": filter, "limit": _PFM_QUERY_PAGE_SIZE, "offset": offset})
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

            # Dedupe: a repeated UUID across pages would otherwise be fetched twice.
            new_count = 0
            for uuid in page:
                if uuid not in seen:
                    seen.add(uuid)
                    uuids.append(uuid)
                    new_count += 1

            # A short page is the last page. Check this before `total`, so a `total`
            # that under-reports can never truncate a full page of results.
            if len(page) < _PFM_QUERY_PAGE_SIZE:
                break

            # A full page that contributed nothing new means the server stopped honoring
            # `offset` and is replaying a page. Progress has to be judged on new UUIDs:
            # the dedupe keeps `uuids` from growing here, so any cap measured against it
            # would never be reached.
            if new_count == 0:
                logger.warning(
                    "PFM QueryRule returned a full page with no new rules for filter %r "
                    "at offset %d; stopping to avoid re-requesting the same page.",
                    filter,
                    offset,
                )
                break

            total = (
                (response.get("body") or {})
                .get("meta", {})
                .get("pagination", {})
                .get("total")
            )
            # Exact agreement only. It saves one empty round-trip when `total` is an exact
            # multiple of the page size. `len(uuids) > total` means `total` under-reports,
            # and trusting it there would silently drop every later page; `<` means a
            # duplicate was deduped and there is more to fetch.
            if total is not None and len(uuids) == total:
                break

            offset += len(page)

            # Bound on `offset`, which advances on every iteration, rather than on
            # len(uuids), which the dedupe can hold flat.
            if offset >= _PFM_MAX_RULES:
                logger.warning(
                    "PFM rule pagination hit the %d-rule cap for filter %r; "
                    "results are truncated.",
                    _PFM_MAX_RULES,
                    filter,
                )
                break

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
