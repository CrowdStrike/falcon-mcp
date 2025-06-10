"""CrowdStrike Falcon API client."""

import os
from typing import Dict, List, Optional, Any
import structlog
from falconpy import Hosts, Detects, SpotlightVulnerabilities

logger = structlog.get_logger(__name__)


class FalconClient:
    """CrowdStrike Falcon API client wrapper."""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, 
                 base_url: Optional[str] = None):
        """Initialize Falcon client.
        
        Args:
            client_id: Falcon API client ID (defaults to FALCON_CLIENT_ID env var)
            client_secret: Falcon API client secret (defaults to FALCON_CLIENT_SECRET env var)  
            base_url: Falcon API base URL (defaults to FALCON_BASE_URL env var or auto-detect)
        """
        self.client_id = client_id or os.getenv("FALCON_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("FALCON_CLIENT_SECRET")
        self.base_url = base_url or os.getenv("FALCON_BASE_URL")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Falcon API credentials must be provided via parameters or environment variables")
        
        # Initialize service classes
        auth_config = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        if self.base_url:
            auth_config["base_url"] = self.base_url
            
        self.hosts = Hosts(**auth_config)
        self.detects = Detects(**auth_config)
        self.vulnerabilities = SpotlightVulnerabilities(**auth_config)
        
        logger.info("falcon_client_initialized")
    
    def get_host_by_id(self, host_id: str) -> Dict[str, Any]:
        """Get detailed information about a host by its ID.
        
        Args:
            host_id: The Falcon host ID (AID)
            
        Returns:
            Host details dictionary
            
        Raises:
            ValueError: If host not found or API error
        """
        logger.info("getting_host_by_id", host_id=host_id)
        
        # Get host details
        response = self.hosts.GetDeviceDetails(ids=[host_id])
        
        if response["status_code"] != 200:
            error_msg = f"Failed to get host details: {response.get('body', {}).get('errors', 'Unknown error')}"
            logger.error("host_details_failed", host_id=host_id, error=error_msg)
            raise ValueError(error_msg)
        
        resources = response.get("body", {}).get("resources", [])
        if not resources:
            error_msg = f"Host with ID {host_id} not found"
            logger.error("host_not_found", host_id=host_id)
            raise ValueError(error_msg)
        
        host_data = resources[0]
        logger.info("host_details_retrieved", host_id=host_id, hostname=host_data.get("hostname"))
        
        return host_data
    
    def get_host_by_hostname(self, hostname: str) -> Dict[str, Any]:
        """Get detailed information about a host by its hostname.
        
        Args:
            hostname: The hostname to search for
            
        Returns:
            Host details dictionary
            
        Raises:
            ValueError: If host not found or API error
        """
        logger.info("getting_host_by_hostname", hostname=hostname)
        
        # Search for host by hostname
        response = self.hosts.QueryDevicesByFilter(
            filter=f"hostname:'{hostname}'"
        )
        
        if response["status_code"] != 200:
            error_msg = f"Failed to search for host: {response.get('body', {}).get('errors', 'Unknown error')}"
            logger.error("host_search_failed", hostname=hostname, error=error_msg)
            raise ValueError(error_msg)
        
        host_ids = response.get("body", {}).get("resources", [])
        if not host_ids:
            error_msg = f"Host with hostname '{hostname}' not found"
            logger.error("host_not_found", hostname=hostname)
            raise ValueError(error_msg)
        
        # Get details for the first matching host
        return self.get_host_by_id(host_ids[0])
    
    def get_host_events(self, host_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent detection events for a host.
        
        Args:
            host_id: The Falcon host ID (AID)
            limit: Maximum number of events to return (default: 10)
            
        Returns:
            List of detection events
            
        Raises:
            ValueError: If API error occurs
        """
        logger.info("getting_host_events", host_id=host_id, limit=limit)
        
        # Search for detections on this host
        response = self.detects.QueryDetects(
            filter=f"device.device_id:'{host_id}'",
            limit=limit,
            sort="first_behavior|desc"
        )
        
        if response["status_code"] != 200:
            error_msg = f"Failed to search detections: {response.get('body', {}).get('errors', 'Unknown error')}"
            logger.error("detections_search_failed", host_id=host_id, error=error_msg)
            raise ValueError(error_msg)
        
        detection_ids = response.get("body", {}).get("resources", [])
        if not detection_ids:
            logger.info("no_detections_found", host_id=host_id)
            return []
        
        # Get detection details
        details_response = self.detects.GetDetectSummaries(ids=detection_ids)
        
        if details_response["status_code"] != 200:
            error_msg = f"Failed to get detection details: {details_response.get('body', {}).get('errors', 'Unknown error')}"
            logger.error("detection_details_failed", host_id=host_id, error=error_msg)
            raise ValueError(error_msg)
        
        events = details_response.get("body", {}).get("resources", [])
        logger.info("host_events_retrieved", host_id=host_id, event_count=len(events))
        
        return events
    
    def search_hosts_combined(self, query_filter: str = "", limit: int = 100, 
                             sort: str = "hostname.asc", fields: str = "") -> Dict[str, Any]:
        """Search for hosts using advanced filtering and return full host records.
        
        Args:
            query_filter: FQL filter expression to search hosts
            limit: Maximum number of hosts to return (1-5000)
            sort: Sort expression (property.direction format)
            fields: Comma-separated list of fields to return
            
        Returns:
            Search results with full host records
            
        Raises:
            ValueError: If search fails or API error
        """
        logger.info("search_hosts_combined", query_filter=query_filter, limit=limit, sort=sort, fields=fields)
        
        # Build parameters for the API call
        params = {
            "limit": limit,
            "sort": sort
        }
        
        if query_filter:
            params["filter"] = query_filter
            
        if fields:
            params["fields"] = fields
        
        # Use the combined search endpoint that returns full host records
        response = self.hosts.CombinedDevicesByFilter(**params)
        
        if response["status_code"] != 200:
            error_msg = f"Failed to search hosts: {response.get('body', {}).get('errors', 'Unknown error')}"
            logger.error("host_search_combined_failed", query_filter=query_filter, error=error_msg)
            raise ValueError(error_msg)
        
        search_results = response.get("body", {})
        resources = search_results.get("resources", [])
        
        logger.info("host_search_combined_completed", 
                   query_filter=query_filter, 
                   hosts_found=len(resources), 
                   limit=limit)
        
        return search_results
    
    def search_vulnerabilities_combined(self, query_filter: str = "", limit: int = 100,
                                      sort: str = "created_timestamp.desc", facet: str = "") -> Dict[str, Any]:
        """Search for vulnerabilities using advanced filtering and return full vulnerability records.
        
        Args:
            query_filter: FQL filter expression to search vulnerabilities
            limit: Maximum number of vulnerabilities to return (1-5000)
            sort: Sort expression (property.direction format)
            facet: Detail blocks to include (host_info, remediation, cve, evaluation_logic)
            
        Returns:
            Search results with full vulnerability records
            
        Raises:
            ValueError: If search fails or API error
        """
        logger.info("search_vulnerabilities_combined", query_filter=query_filter, limit=limit, sort=sort, facet=facet)
        
        # Build parameters for the API call
        params = {
            "limit": limit,
            "sort": sort
        }
        
        if query_filter:
            params["filter"] = query_filter
            
        if facet:
            params["facet"] = facet
        
        # Use the combined search endpoint that returns full vulnerability records
        response = self.vulnerabilities.combinedQueryVulnerabilities(**params)
        
        if response["status_code"] != 200:
            error_msg = f"Failed to search vulnerabilities: {response.get('body', {}).get('errors', 'Unknown error')}"
            logger.error("vulnerability_search_combined_failed", query_filter=query_filter, error=error_msg)
            raise ValueError(error_msg)
        
        search_results = response.get("body", {})
        resources = search_results.get("resources", [])
        
        logger.info("vulnerability_search_combined_completed", 
                   query_filter=query_filter, 
                   vulnerabilities_found=len(resources), 
                   limit=limit)
        
        return search_results
    
    def get_vulnerability_details(self, vulnerability_ids: List[str]) -> List[Dict[str, Any]]:
        """Get detailed information about vulnerabilities by their IDs.
        
        Args:
            vulnerability_ids: List of vulnerability IDs to retrieve
            
        Returns:
            List of vulnerability detail dictionaries
            
        Raises:
            ValueError: If API error occurs
        """
        logger.info("getting_vulnerability_details", vulnerability_count=len(vulnerability_ids))
        
        # Get vulnerability details
        response = self.vulnerabilities.getVulnerabilities(ids=vulnerability_ids)
        
        if response["status_code"] != 200:
            error_msg = f"Failed to get vulnerability details: {response.get('body', {}).get('errors', 'Unknown error')}"
            logger.error("vulnerability_details_failed", error=error_msg)
            raise ValueError(error_msg)
        
        resources = response.get("body", {}).get("resources", [])
        logger.info("vulnerability_details_retrieved", vulnerability_count=len(resources))
        
        return resources 