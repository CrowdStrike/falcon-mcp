"""Integration tests for the IDP (Identity Protection) module."""

import pytest

from falcon_mcp.modules.idp import IdpModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestIdpIntegration(BaseIntegrationTest):
    """Integration tests for IDP module with real API calls.

    Validates:
    - Correct FalconPy operation name (api_preempt_proxy_post_graphql)
    - GraphQL query structure and entity resolution
    - Investigation types return expected data structures
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the IDP module with a real client."""
        self.module = IdpModule(falcon_client)

    def test_investigate_entity_with_entity_names(self):
        """Test investigate_entity with entity names.

        Validates the api_preempt_proxy_post_graphql operation for entity resolution.
        """
        result = self.call_method(
            self.module.investigate_entity,
            entity_names=["Administrator"],
            investigation_types=["entity_details"],
            limit=5,
        )

        # Result should be a dict with investigation_summary
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "investigation_summary" in result, "Missing investigation_summary in response"

        summary = result["investigation_summary"]
        assert "status" in summary, "Missing status in investigation_summary"

        # If entities were found, verify structure
        if summary.get("status") == "completed":
            assert "entity_details" in result or "entities" in result, "Missing entity data in successful response"

    def test_investigate_entity_with_email_addresses(self):
        """Test investigate_entity with email addresses.

        Tests USER entity type resolution via secondaryDisplayNames filter.
        """
        result = self.call_method(
            self.module.investigate_entity,
            email_addresses=["admin@example.com"],
            investigation_types=["entity_details"],
            limit=5,
        )

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "investigation_summary" in result, "Missing investigation_summary in response"

    def test_investigate_entity_with_domain_names(self):
        """Test investigate_entity with domain names.

        Tests entity resolution with domain context.
        """
        result = self.call_method(
            self.module.investigate_entity,
            entity_names=["Administrator"],
            domain_names=["CORP.LOCAL"],
            investigation_types=["entity_details"],
            limit=5,
        )

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "investigation_summary" in result, "Missing investigation_summary in response"

    def test_investigate_entity_timeline_analysis(self):
        """Test investigate_entity with timeline_analysis investigation type.

        Validates GraphQL timeline query structure.
        """
        # First, find an entity to investigate
        result = self.call_method(
            self.module.investigate_entity,
            entity_names=["Administrator"],
            investigation_types=["entity_details"],
            limit=1,
        )

        if result.get("investigation_summary", {}).get("status") != "completed":
            self.skip_with_warning(
                "No entities found for timeline analysis test",
                context="test_investigate_entity_timeline_analysis",
            )

        entity_ids = result.get("investigation_summary", {}).get("resolved_entity_ids", [])
        if not entity_ids:
            self.skip_with_warning(
                "No entity IDs resolved for timeline analysis test",
                context="test_investigate_entity_timeline_analysis",
            )

        # Now test timeline analysis
        timeline_result = self.call_method(
            self.module.investigate_entity,
            entity_ids=entity_ids[:1],
            investigation_types=["timeline_analysis"],
            limit=10,
        )

        assert isinstance(timeline_result, dict), f"Expected dict, got {type(timeline_result)}"
        assert "investigation_summary" in timeline_result, "Missing investigation_summary"

        if timeline_result.get("investigation_summary", {}).get("status") == "completed":
            assert "timeline_analysis" in timeline_result, "Missing timeline_analysis in successful response"

    def test_investigate_entity_relationship_analysis(self):
        """Test investigate_entity with relationship_analysis investigation type.

        Validates GraphQL relationship/association query structure.
        """
        # First, find an entity to investigate
        result = self.call_method(
            self.module.investigate_entity,
            entity_names=["Administrator"],
            investigation_types=["entity_details"],
            limit=1,
        )

        if result.get("investigation_summary", {}).get("status") != "completed":
            self.skip_with_warning(
                "No entities found for relationship analysis test",
                context="test_investigate_entity_relationship_analysis",
            )

        entity_ids = result.get("investigation_summary", {}).get("resolved_entity_ids", [])
        if not entity_ids:
            self.skip_with_warning(
                "No entity IDs resolved for relationship analysis test",
                context="test_investigate_entity_relationship_analysis",
            )

        # Now test relationship analysis
        relationship_result = self.call_method(
            self.module.investigate_entity,
            entity_ids=entity_ids[:1],
            investigation_types=["relationship_analysis"],
            relationship_depth=2,
            limit=10,
        )

        assert isinstance(relationship_result, dict), f"Expected dict, got {type(relationship_result)}"
        assert "investigation_summary" in relationship_result, "Missing investigation_summary"

        if relationship_result.get("investigation_summary", {}).get("status") == "completed":
            assert "relationship_analysis" in relationship_result, "Missing relationship_analysis in successful response"

    def test_investigate_entity_risk_assessment(self):
        """Test investigate_entity with risk_assessment investigation type.

        Validates GraphQL risk score and factors query structure.
        """
        # First, find an entity to investigate
        result = self.call_method(
            self.module.investigate_entity,
            entity_names=["Administrator"],
            investigation_types=["entity_details"],
            limit=1,
        )

        if result.get("investigation_summary", {}).get("status") != "completed":
            self.skip_with_warning(
                "No entities found for risk assessment test",
                context="test_investigate_entity_risk_assessment",
            )

        entity_ids = result.get("investigation_summary", {}).get("resolved_entity_ids", [])
        if not entity_ids:
            self.skip_with_warning(
                "No entity IDs resolved for risk assessment test",
                context="test_investigate_entity_risk_assessment",
            )

        # Now test risk assessment
        risk_result = self.call_method(
            self.module.investigate_entity,
            entity_ids=entity_ids[:1],
            investigation_types=["risk_assessment"],
            limit=10,
        )

        assert isinstance(risk_result, dict), f"Expected dict, got {type(risk_result)}"
        assert "investigation_summary" in risk_result, "Missing investigation_summary"

        if risk_result.get("investigation_summary", {}).get("status") == "completed":
            assert "risk_assessment" in risk_result, "Missing risk_assessment in successful response"

    def test_investigate_entity_multiple_types(self):
        """Test investigate_entity with multiple investigation types."""
        result = self.call_method(
            self.module.investigate_entity,
            entity_names=["Administrator"],
            investigation_types=["entity_details", "risk_assessment"],
            limit=5,
        )

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "investigation_summary" in result, "Missing investigation_summary"

        summary = result["investigation_summary"]
        assert "investigation_types" in summary, "Missing investigation_types in summary"
        assert len(summary["investigation_types"]) == 2, "Expected 2 investigation types"

    def test_investigate_entity_validation_error(self):
        """Test investigate_entity returns error when no identifiers provided."""
        result = self.call_method(
            self.module.investigate_entity,
            investigation_types=["entity_details"],
        )

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "error" in result, "Expected error when no identifiers provided"
        assert "investigation_summary" in result, "Missing investigation_summary in error response"
        assert result["investigation_summary"]["status"] == "failed", "Expected failed status"

    def test_operation_name_is_correct(self):
        """Validate that FalconPy operation name is correct.

        If operation name is wrong, the API call will fail with an error.
        """
        result = self.call_method(
            self.module.investigate_entity,
            entity_names=["Administrator"],
            investigation_types=["entity_details"],
            limit=1,
        )

        # Should not have an error about invalid operation
        if isinstance(result, dict) and "error" in result:
            error_msg = result["error"].lower()
            assert "operation" not in error_msg, f"Operation name error: {result['error']}"
