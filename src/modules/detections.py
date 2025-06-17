# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Detections module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon detections.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP
from pydantic import Field

from ..common.logging import get_logger
from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters
from .base import BaseModule

logger = get_logger(__name__)


class DetectionsModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon detections."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server,
            self.search_detections,
            name="search_detections"
        )

        self._add_tool(
            server,
            self.get_detection_details,
            name="get_detection_details"
        )

    def search_detections(
        self,
        filter: Optional[str] = Field(default=None, description="Filter detections using a query in Falcon Query Language (FQL) An asterisk wildcard * includes all results.", examples={"behaviors.sha256:'87b8a76d9c657cb3954936b8afa58652c2a01b2f7d26345b9aff0c831c5cead3'", "status:'New'"}),
        limit: Optional[int] = Field(default=100, ge=1, le=9999, description="The maximum number of detections to return in this response (default: 100; max: 9999). Use with the offset parameter to manage pagination of results."),
        offset: Optional[int] = Field(default=0, ge=0, description="The first detection to return, where 0 is the latest detection. Use with the limit parameter to manage pagination of results."),
        q: Optional[str] = Field(default=None, description="Search all detection metadata for the provided string."),
        sort: Optional[str] = Field(default=None, description="""Sort detections using these options:

    first_behavior: Timestamp of the first behavior associated with this detection last_behavior: Timestamp of the last behavior associated with this detection
    max_severity: Highest severity of the behaviors associated with this detection
    max_confidence: Highest confidence of the behaviors associated with this detection
    adversary_id: ID of the adversary associated with this detection, if any
    devices.hostname: Hostname of the host where this detection was detected
    Sort either asc (ascending) or desc (descending).

    For example: last_behavior|asc""", examples={"last_behavior|asc"}),
    ) -> List[Dict[str, Any]]:
        """Search for detections in your CrowdStrike environment.

        Args:
            filter: Filter detections using a query in Falcon Query Language (FQL) An asterisk wildcard * includes all results.
            limit: The maximum number of detections to return in this response (default: 100; max: 9999). Use with the offset parameter to manage pagination of results.
            offset: The first detection to return, where 0 is the latest detection. Use with the limit parameter to manage pagination of results.
            q: Search all detection metadata for the provided string.
            sort: Sort detections using these options:
                first_behavior: Timestamp of the first behavior associated with this detection last_behavior: Timestamp of the last behavior associated with this detection
                max_severity: Highest severity of the behaviors associated with this detection
                max_confidence: Highest confidence of the behaviors associated with this detection
                adversary_id: ID of the adversary associated with this detection, if any
                devices.hostname: Hostname of the host where this detection was detected
                Sort either asc (ascending) or desc (descending).

                For example: last_behavior|asc

        Available FQL Filters:
            adversary_ids
            assigned_to_name
            cid
            date_updated
            detection_id
            first_behavior
            last_behavior
            max_confidence
            max_severity
            max_severity_displayname
            seconds_to_resolved
            seconds_to_triaged
            status
            behaviors
                alleged_filetype
                behavior_id
                cmdline
                confidence
                contral_graph_id
                device_id
                filename
                ioc_source
                ioc_type
                ioc_value
                md5
                objective
                parent_details.parent_cmdline
                parent_details.parent_md5
                parent_details.parent_process_graph_id
                parent_details.parent_process_id
                parent_details.parent_sha256
                pattern_disposition
                scenario
                severity
                sha256
                tactic
                technique
                timestamp
                triggering_process_graph_id
                triggering_process_id
                user_id
                user_name
            device
                agent_load_flags
                agent_local_time
                agent_version
                bios_manufacturer
                bios_version
                cid	machine_domain
                config_id_base
                config_id_build
                config_id_platform
                cpu_signature
                device_id
                external_ip
                first_seen
                hostname
                last_seen
                local_ip
                mac_address
                major_version
                minor_version
                modified_timestamp
                os_version
                ou
                platform_id
                platform_name
                product_type
                product_type_desc
                reduced_functionality_mode
                release_group
                serial_number
                site_name
                status
                system_manufacturer
                system_product_name
            hostinfo.domain
            hostinfo.active_directory_dn_display
            quarantined_files.id
            quarantined_files.sha256
            quarantined_files.paths
            quarantined_files.state

        Returns:
            List of detection details
        """
        # Prepare parameters
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "q": q,
            "sort": sort,
        })

        # Define the operation name
        operation = "QueryDetects"

        logger.debug("Searching detections with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get detection IDs
        detection_ids = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search detections",
            default_result=[]
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if isinstance(detection_ids, dict) and "error" in detection_ids:
            return [detection_ids]

        # If we have detection IDs, get the details for each one
        if detection_ids:
            details_operation = "GetDetectSummaries"
            details_response = self.client.command(
                details_operation,
                body={"ids": detection_ids}
            )

            # Use handle_api_response for the details response
            details = handle_api_response(
                details_response,
                operation=details_operation,
                error_message="Failed to get detection details",
                default_result=[]
            )

            # If handle_api_response returns an error dict instead of a list,
            # it means there was an error, so we return it wrapped in a list
            if isinstance(details, dict) and "error" in details:
                return [details]

            return details

        return []

    def get_detection_details(
        self,
        ids: List[str] = Field(description="ID(s) of the detections to retrieve. View key attributes of detections, including the associated host, disposition, objective/tactic/technique, adversary, and more. Specify one or more detection IDs (max 1000 per request). Find detection IDs with the QueryDetects operation, the Falcon console, or the Streaming API."),
    ) -> Dict[str, Any]:
        """View information about detections. Gets detailed information about a specific detection.

        Args:
            ids: ID(s) of the detections to retrieve. View key attributes of detections, including the associated host, disposition, objective/tactic/technique, adversary, and more. Specify one or more detection IDs (max 1000 per request). Find detection IDs with the QueryDetects operation, the Falcon console, or the Streaming API.

        Returns:
            Detection details
        """
        # Define the operation name
        operation = "GetDetectSummaries"

        logger.debug("Getting detection details for ID: %s", ids)

        return self._base_get_by_ids(
            operation=operation,
            ids=ids,
        )
