"""Per-call-site wiring tests for ``BaseModule._reorder_by_ids``.

``_reorder_by_ids`` exists because "get entities by IDs" endpoints return resources in
arbitrary order, discarding the sort the query step applied. ``tests/modules/test_base.py``
already covers the helper's own logic; what is untested is the *wiring* at each call site:
whether a tool actually calls it, against the right ID list, with the right ``id_field``.

Each case drives one tool with a stubbed query step (IDs ``a, b, c``) and a stubbed get
step that returns the entities **reversed**, then asserts the tool's output comes back in
``a, b, c`` order. That fails if a site drops the reorder call, passes the wrong
``id_field``, or reorders against the wrong list.

Deliberately out of scope: parameter forwarding. These tests patch the helpers that bracket
the reorder call rather than ``client.command``, so they say nothing about which operation
name or parameters a site sends. Per-module tests cover that.

``test_table_covers_every_call_site`` re-derives the live call sites from the source with
the same AST scan used to build the table, so a newly added site fails here until it gets a
case — the same guard spirit as ``test_filter_hints_registry_covers_search_tools``.
"""

import ast
import inspect
import pathlib
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic.fields import FieldInfo

from falcon_mcp.client import FalconClient
from falcon_mcp.modules.agentworks import AgentworksModule
from falcon_mcp.modules.cases import CasesModule
from falcon_mcp.modules.cloud.cloud import CloudModule
from falcon_mcp.modules.custom_ioa import CustomIOAModule
from falcon_mcp.modules.data_protection import DataProtectionModule
from falcon_mcp.modules.detections import DetectionsModule
from falcon_mcp.modules.exclusions import ExclusionsModule
from falcon_mcp.modules.firewall import FirewallModule
from falcon_mcp.modules.hosts import HostsModule
from falcon_mcp.modules.ioc import IOCModule
from falcon_mcp.modules.policies import PoliciesModule
from falcon_mcp.modules.quarantine import QuarantineModule
from falcon_mcp.modules.recon import ReconModule
from falcon_mcp.modules.rtr import RTRModule
from falcon_mcp.modules.scheduled_reports import ScheduledReportsModule
from falcon_mcp.modules.zero_trust_assessment import ZeroTrustAssessmentModule

MODULES_DIR = pathlib.Path("falcon_mcp/modules")

#: The IDs the stubbed query step reports, in the order the caller asked for.
ORDERED_IDS = ["a", "b", "c"]

#: A cloud asset record shaped so it survives the insight grouping/filtering in
#: ``cloud_insights``: an asset whose ``cloud_context.insights.external`` has no
#: well-formed entry is dropped from the response entirely, which would mask a
#: reorder regression as an empty result.
CLOUD_INSIGHT_EXTRA: dict[str, Any] = {
    "cloud_context": {"insights": {"external": [{"id": "insight-1", "stringValue": "v"}]}}
}


@dataclass(frozen=True)
class ReorderCase:
    """One ``_reorder_by_ids`` call site, and how to drive the tool that reaches it."""

    tool: str
    module_cls: type
    method: str
    id_field: str
    site: tuple[str, str]
    kwargs: dict[str, Any] = field(default_factory=dict)
    #: Key holding the entity's identity in the tool's *output*, when post-processing
    #: renames it (cloud insights re-emits ``id`` as ``asset_id``).
    out_id_field: str | None = None
    #: Extra keys every fake entity carries, for sites that post-process entities.
    entity_extra: dict[str, Any] = field(default_factory=dict)
    #: Helper returning the query-step IDs. ``None`` for sites with no query step,
    #: which reorder against caller-supplied IDs instead.
    query_patch: str | None = "_base_search_with_meta"
    #: Helper returning the hydrated entities.
    get_patch: str = "_base_get_by_ids"
    #: Extra attributes to patch on the module before calling the tool.
    extra_patches: dict[str, Any] = field(default_factory=dict)
    #: What the query step returns, when the endpoint hands back something other than
    #: bare ID strings (Zero Trust Assessment returns ``{aid, score}`` records).
    query_resources: list[Any] | None = None

    @property
    def output_key(self) -> str:
        return self.out_id_field or self.id_field

    def __str__(self) -> str:  # keeps pytest -k / IDs readable
        suffix = "".join(f"[{v}]" for v in self.kwargs.values() if isinstance(v, str))
        return f"{self.tool}{suffix}"


