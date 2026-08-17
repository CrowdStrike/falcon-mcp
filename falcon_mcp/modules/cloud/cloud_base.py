"""Shared base class for all Cloud Security mixins."""

from typing import Any

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule


class _CloudBase(BaseModule):
    """Extends BaseModule with cloud-specific shared helpers."""

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

        Queries QueryRule with the provided filter (500 per page), then fetches
        full rule details via GetRule in batches of 100.

        Args:
            filter: FQL filter string passed to QueryRule (e.g.
                    "rule_domain:'CSPM'+rule_subdomain:'Insight'").

        Returns:
            Flat list of raw rule dicts. Empty if none found.

        Raises:
            RuntimeError: If any API call returns an error.
        """
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
            if len(page) < 500:
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
