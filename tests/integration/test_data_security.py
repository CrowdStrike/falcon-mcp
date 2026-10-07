"""Integration tests for the Data Security module."""

import re
import time

import pytest

from falcon_mcp.modules.data_security import DataSecurityModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDataSecurityIntegration(BaseIntegrationTest):
    """Integration tests for Data Security module with real API calls.

    Validates:
    - Correct FalconPy operation names dispatched by the generic
      search_data_security_entities / get_data_security_entities tools
      (e.g. queries_classification_get_v2, entities_classification_get_v2,
      queries_content_pattern_get_v2, entities_content_pattern_get)
    - Two-step search pattern returns full details, not just IDs
    - GET with params usage for get_by_ids (use_params=True)
    - platform_name parameter handling for policies
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Data Security module with a real client."""
        self.module = DataSecurityModule(falcon_client)

    # --- Classifications ---

    def test_search_classifications(self):
        """Test that searching classifications returns results."""
        result = self.call_method(
            self.module.search_data_security_entities, entity_type="classification", limit=5
        )

        self.assert_no_error(result, context="search classification")
        self.assert_valid_list_response(result, min_length=0, context="search classification")

    def test_search_classifications_returns_full_details(self):
        """Test that classifications include full entity details."""
        result = self._unwrap_results(
            self.call_method(
                self.module.search_data_security_entities, entity_type="classification", limit=2
            )
        )

        if not result or isinstance(result, dict):
            self.skip_with_warning("No classifications found", "classifications details")
            return

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "cid", "created_at", "classification_properties"],
            context="search classification full details",
        )

    def test_search_classifications_with_filter(self):
        """Test classification search with FQL filter."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="classification",
            filter="created_at:>'2024-01-01'",
            limit=3,
        )

        self.assert_no_error(result, context="search classification with filter")

    def test_search_classifications_with_sort(self):
        """Test classification search with sort parameter."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="classification",
            sort="name.asc",
            limit=3,
        )

        self.assert_no_error(result, context="search classification with sort")
        self.assert_valid_list_response(
            result, min_length=0, context="search classification with sort"
        )

    def test_policy_precedence_sorts_ascending_but_not_descending(self):
        """Backs the policy FQL guide's precedence sort fields with a live check.

        `precedence.asc` orders correctly (4 of 4 trials, 20 of 20 distinct values) while
        `precedence.desc` does not (0 of 4). Both directions are pinned together so the
        asymmetry is what fails if either half changes: if desc starts working, list
        `precedence.desc` in the policy FQL guide's sort fields; if asc stops, the guide is
        wrong the other way.

        Not a `_reorder_by_ids` concern — this endpoint's get step preserves the order it is
        handed (0 of 4 trials scrambled), so the defect is in the API's own sort.
        """

        def precedences(direction: str) -> list:
            result = self.call_method(
                self.module.search_data_security_entities,
                entity_type="policy",
                platform_name="win",
                sort=f"precedence.{direction}",
                limit=20,
            )
            self.assert_no_error(result, context=f"dp policies precedence.{direction}")
            return [p["precedence"] for p in self._unwrap_results(result)]

        ascending = precedences("asc")
        descending = precedences("desc")

        assert (
            len(ascending) > 1
        ), f"Need 2+ win data-security policies to compare order, got {len(ascending)}"
        assert ascending == sorted(ascending), (
            f"precedence.asc is no longer ascending, so the policy FQL guide's listing of "
            f"precedence.asc as a sort field is wrong: {ascending}"
        )
        assert descending != sorted(descending, reverse=True), (
            "precedence.desc now returns correctly ordered results — the known defect is "
            "fixed. Add precedence.desc to the policy FQL guide's sort fields. "
            f"Got: {descending}"
        )

    @staticmethod
    def _collation_key(name: str) -> str:
        """The v1 endpoints sort names ignoring case and punctuation ('CLI monitoring'
        before 'CL-LarkDemo'), with non-ASCII names last; mirror that to compare."""
        return re.sub(r"[^0-9a-z\u0080-\uffff]", "", name.lower())

    def test_name_sort_orders_both_directions(self):
        """Backs the guides' `name.asc` / `name.desc` sort fields with a live check.

        Web locations and local applications are included because their SDK spec
        omits `sort` even though the API accepts and honors it.
        """
        for entity_type in (
            "content_pattern",
            "web_location",
            "local_application",
            "local_application_group",
        ):
            for direction in ("asc", "desc"):
                result = self.call_method(
                    self.module.search_data_security_entities,
                    entity_type=entity_type,
                    sort=f"name.{direction}",
                    limit=20,
                )
                self.assert_no_error(result, context=f"{entity_type} name.{direction}")
                keys = [self._collation_key(e["name"]) for e in self._unwrap_results(result)]
                assert len(set(keys)) > 1, f"Need 2+ distinct {entity_type} names, got {keys}"
                assert keys == sorted(keys, reverse=(direction == "desc")), (
                    f"{entity_type} name.{direction} is not ordered: {keys}"
                )

    def _ids_matching(self, entity_type: str, fql: str, **kwargs) -> list[str]:
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type=entity_type,
            filter=fql,
            limit=50,
            **kwargs,
        )
        self.assert_no_error(result, context=f"{entity_type} {fql}")
        return [e["id"] for e in self._unwrap_results(result)]

    def test_name_and_email_match_only_with_tilde(self):
        """Backs the classification and policy guides: `~` matches, exact returns nothing.

        The fixture comes from an unfiltered search. Each pair of queries shares the
        fixture's exact created_at, so the operator is the only difference between them.
        """
        cases = [
            ("classification", "created_by", {}),
            ("classification", "name", {}),
            ("policy", "modified_by", {"platform_name": "win"}),
            ("policy", "name", {"platform_name": "win"}),
            ("policy", "description", {"platform_name": "win"}),
        ]
        for entity_type, field, kwargs in cases:
            fixtures = self._unwrap_results(
                self.call_method(
                    self.module.search_data_security_entities,
                    entity_type=entity_type,
                    limit=50,
                    **kwargs,
                )
            )
            fixture = next(
                (e for e in fixtures if e.get(field) and "'" not in e[field] and e.get("created_at")),
                None,
            )
            assert fixture, f"No {entity_type} with a quote-free {field} to test against"
            pin = f"created_at:'{fixture['created_at']}'"
            value = fixture[field]

            tilde = self._ids_matching(entity_type, f"{field}:~'{value}'+{pin}", **kwargs)
            exact = self._ids_matching(entity_type, f"{field}:'{value}'+{pin}", **kwargs)

            assert fixture["id"] in tilde, f"{entity_type} {field}:~ missed its own value {value!r}"
            assert fixture["id"] not in exact, (
                f"{entity_type} {field}:'...' exact match now works — update the FQL guide, "
                f"which says only ~ matches. Value: {value!r}"
            )

    def test_documented_v1_fields_find_a_known_record(self):
        """Backs the content pattern, cloud application and web location guides.

        Each fixture comes from an unfiltered search. Every check is ANDed with the
        fixture's exact name, which these endpoints match exactly, so a field the API
        ignored or rejected would drop the fixture rather than pass on volume.
        """
        checks = {
            "content_pattern": lambda e: [f"created:'{e['created']}'", f"last_updated:'{e['last_updated']}'"],
            "cloud_application": lambda e: [f"created:'{e['created']}'", f"last_updated:'{e['last_updated']}'"],
            "web_location": lambda e: [
                f"created:'{e['created']}'",
                f"last_updated:'{e['last_updated']}'",
                f"web_location_group_id:'{e['web_location_group_ids'][0]}'",
                f"web_location_group_count:{len(e['web_location_group_ids'])}",
            ],
        }
        for entity_type, clauses in checks.items():
            records = self._unwrap_results(
                self.call_method(
                    self.module.search_data_security_entities, entity_type=entity_type, limit=100
                )
            )
            fixture = next(
                (
                    e
                    for e in records
                    if e.get("name", "").strip()
                    and "'" not in e["name"]
                    and (entity_type != "web_location" or e.get("web_location_group_ids"))
                ),
                None,
            )
            assert fixture, f"No usable {entity_type} fixture in the first 100 records"
            pin = f"name:'{fixture['name']}'"
            for clause in clauses(fixture):
                ids = self._ids_matching(entity_type, f"{clause}+{pin}")
                assert fixture["id"] in ids, f"{entity_type} {clause} did not find its own record"

        # Records omit supports_network_inspection when it is false, so each side is checked
        # against the value it returns rather than the presence of results.
        by_value = {}
        for value in ("true", "false"):
            result = self.call_method(
                self.module.search_data_security_entities,
                entity_type="web_location",
                filter=f"supports_network_inspection:{value}",
                limit=50,
            )
            self.assert_no_error(result, context=f"web_location supports_network_inspection:{value}")
            by_value[value] = self._unwrap_results(result)
            assert by_value[value], f"web_location supports_network_inspection:{value} returned nothing"
        assert all(e.get("supports_network_inspection") is True for e in by_value["true"]), (
            "supports_network_inspection:true returned a record without it set"
        )
        assert all(e.get("supports_network_inspection") is not True for e in by_value["false"]), (
            "supports_network_inspection:false returned a record with it set"
        )

    def test_relative_dates_are_rejected_outside_classification_and_policy(self):
        """Backs the guides' note that only classification and policy accept now-Nd."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="content_pattern",
            filter="created:>'now-7d'",
            limit=1,
        )
        errors = result.get("results") if isinstance(result, dict) else result
        assert errors and "error" in errors[0], (
            "content_pattern now accepts relative dates — drop the 'relative dates are "
            f"rejected' note from the v1 FQL guides and the filter hint. Got: {result}"
        )
        assert errors[0]["details"]["status_code"] == 400

        ok = self._ids_matching("classification", "created_at:>'now-3650d'")
        assert ok, "classification no longer accepts relative dates"

    # --- Policies ---

    def test_search_policies_windows(self):
        """Test that policy search works with platform_name='win'."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="policy",
            platform_name="win",
            limit=5,
        )

        self.assert_no_error(result, context="search policy win")
        self.assert_valid_list_response(result, min_length=0, context="search policy win")

    def test_search_policies_mac(self):
        """Test that policy search works with platform_name='mac'."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="policy",
            platform_name="mac",
            limit=5,
        )

        self.assert_no_error(result, context="search policy mac")
        self.assert_valid_list_response(result, min_length=0, context="search policy mac")

    def test_search_policies_returns_full_details(self):
        """Test that policies include full entity details."""
        result = self._unwrap_results(
            self.call_method(
                self.module.search_data_security_entities,
                entity_type="policy",
                platform_name="win",
                limit=2,
            )
        )

        if not result or isinstance(result, dict):
            self.skip_with_warning("No win policies found", "policies details")
            return

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "platform_name", "is_enabled", "precedence"],
            context="search policy full details",
        )

    def test_search_policies_with_filter(self):
        """Test policy search with FQL filter."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="policy",
            platform_name="win",
            filter="is_enabled:true",
            limit=3,
        )

        self.assert_no_error(result, context="search policy with filter")

    # --- Content Patterns ---

    def test_search_content_patterns(self):
        """Test that content pattern search returns results."""
        result = self.call_method(
            self.module.search_data_security_entities, entity_type="content_pattern", limit=5
        )

        self.assert_no_error(result, context="search content_pattern")
        self.assert_valid_list_response(result, min_length=0, context="search content_pattern")

    def test_search_content_patterns_returns_full_details(self):
        """Test that content patterns include full entity details."""
        result = self._unwrap_results(
            self.call_method(
                self.module.search_data_security_entities, entity_type="content_pattern", limit=2
            )
        )

        if not result or isinstance(result, dict):
            self.skip_with_warning("No content patterns found", "content patterns details")
            return

        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "type", "category", "region"],
            context="search content_pattern full details",
        )

    def test_search_content_patterns_with_filter(self):
        """Test content pattern search with FQL filter."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="content_pattern",
            filter="deleted:false",
            limit=3,
        )

        self.assert_no_error(result, context="search content_pattern with filter")

    def test_search_content_patterns_by_type(self):
        """Test filtering content patterns by type."""
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="content_pattern",
            filter="type:'predefined'",
            limit=3,
        )

        self.assert_no_error(result, context="search content_pattern by type")
        self.assert_valid_list_response(
            result, min_length=0, context="search content_pattern by type"
        )

    # --- Operation Name Validation ---

    def test_operation_names_are_correct(self):
        """Validate that core read (query + get) FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        This is the primary defense against gotchas like the
        entities_content_pattern_get no-_v2 naming.
        """
        # queries_classification_get_v2 + entities_classification_get_v2
        result = self.call_method(
            self.module.search_data_security_entities, entity_type="classification", limit=1
        )
        self.assert_no_error(result, context="classification operation names")

        # queries_policy_get_v2 + entities_policy_get_v2
        result = self.call_method(
            self.module.search_data_security_entities,
            entity_type="policy",
            platform_name="win",
            limit=1,
        )
        self.assert_no_error(result, context="policy operation names")

        # queries_content_pattern_get_v2 + entities_content_pattern_get (no _v2!)
        result = self.call_method(
            self.module.search_data_security_entities, entity_type="content_pattern", limit=1
        )
        self.assert_no_error(result, context="content_pattern operation names")

    def test_additional_search_operation_names_are_correct(self):
        """Validate the query + get operation names for the remaining entity types."""
        entity_types = [
            "cloud_application",
            "enterprise_account",
            "web_location",
            "local_application",
            "local_application_group",
            "sensitivity_label",
            "file_type",
        ]
        for entity_type in entity_types:
            result = self.call_method(
                self.module.search_data_security_entities, entity_type=entity_type, limit=1
            )
            self.assert_no_error(result, context=f"{entity_type} operation names")
            self.assert_valid_list_response(result, min_length=0, context=f"{entity_type} response")

    # --- Write roundtrips ---
    #
    # Each test creates uniquely named entities, updates them through the tool, re-reads
    # them, and deletes everything it created in a finally block. The module has no delete
    # tool, so cleanup calls the delete operations directly.

    _DELETE_OPS = {
        "content_pattern": "entities_content_pattern_delete",
        "cloud_application": "entities_cloud_application_delete",
        "enterprise_account": "entities_enterprise_account_delete",
        "web_location": "entities_web_location_delete_v2",
        "local_application": "entities_local_application_delete",
        "local_application_group": "entities_local_application_group_delete",
        "classification": "entities_classification_delete_v2",
        "policy": "entities_policy_delete_v2",
    }

    @pytest.fixture
    def created(self, falcon_client):
        """Collect (entity_type, id, extra_params) and delete them in reverse order."""
        entities: list[tuple[str, str, dict]] = []
        yield entities
        for entity_type, entity_id, extra in reversed(entities):
            falcon_client.command(
                self._DELETE_OPS[entity_type], parameters={"ids": [entity_id], **extra}
            )

    def _create(self, created, entity_type: str, body: dict, platform_name=None) -> dict:
        result = self.call_method(
            self.module.create_data_security_entity,
            entity_type=entity_type,
            body=body,
            platform_name=platform_name,
        )
        self.assert_no_error(result, context=f"create {entity_type}")
        assert isinstance(result, list) and result and result[0].get("id"), (
            f"create {entity_type} returned no entity: {result}"
        )
        extra = {"platform_name": platform_name} if platform_name else {}
        created.append((entity_type, result[0]["id"], extra))
        return result[0]

    def _update(self, entity_type: str, body: dict, platform_name=None) -> None:
        result = self.call_method(
            self.module.update_data_security_entity,
            entity_type=entity_type,
            body=body,
            platform_name=platform_name,
        )
        self.assert_no_error(result, context=f"update {entity_type}")

    def _get(self, entity_type: str, entity_id: str) -> dict:
        result = self.call_method(
            self.module.get_data_security_entities, entity_type=entity_type, ids=[entity_id]
        )
        self.assert_no_error(result, context=f"get {entity_type}")
        assert isinstance(result, list) and len(result) == 1, f"get {entity_type}: {result}"
        return result[0]

    @staticmethod
    def _name(kind: str) -> str:
        return f"fmcp-it-{kind}-{int(time.time() * 1000)}"

    def test_content_pattern_partial_update_roundtrip(self, created):
        """A partial content pattern update changes only the supplied field."""
        cp = self._create(
            created,
            "content_pattern",
            {
                "name": self._name("cp"),
                "category": "Custom",
                "description": "before",
                "regexes": ["FMCPIT[0-9]{6}"],
                "min_match_threshold": 1,
                "region": "ALL",
            },
        )
        self._update("content_pattern", {"id": cp["id"], "description": "after"})

        after = self._get("content_pattern", cp["id"])
        assert after["description"] == "after"
        assert after["name"] == cp["name"]
        assert after["regexes"] == cp["regexes"]

    def test_web_location_update_roundtrip(self, created):
        """A web location created under a cloud application can be renamed."""
        app = self._create(
            created,
            "cloud_application",
            {"name": self._name("app"), "urls": [{"fqdn": f"{self._name('fqdn')}.example.com", "path": ""}]},
        )
        wl = self._create(
            created,
            "web_location",
            {"name": self._name("wl"), "application_id": app["id"], "type": "custom"},
        )
        new_name = f"{wl['name']}-renamed"
        self._update("web_location", {"id": wl["id"], "name": new_name})

        after = self._get("web_location", wl["id"])
        assert after["name"] == new_name
        assert after["application_id"] == app["id"]

    def test_local_application_partial_update_keeps_other_fields(self, created):
        """Partial updates to a local application and its group leave unsupplied fields intact."""
        group = self._create(
            created,
            "local_application_group",
            {"name": self._name("grp"), "description": "before"},
        )
        app = self._create(
            created,
            "local_application",
            {
                "name": self._name("la"),
                "executable_name": f"fmcpit{int(time.time())}.exe",
                "group_ids": [group["id"]],
                "apply_rules_for_children_processes": True,
            },
        )

        self._update("local_application", {"id": app["id"], "enable_rename_detection": True})
        app_after = self._get("local_application", app["id"])
        assert app_after["enable_rename_detection"] is True
        assert app_after["group_ids"] == [group["id"]], app_after
        assert app_after["apply_rules_for_children_processes"] is True, app_after
        assert app_after["executable_name"] == app["executable_name"]

        self._update("local_application_group", {"id": group["id"], "description": "after"})
        group_after = self._get("local_application_group", group["id"])
        assert group_after["description"] == "after"
        assert group_after["name"] == group["name"]
        assert group_after["local_application_ids"] == [app["id"]], group_after

    def test_enterprise_account_partial_update_keeps_other_fields(self, created):
        """A partial enterprise account update leaves its domains and application group intact."""
        domains = [f"{self._name('ea')}.example.com"]
        account = self._create(
            created,
            "enterprise_account",
            {
                "name": self._name("ea"),
                "application_group_id": "microsoft",
                "plugin_config_id": "",
                "domains": domains,
            },
        )
        new_name = f"{account['name']}-renamed"
        self._update("enterprise_account", {"id": account["id"], "name": new_name})

        after = self._get("enterprise_account", account["id"])
        assert after["name"] == new_name
        assert after["domains"] == domains, after
        assert after["application_group_id"] == "microsoft", after

    def test_classification_partial_update_keeps_rules(self, created):
        """Updating only the protection mode keeps the classification's rules and patterns."""
        cp = self._create(
            created,
            "content_pattern",
            {
                "name": self._name("cp"),
                "category": "Custom",
                "regexes": ["FMCPIT[0-9]{6}"],
                "min_match_threshold": 1,
                "region": "ALL",
            },
        )
        cls = self._create(
            created,
            "classification",
            {
                "name": self._name("cls"),
                "classification_properties": {
                    "content_patterns": [cp["id"]],
                    "content_patterns_operator": "or",
                    "protection_mode": "monitor",
                    "rules": [
                        {
                            "user_scope": "all",
                            "detection_severity": "low",
                            "response_action": "allow",
                            "trigger_detection": False,
                            "notify_end_user": False,
                            "enable_usb_devices": True,
                            "enable_printer_egress": False,
                            "enable_web_locations": False,
                            "web_locations_scope": "all",
                            "enable_local_application_groups": False,
                        }
                    ],
                },
            },
        )
        self._update(
            "classification",
            {"id": cls["id"], "classification_properties": {"protection_mode": "simulate"}},
        )

        props = self._get("classification", cls["id"])["classification_properties"]
        assert props["protection_mode"] == "simulate"
        assert props["content_patterns"] == [cp["id"]]
        assert len(props["rules"]) == 1

    def test_policy_partial_update_roundtrip(self, created):
        """A disabled policy with no host groups can be created and partially updated."""
        policy = self._create(
            created,
            "policy",
            {"name": self._name("pol"), "description": "before", "is_enabled": False},
            platform_name="win",
        )
        self._update(
            "policy", {"id": policy["id"], "description": "after"}, platform_name="win"
        )

        after = self._get("policy", policy["id"])
        assert after["description"] == "after"
        assert after["is_enabled"] is False
        assert after["name"] == policy["name"]