CASES: list[ReorderCase] = [
    # --- Standard two-step sites: _base_search_with_meta -> _base_get_by_ids ---
    ReorderCase(
        tool="falcon_search_hosts",
        module_cls=HostsModule,
        method="search_hosts",
        id_field="device_id",
        site=("falcon_mcp/modules/hosts.py", "search_hosts"),
    ),
    ReorderCase(
        tool="falcon_search_detections",
        module_cls=DetectionsModule,
        method="search_detections",
        id_field="composite_id",
        site=("falcon_mcp/modules/detections.py", "search_detections"),
    ),
    ReorderCase(
        tool="falcon_search_cases",
        module_cls=CasesModule,
        method="search_cases",
        id_field="id",
        site=("falcon_mcp/modules/cases.py", "search_cases"),
    ),
    ReorderCase(
        tool="falcon_search_iocs",
        module_cls=IOCModule,
        method="search_iocs",
        id_field="id",
        site=("falcon_mcp/modules/ioc.py", "search_iocs"),
    ),
    ReorderCase(
        tool="falcon_search_quarantined_files",
        module_cls=QuarantineModule,
        method="search_quarantined_files",
        id_field="id",
        site=("falcon_mcp/modules/quarantine.py", "search_quarantined_files"),
    ),
    ReorderCase(
        tool="falcon_search_sessions",
        module_cls=RTRModule,
        method="search_sessions",
        id_field="id",
        site=("falcon_mcp/modules/rtr.py", "search_sessions"),
    ),
    ReorderCase(
        tool="falcon_search_zta_assessments",
        module_cls=ZeroTrustAssessmentModule,
        method="search_zta_assessments",
        id_field="aid",
        # getAssessmentsByScoreV1 returns {aid, score} records, not bare IDs.
        query_resources=[{"aid": entity_id, "score": 1} for entity_id in ORDERED_IDS],
        site=("falcon_mcp/modules/zero_trust_assessment.py", "search_zta_assessments"),
    ),
    ReorderCase(
        tool="falcon_search_firewall_rules",
        module_cls=FirewallModule,
        method="search_firewall_rules",
        id_field="id",
        site=("falcon_mcp/modules/firewall.py", "search_firewall_rules"),
    ),
    ReorderCase(
        tool="falcon_search_firewall_rule_groups",
        module_cls=FirewallModule,
        method="search_firewall_rule_groups",
        id_field="id",
        site=("falcon_mcp/modules/firewall.py", "search_firewall_rule_groups"),
    ),
    ReorderCase(
        tool="falcon_search_firewall_policy_rules",
        module_cls=FirewallModule,
        method="search_firewall_policy_rules",
        id_field="id",
        kwargs={"policy_id": "policy-1"},
        site=("falcon_mcp/modules/firewall.py", "search_firewall_policy_rules"),
    ),
    ReorderCase(
        tool="falcon_search_data_protection_classifications",
        module_cls=DataProtectionModule,
        method="search_data_protection_classifications",
        id_field="id",
        site=(
            "falcon_mcp/modules/data_protection.py",
            "search_data_protection_classifications",
        ),
    ),
    ReorderCase(
        tool="falcon_search_data_protection_policies",
        module_cls=DataProtectionModule,
        method="search_data_protection_policies",
        id_field="id",
        kwargs={"platform_name": "win"},
        site=("falcon_mcp/modules/data_protection.py", "search_data_protection_policies"),
    ),
    ReorderCase(
        tool="falcon_search_data_protection_content_patterns",
        module_cls=DataProtectionModule,
        method="search_data_protection_content_patterns",
        id_field="id",
        site=(
            "falcon_mcp/modules/data_protection.py",
            "search_data_protection_content_patterns",
        ),
    ),
    ReorderCase(
        tool="falcon_search_scheduled_reports",
        module_cls=ScheduledReportsModule,
        method="search_scheduled_reports",
        id_field="id",
        site=("falcon_mcp/modules/scheduled_reports.py", "search_scheduled_reports"),
    ),
    ReorderCase(
        tool="falcon_search_report_executions",
        module_cls=ScheduledReportsModule,
        method="search_report_executions",
        id_field="id",
        site=("falcon_mcp/modules/scheduled_reports.py", "search_report_executions"),
    ),
    ReorderCase(
        tool="falcon_search_recon_notifications",
        module_cls=ReconModule,
        method="search_recon_notifications",
        id_field="id",
        site=("falcon_mcp/modules/recon.py", "search_recon_notifications"),
    ),
    ReorderCase(
        tool="falcon_search_recon_rules",
        module_cls=ReconModule,
        method="search_recon_rules",
        id_field="id",
        site=("falcon_mcp/modules/recon.py", "search_recon_rules"),
    ),
    ReorderCase(
        tool="falcon_search_recon_exposed_data_records",
        module_cls=ReconModule,
        method="search_recon_exposed_data_records",
        id_field="id",
        site=("falcon_mcp/modules/recon.py", "search_recon_exposed_data_records"),
    ),
    # --- Discriminated site: one reorder call serves four exclusion types ---
    *[
        ReorderCase(
            tool="falcon_search_exclusions",
            module_cls=ExclusionsModule,
            method="search_exclusions",
            id_field="id",
            kwargs={"exclusion_type": exclusion_type},
            site=("falcon_mcp/modules/exclusions.py", "_search_by_type"),
        )
        for exclusion_type in ("ioa", "ml", "sensor_visibility", "certificate")
    ],
    # --- Discriminated site: only device_control takes the two-step reorder path.
    # The other five policy types are pinned by test_policies_single_call_types_skip_reorder.
    ReorderCase(
        tool="falcon_search_policies",
        module_cls=PoliciesModule,
        method="search_policies",
        id_field="id",
        kwargs={"policy_type": "device_control"},
        site=("falcon_mcp/modules/policies.py", "_search_by_type"),
    ),
    # --- Cloud sites. _batch_get_cspm_assets and _batch_get_iom_entities both route
    # through _base_get_by_ids, so the standard get seam reaches them.
    ReorderCase(
        tool="falcon_search_cspm_assets",
        module_cls=CloudModule,
        method="search_cspm_assets",
        id_field="id",
        site=("falcon_mcp/modules/cloud/cloud_assets.py", "search_cspm_assets"),
    ),
    ReorderCase(
        tool="falcon_search_iom_findings",
        module_cls=CloudModule,
        method="search_iom_findings",
        id_field="id",
        site=("falcon_mcp/modules/cloud/cloud_iom.py", "search_iom_findings"),
    ),
    ReorderCase(
        tool="falcon_search_cloud_insights",
        module_cls=CloudModule,
        method="search_cloud_insights",
        id_field="id",
        out_id_field="asset_id",
        entity_extra=CLOUD_INSIGHT_EXTRA,
        # Skip the Policy Framework round-trip that builds the auto filter.
        extra_patches={"_build_insight_filter": lambda _fql: ("insights.id:['x']", 1)},
        site=("falcon_mcp/modules/cloud/cloud_insights.py", "search_cloud_insights"),
    ),
    # --- No query step: reorders against the caller's own ID list ---
    ReorderCase(
        tool="falcon_get_cloud_asset_insights",
        module_cls=CloudModule,
        method="get_cloud_asset_insights",
        id_field="id",
        out_id_field="asset_id",
        kwargs={"asset_ids": ORDERED_IDS},
        entity_extra=CLOUD_INSIGHT_EXTRA,
        query_patch=None,
        site=("falcon_mcp/modules/cloud/cloud_insights.py", "get_cloud_asset_insights"),
    ),
    # --- Sites whose query step is _base_search_api_call (no pagination tuple) ---
    ReorderCase(
        tool="falcon_list_case_templates",
        module_cls=CasesModule,
        method="list_case_templates",
        id_field="id",
        query_patch="_base_search_api_call",
        site=("falcon_mcp/modules/cases.py", "list_case_templates"),
    ),
    ReorderCase(
        tool="falcon_get_ioa_platforms",
        module_cls=CustomIOAModule,
        method="get_ioa_platforms",
        id_field="id",
        query_patch="_base_search_api_call",
        site=("falcon_mcp/modules/custom_ioa.py", "get_ioa_platforms"),
    ),
    ReorderCase(
        tool="falcon_get_ioa_rule_types",
        module_cls=CustomIOAModule,
        method="get_ioa_rule_types",
        id_field="id",
        query_patch="_base_search_api_call",
        site=("falcon_mcp/modules/custom_ioa.py", "get_ioa_rule_types"),
    ),
    # --- Sites that bypass the base helpers and call client.command directly ---
    ReorderCase(
        tool="falcon_search_cspm_suppression_rules",
        module_cls=CloudModule,
        method="search_cspm_suppression_rules",
        id_field="id",
        query_patch="client.command",
        get_patch="client.command",
        site=("falcon_mcp/modules/cloud/cloud_iom.py", "search_cspm_suppression_rules"),
    ),
    # One reorder call in the shared _search_agentworks helper serves all three
    # agentworks search tools; each public tool is driven so a wrapper cannot bypass it.
    *[
        ReorderCase(
            tool=f"falcon_{method}",
            module_cls=AgentworksModule,
            method=method,
            id_field="id",
            query_patch="client.command",
            get_patch="client.command",
            site=("falcon_mcp/modules/agentworks.py", "_search_agentworks"),
        )
        for method in (
            "search_agentworks_agents",
            "search_agentworks_agent_versions",
            "search_agentworks_spans",
        )
    ],
]


