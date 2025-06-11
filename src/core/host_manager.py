"""Host management functionality for Falcon MCP."""

from typing import Dict, List, Any, Optional
import structlog
from datetime import datetime
from .falcon_client import FalconClient

logger = structlog.get_logger(__name__)


class HostManager:
    """Manages host-related operations for Falcon MCP."""
    
    def __init__(self, falcon_client: FalconClient):
        """Initialize host manager.
        
        Args:
            falcon_client: Initialized Falcon API client
        """
        self.falcon_client = falcon_client
        logger.info("host_manager_initialized")
    
    def get_host_technical_details(self, host_identifier: str) -> str:
        """Get comprehensive technical details for a host.
        
        Args:
            host_identifier: Host ID (AID) or hostname
            
        Returns:
            Formatted technical details string
            
        Raises:
            ValueError: If host not found or API error
        """
        if not host_identifier or not isinstance(host_identifier, str):
            raise ValueError("Host identifier must be a non-empty string")
        
        # Sanitize input for safety
        host_identifier = host_identifier.strip()
        
        logger.info("getting_host_technical_details", identifier=host_identifier)
        
        try:
            # Determine if identifier is a host ID or hostname
            if len(host_identifier) == 32 and host_identifier.replace('-', '').isalnum():
                # Looks like a host ID (AID)
                host_data = self.falcon_client.get_host_by_id(host_identifier)
            else:
                # Treat as hostname
                host_data = self.falcon_client.get_host_by_hostname(host_identifier)
            
            return self._format_host_details(host_data)
            
        except Exception as e:
            logger.error("failed_to_get_host_details", identifier=host_identifier, error=str(e))
            raise
    
    def get_host_recent_events(self, host_identifier: str, limit: int = 10) -> str:
        """Get recent detection events for a host.
        
        Args:
            host_identifier: Host ID (AID) or hostname
            limit: Maximum number of events to return
            
        Returns:
            Formatted events string
            
        Raises:
            ValueError: If host not found or API error
        """
        if not host_identifier or not isinstance(host_identifier, str):
            raise ValueError("Host identifier must be a non-empty string")
        
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        
        if limit > 5000:  # Falcon API limit
            raise ValueError("Limit cannot exceed 5000")
        
        # Sanitize input for safety
        host_identifier = host_identifier.strip()
        
        logger.info("getting_host_recent_events", identifier=host_identifier, limit=limit)
        
        try:
            # Get host details first to ensure it exists and get the AID
            if len(host_identifier) == 32 and host_identifier.replace('-', '').isalnum():
                host_id = host_identifier
                host_data = self.falcon_client.get_host_by_id(host_identifier)
            else:
                host_data = self.falcon_client.get_host_by_hostname(host_identifier)
                host_id = host_data.get("device_id")
            
            # Get events
            events = self.falcon_client.get_host_events(host_id, limit)
            
            return self._format_host_events(host_data, events, limit)
            
        except Exception as e:
            logger.error("failed_to_get_host_events", identifier=host_identifier, error=str(e))
            raise
    
    def _format_host_details(self, host_data: Dict[str, Any]) -> str:
        """Format host details into a readable string.
        
        Args:
            host_data: Raw host data from Falcon API
            
        Returns:
            Formatted host details
        """
        details = []
        details.append("# CrowdStrike Falcon Host Technical Details")
        details.append("=" * 50)
        
        # Basic Information
        details.append("\n## Basic Information")
        details.append(f"• **Hostname**: {host_data.get('hostname', 'N/A')}")
        details.append(f"• **Host ID (AID)**: {host_data.get('device_id', 'N/A')}")
        details.append(f"• **Computer Name**: {host_data.get('computer_name', 'N/A')}")
        details.append(f"• **Status**: {host_data.get('status', 'N/A')}")
        details.append(f"• **Agent Version**: {host_data.get('agent_version', 'N/A')}")
        
        # System Information
        details.append("\n## System Information")
        details.append(f"• **Operating System**: {host_data.get('os_version', 'N/A')}")
        details.append(f"• **Platform**: {host_data.get('platform_name', 'N/A')}")
        details.append(f"• **Architecture**: {host_data.get('os_build', 'N/A')}")
        details.append(f"• **Kernel Version**: {host_data.get('kernel_version', 'N/A')}")
        details.append(f"• **System Manufacturer**: {host_data.get('system_manufacturer', 'N/A')}")
        details.append(f"• **System Product Name**: {host_data.get('system_product_name', 'N/A')}")
        
        # Network Information
        details.append("\n## Network Information")
        details.append(f"• **External IP**: {host_data.get('external_ip', 'N/A')}")
        details.append(f"• **Local IP**: {host_data.get('local_ip', 'N/A')}")
        details.append(f"• **MAC Address**: {host_data.get('mac_address', 'N/A')}")
        
        # Domain and Groups
        details.append("\n## Domain and Groups")
        details.append(f"• **Machine Domain**: {host_data.get('machine_domain', 'N/A')}")
        details.append(f"• **OU**: {host_data.get('ou', 'N/A')}")
        
        groups = host_data.get('groups', [])
        if groups:
            details.append(f"• **Groups**: {', '.join(groups)}")
        else:
            details.append("• **Groups**: None assigned")
        
        # Agent Information
        details.append("\n## Agent Information")
        details.append(f"• **Agent Load Flags**: {host_data.get('agent_load_flags', 'N/A')}")
        details.append(f"• **Config ID Build**: {host_data.get('config_id_build', 'N/A')}")
        details.append(f"• **Config ID Platform**: {host_data.get('config_id_platform', 'N/A')}")
        
        # Timestamps
        details.append("\n## Important Timestamps")
        
        first_seen = host_data.get('first_seen')
        if first_seen:
            first_seen_dt = datetime.fromisoformat(first_seen.replace('Z', '+00:00'))
            details.append(f"• **First Seen**: {first_seen_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        last_seen = host_data.get('last_seen')
        if last_seen:
            last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
            details.append(f"• **Last Seen**: {last_seen_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        modified_timestamp = host_data.get('modified_timestamp')
        if modified_timestamp:
            modified_dt = datetime.fromisoformat(modified_timestamp.replace('Z', '+00:00'))
            details.append(f"• **Last Modified**: {modified_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Policies
        details.append("\n## Applied Policies")
        policies = host_data.get('policies', {})
        
        # Handle both dictionary and list formats for policies
        if isinstance(policies, dict):
            # Dictionary format: policy_type -> policy_info
            for policy_type, policy_info in policies.items():
                if isinstance(policy_info, dict):
                    policy_id = policy_info.get('policy_id', 'N/A')
                    applied_date = policy_info.get('applied_date', 'N/A')
                    details.append(f"• **{policy_type.title()}**: {policy_id} (Applied: {applied_date})")
        elif isinstance(policies, list):
            # List format: list of policy objects
            for policy_info in policies:
                if isinstance(policy_info, dict):
                    policy_type = policy_info.get('policy_type', 'Unknown Policy')
                    policy_id = policy_info.get('policy_id', 'N/A')
                    applied_date = policy_info.get('applied_date', 'N/A')
                    details.append(f"• **{policy_type.title()}**: {policy_id} (Applied: {applied_date})")
        else:
            details.append("• **No policies found or unsupported policy format**")
        
        return "\n".join(details)
    
    def _format_host_events(self, host_data: Dict[str, Any], events: List[Dict[str, Any]], limit: int) -> str:
        """Format host events into a readable string.
        
        Args:
            host_data: Host information
            events: List of detection events
            limit: Number of events requested
            
        Returns:
            Formatted events string
        """
        details = []
        details.append("# CrowdStrike Falcon Host Recent Events")
        details.append("=" * 50)
        
        hostname = host_data.get('hostname', 'Unknown')
        host_id = host_data.get('device_id', 'Unknown')
        
        details.append(f"\n**Host**: {hostname} (ID: {host_id})")
        details.append(f"**Requested Events**: Last {limit} events")
        details.append(f"**Found Events**: {len(events)}")
        
        if not events:
            details.append("\n⚠️  **No recent detection events found for this host.**")
            details.append("\nThis could indicate:")
            details.append("• The host has no recent security detections")
            details.append("• Events may be older than the default query timeframe")
            details.append("• The host may not be actively monitored")
            return "\n".join(details)
        
        details.append(f"\n## Recent Detection Events")
        
        for i, event in enumerate(events, 1):
            details.append(f"\n### Event #{i}")
            details.append(f"• **Detection ID**: {event.get('detection_id', 'N/A')}")
            details.append(f"• **Status**: {event.get('status', 'N/A')}")
            details.append(f"• **Severity**: {event.get('max_severity_displayname', 'N/A')}")
            
            # Timestamp
            created_timestamp = event.get('created_timestamp')
            if created_timestamp:
                created_dt = datetime.fromisoformat(created_timestamp.replace('Z', '+00:00'))
                details.append(f"• **Detected**: {created_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            # Behavior information
            behaviors = event.get('behaviors', [])
            if behaviors:
                behavior = behaviors[0]  # Show first behavior
                details.append(f"• **Technique**: {behavior.get('tactic', 'N/A')} - {behavior.get('technique', 'N/A')}")
                details.append(f"• **Scenario**: {behavior.get('scenario', 'N/A')}")
                details.append(f"• **Objective**: {behavior.get('objective', 'N/A')}")
                
                # Show command line if available
                cmdline = behavior.get('cmdline')
                if cmdline:
                    details.append(f"• **Command Line**: `{cmdline[:100]}{'...' if len(cmdline) > 100 else ''}`")
                
                # Show filename if available
                filename = behavior.get('filename')
                if filename:
                    details.append(f"• **Filename**: {filename}")
            
            # Show assigned users if available
            assigned_to_uuid = event.get('assigned_to_uuid')
            if assigned_to_uuid:
                details.append(f"• **Assigned To**: {assigned_to_uuid}")
        
        return "\n".join(details)
    
    def search_hosts_advanced(
        self,
        query_filter: str = "",
        limit: int = 100,
        sort: str = "hostname.asc",
        fields: str = "",
        include_details: bool = False
    ) -> str:
        """Advanced host search using Falcon Query Language (FQL).
        
        Args:
            query_filter: FQL filter expression
            limit: Maximum number of hosts to return (1-5000)
            sort: Sort expression (property.direction)
            fields: Comma-separated list of fields to return
            include_details: Whether to include full host details for each result
            
        Returns:
            Formatted search results
            
        Raises:
            ValueError: If search fails or parameters are invalid
        """
        # Validate input parameters
        if not isinstance(query_filter, str):
            raise ValueError("Query filter must be a string")
        
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        
        if limit > 5000:  # Falcon API limit
            raise ValueError("Limit cannot exceed 5000")
        
        if not isinstance(sort, str):
            raise ValueError("Sort parameter must be a string")
        
        if not isinstance(fields, str):
            raise ValueError("Fields parameter must be a string")
        
        if not isinstance(include_details, bool):
            raise ValueError("Include details parameter must be a boolean")
        
        # Sanitize string inputs
        query_filter = query_filter.strip()
        sort = sort.strip()
        fields = fields.strip()
        
        logger.info("search_hosts_advanced_called", 
                   query_filter=query_filter, limit=limit, sort=sort, 
                   fields=fields, include_details=include_details)
        
        try:
            # Use combined search which returns full host records
            search_results = self.falcon_client.search_hosts_combined(
                query_filter=query_filter,
                limit=limit,
                sort=sort,
                fields=fields
            )
            
            return self._format_host_search_results(
                search_results, 
                query_filter, 
                limit, 
                sort, 
                fields, 
                include_details
            )
            
        except Exception as e:
            logger.error("failed_to_search_hosts_advanced", 
                        query_filter=query_filter, error=str(e))
            raise
    
    def _format_host_search_results(
        self,
        search_results: Dict[str, Any],
        query_filter: str,
        limit: int,
        sort: str,
        fields: str,
        include_details: bool
    ) -> str:
        """Format host search results into a readable string.
        
        Args:
            search_results: Raw search results from Falcon API
            query_filter: Original filter used
            limit: Limit used
            sort: Sort used
            fields: Fields requested
            include_details: Whether details were requested
            
        Returns:
            Formatted search results
        """
        details = []
        details.append("# 🔍 CrowdStrike Falcon Advanced Host Search Results")
        details.append("=" * 60)
        
        # Search parameters
        details.append("\n## 🎯 Search Parameters")
        details.append(f"• **Filter**: {query_filter if query_filter else 'None (all hosts)'}")
        details.append(f"• **Limit**: {limit}")
        details.append(f"• **Sort**: {sort}")
        details.append(f"• **Fields**: {fields if fields else 'Default fields'}")
        details.append(f"• **Include Details**: {'Yes' if include_details else 'No'}")
        
        # Results summary
        hosts = search_results.get("resources", [])
        total_found = len(hosts)
        
        details.append(f"\n## 📊 Results Summary")
        details.append(f"• **Hosts Found**: {total_found}")
        
        if total_found == 0:
            details.append("\n⚠️  **No hosts found matching the search criteria.**")
            details.append("\n💡 **Suggestions:**")
            details.append("• Check your filter syntax (use single quotes around values)")
            details.append("• Verify property names are correct")
            details.append("• Try a broader search or remove some filter conditions")
            details.append("• Use wildcard searches (e.g., hostname:'web*')")
            return "\n".join(details)
        
        if total_found >= limit:
            details.append(f"• **Note**: Results limited to {limit}. There may be more hosts matching your criteria.")
        
        # Show results
        details.append(f"\n## 📋 Host Results")
        
        if include_details:
            # Full details mode - show comprehensive information for each host
            details.append("\n### Full Host Details")
            for i, host in enumerate(hosts, 1):
                details.append(f"\n--- Host #{i} ---")
                details.append(self._format_single_host_summary(host, detailed=True))
        else:
            # Summary mode - show key information in a table-like format
            details.append("\n### Host Summary")
            details.append("```")
            details.append(f"{'#':<3} {'Hostname':<25} {'Platform':<10} {'Status':<15} {'Last Seen':<20} {'Host ID'}")
            details.append("-" * 100)
            
            for i, host in enumerate(hosts, 1):
                hostname = host.get('hostname', 'N/A')[:24]
                platform = host.get('platform_name', 'N/A')[:9]
                status = host.get('status', 'N/A')[:14]
                
                # Format last seen
                last_seen = host.get('last_seen', 'N/A')
                if last_seen and last_seen != 'N/A':
                    try:
                        last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                        last_seen_str = last_seen_dt.strftime('%Y-%m-%d %H:%M')[:19]
                    except:
                        last_seen_str = last_seen[:19]
                else:
                    last_seen_str = 'N/A'
                
                host_id = host.get('device_id', 'N/A')
                
                details.append(f"{i:<3} {hostname:<25} {platform:<10} {status:<15} {last_seen_str:<20} {host_id}")
            
            details.append("```")
        
        # Additional information section
        details.append(f"\n## 📈 Analysis")
        
        # Platform breakdown
        platform_counts = {}
        status_counts = {}
        for host in hosts:
            platform = host.get('platform_name', 'Unknown')
            status = host.get('status', 'Unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
        
        details.append("\n### Platform Distribution")
        for platform, count in sorted(platform_counts.items()):
            details.append(f"• **{platform}**: {count} hosts")
        
        details.append("\n### Status Distribution")
        for status, count in sorted(status_counts.items()):
            details.append(f"• **{status}**: {count} hosts")
        
        # Recent activity analysis
        now = datetime.now()
        recent_count = 0
        old_count = 0
        
        for host in hosts:
            last_seen = host.get('last_seen')
            if last_seen:
                try:
                    last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                    days_ago = (now - last_seen_dt.replace(tzinfo=None)).days
                    if days_ago <= 7:
                        recent_count += 1
                    elif days_ago > 30:
                        old_count += 1
                except:
                    pass
        
        details.append("\n### Activity Analysis")
        details.append(f"• **Active (last 7 days)**: {recent_count} hosts")
        details.append(f"• **Potentially stale (>30 days)**: {old_count} hosts")
        
        # Usage tips
        details.append(f"\n## 💡 Next Steps")
        details.append("• Use `get_host_details(host_id)` for detailed information about specific hosts")
        details.append("• Use `get_host_events(host_id)` to check for recent security events")
        if not include_details and total_found > 0:
            details.append("• Re-run with `include_details=True` for comprehensive host information")
        if total_found >= limit:
            details.append(f"• Increase limit (max 5000) or add more specific filters to see all results")
        
        return "\n".join(details)
    
    def _format_single_host_summary(self, host_data: Dict[str, Any], detailed: bool = False) -> str:
        """Format a single host's information.
        
        Args:
            host_data: Single host data
            detailed: Whether to show detailed information
            
        Returns:
            Formatted host information
        """
        if detailed:
            # Return full details using existing method
            return self._format_host_details(host_data)
        else:
            # Return summary information
            summary = []
            summary.append(f"**Hostname**: {host_data.get('hostname', 'N/A')}")
            summary.append(f"**Host ID**: {host_data.get('device_id', 'N/A')}")
            summary.append(f"**Platform**: {host_data.get('platform_name', 'N/A')}")
            summary.append(f"**Status**: {host_data.get('status', 'N/A')}")
            
            # Add last seen if available
            last_seen = host_data.get('last_seen')
            if last_seen:
                try:
                    last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                    summary.append(f"**Last Seen**: {last_seen_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                except:
                    summary.append(f"**Last Seen**: {last_seen}")
            
            return "\n".join(summary)
    
    def search_hosts_by_vulnerabilities(
        self,
        vulnerability_filter: str = "",
        limit: int = 100,
        sort: str = "created_timestamp.desc",
        include_host_details: bool = False,
        include_vulnerability_details: bool = False
    ) -> str:
        """Search for hosts that have specific vulnerabilities.
        
        Args:
            vulnerability_filter: FQL filter expression for vulnerability search
            limit: Maximum number of vulnerabilities to process (1-1000)
            sort: Sort expression for vulnerabilities
            include_host_details: Whether to include full host details
            include_vulnerability_details: Whether to include vulnerability details
            
        Returns:
            Formatted search results showing affected hosts and vulnerabilities
            
        Raises:
            ValueError: If search fails or parameters are invalid
        """
        # Validate input parameters
        if not isinstance(vulnerability_filter, str):
            raise ValueError("Vulnerability filter must be a string")
        
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        
        if limit > 1000:  # Practical limit for vulnerability processing
            raise ValueError("Limit cannot exceed 1000 for vulnerability searches")
        
        if not isinstance(sort, str):
            raise ValueError("Sort parameter must be a string")
        
        if not isinstance(include_host_details, bool):
            raise ValueError("Include host details parameter must be a boolean")
        
        if not isinstance(include_vulnerability_details, bool):
            raise ValueError("Include vulnerability details parameter must be a boolean")
        
        # Sanitize string inputs
        vulnerability_filter = vulnerability_filter.strip()
        sort = sort.strip()
        
        logger.info("search_hosts_by_vulnerabilities_called", 
                   vulnerability_filter=vulnerability_filter, limit=limit, sort=sort,
                   include_host_details=include_host_details, include_vulnerability_details=include_vulnerability_details)
        
        try:
            # Step 1: Search for vulnerabilities using the provided filter
            # Include host_info facet to get host information with vulnerabilities
            vulnerability_results = self.falcon_client.search_vulnerabilities_combined(
                query_filter=vulnerability_filter,
                limit=limit,
                sort=sort,
                facet="host_info,cve"  # Include host info and CVE details
            )
            
            vulnerabilities = vulnerability_results.get("resources", [])
            
            if not vulnerabilities:
                return self._format_no_vulnerabilities_found(vulnerability_filter)
            
            # Step 2: Extract unique host IDs (AIDs) from vulnerabilities
            host_aids = set()
            vulnerability_by_host = {}
            
            for vuln in vulnerabilities:
                aid = vuln.get("aid")
                if aid:
                    host_aids.add(aid)
                    if aid not in vulnerability_by_host:
                        vulnerability_by_host[aid] = []
                    vulnerability_by_host[aid].append(vuln)
            
            logger.info("extracted_host_aids", unique_hosts=len(host_aids), total_vulnerabilities=len(vulnerabilities))
            
            # Step 3: Get host details for all affected hosts (if they have Falcon sensor)
            hosts_data = {}
            if host_aids:
                try:
                    # Convert set to list for API call
                    aid_list = list(host_aids)
                    
                    # Get host details for all AIDs at once
                    for aid in aid_list:
                        try:
                            host_data = self.falcon_client.get_host_by_id(aid)
                            hosts_data[aid] = host_data
                        except Exception as e:
                            # Some vulnerabilities may be on assets without Falcon sensor
                            logger.warning("failed_to_get_host_details", aid=aid, error=str(e))
                            hosts_data[aid] = {"device_id": aid, "hostname": "Unknown (No Falcon Sensor)", "platform_name": "Unknown"}
                
                except Exception as e:
                    logger.error("failed_to_get_host_details_bulk", error=str(e))
                    # Fallback: mark all as unknown
                    for aid in host_aids:
                        hosts_data[aid] = {"device_id": aid, "hostname": "Unknown", "platform_name": "Unknown"}
            
            # Step 4: Format results
            return self._format_vulnerability_search_results(
                vulnerabilities=vulnerabilities,
                vulnerability_by_host=vulnerability_by_host,
                hosts_data=hosts_data,
                vulnerability_filter=vulnerability_filter,
                limit=limit,
                sort=sort,
                include_host_details=include_host_details,
                include_vulnerability_details=include_vulnerability_details
            )
            
        except Exception as e:
            logger.error("failed_to_search_hosts_by_vulnerabilities", 
                        vulnerability_filter=vulnerability_filter, error=str(e))
            raise
    
    def _format_no_vulnerabilities_found(self, vulnerability_filter: str) -> str:
        """Format message when no vulnerabilities are found."""
        details = []
        details.append("# 🔎 CrowdStrike Falcon - Hosts by Vulnerabilities Search")
        details.append("=" * 60)
        
        details.append(f"\n## 🎯 Search Parameters")
        details.append(f"• **Vulnerability Filter**: {vulnerability_filter if vulnerability_filter else 'None (all vulnerabilities)'}")
        
        details.append(f"\n## 📊 Results Summary")
        details.append("• **Vulnerabilities Found**: 0")
        details.append("• **Affected Hosts**: 0")
        
        details.append("\n⚠️  **No vulnerabilities found matching the search criteria.**")
        details.append("\n💡 **Suggestions:**")
        details.append("• Check your vulnerability filter syntax (use single quotes around values)")
        details.append("• Verify CVE IDs are correct (e.g., cve.id:['CVE-2024-1234'])")
        details.append("• Try broader criteria like cve.severity:['HIGH','CRITICAL']")
        details.append("• Check if status:'open' is filtering out closed vulnerabilities")
        details.append("• Ensure date ranges are in UTC format: 'YYYY-MM-DDTHH:MM:SSZ'")
        
        return "\n".join(details)
    
    def _format_vulnerability_search_results(
        self,
        vulnerabilities: List[Dict[str, Any]],
        vulnerability_by_host: Dict[str, List[Dict[str, Any]]],
        hosts_data: Dict[str, Dict[str, Any]],
        vulnerability_filter: str,
        limit: int,
        sort: str,
        include_host_details: bool,
        include_vulnerability_details: bool
    ) -> str:
        """Format vulnerability search results into a readable string."""
        details = []
        details.append("# 🔎 CrowdStrike Falcon - Hosts by Vulnerabilities Search Results")
        details.append("=" * 70)
        
        # Search parameters
        details.append("\n## 🎯 Search Parameters")
        details.append(f"• **Vulnerability Filter**: {vulnerability_filter if vulnerability_filter else 'None (all vulnerabilities)'}")
        details.append(f"• **Limit**: {limit} vulnerabilities")
        details.append(f"• **Sort**: {sort}")
        details.append(f"• **Include Host Details**: {'Yes' if include_host_details else 'No'}")
        details.append(f"• **Include Vulnerability Details**: {'Yes' if include_vulnerability_details else 'No'}")
        
        # Results summary
        total_vulnerabilities = len(vulnerabilities)
        unique_hosts = len(vulnerability_by_host)
        
        details.append(f"\n## 📊 Results Summary")
        details.append(f"• **Vulnerabilities Found**: {total_vulnerabilities}")
        details.append(f"• **Unique Hosts Affected**: {unique_hosts}")
        
        if total_vulnerabilities >= limit:
            details.append(f"• **Note**: Results limited to {limit} vulnerabilities. There may be more matching your criteria.")
        
        # Analyze vulnerability severity distribution
        severity_counts = {}
        status_counts = {}
        platform_counts = {}
        
        for vuln in vulnerabilities:
            cve_info = vuln.get("cve", {})
            severity = cve_info.get("severity", "UNKNOWN")
            status = vuln.get("status", "unknown")
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Platform from host_info in vulnerability record
            host_info = vuln.get("host_info", {})
            platform = host_info.get("platform_name", "Unknown")
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        details.append(f"\n## 📈 Vulnerability Analysis")
        
        details.append("\n### Severity Distribution")
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                details.append(f"• **{severity}**: {count} vulnerabilities")
        
        details.append("\n### Status Distribution")
        for status, count in sorted(status_counts.items()):
            details.append(f"• **{status}**: {count} vulnerabilities")
        
        details.append("\n### Platform Distribution")
        for platform, count in sorted(platform_counts.items()):
            details.append(f"• **{platform}**: {count} vulnerabilities")
        
        # Show affected hosts
        details.append(f"\n## 🖥️ Affected Hosts")
        
        if include_host_details or include_vulnerability_details:
            # Detailed view - show each host with its vulnerabilities
            details.append("\n### Detailed Host and Vulnerability Information")
            
            for i, (aid, host_vulns) in enumerate(vulnerability_by_host.items(), 1):
                host_data = hosts_data.get(aid, {})
                hostname = host_data.get("hostname", "Unknown")
                platform = host_data.get("platform_name", "Unknown")
                
                details.append(f"\n--- Host #{i}: {hostname} ---")
                details.append(f"**Host ID (AID)**: {aid}")
                details.append(f"**Platform**: {platform}")
                details.append(f"**Vulnerabilities**: {len(host_vulns)}")
                
                if include_host_details:
                    # Show comprehensive host details
                    details.append("\n**Host Details:**")
                    details.append(self._format_single_host_summary(host_data, detailed=True))
                
                if include_vulnerability_details:
                    # Show vulnerability details for this host
                    details.append(f"\n**Vulnerability Details for {hostname}:**")
                    for j, vuln in enumerate(host_vulns, 1):
                        details.append(f"\n  Vulnerability #{j}:")
                        details.append(self._format_single_vulnerability_summary(vuln))
        else:
            # Summary view - show hosts in a table format
            details.append("\n### Host Summary")
            details.append("```")
            details.append(f"{'#':<3} {'Hostname':<25} {'Platform':<10} {'Vuln Count':<10} {'Most Severe':<12} {'Host ID'}")
            details.append("-" * 100)
            
            for i, (aid, host_vulns) in enumerate(vulnerability_by_host.items(), 1):
                host_data = hosts_data.get(aid, {})
                hostname = host_data.get("hostname", "Unknown")[:24]
                platform = host_data.get("platform_name", "Unknown")[:9]
                vuln_count = len(host_vulns)
                
                # Find most severe vulnerability for this host
                most_severe = "UNKNOWN"
                severity_priority = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}
                max_priority = 0
                
                for vuln in host_vulns:
                    cve_info = vuln.get("cve", {})
                    severity = cve_info.get("severity", "UNKNOWN")
                    priority = severity_priority.get(severity, 0)
                    if priority > max_priority:
                        max_priority = priority
                        most_severe = severity
                
                details.append(f"{i:<3} {hostname:<25} {platform:<10} {vuln_count:<10} {most_severe:<12} {aid}")
            
            details.append("```")
        
        # CVE Summary
        details.append(f"\n## 🚨 CVE Summary")
        cve_counts = {}
        critical_cves = []
        
        for vuln in vulnerabilities:
            cve_info = vuln.get("cve", {})
            cve_id = cve_info.get("id", "Unknown")
            severity = cve_info.get("severity", "UNKNOWN")
            
            if cve_id != "Unknown":
                cve_counts[cve_id] = cve_counts.get(cve_id, 0) + 1
                if severity == "CRITICAL":
                    critical_cves.append(cve_id)
        
        # Show top CVEs
        if cve_counts:
            sorted_cves = sorted(cve_counts.items(), key=lambda x: x[1], reverse=True)
            details.append(f"\n### Top CVEs by Host Count")
            for cve_id, host_count in sorted_cves[:10]:  # Top 10
                details.append(f"• **{cve_id}**: {host_count} hosts affected")
        
        if critical_cves:
            unique_critical = list(set(critical_cves))
            details.append(f"\n### Critical CVEs Found")
            for cve_id in unique_critical:
                host_count = cve_counts.get(cve_id, 0)
                details.append(f"• **{cve_id}**: {host_count} hosts affected")
        
        # Next steps
        details.append(f"\n## 💡 Next Steps")
        details.append("• Use `get_host_details(host_id)` for detailed information about specific hosts")
        details.append("• Use `get_host_events(host_id)` to check for related security events")
        details.append("• Consider containment actions for hosts with critical vulnerabilities")
        if not include_host_details:
            details.append("• Re-run with `include_host_details=True` for comprehensive host information")
        if not include_vulnerability_details:
            details.append("• Re-run with `include_vulnerability_details=True` to see specific vulnerability details")
        details.append("• Use `search_hosts_advanced()` with specific AIDs for additional host filtering")
        
        return "\n".join(details)
    
    def _format_single_vulnerability_summary(self, vuln_data: Dict[str, Any]) -> str:
        """Format a single vulnerability's information."""
        summary = []
        
        # Basic vulnerability info
        vuln_id = vuln_data.get("id", "Unknown")
        status = vuln_data.get("status", "unknown")
        confidence = vuln_data.get("confidence", "unknown")
        
        summary.append(f"    **Vulnerability ID**: {vuln_id}")
        summary.append(f"    **Status**: {status}")
        summary.append(f"    **Confidence**: {confidence}")
        
        # CVE information
        cve_info = vuln_data.get("cve", {})
        if cve_info:
            cve_id = cve_info.get("id", "N/A")
            severity = cve_info.get("severity", "UNKNOWN")
            base_score = cve_info.get("base_score", "N/A")
            exploit_status = cve_info.get("exploit_status", "N/A")
            is_cisa_kev = cve_info.get("is_cisa_kev", False)
            
            summary.append(f"    **CVE ID**: {cve_id}")
            summary.append(f"    **Severity**: {severity}")
            summary.append(f"    **Base Score**: {base_score}")
            summary.append(f"    **Exploit Status**: {exploit_status}")
            summary.append(f"    **CISA KEV**: {'Yes' if is_cisa_kev else 'No'}")
        
        # Timestamps
        created = vuln_data.get("created_timestamp")
        updated = vuln_data.get("updated_timestamp")
        
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                summary.append(f"    **Created**: {created_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            except:
                summary.append(f"    **Created**: {created}")
        
        if updated:
            try:
                updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                summary.append(f"    **Updated**: {updated_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            except:
                summary.append(f"    **Updated**: {updated}")
        
        return "\n".join(summary) 