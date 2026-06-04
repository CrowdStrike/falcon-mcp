"""
Tests for the Exclusions module.
"""

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.exclusions import ExclusionsModule
from tests.modules.utils.test_modules import TestModules

MUTATING_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True,
)

# Maps exclusion_type -> (query_op, get_op, create_op, update_op, delete_op).
EXPECTED_OPS = {
    "ioa": (
        "ss_ioa_exclusions_search_v2",
        "ss_ioa_exclusions_get_v2",
        "ss_ioa_exclusions_create_v2",
        "ss_ioa_exclusions_update_v2",
        "ss_ioa_exclusions_delete_v2",
    ),
    "ml": (
        "exclusions_search_v2",
        "exclusions_get_v2",
        "exclusions_create_v2",
        "exclusions_update_v2",
        "exclusions_delete_v2",
    ),
    "sensor_visibility": (
        "querySensorVisibilityExclusionsV1",
        "getSensorVisibilityExclusionsV1",
        "createSVExclusionsV1",
        "updateSensorVisibilityExclusionsV1",
        "deleteSensorVisibilityExclusionsV1",
    ),
    "certificate": (
        "cb_exclusions_query_v1",
        "cb_exclusions_get_v1",
        "cb_exclusions_create_v1",
        "cb_exclusions_update_v1",
        "cb_exclusions_delete_v1",
    ),
}


