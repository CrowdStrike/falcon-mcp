"""FastMCP server implementation for CrowdStrike Falcon."""

import structlog
from fastmcp import FastMCP
from src.core.services import initialize_falcon_services, get_host_manager

# Initialize structured logging
logger = structlog.get_logger(__name__)

# Create FastMCP app
app = FastMCP("CrowdStrike Falcon MCP")


@app.tool()
def get_host_details(host_identifier: str) -> str:
    """Get comprehensive technical details for a CrowdStrike Falcon host.
    
    Retrieves detailed technical information about a host monitored by CrowdStrike Falcon,
    including system specifications, network configuration, agent status, and applied policies.
    
    Args:
        host_identifier: Host ID (AID) or hostname to retrieve details for
        
    Returns:
        Formatted technical details about the host
        
    Example usage:
        - get_host_details("123456789012345678901234567890ab")  # Using Host ID (AID)
        - get_host_details("myhost-123")  # Using hostname
    """
    logger.info("get_host_details_called", identifier=host_identifier)
    
    try:
        host_manager = get_host_manager()
        return host_manager.get_host_technical_details(host_identifier)
    except Exception as e:
        error_msg = f"Failed to retrieve host details for '{host_identifier}': {str(e)}"
        logger.error("get_host_details_failed", identifier=host_identifier, error=str(e))
        return error_msg


@app.tool()
def get_host_events(host_identifier: str, limit: int = 10) -> str:
    """Get recent detection events for a CrowdStrike Falcon host.
    
    Retrieves the most recent security detection events for a specific host,
    including event details, severity, tactics, techniques, and behavioral information.
    
    Args:
        host_identifier: Host ID (AID) or hostname to retrieve events for
        limit: Maximum number of recent events to return (1-50, default: 10)
        
    Returns:
        Formatted list of recent detection events for the host
        
    Example usage:
        - get_host_events("myhost-123", 5)  # Get last 5 events for hostname
        - get_host_events("123456789012345678901234567890ab")  # Get last 10 events using Host ID
    """
    logger.info("get_host_events_called", identifier=host_identifier, limit=limit)
    
    # Validate limit
    if limit < 1 or limit > 50:
        return "Error: Limit must be between 1 and 50"
    
    try:
        host_manager = get_host_manager()
        return host_manager.get_host_recent_events(host_identifier, limit)
    except Exception as e:
        error_msg = f"Failed to retrieve events for host '{host_identifier}': {str(e)}"
        logger.error("get_host_events_failed", identifier=host_identifier, error=str(e))
        return error_msg


@app.tool()
def search_hosts_advanced(
    query_filter: str = "",
    limit: int = 100,
    sort: str = "hostname.asc",
    fields: str = "",
    include_details: bool = False
) -> str:
    """🔍 Advanced Host Search - Search CrowdStrike Falcon hosts using powerful filtering capabilities.
    
    This tool provides comprehensive host search functionality using Falcon Query Language (FQL).
    You can search hosts by ANY combination of properties including system specs, network info,
    timestamps, agent details, and more. Perfect for inventory management, compliance checking,
    threat hunting, and operational analysis.
    
    📖 COMPLETE DOCUMENTATION & EXAMPLES GUIDE:
    
    Args:
        query_filter: FQL filter expression to search hosts. Uses Falcon Query Language syntax.
                     Leave empty to get all hosts (up to limit). See extensive examples below.
        limit: Maximum number of hosts to return (1-5000, default: 100)
        sort: Sort expression using format "property.direction" where direction is "asc" or "desc"
              Example: "hostname.asc", "last_seen.desc", "os_version.asc"  
        fields: Comma-separated list of specific fields to return. Leave empty for default fields.
                Example: "hostname,device_id,platform_name,last_seen"
        include_details: If True, returns full host details for each result (slower but comprehensive)
    
    Returns:
        Formatted search results with host information
    
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
    
    💡 Pro Tips:
    • Start with simple queries and add complexity gradually
    • Use include_details=True for troubleshooting but limit results for performance
    • Sort by last_seen.desc to find most recently active hosts first
    • Use fields parameter to get only needed data for large queries
    • Test date ranges carefully - timezone is always UTC
    • Combine this tool with get_host_details() for deep investigation
    """
    logger.info("search_hosts_advanced_called", query_filter=query_filter, limit=limit, sort=sort, fields=fields, include_details=include_details)
    
    # Validate parameters
    if limit < 1 or limit > 5000:
        return "❌ Error: Limit must be between 1 and 5000"
    
    if not sort:
        sort = "hostname.asc"
    
    try:
        host_manager = get_host_manager()
        return host_manager.search_hosts_advanced(
            query_filter=query_filter,
            limit=limit, 
            sort=sort,
            fields=fields,
            include_details=include_details
        )
    except Exception as e:
        error_msg = f"❌ Failed to search hosts with filter '{query_filter}': {str(e)}"
        logger.error("search_hosts_advanced_failed", query_filter=query_filter, error=str(e))
        return error_msg