def _resolve_kwargs(method: Any, supplied: dict[str, Any]) -> dict[str, Any]:
    """Build a full kwargs dict, resolving Pydantic ``Field`` defaults to real values.

    Tool parameters default to ``FieldInfo`` objects, which FastMCP resolves at call time
    but a direct Python call does not. Some sites do arithmetic on those values before the
    patched helper is reached (``exclusions._clamp_limit`` on ``limit``), so leaving a
    ``FieldInfo`` in place raises instead of exercising the reorder path.
    """
    resolved: dict[str, Any] = {}
    for name, param in inspect.signature(method).parameters.items():
        if name in supplied:
            resolved[name] = supplied[name]
            continue
        default = param.default
        if isinstance(default, FieldInfo):
            assert not default.is_required(), (
                f"{method.__qualname__} parameter {name!r} is required; "
                "add it to the case's kwargs"
            )
            resolved[name] = default.default
        elif default is not inspect.Parameter.empty:
            resolved[name] = default
        else:
            raise AssertionError(
                f"{method.__qualname__} parameter {name!r} has no default; "
                "add it to the case's kwargs"
            )
    return resolved


def _extract_rows(result: Any) -> list[dict[str, Any]]:
    """Pull the ordered record list out of a tool result.

    Search tools return the pagination envelope; a few sites return the reordered list
    directly.
    """
    if isinstance(result, dict):
        assert "results" in result, f"unexpected dict result: {sorted(result)}"
        return result["results"]
    assert isinstance(result, list), f"unexpected result type: {type(result)}"
    return result