class TestExclusionsModule(TestModules):
    """Test cases for the Exclusions module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ExclusionsModule)

    # ---- Registration ----------------------------------------------------------

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_exclusions",
            "falcon_create_exclusion",
            "falcon_update_exclusion",
            "falcon_delete_exclusions",
            "falcon_search_certificates",
            "falcon_get_certificate_details",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_exclusions_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Mutating tools must carry the correct annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_exclusions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_certificates", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_get_certificate_details", READ_ONLY_ANNOTATIONS
        )
        self.assert_tool_annotations("falcon_create_exclusion", MUTATING_ANNOTATIONS)
        self.assert_tool_annotations("falcon_update_exclusion", MUTATING_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_delete_exclusions", DESTRUCTIVE_ANNOTATIONS
        )

    # ---- Search ----------------------------------------------------------------

    def _search_responses(self):
        query_response = {
            "status_code": 200,
            "body": {"resources": ["excl-1", "excl-2"]},
        }
        get_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "excl-1", "value": "/tmp/a"},
                    {"id": "excl-2", "value": "/tmp/b"},
                ]
            },
        }
        return query_response, get_response

    def test_search_exclusions_per_type(self):
        """Each type queries then gets, using the correct operation names."""
        for excl_type, ops in EXPECTED_OPS.items():
            with self.subTest(exclusion_type=excl_type):
                self.mock_client.command.reset_mock()
                self.mock_client.command.side_effect = self._search_responses()

                result = self.module.search_exclusions(
                    exclusion_type=excl_type,
                    filter="value:'/tmp/*'",
                    limit=50,
                    sort=None,
                    offset=0,
                )

                self.assertEqual(self.mock_client.command.call_count, 2)
                first_call = self.mock_client.command.call_args_list[0]
                second_call = self.mock_client.command.call_args_list[1]
                self.assertEqual(first_call[0][0], ops[0])
                self.assertEqual(second_call[0][0], ops[1])
                self.assertEqual(len(result), 2)
                self.assertEqual(result[0]["id"], "excl-1")

    def test_search_invalid_type(self):
        """An invalid exclusion_type returns an error response, not a crash."""
        result = self.module.search_exclusions(
            exclusion_type="bogus",
            filter=None,
            limit=10,
            sort=None,
            offset=0,
        )
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        # No API call should have happened.
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_search_empty_returns_fql_guide(self):
        """Empty query results include the FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        result = self.module.search_exclusions(
            exclusion_type="ml",
            filter="value:'nothing'",
            limit=10,
            sort=None,
            offset=0,
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_search_error_returns_fql_guide(self):
        """Query errors include the FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        result = self.module.search_exclusions(
            exclusion_type="ioa",
            filter="bad filter",
            limit=10,
            sort=None,
            offset=0,
        )
        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)
        self.assertIn("error", result["results"][0])

    def test_sort_normalization(self):
        """ioa/ml/sv append .desc when no direction is given; certificate passes through."""
        # ML: bare 'created_on' -> 'created_on.desc'
        self.mock_client.command.side_effect = self._search_responses()
        self.module.search_exclusions(
            exclusion_type="ml",
            filter=None,
            limit=10,
            sort="created_on",
            offset=0,
        )
        ml_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(ml_call[1]["parameters"]["sort"], "created_on.desc")

        # Certificate: bare 'created_on' stays unchanged.
        self.mock_client.command.reset_mock()
        self.mock_client.command.side_effect = self._search_responses()
        self.module.search_exclusions(
            exclusion_type="certificate",
            filter=None,
            limit=10,
            sort="created_on",
            offset=0,
        )
        cert_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(cert_call[1]["parameters"]["sort"], "created_on")

    def test_sort_existing_direction_preserved(self):
        """An explicit direction suffix is not doubled."""
        self.mock_client.command.side_effect = self._search_responses()
        self.module.search_exclusions(
            exclusion_type="ioa",
            filter=None,
            limit=10,
            sort="created_on.asc",
            offset=0,
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[1]["parameters"]["sort"], "created_on.asc")

    def test_limit_clamp(self):
        """Certificate clamps limit to 100; other types keep their value."""
        self.mock_client.command.side_effect = self._search_responses()
        self.module.search_exclusions(
            exclusion_type="certificate",
            filter=None,
            limit=200,
            sort=None,
            offset=0,
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[1]["parameters"]["limit"], 100)

    # ---- Create ----------------------------------------------------------------

    def _create_response(self, entity):
        return {"status_code": 201, "body": {"resources": [entity]}}

    def _create_kwargs(self, **overrides):
        """Full create kwargs with everything None unless overridden."""
        base = dict(
            name=None,
            value=None,
            pattern_id=None,
            ifn_regex=None,
            cl_regex=None,
            parent_ifn_regex=None,
            parent_cl_regex=None,
            grandparent_ifn_regex=None,
            grandparent_cl_regex=None,
            certificate=None,
            status=None,
            excluded_from=None,
            is_descendant_process=None,
            host_groups=None,
            applied_globally=None,
            description=None,
            comment=None,
        )
        base.update(overrides)
        return base

    def test_create_ioa_wrapped_body_and_host_groups(self):
        """IOA create wraps the body and maps host_groups to the host_groups key."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "ioa-1", "name": "n"}
        )
        result = self.module.create_exclusion(
            exclusion_type="ioa",
            **self._create_kwargs(
                name="my-ioa",
                pattern_id="569",
                ifn_regex="/tmp/x",
                cl_regex="/tmp/x",
                host_groups=["grp-1"],
            ),
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "ss_ioa_exclusions_create_v2")
        body = call[1]["body"]
        self.assertIn("exclusions", body)
        excl = body["exclusions"][0]
        self.assertEqual(excl["host_groups"], ["grp-1"])
        self.assertEqual(excl["pattern_id"], "569")
        self.assertEqual(result[0]["id"], "ioa-1")

    def test_create_ml_wrapped_body_and_groups(self):
        """ML create wraps the body and maps host_groups to the groups key."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "ml-1", "value": "/tmp/a"}
        )
        self.module.create_exclusion(
            exclusion_type="ml",
            **self._create_kwargs(
                value="/tmp/a",
                excluded_from=["blocking"],
                host_groups=["grp-1"],
            ),
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "exclusions_create_v2")
        body = call[1]["body"]
        self.assertIn("exclusions", body)
        excl = body["exclusions"][0]
        self.assertEqual(excl["groups"], ["grp-1"])
        self.assertNotIn("host_groups", excl)

    def test_create_sv_flat_body_and_groups(self):
        """Sensor visibility create uses a flat body with the groups key."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "sv-1", "value": "/tmp/a"}
        )
        self.module.create_exclusion(
            exclusion_type="sensor_visibility",
            **self._create_kwargs(value="/tmp/a", host_groups=["grp-1"]),
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "createSVExclusionsV1")
        body = call[1]["body"]
        self.assertNotIn("exclusions", body)
        self.assertEqual(body["value"], "/tmp/a")
        self.assertEqual(body["groups"], ["grp-1"])

    def test_create_certificate_wrapped_body_and_host_groups(self):
        """Certificate create wraps the body and maps host_groups to the host_groups key."""
        cert = {"issuer": "CN=x", "thumbprint": "abc"}
        self.mock_client.command.return_value = self._create_response(
            {"id": "cert-1", "name": "n"}
        )
        self.module.create_exclusion(
            exclusion_type="certificate",
            **self._create_kwargs(
                name="trusted",
                certificate=cert,
                status="enabled",
                host_groups=["grp-1"],
            ),
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "cb_exclusions_create_v1")
        body = call[1]["body"]
        self.assertIn("exclusions", body)
        excl = body["exclusions"][0]
        self.assertEqual(excl["host_groups"], ["grp-1"])
        self.assertEqual(excl["status"], "enabled")
        self.assertEqual(excl["certificate"], cert)

    # ---- Create validate-and-guide negatives -----------------------------------

    def test_create_invalid_type(self):
        """Invalid type returns an error and makes no API call."""
        result = self.module.create_exclusion(
            exclusion_type="bogus", **self._create_kwargs(value="x")
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_create_ml_missing_value(self):
        """ML create without value returns a guiding error, no API call."""
        result = self.module.create_exclusion(
            exclusion_type="ml", **self._create_kwargs()
        )
        self.assertIn("error", result[0])
        self.assertIn("value", result[0]["error"])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_create_ioa_missing_pattern_id(self):
        """IOA create without pattern_id returns a guiding error, no API call."""
        result = self.module.create_exclusion(
            exclusion_type="ioa",
            **self._create_kwargs(name="n", ifn_regex="/x", cl_regex="/x"),
        )
        self.assertIn("error", result[0])
        self.assertIn("pattern_id", result[0]["error"])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_create_ioa_both_regex_wildcard(self):
        """IOA create with ifn_regex='.*' and cl_regex='.*' is rejected."""
        result = self.module.create_exclusion(
            exclusion_type="ioa",
            **self._create_kwargs(
                name="n", pattern_id="1", ifn_regex=".*", cl_regex=".*"
            ),
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_create_sv_empty_host_groups(self):
        """Sensor visibility create with no host_groups returns a guiding error."""
        result = self.module.create_exclusion(
            exclusion_type="sensor_visibility",
            **self._create_kwargs(value="/tmp/a"),
        )
        self.assertIn("error", result[0])
        self.assertIn("host_groups", result[0]["error"])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_create_certificate_bad_status(self):
        """Certificate create with an invalid status is rejected."""
        result = self.module.create_exclusion(
            exclusion_type="certificate",
            **self._create_kwargs(
                name="n", certificate={"thumbprint": "x"}, status="bad"
            ),
        )
        self.assertIn("error", result[0])
        self.assertIn("status", result[0]["error"])
        self.assertEqual(self.mock_client.command.call_count, 0)

    # ---- Update ----------------------------------------------------------------

    def test_update_missing_id(self):
        """Update without an id returns a guiding error."""
        result = self.module.update_exclusion(
            exclusion_type="ml", id=None, **self._create_kwargs(value="/tmp/a")
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_update_invalid_type(self):
        """Update with an invalid type returns an error."""
        result = self.module.update_exclusion(
            exclusion_type="bogus", id="x", **self._create_kwargs(value="/tmp/a")
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_update_flat_type_id_top_level(self):
        """Sensor visibility update places id at the top level of the flat body."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "sv-1", "value": "/tmp/a"}
        )
        self.module.update_exclusion(
            exclusion_type="sensor_visibility",
            id="sv-1",
            **self._create_kwargs(value="/tmp/a", host_groups=["grp-1"]),
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "updateSensorVisibilityExclusionsV1")
        body = call[1]["body"]
        self.assertEqual(body["id"], "sv-1")
        self.assertNotIn("exclusions", body)

    def test_update_wrapped_type_id_inside_object(self):
        """IOA/ML/certificate updates put id inside the exclusions object."""
        self.mock_client.command.return_value = self._create_response(
            {"id": "ioa-1", "name": "n"}
        )
        self.module.update_exclusion(
            exclusion_type="ioa",
            id="ioa-1",
            **self._create_kwargs(
                name="n",
                pattern_id="569",
                ifn_regex="/x",
                cl_regex="/x",
            ),
        )
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "ss_ioa_exclusions_update_v2")
        body = call[1]["body"]
        self.assertEqual(body["exclusions"][0]["id"], "ioa-1")

    # ---- Delete ----------------------------------------------------------------

    def test_delete_per_type(self):
        """Delete uses the right op name and passes ids as query params."""
        for excl_type, ops in EXPECTED_OPS.items():
            with self.subTest(exclusion_type=excl_type):
                self.mock_client.command.reset_mock()
                self.mock_client.command.return_value = {
                    "status_code": 200,
                    "body": {"resources": [{"id": "x"}]},
                }
                self.module.delete_exclusions(
                    exclusion_type=excl_type, ids=["x", "y"], comment="cleanup"
                )
                call = self.mock_client.command.call_args_list[0]
                self.assertEqual(call[0][0], ops[4])
                self.assertEqual(call[1]["parameters"]["ids"], ["x", "y"])

    def test_delete_empty_ids(self):
        """Delete with no ids returns a guiding error."""
        result = self.module.delete_exclusions(
            exclusion_type="ml", ids=None, comment=None
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_delete_invalid_type(self):
        """Delete with an invalid type returns an error."""
        result = self.module.delete_exclusions(
            exclusion_type="bogus", ids=["x"], comment=None
        )
        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    # ---- Certificate discovery -------------------------------------------------

    def test_search_certificates(self):
        """search_certificates queries the certificate exclusion operations."""
        self.mock_client.command.side_effect = self._search_responses()
        result = self.module.search_certificates(
            filter=None, limit=50, sort=None, offset=0
        )
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(first_call[0][0], "cb_exclusions_query_v1")
        self.assertEqual(second_call[0][0], "cb_exclusions_get_v1")
        self.assertEqual(len(result), 2)

    def test_get_certificate_details(self):
        """get_certificate_details calls certificates_get_v1 with the sha256."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "abc", "certificate": {}}]},
        }
        result = self.module.get_certificate_details(sha256="abc123")
        call = self.mock_client.command.call_args_list[0]
        self.assertEqual(call[0][0], "certificates_get_v1")
        self.assertEqual(call[1]["parameters"]["ids"], ["abc123"])
        self.assertEqual(result[0]["id"], "abc")
