"""What each query endpoint validates, which is what an empty result is allowed to prove.

Every "zero rows means that value is wrong" conclusion in the suites that probe FQL
vocabularies rests on knowing whether the endpoint under test can even report a bad value.
Three behaviours exist, and they are a property of the individual operation:

- **value-validating** — an impossible value is a 400. Enum membership is decidable with no
  tenant data at all.
- **field-validating** — only the field name is checked. A bad value is indistinguishable
  from a value nothing happens to match, so membership needs rows.
- **silent** — an unknown *field* is an empty HTTP 200. Nothing an empty result says can be
  trusted, ever.

These are pinned rather than assumed because they are not inheritable: within the Discover
module `search_unmanaged_assets` only checks field names while `search_applications`, one
method away, rejects a bad value outright; and `search_exclusions` changes behaviour with
its own `exclusion_type` argument. A test elsewhere that reads an empty 200 as evidence is
only sound while its endpoint's row here still says so — if one of these flips, that test
has gone blind and this is what says which one.
"""

import pytest

from falcon_mcp.modules.cloud.cloud import CloudModule
from falcon_mcp.modules.discover import DiscoverModule
from falcon_mcp.modules.exclusions import ExclusionsModule
from falcon_mcp.modules.firewall import FirewallModule
from falcon_mcp.modules.hosts import HostsModule
from falcon_mcp.modules.intel import IntelModule
from falcon_mcp.modules.ioc import IOCModule
from falcon_mcp.modules.policies import PoliciesModule
from falcon_mcp.modules.quarantine import QuarantineModule
from falcon_mcp.modules.recon import ReconModule
from falcon_mcp.modules.spotlight import SpotlightModule
from tests.integration.utils.base_integration_test import (
    ENDPOINT_FIELD_VALIDATING,
    ENDPOINT_SILENT,
    ENDPOINT_VALUE_VALIDATING,
    BaseIntegrationTest,
)

_BOGUS_FIELD = "zzz_not_a_field:'x'"

#: (label, module class, method name, bogus-value filter, extra kwargs, expected class).
#: The bogus-value probe names a real field with a value that cannot exist — for a typed
#: field a type violation, otherwise an impossible enum member.
CASES = [
    ("hosts", HostsModule, "search_hosts", "platform_name:'ZZZ_NOPE'", {}, ENDPOINT_FIELD_VALIDATING),
    ("iocs", IOCModule, "search_iocs", "type:'zzz_nope'", {}, ENDPOINT_SILENT),
    ("recon_notifications", ReconModule, "search_recon_notifications", "status:'zzz-nope'", {}, ENDPOINT_SILENT),
    ("recon_rules", ReconModule, "search_recon_rules", "status:'zzz_nope'", {}, ENDPOINT_SILENT),
    ("actors", IntelModule, "query_actor_entities", "motivations.value:'ZZZ Nope'", {}, ENDPOINT_FIELD_VALIDATING),
    ("reports", IntelModule, "query_report_entities", "type:'ZZZ_NOPE'", {}, ENDPOINT_FIELD_VALIDATING),
    ("policies", PoliciesModule, "search_policies", "platform_name:'ZZZ_NOPE'", {"policy_type": "prevention"}, ENDPOINT_FIELD_VALIDATING),
    ("firewall_rule_groups", FirewallModule, "search_firewall_rule_groups", "platform:'zzz_nope'", {}, ENDPOINT_FIELD_VALIDATING),
    ("quarantined_files", QuarantineModule, "search_quarantined_files", "state:'zzz_nope'", {}, ENDPOINT_SILENT),
    ("applications", DiscoverModule, "search_applications", "is_suspicious:'zzz_nope'", {}, ENDPOINT_VALUE_VALIDATING),
    ("unmanaged_assets", DiscoverModule, "search_unmanaged_assets", "platform_name:'ZZZ_NOPE'", {}, ENDPOINT_FIELD_VALIDATING),
    ("managed_assets", DiscoverModule, "search_managed_assets", "platform_name:'ZZZ_NOPE'", {}, ENDPOINT_FIELD_VALIDATING),
    ("vulnerabilities", SpotlightModule, "search_vulnerabilities", "cve.severity:'ZZZ_NOPE'", {}, ENDPOINT_FIELD_VALIDATING),
    ("cloud_risks", CloudModule, "search_cloud_risks", "severity:'ZZZ_NOPE'", {}, ENDPOINT_FIELD_VALIDATING),
    ("images_vulnerabilities", CloudModule, "search_images_vulnerabilities", "severity:'ZZZ_NOPE'", {}, ENDPOINT_FIELD_VALIDATING),
    ("iom_findings", CloudModule, "search_iom_findings", "severity:'zzz_nope'", {}, ENDPOINT_FIELD_VALIDATING),
    # Two exclusion types, because this one endpoint answers an unknown field differently
    # depending on which sub-API `exclusion_type` routes to.
    ("exclusions[ml]", ExclusionsModule, "search_exclusions", "applied_globally:'zzz_nope'", {"exclusion_type": "ml"}, ENDPOINT_SILENT),
    ("exclusions[sensor_visibility]", ExclusionsModule, "search_exclusions", "applied_globally:'zzz_nope'", {"exclusion_type": "sensor_visibility"}, ENDPOINT_VALUE_VALIDATING),
]


@pytest.mark.integration
class TestFilterClassification(BaseIntegrationTest):
    """Pin what each probed query endpoint validates."""

    @pytest.mark.parametrize(
        ("label", "module_cls", "method_name", "bogus_value", "kwargs", "expected"),
        CASES,
        ids=[case[0] for case in CASES],
    )
    def test_endpoint_validation_class(
        self, falcon_client, label, module_cls, method_name, kwargs, bogus_value, expected
    ):
        """The endpoint still validates what the vocabulary tests assume it validates."""
        self.module = module_cls(falcon_client)
        actual = self.classify_endpoint(
            getattr(self.module, method_name),
            _BOGUS_FIELD,
            bogus_value,
            context=label,
            **kwargs,
        )
        assert actual == expected, (
            f"{label} is now {actual}, not {expected}. Every test that reads an empty 200 "
            f"from this endpoint as evidence about a *value* needs rechecking: moving "
            f"toward 'silent' makes those tests vacuous, and moving toward "
            f"'value-validating' means a previously untestable value is now decidable."
        )
