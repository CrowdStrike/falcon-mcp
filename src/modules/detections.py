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
        filter: Optional[str] = Field(default=None, examples={"behaviors.sha256:'87b8a76d9c657cb3954936b8afa58652c2a01b2f7d26345b9aff0c831c5cead3'", "status:'New'"}),
        limit: Optional[int] = Field(default=100, ge=1, le=9999),
        offset: Optional[int] = Field(default=0, ge=0),
        q: Optional[str] = Field(default=None),
        sort: Optional[str] = Field(default=None, examples={"max_severity.desc", "last_behavior.desc"}),
    ) -> List[Dict[str, Any]]:
        """Search for detections in your CrowdStrike environment.

        Args:
            filter: Filter detections using a query in Falcon Query Language (FQL) An asterisk wildcard * includes all results. You must use FQL and never use JSON.
            limit: The maximum number of detections to return in this response (default: 100; max: 9999). Use with the offset parameter to manage pagination of results.
            offset: The first detection to return, where 0 is the latest detection. Use with the limit parameter to manage pagination of results.
            q: Search all detection metadata for the provided string.
            sort: Sort detections using these options:
                first_behavior: Timestamp of the first behavior associated with this detection
                last_behavior: Timestamp of the last behavior associated with this detection
                max_severity: Highest severity of the behaviors associated with this detection (recommended when filtering by severity)
                max_confidence: Highest confidence of the behaviors associated with this detection
                device.hostname: Hostname of the host where this detection was detected

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'max_severity.desc' or 'max_severity|desc'

                When searching for high severity detections, use 'max_severity.desc' to get the highest severity detections first.
                For chronological ordering, use 'last_behavior.desc' for most recent detections first.

                Examples: 'max_severity.desc', 'last_behavior.desc'

    🎯 FALCON QUERY LANGUAGE (FQL) COMPREHENSIVE GUIDE:
    
    === BASIC SYNTAX ===
    property_name:[operator]'value'
    
    === AVAILABLE OPERATORS ===
    • No operator = equals (default)
    • ! = not equal to
    • > = greater than  
    • >= = greater than or equal
    • < = less than
    • <= = less than or equal  
    • ~ = text match (ignores case, spaces, punctuation)
    • !~ = does not text match
    • * = wildcard matching (one or more characters)
    
    === DATA TYPES & SYNTAX ===
    • Strings: 'value' or ['exact_value'] for exact match
    • Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format) 
    • Booleans: true or false (no quotes)
    • Numbers: 123 (no quotes)
    • Wildcards: 'partial*' or '*partial' or '*partial*'
    • IP addresses: Support wildcards like '192.168.*'
    
    === COMBINING CONDITIONS ===
    • + = AND condition
    • , = OR condition  
    • ( ) = Group expressions
    
    🏷️ SEARCHABLE HOST PROPERTIES (Complete List):
    
    === IDENTIFICATION ===
    • device_id: Host unique identifier (AID)
    • hostname: Machine hostname (supports wildcards)
    • computer_name: Computer display name
    • serial_number: Hardware serial number
    • mac_address: Network MAC address
    
    === SYSTEM INFORMATION ===  
    • platform_name: OS platform (Windows, Mac, Linux)
    • os_version: Operating system version
    • major_version: OS major version number
    • minor_version: OS minor version number
    • system_manufacturer: Hardware manufacturer
    • system_product_name: System model/product name
    • bios_manufacturer: BIOS manufacturer
    • bios_version: BIOS version
    • cpu_signature: CPU type/signature
    
    === NETWORK INFORMATION ===
    • local_ip: Internal IP address (supports wildcards with local_ip.raw)
    • external_ip: External/public IP address  
    • machine_domain: Active Directory domain
    • ou: Organizational Unit
    • site_name: AD site name
    
    === AGENT & CONFIGURATION ===
    • agent_version: Falcon agent version
    • agent_load_flags: Agent configuration flags
    • config_id_base: Configuration base ID
    • config_id_build: Configuration build ID  
    • config_id_platform: Platform configuration ID
    • platform_id: Platform identifier
    • product_type_desc: Product type description
    • release_group: Sensor deployment group
    
    === STATUS & TIMESTAMPS ===
    • status: Host status (normal, containment_pending, contained, lift_containment_pending)
    • first_seen: First connection timestamp
    • last_seen: Most recent connection timestamp  
    • last_login_timestamp: User login timestamp
    • modified_timestamp: Last record update timestamp
    • max_severity: Value can be any integer between 1-100
    • max_severity_displayname: informational, low, medium, high, critical
    
    === SPECIALIZED PROPERTIES ===
    • reduced_functionality_mode: RFM status (yes, no, blank for unknown)
    • linux_sensor_mode: Linux mode (Kernel Mode, User Mode)
    • deployment_type: Linux deployment (Standard, DaemonSet)
    • tags: Falcon grouping tags
    
    💡 PRACTICAL SEARCH EXAMPLES:
    
    === BASIC SEARCHES ===
    Find Windows servers:
    platform_name:'Windows'
    
    Find specific hostname:
    hostname:'web-server-01'
    
    Find hosts with hostname starting with 'web':
    hostname:'web*'
    
    === NETWORK-BASED SEARCHES ===
    Find hosts in specific IP range:
    local_ip.raw:*'192.168.1.*'
    
    Find hosts by external IP:
    external_ip:'203.0.113.45'
    
    Find hosts in specific domain:
    machine_domain:'contoso.com'
    
    === TIME-BASED SEARCHES ===
    Find hosts not seen in last 30 days:
    last_seen:<'2024-01-01T00:00:00Z'
    
    Find recently joined hosts (last 7 days):
    first_seen:>'2024-01-15T00:00:00Z'
    
    === STATUS & HEALTH SEARCHES ===
    Find contained hosts:
    status:'contained'
    
    Find hosts in reduced functionality mode:
    reduced_functionality_mode:'yes'
    
    Find offline hosts (not seen in 24 hours):
    last_seen:<'2024-01-20T00:00:00Z'
    
    === SYSTEM SPECIFICATION SEARCHES ===
    Find Linux hosts:
    platform_name:'Linux'
    
    Find VMware virtual machines:
    system_manufacturer:'VMware, Inc.'
    
    Find specific OS version:
    os_version:'Windows Server 2019'
    
    Find hosts with old agent versions:
    agent_version:<'7.0.0'
    
    === ADVANCED COMBINED SEARCHES ===
    Find Windows servers in production domain not seen recently:
    platform_name:'Windows'+machine_domain:'prod.company.com'+last_seen:<'2024-01-15T00:00:00Z'
    
    Find either Linux hosts OR hosts with specific hostname pattern:
    (platform_name:'Linux'),(hostname:'app-*')
    
    Find critical infrastructure hosts (complex grouping):
    (hostname:'dc-*'+platform_name:'Windows'),(hostname:'db-*'+status:'normal')
    
    Find hosts by multiple criteria with exclusions:
    platform_name:'Windows'+hostname:!'test-*'+status:!'contained'
    
    Find hosts needing attention (old, offline, or contained):
    (last_seen:<'2024-01-10T00:00:00Z'),(status:'contained'),(agent_version:<'6.0.0')
    
    === COMPLIANCE & INVENTORY SEARCHES ===
    Find untagged hosts:
    tags:!*
    
    Find hosts with specific tags:
    tags:'production'
    
    Find hosts by manufacturer for hardware inventory:
    system_manufacturer:'Dell Inc.'
    
    Find hosts by deployment group:
    release_group:'production-sensors'
    
    === SECURITY-FOCUSED SEARCHES ===
    Find hosts with suspicious external IPs:
    external_ip.raw:*'10.*'
    
    Find hosts that haven't checked in (potential compromise):
    last_seen:<'2024-01-18T00:00:00Z'+status:'normal'
    
    Find hosts with modified configurations:
    modified_timestamp:>'2024-01-15T00:00:00Z'
    
    🚀 USAGE EXAMPLES:
    
    # Find all Windows hosts sorted by hostname
    search_hosts_advanced("platform_name:'Windows'", limit=50, sort="hostname.asc")
    
    # Find hosts not seen in 30 days with full details  
    search_hosts_advanced("last_seen:<'2024-01-01T00:00:00Z'", limit=25, include_details=True)
    
    # Find Linux hosts in specific IP range
    search_hosts_advanced("platform_name:'Linux'+local_ip.raw:*'10.0.*'", limit=100)
    
    # Get basic inventory - just hostnames and IDs
    search_hosts_advanced("", limit=1000, fields="hostname,device_id,platform_name")
    
    # Find contained or pending containment hosts
    search_hosts_advanced("(status:'contained'),(status:'containment_pending')", sort="modified_timestamp.desc")
    
    # Complex search: Production Windows servers, healthy, recent
    search_hosts_advanced("platform_name:'Windows'+hostname:'prod-*'+status:'normal'+last_seen:>'2024-01-15T00:00:00Z'")
    
    ⚠️ IMPORTANT NOTES:
    • Use single quotes around string values: 'value'
    • Use square brackets for exact matches: ['exact_value']  
    • Wildcard searches may be limited (one * per property in some cases)
    • Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
    • Maximum 20 properties per FQL statement
    • Boolean values: true/false (no quotes)
    • For IP wildcards, use local_ip.raw property
    • Complex queries may take longer to execute

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
        if self._is_error(detection_ids):
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
            if self._is_error(details):
                return [details]

            return details

        return []

    def get_detection_details(
        self,
        ids: List[str] = Field(),
    ) -> List[Dict[str, Any]]|Dict[str, Any]:
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
