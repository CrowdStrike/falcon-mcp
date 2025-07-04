# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Hosts module for Falcon MCP Server

This module provides tools for accessing and managing CrowdStrike Falcon hosts/devices.
"""
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP
from pydantic import Field

from ..common.logging import get_logger
from ..common.errors import handle_api_response
from ..common.utils import prepare_api_parameters
from ..resources.hosts import SEARCH_HOSTS_FQL_DOCUMENTATION
from .base import BaseModule

logger = get_logger(__name__)


class HostsModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon hosts/devices."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server,
            self.search_hosts,
            name="search_hosts"
        )

        self._add_tool(
            server,
            self.search_hosts_fql_filter_guide,
            name="search_hosts_fql_filter_guide"
        )

        self._add_tool(
            server,
            self.get_host_details,
            name="get_host_details"
        )

    def search_hosts(
        self,
        filter: Optional[str] = Field(default=None, description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon_search_hosts_fql_filter_guide` tool when building this filter parameter.", examples={"platform_name:'Windows'", "hostname:'PC*'"}),
        limit: Optional[int] = Field(default=100, ge=1, le=5000),
        offset: Optional[int] = Field(default=0, ge=0),
        sort: Optional[str] = Field(default=None, examples={"hostname.asc", "last_seen.desc"}),
    ) -> List[Dict[str, Any]]:
        """Search for hosts in your CrowdStrike environment.

        IMPORTANT: You must use the tool `falcon_search_hosts_fql_filter_guide` whenever you want to use the `filter` parameter. This tool contains the guide on how to build the FQL `filter` parameter for `search_hosts` tool.

        Args:
            filter: Filter hosts using a query in Falcon Query Language (FQL). An asterisk wildcard * includes all results. You must use FQL and never use JSON.
            limit: The maximum number of hosts to return in this response (default: 100; max: 5000). Use with the offset parameter to manage pagination of results.
            offset: The first host to return, where 0 is the latest host. Use with the limit parameter to manage pagination of results.
            sort: Sort hosts using these options:
                hostname: Host name/computer name
                last_seen: Timestamp when the host was last seen
                first_seen: Timestamp when the host was first seen
                modified_timestamp: When the host record was last modified
                platform_name: Operating system platform
                agent_version: CrowdStrike agent version
                os_version: Operating system version
                external_ip: External IP address

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'hostname.desc' or 'hostname|desc'

                Examples: 'hostname.asc', 'last_seen.desc', 'platform_name.asc'

        🎯 FALCON QUERY LANGUAGE (FQL) COMPREHENSIVE GUIDE FOR HOSTS:

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

        === COMBINING CONDITIONS ===
        • + = AND condition
        • , = OR condition
        • ( ) = Group expressions

        🖥️ HOST PROPERTIES (Complete List):

        === IDENTIFICATION & CORE ===
        • device_id: Unique device identifier
        • hostname: Host name/computer name (supports wildcards)
        • cid: Customer ID
        • agent_version: CrowdStrike agent version
        • serial_number: Device serial number

        === PLATFORM & SYSTEM ===
        • platform_name: Operating system platform
          Available Options:
            - 'Windows'
            - 'Mac'
            - 'Linux'
        • platform_id: Numeric platform identifier
        • os_version: Operating system version
        • major_version: Major OS version number
        • minor_version: Minor OS version number
        • kernel_version: Linux kernel version
        • product_type_desc: System type
          Available Options:
            - 'Workstation'
            - 'Server'
            - 'Domain Controller'

        === NETWORK INFORMATION ===
        • external_ip: External IP address as seen by CrowdStrike
        • local_ip: Local/internal IP address
        • local_ip.raw: IP address with wildcard support (use *'192.168.1.*')
        • connection_ip: Current connection IP
        • default_gateway_ip: Default gateway IP
        • mac_address: MAC address
        • connection_mac_address: Connection MAC address

        === STATUS & CONTAINMENT ===
        • status: Host containment status
          Available Options:
            - 'normal' (normal operations)
            - 'containment_pending' (containment in progress)
            - 'contained' (host contained)
            - 'lift_containment_pending' (lifting containment)
        • filesystem_containment_status: File system containment status
        • reduced_functionality_mode: RFM status ('yes', 'no', or blank)
        • rtr_state: Real Time Response state

        === TIMESTAMPS ===
        • first_seen: When host first connected to Falcon
        • last_seen: Most recent connection to Falcon
        • modified_timestamp: Last host record update
        • agent_local_time: Agent's local timestamp

        === HARDWARE & BIOS ===
        • bios_manufacturer: BIOS manufacturer name
        • bios_version: BIOS version
        • system_manufacturer: System manufacturer
        • system_product_name: System product name
        • cpu_signature: CPU signature
        • cpu_vendor: CPU vendor code
        • chassis_type: Chassis type code
        • chassis_type_desc: Chassis type description

        === DOMAIN & GROUPS ===
        • machine_domain: Active Directory domain
        • ou: Organizational unit
        • groups: Host groups
        • tags: Falcon grouping tags

        === CLOUD & VIRTUALIZATION ===
        • service_provider: Cloud provider ('AZURE', 'AWS', 'GCP', etc.)
        • service_provider_account_id: Cloud account ID
        • instance_id: Cloud instance ID
        • k8s_cluster_id: Kubernetes cluster ID
        • deployment_type: Deployment type ('Standard', 'DaemonSet')
        • linux_sensor_mode: Linux sensor mode ('Kernel Mode', 'User Mode')

        === CONFIGURATION ===
        • config_id_base: Agent configuration base ID
        • config_id_build: Agent configuration build ID
        • config_id_platform: Agent configuration platform ID
        • agent_load_flags: Agent load flags

        💡 PRACTICAL HOST SEARCH EXAMPLES:

        === PLATFORM-BASED SEARCHES ===
        Find Windows hosts:
        platform_name:'Windows'

        Find Linux servers:
        platform_name:'Linux'+product_type_desc:'Server'

        Find Mac workstations:
        platform_name:'Mac'+product_type_desc:'Workstation'

        === HOSTNAME SEARCHES ===
        Find hosts with specific hostname pattern:
        hostname:'PC*'

        Find hosts containing specific text:
        hostname:'*server*'

        Find specific host:
        hostname:'DESKTOP-ABC123'

        === STATUS-BASED SEARCHES ===
        Find normal/healthy hosts:
        status:'normal'

        Find contained hosts:
        status:'contained'

        Find hosts with reduced functionality:
        reduced_functionality_mode:'yes'

        === NETWORK-BASED SEARCHES ===
        Find hosts by IP range:
        local_ip.raw:*'192.168.1.*'

        Find hosts by external IP:
        external_ip:'203.0.113.10'

        Find hosts by MAC address pattern:
        mac_address:'00:50:56:*'

        === TIME-BASED SEARCHES ===
        Find recently seen hosts (last 24 hours):
        last_seen:>'2024-01-20T00:00:00Z'

        Find hosts first seen in date range:
        first_seen:>='2024-01-15T00:00:00Z'+first_seen:<='2024-01-20T00:00:00Z'

        Find hosts not seen recently (offline):
        last_seen:<'2024-01-15T00:00:00Z'

        === AGENT & VERSION SEARCHES ===
        Find hosts with specific agent version:
        agent_version:'7.26.*'

        Find hosts with older agents:
        agent_version:<'7.20.0'

        Find hosts with specific OS version:
        os_version:'*Windows 10*'

        === CLOUD & INFRASTRUCTURE SEARCHES ===
        Find Azure hosts:
        service_provider:'AZURE'

        Find AWS hosts:
        service_provider:'AWS'

        Find Kubernetes hosts:
        deployment_type:'DaemonSet'

        Find Docker/container hosts:
        k8s_cluster_id:*

        === HARDWARE-BASED SEARCHES ===
        Find VMware virtual machines:
        system_manufacturer:'VMware*'

        Find Microsoft virtual machines:
        system_manufacturer:'Microsoft Corporation'

        Find specific BIOS manufacturer:
        bios_manufacturer:'American Megatrends*'

        === ADVANCED COMBINED SEARCHES ===
        Find Windows servers that are online:
        platform_name:'Windows'+product_type_desc:'Server'+status:'normal'

        Find Linux hosts in specific domain:
        platform_name:'Linux'+machine_domain:'company.local'

        Find contained Windows workstations:
        platform_name:'Windows'+product_type_desc:'Workstation'+status:'contained'

        Find Azure Linux servers seen recently:
        service_provider:'AZURE'+platform_name:'Linux'+product_type_desc:'Server'+last_seen:>'2024-01-18T00:00:00Z'

        Find hosts with specific tags:
        tags:'*production*'

        === BULK FILTERING SEARCHES ===
        Find multiple platform types:
        (platform_name:'Windows'),(platform_name:'Linux')

        Find various system types:
        (product_type_desc:'Server'),(product_type_desc:'Workstation')

        Find hosts in multiple subnets:
        (local_ip.raw:*'192.168.1.*'),(local_ip.raw:*'10.0.1.*')

        === TROUBLESHOOTING SEARCHES ===
        Find hosts with issues:
        (status:'containment_pending'),(status:'contained'),(reduced_functionality_mode:'yes')

        Find offline hosts:
        last_seen:<'2024-01-15T00:00:00Z'

        Find hosts needing attention:
        (rtr_state:!'')+status:'normal'

        🚀 USAGE EXAMPLES:

        # Find Windows workstations sorted by hostname
        falcon_search_hosts(filter="platform_name:'Windows'+product_type_desc:'Workstation'", limit=50, sort="hostname.asc")

        # Find recently seen Linux servers
        falcon_search_hosts(filter="platform_name:'Linux'+product_type_desc:'Server'+last_seen:>'2024-01-15T00:00:00Z'", limit=25)

        # Find hosts by hostname pattern
        falcon_search_hosts(filter="hostname:'SERVER*'", limit=100, sort="last_seen.desc")

        # Find Azure virtual machines
        falcon_search_hosts(filter="service_provider:'AZURE'+system_manufacturer:'Microsoft Corporation'", limit=50)

        # Find contained hosts needing attention
        falcon_search_hosts(filter="status:'contained'", sort="modified_timestamp.desc")

        ⚠️ IMPORTANT NOTES:
        • Use single quotes around string values: 'value'
        • Use square brackets for exact matches: ['exact_value']
        • Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
        • Hostname supports wildcards: 'PC*', '*server*'
        • IP wildcards require local_ip.raw with specific syntax
        • Complex queries may take longer to execute
        • Status values: normal, containment_pending, contained, lift_containment_pending

        Returns:
            List of host details
        """
        # Prepare parameters for QueryDevicesByFilter
        params = prepare_api_parameters({
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        })

        # Define the operation name
        operation = "QueryDevicesByFilter"

        logger.debug("Searching hosts with params: %s", params)

        # Make the API request to get device IDs
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get device IDs
        device_ids = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to search hosts",
            default_result=[]
        )

        # If handle_api_response returns an error dict instead of a list,
        # it means there was an error, so we return it wrapped in a list
        if self._is_error(device_ids):
            return [device_ids]

        # If we have device IDs, get the details for each one
        if device_ids:
            # Use the base method to get device details
            details = self._base_get_by_ids(
                operation="PostDeviceDetailsV2",
                ids=device_ids,
                id_key="ids"
            )

            # If handle_api_response returns an error dict instead of a list,
            # it means there was an error, so we return it wrapped in a list
            if self._is_error(details):
                return [details]

            return details

        return []

    def search_hosts_fql_filter_guide(self) -> str:
        """
        Returns the guide for the `filter` param of the `falcon_search_hosts` tool.

        IMPORTANT: Before running `falcon_search_hosts`, always call this tool to get information about how to build the FQL for the filter.
        """
        return SEARCH_HOSTS_FQL_DOCUMENTATION

    def get_host_details(
        self,
        ids: List[str] = Field(description="Host device IDs to retrieve details for"),
    ) -> List[Dict[str, Any]]|Dict[str, Any]:
        """Get detailed information about specific hosts by their device IDs.

        Args:
            ids: List of host device IDs to retrieve details for. You can get device IDs from the search_hosts operation, the Falcon console, or the Streaming API. Maximum: 5000 IDs per request.

        Returns:
            Host details for the specified device IDs
        """
        logger.debug("Getting host details for IDs: %s", ids)

        # Handle empty list case - return empty list without making API call
        if not ids:
            return []

        # Use the base method to get device details
        return self._base_get_by_ids(
            operation="PostDeviceDetailsV2",
            ids=ids,
            id_key="ids"
        )