@app.tool()
def search_hosts_by_vulnerabilities(
    vulnerability_filter: str = "",
    limit: int = 100,
    sort: str = "created_timestamp.desc",
    include_host_details: bool = False,
    include_vulnerability_details: bool = False
) -> str:
    """🔎 Search Hosts by Vulnerabilities - Find hosts based on vulnerability criteria using CrowdStrike Spotlight.
    
    This tool enables searching for hosts that have specific vulnerabilities, allowing you to:
    • Find hosts affected by specific CVEs
    • Identify hosts with critical vulnerabilities
    • Locate systems with open security issues
    • Analyze vulnerability exposure across your environment
    
    The tool works by:
    1. Querying CrowdStrike Spotlight Vulnerabilities service with your criteria
    2. Extracting unique host identifiers (AIDs) from vulnerability results
    3. Retrieving host information for those systems
    4. Providing combined vulnerability and host data
    
    Args:
        vulnerability_filter: FQL filter for vulnerability search. Uses Spotlight Vulnerabilities syntax.
                            Leave empty to get hosts with any vulnerabilities (up to limit).
        limit: Maximum number of vulnerabilities to process (1-1000, default: 100).
               Note: This limits vulnerabilities, not hosts. Multiple vulnerabilities may affect the same host.
        sort: Sort vulnerabilities by property.direction format.
              Supported: "created_timestamp.desc", "closed_timestamp.desc", "updated_timestamp.desc"
        include_host_details: If True, includes comprehensive host information for each affected system
        include_vulnerability_details: If True, includes detailed vulnerability information alongside host data
    
    Returns:
        Formatted results showing affected hosts and their vulnerability information
    
    🎯 VULNERABILITY FILTER EXAMPLES:
    
    === CVE-SPECIFIC SEARCHES ===
    Find hosts with specific CVE:
    cve.id:['CVE-2024-1234']
    
    Find hosts with multiple CVEs:
    cve.id:['CVE-2024-1234','CVE-2024-5678']
    
    Find hosts with any CVE except specific ones:
    cve.id:!['CVE-2024-1234','CVE-2024-5678']
    
    === SEVERITY-BASED SEARCHES ===
    Find hosts with critical vulnerabilities:
    cve.severity:'CRITICAL'
    
    Find hosts with high or critical vulnerabilities:
    cve.severity:['HIGH','CRITICAL']
    
    Find hosts with any severity except low:
    cve.severity:!'LOW'
    
    === STATUS-BASED SEARCHES ===
    Find hosts with open vulnerabilities:
    status:'open'
    
    Find hosts with open critical vulnerabilities:
    status:'open'+cve.severity:'CRITICAL'
    
    Find hosts with recently closed vulnerabilities:
    status:'closed'+closed_timestamp:>'2024-01-15T00:00:00Z'
    
    === EXPLOIT-BASED SEARCHES ===
    Find hosts with actively exploited vulnerabilities:
    cve.exploit_status:'90'
    
    Find hosts with any known exploits:
    cve.exploit_status:!'0'
    
    Find hosts with CISA KEV catalog vulnerabilities:
    cve.is_cisa_kev:true
    
    === ExPRT RATING SEARCHES ===
    Find hosts with high ExPRT-rated vulnerabilities:
    cve.exprt_rating:'HIGH'
    
    Find hosts with critical or high ExPRT ratings:
    cve.exprt_rating:['CRITICAL','HIGH']
    
    === PLATFORM-SPECIFIC SEARCHES ===
    Find Windows hosts with vulnerabilities:
    host_info.platform_name:'Windows'
    
    Find Linux servers with critical vulnerabilities:
    host_info.platform_name:'Linux'+cve.severity:'CRITICAL'
    
    Find internet-exposed hosts with vulnerabilities:
    host_info.internet_exposure:'Yes'
    
    === TIME-BASED SEARCHES ===
    Find recently discovered vulnerabilities:
    created_timestamp:>'2024-01-15T00:00:00Z'
    
    Find old unpatched vulnerabilities:
    created_timestamp:<'2023-01-01T00:00:00Z'+status:'open'
    
    Find vulnerabilities updated in last week:
    updated_timestamp:>'2024-01-15T00:00:00Z'
    
    === HOST MANAGEMENT SEARCHES ===
    Find vulnerabilities on managed hosts (with Falcon sensor):
    host_info.managed_by:'Falcon sensor'
    
    Find vulnerabilities on unmanaged assets:
    host_info.managed_by:'Unmanaged'
    
    Find vulnerabilities on critical assets:
    host_info.asset_criticality:['Critical','High']
    
    === COMPLEX COMBINED SEARCHES ===
    Find critical production vulnerabilities:
    cve.severity:'CRITICAL'+status:'open'+host_info.tags:['production']
    
    Find exploitable Windows vulnerabilities:
    cve.exploit_status:!'0'+host_info.platform_name:'Windows'+status:'open'
    
    Find CISA KEV vulnerabilities on internet-exposed systems:
    cve.is_cisa_kev:true+host_info.internet_exposure:'Yes'+status:'open'
    
    🚀 USAGE EXAMPLES:
    
    # Find hosts with a specific CVE
    search_hosts_by_vulnerabilities("cve.id:['CVE-2024-1234']")
    
    # Find hosts with open critical vulnerabilities
    search_hosts_by_vulnerabilities("status:'open'+cve.severity:'CRITICAL'", limit=50)
    
    # Find Windows hosts with high-severity vulnerabilities
    search_hosts_by_vulnerabilities("host_info.platform_name:'Windows'+cve.severity:'HIGH'")
    
    # Find hosts with actively exploited vulnerabilities (full details)
    search_hosts_by_vulnerabilities("cve.exploit_status:'90'", include_host_details=True, include_vulnerability_details=True)
    
    # Find internet-exposed hosts with CISA KEV vulnerabilities
    search_hosts_by_vulnerabilities("cve.is_cisa_kev:true+host_info.internet_exposure:'Yes'")
    
    # Find production hosts with recent critical vulnerabilities
    search_hosts_by_vulnerabilities("host_info.tags:['production']+cve.severity:'CRITICAL'+created_timestamp:>'2024-01-01T00:00:00Z'", sort="created_timestamp.desc")
    
    ⚠️ IMPORTANT NOTES:
    • Limit applies to vulnerabilities processed, not unique hosts
    • Multiple vulnerabilities may affect the same host (results will be deduplicated)
    • Use include_host_details=True for comprehensive host information (slower)
    • Use include_vulnerability_details=True to see specific vulnerability information
    • Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
    • Higher limits may take longer to process due to API calls for each unique host
    
    💡 Pro Tips:
    • Start with specific CVEs or severity filters for focused results
    • Use status:'open' to focus on current vulnerabilities
    • Combine with host filters to target specific environments
    • Use sorting to prioritize recent vulnerabilities: sort="created_timestamp.desc"
    • For risk prioritization, use severity filters (cannot sort by base_score or severity)
    • For large environments, use specific filters to avoid timeout issues
    """
    logger.info("search_hosts_by_vulnerabilities_called", 
               vulnerability_filter=vulnerability_filter, limit=limit, sort=sort,
               include_host_details=include_host_details, include_vulnerability_details=include_vulnerability_details)
    
    # Validate parameters
    if limit < 1 or limit > 1000:
        return "❌ Error: Limit must be between 1 and 1000"
    
    if not sort:
        sort = "created_timestamp.desc"
    
    try:
        host_manager = get_host_manager()
        return host_manager.search_hosts_by_vulnerabilities(
            vulnerability_filter=vulnerability_filter,
            limit=limit,
            sort=sort,
            include_host_details=include_host_details,
            include_vulnerability_details=include_vulnerability_details
        )
    except Exception as e:
        error_msg = f"❌ Failed to search hosts by vulnerabilities with filter '{vulnerability_filter}': {str(e)}"
        logger.error("search_hosts_by_vulnerabilities_failed", vulnerability_filter=vulnerability_filter, error=str(e))
        return error_msg


def main() -> None:
    """Run the MCP server."""
    logger.info("starting_crowdstrike_falcon_mcp_server")
    
    try:
        # Initialize Falcon services
        initialize_falcon_services()
        logger.info("falcon_services_ready")
        
        # Run the server
        app.run()
    except Exception as e:
        logger.error("failed_to_start_server", error=str(e))
        raise


if __name__ == "__main__":
    main() 
