"""
Intel module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon intelligence data.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP

from ..common.logging import get_logger
from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters, extract_first_resource
from .base import BaseModule


class IntelModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon intelligence data."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register Query tools
        self._add_tool(
            server,
            self.query_intel_actor_entities,
            name="intel_query_intel_actor_entities",
            description="Search for actors that match provided FQL filters."
        )

        self._add_tool(
            server,
            self.query_intel_indicator_entities,
            name="intel_query_intel_indicator_entities",
            description="Search for indicators that match provided FQL filters."
        )

        self._add_tool(
            server,
            self.query_intel_report_entities,
            name="intel_query_intel_report_entities",
            description="Search for reports that match provided FQL filters."
        )

        self._add_tool(
            server,
            self.query_intel_rule_entities,
            name="intel_query_intel_rule_entities",
            description="Search for rules that match provided FQL filters."
        )

        # Register Get tools
        self._add_tool(
            server,
            self.get_intel_actor_entities,
            name="intel_get_intel_actor_entities",
            description="Get detailed information about actors by providing actor IDs."
        )

        self._add_tool(
            server,
            self.get_intel_indicator_entities,
            name="intel_get_intel_indicator_entities",
            description="Get detailed information about indicators by providing indicator IDs."
        )

        self._add_tool(
            server,
            self.get_intel_report_pdf,
            name="intel_get_intel_report_pdf",
            description="Get a PDF report by providing a report ID."
        )

        self._add_tool(
            server,
            self.get_intel_report_entities,
            name="intel_get_intel_report_entities",
            description="Get detailed information about reports by providing report IDs."
        )

        self._add_tool(
            server,
            self.get_intel_rule_entities,
            name="intel_get_intel_rule_entities",
            description="Get detailed information about rules by providing rule IDs."
        )

        self._add_tool(
            server,
            self.get_intel_rule_file,
            name="intel_get_intel_rule_file",
            description="Download the rule file for the specified rule ID."
        )

        self._add_tool(
            server,
            self.get_latest_intel_indicator_timestamp,
            name="intel_get_latest_intel_indicator_timestamp",
            description="Get the timestamp of the latest indicator."
        )

        self._add_tool(
            server,
            self.get_mitre_report,
            name="intel_get_mitre_report",
            description="Get the MITRE ATT&CK tactics and techniques for a specific actor."
        )

        self._add_tool(
            server,
            self.get_rule_details,
            name="intel_get_rule_details",
            description="Get detailed information about a specific rule."
        )

        self._add_tool(
            server,
            self.get_rules_details,
            name="intel_get_rules_details",
            description="Get detailed information about multiple rules."
        )

        self._add_tool(
            server,
            self.get_rule_preview,
            name="intel_get_rule_preview",
            description="Get a preview of a rule by providing a rule ID."
        )

        self._add_tool(
            server,
            self.get_vulnerabilities,
            name="intel_get_vulnerabilities",
            description="Get vulnerabilities by providing vulnerability IDs."
        )

    def query_intel_actor_entities(
        self, filter: Optional[str] = None, limit: int = 100, offset: int = 0, sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for actors that match provided FQL filters.

        Args:
            filter: The filter expression that should be used to limit the results. FQL syntax.
            limit: The maximum number of records to return in this response. [Integer, 1-500]. Use with the offset parameter to manage pagination of results.
            offset: The offset to start retrieving records from. Integer. Use with the limit parameter to manage pagination of results.
            sort: The property to sort by. FQL syntax. Ex: created_date.desc

        Returns:
            Tool returns CrowdStrike Intel actors.
        """
        return self._base_query(
            operation="QueryIntelActorEntities",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def query_intel_indicator_entities(
        self, filter: Optional[str] = None, limit: int = 100, offset: int = 0, sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for indicators that match provided FQL filters.

        Args:
            filter: The filter expression that should be used to limit the results. FQL syntax.
            limit: The maximum number of records to return in this response. [Integer, 1-500]. Use with the offset parameter to manage pagination of results.
            offset: The offset to start retrieving records from. Integer. Use with the limit parameter to manage pagination of results.
            sort: The property to sort by. FQL syntax. Ex: created_date.desc

        Returns:
            Tool returns CrowdStrike Intel indicators.
        """
        return self._base_query(
            operation="QueryIntelIndicatorEntities",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def query_intel_report_entities(
        self, filter: Optional[str] = None, limit: int = 100, offset: int = 0, sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for reports that match provided FQL filters.

        Args:
            filter: The filter expression that should be used to limit the results. FQL syntax.
            limit: The maximum number of records to return in this response. [Integer, 1-500]. Use with the offset parameter to manage pagination of results.
            offset: The offset to start retrieving records from. Integer. Use with the limit parameter to manage pagination of results.
            sort: The property to sort by. FQL syntax. Ex: created_date.desc

        Returns:
            Tool returns CrowdStrike Intel reports.
        """
        return self._base_query(
            operation="QueryIntelReportEntities",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def query_intel_rule_entities(
        self, filter: Optional[str] = None, limit: int = 100, offset: int = 0, sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for rules that match provided FQL filters.

        Args:
            filter: The filter expression that should be used to limit the results. FQL syntax.
            limit: The maximum number of records to return in this response. [Integer, 1-500]. Use with the offset parameter to manage pagination of results.
            offset: The offset to start retrieving records from. Integer. Use with the limit parameter to manage pagination of results.
            sort: The property to sort by. FQL syntax. Ex: created_date.desc

        Returns:
            Tool returns CrowdStrike Intel rules.
        """
        return self._base_query(
            operation="QueryIntelRuleEntities",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def get_intel_actor_entities(self, ids: List[str]) -> Dict[str, Any]:
        """Get detailed information about actors by providing actor IDs.

        Args:
            ids: Actor ID(s) to retrieve.

        Returns:
            Tool returns CrowdStrike Intel actors.
        """
        return self._base_get(
            operation="GetIntelActorEntities",
            ids=ids,
        )

    def get_intel_indicator_entities(self, ids: List[str]) -> Dict[str, Any]:
        """Get detailed information about indicators by providing indicator IDs.

        Args:
            ids: Indicator ID(s) to retrieve.

        Returns:
            Tool returns CrowdStrike Intel indicators.
        """
        return self._base_get(
            operation="GetIntelIndicatorEntities",
            ids=ids,
        )

    def get_intel_report_pdf(self, id: str) -> Dict[str, Any]:
        """Get a PDF report by providing a report ID.

        Args:
            id: Report ID to retrieve the PDF for.

        Returns:
            Tool returns the PDF report.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "id": id
        })

        # Define the operation name (used for error handling)
        operation = "GetIntelReportPDF"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to retrieve PDF report",
            default_result={}
        )

    def get_intel_report_entities(self, ids: List[str]) -> Dict[str, Any]:
        """Get detailed information about reports by providing report IDs.

        Args:
            ids: Report ID(s) to retrieve.

        Returns:
            Tool returns CrowdStrike Intel reports.
        """
        return self._base_get(
            operation="GetIntelReportEntities",
            ids=ids,
        )

    def get_intel_rule_entities(self, ids: List[str]) -> Dict[str, Any]:
        """Get detailed information about rules by providing rule IDs.

        Args:
            ids: Rule ID(s) to retrieve.

        Returns:
            Tool returns CrowdStrike Intel rules.
        """
        return self._base_get(
            operation="GetIntelRuleEntities",
            ids=ids,
        )

    def get_intel_rule_file(self, id: str, format: Optional[str] = None) -> Dict[str, Any]:
        """Download the rule file for the specified rule ID.

        Args:
            id: Rule ID to retrieve the file for.
            format: The format of the rule file. If not provided, the default format is used.

        Returns:
            Tool returns the rule file.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "id": id,
            "format": format
        })

        # Define the operation name (used for error handling)
        operation = "GetIntelRuleFile"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to retrieve rule file",
            default_result={}
        )

    def get_latest_intel_indicator_timestamp(self) -> Dict[str, Any]:
        """Get the timestamp of the latest indicator.

        Returns:
            Tool returns the timestamp of the latest indicator.
        """
        # Define the operation name (used for error handling)
        operation = "GetLatestIntelIndicatorTimestamp"

        # Make the API request
        response = self.client.command(operation)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to retrieve latest indicator timestamp",
            default_result={}
        )

    def get_mitre_report(self, id: str) -> Dict[str, Any]:
        """Get the MITRE ATT&CK tactics and techniques for a specific actor.

        Args:
            id: Actor ID to retrieve the MITRE report for.

        Returns:
            Tool returns the MITRE ATT&CK tactics and techniques.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "id": id
        })

        # Define the operation name (used for error handling)
        operation = "GetMitreReport"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to retrieve MITRE report",
            default_result={}
        )

    def get_rule_details(self, ids: List[str]) -> Dict[str, Any]:
        """Get detailed information about a specific rule.

        Args:
            ids: Rule ID(s) to retrieve details for.

        Returns:
            Tool returns detailed information about the rule.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "ids": ids
        })

        # Define the operation name (used for error handling)
        operation = "GetRuleDetails"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to retrieve rule details",
            default_result={}
        )

    def get_rules_details(self, ids: List[str]) -> Dict[str, Any]:
        """Get detailed information about multiple rules.

        Args:
            ids: Rule ID(s) to retrieve details for.

        Returns:
            Tool returns detailed information about the rules.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "ids": ids
        })

        # Define the operation name (used for error handling)
        operation = "GetRulesDetails"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to retrieve rules details",
            default_result={}
        )

    def get_rule_preview(self, id: str, format: Optional[str] = None) -> Dict[str, Any]:
        """Get a preview of a rule by providing a rule ID.

        Args:
            id: Rule ID to retrieve the preview for.
            format: The format of the rule preview. If not provided, the default format is used.

        Returns:
            Tool returns the rule preview.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "id": id,
            "format": format
        })

        # Define the operation name (used for error handling)
        operation = "GetRulePreview"

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to retrieve rule preview",
            default_result={}
        )

    def get_vulnerabilities(self, ids: List[str]) -> Dict[str, Any]:
        """Get vulnerabilities by providing vulnerability IDs.

        Args:
            ids: Vulnerability ID(s) to retrieve.

        Returns:
            Tool returns CrowdStrike vulnerabilities.
        """
        return self._base_get(
            operation="GetVulnerabilities",
            ids=ids,
        )

    def _base_query(
        self, operation: str, filter: Optional[str] = None, limit: int = 100, offset: int = 0, sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Base method for query operations.

        Args:
            operation: The API operation to perform.
            filter: The filter expression that should be used to limit the results. FQL syntax.
            limit: The maximum number of records to return in this response.
            offset: The offset to start retrieving records from.
            sort: The property to sort by.

        Returns:
            Dict[str, Any]: The API response.
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        })

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result={}
        )

    def _base_get(
        self, operation: str, ids: List[str],
    ) -> Dict[str, Any]:
        """Base method for get operations.

        Args:
            operation: The API operation to perform.
            ids: ID(s) to retrieve.

        Returns:
            Dict[str, Any]: The API response.
        """
        body = prepare_api_parameters({
            "ids": ids
        })

        # Make the API request
        response = self.client.command(operation, body=body)

        # Handle the response
        return handle_api_response(
            response,
            operation=operation,
            error_message="Failed to perform operation",
            default_result={}
        )