def _api_response(resources: list[Any]) -> dict[str, Any]:
    """A minimal successful FalconPy response body."""
    return {"status_code": 200, "body": {"resources": resources}}


def _drive(case: ReorderCase, entities: list[dict[str, Any]]) -> Any:
    """Call the tool with its query step stubbed to ORDERED_IDS and its get step to
    ``entities``, and return the raw tool result."""
    module = case.module_cls(MagicMock(spec=FalconClient))
    resources: list[Any] = case.query_resources if case.query_resources is not None else list(ORDERED_IDS)

    for name, value in case.extra_patches.items():
        setattr(module, name, value)

    bound = getattr(module, case.method)
    kwargs = _resolve_kwargs(bound, case.kwargs)

    if case.query_patch == "client.command":
        # Both steps go through client.command, in query-then-get order.
        module.client.command = MagicMock(
            side_effect=[_api_response(resources), _api_response(entities)]
        )
        return bound(**kwargs)

    with patch.object(module, case.get_patch, return_value=entities):
        if case.query_patch is None:
            return bound(**kwargs)

        if case.query_patch == "_base_search_with_meta":
            query_return: Any = (resources, {"total": len(resources)})
        else:
            query_return = resources

        with patch.object(module, case.query_patch, return_value=query_return):
            return bound(**kwargs)


@pytest.mark.parametrize("case", CASES, ids=str)
def test_reorder_restores_query_step_order(case: ReorderCase) -> None:
    """The tool re-sorts hydrated entities back into the query step's ID order.

    The stubbed get step hands back the entities reversed, mimicking a get-by-IDs endpoint
    that ignores the requested sort. A correctly wired site undoes that.
    """
    entities = [
        {case.id_field: entity_id, **case.entity_extra} for entity_id in reversed(ORDERED_IDS)
    ]

    rows = _extract_rows(_drive(case, entities))

    assert [row[case.output_key] for row in rows] == ORDERED_IDS, (
        f"{case.tool} did not restore the query-step order; "
        "the site is missing a _reorder_by_ids call or passes the wrong id_field"
    )


@pytest.mark.parametrize(
    "policy_type", ["prevention", "sensor_update", "firewall", "response", "content_update"]
)
def test_policies_single_call_types_skip_reorder(policy_type: str) -> None:
    """The five combined-op policy types never reach the get-by-IDs reorder path.

    Only ``device_control`` is two-step, because its combined op has no V2 and drops
    V2-only fields. The others get full objects from one call, so there is no query order
    to restore — pinning that keeps a future refactor from quietly routing them through
    hydration (or from making device_control single-call and losing its reorder).
    """
    module = PoliciesModule(MagicMock(spec=FalconClient))
    combined = [{"id": entity_id} for entity_id in reversed(ORDERED_IDS)]

    with (
        patch.object(module, "_base_search_with_meta", return_value=(combined, {"total": 3})),
        patch.object(module, "_base_get_by_ids") as mock_get,
    ):
        result = module.search_policies(
            **_resolve_kwargs(module.search_policies, {"policy_type": policy_type})
        )

    mock_get.assert_not_called()
    assert [row["id"] for row in _extract_rows(result)] == list(reversed(ORDERED_IDS))


def _live_call_sites() -> set[tuple[str, str]]:
    """Every ``(module file, enclosing method)`` that calls ``_reorder_by_ids``."""
    sites: set[tuple[str, str]] = set()
    for path in sorted(MODULES_DIR.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for call in ast.walk(node):
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and call.func.attr == "_reorder_by_ids"
                ):
                    sites.add((path.as_posix(), node.name))
                    break
    return sites


def test_table_covers_every_call_site() -> None:
    """Every ``_reorder_by_ids`` call site in the source has a wiring case.

    Derived from the source rather than a hardcoded count, so adding a call site without a
    case fails here and names the offender.
    """
    live = _live_call_sites()
    assert live, "found no _reorder_by_ids call sites — is the AST scan looking in the right place?"

    covered = {case.site for case in CASES}

    assert not live - covered, f"call sites with no wiring case: {sorted(live - covered)}"
    assert not covered - live, f"cases pointing at call sites that no longer exist: {sorted(covered - live)}"
