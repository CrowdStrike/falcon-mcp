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
        # Consider supporting credential providers or vault integrations
        self.client_id = client_id or os.environ.get("FALCON_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("FALCON_CLIENT_SECRET")
        self.base_url = base_url or os.environ.get("FALCON_BASE_URL")
        
        # Validate credentials are not empty before proceeding
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
        
        # Don't log that credentials were initialized - just log that client was initialized
        logger.info("falcon_client_initialized", base_url=self.base_url or "default")
    
    def _handle_api_response(self, response: Dict[str, Any], operation: str) -> List[Any]:
        """Handle API responses consistently.
        
        Args:
            response: API response dictionary
            operation: Description of the operation for logging
            
        Returns:
            Response body resources
            
        Raises:
            ValueError: If API returns an error
        """
        if response["status_code"] != 200:
            errors = response.get("body", {}).get("errors", ["Unknown error"])
            error_msg = f"Failed to {operation}: {errors}"
            logger.error(f"{operation}_failed", error=error_msg, status_code=response["status_code"])
            raise ValueError(error_msg)
        
        body = response.get("body", {})
        resources = body.get("resources", [])
        
        return resources
    
    def _handle_api_response_body(self, response: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle API responses consistently and return full body.
        
        Args:
            response: API response dictionary
            operation: Description of the operation for logging
            
        Returns:
            Response body
            
        Raises:
            ValueError: If API returns an error
        """
        if response["status_code"] != 200:
            errors = response.get("body", {}).get("errors", ["Unknown error"])
            error_msg = f"Failed to {operation}: {errors}"
            logger.error(f"{operation}_failed", error=error_msg, status_code=response["status_code"])
            raise ValueError(error_msg)
        
        body = response.get("body", {})
        
        return body
    
    def get_host_by_id(self, host_id: str) -> Dict[str, Any]:
        """Get detailed information about a host by its ID.
        
        Args:
            host_id: The Falcon host ID (AID)
            
        Returns:
            Host details dictionary
            
        Raises:
            ValueError: If host not found or API error
        """
        if not host_id or not isinstance(host_id, str):
            raise ValueError("Host ID must be a non-empty string")
        
        # Sanitize host_id for FQL injection prevention
        host_id = host_id.strip().replace("'", "''")  # Escape single quotes for FQL
        
        logger.info("getting_host_by_id", host_id=host_id)
        
        # Get host details
        response = self.hosts.GetDeviceDetails(ids=[host_id])
        
        resources = self._handle_api_response(response, "get host details")
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
        if not hostname or not isinstance(hostname, str):
            raise ValueError("Hostname must be a non-empty string")
        
        # Sanitize hostname for FQL injection prevention
        hostname = hostname.strip().replace("'", "''")  # Escape single quotes for FQL
        
        logger.info("getting_host_by_hostname", hostname=hostname)
        
        # Search for host by hostname
        response = self.hosts.QueryDevicesByFilter(
            filter=f"hostname:'{hostname}'"
        )
        
        host_ids = self._handle_api_response(response, "search for host")
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
        if not host_id or not isinstance(host_id, str):
            raise ValueError("Host ID must be a non-empty string")
        
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        
        if limit > 5000:  # Falcon API limit
            raise ValueError("Limit cannot exceed 5000")
        
        # Sanitize host_id for FQL injection prevention
        host_id = host_id.strip().replace("'", "''")  # Escape single quotes for FQL
        
        logger.info("getting_host_events", host_id=host_id, limit=limit)
        
        # Search for detections on this host
        response = self.detects.QueryDetects(
            filter=f"device.device_id:'{host_id}'",
            limit=limit,
            sort="first_behavior|desc"
        )
        
        detection_ids = self._handle_api_response(response, "search detections")
        if not detection_ids:
            logger.info("no_detections_found", host_id=host_id)
            return []
        
        # Get detection details
        details_response = self.detects.GetDetectSummaries(ids=detection_ids)
        
        events = self._handle_api_response(details_response, "get detection details")
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
        
        # Sanitize string inputs for FQL injection prevention
        if query_filter:
            query_filter = query_filter.strip().replace("'", "''")  # Escape single quotes for FQL
        
        sort = sort.strip()
        fields = fields.strip()
        
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
        
        search_results = self._handle_api_response_body(response, "search hosts")
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
        # Validate input parameters
        if not isinstance(query_filter, str):
            raise ValueError("Query filter must be a string")
        
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        
        if limit > 5000:  # Falcon API limit
            raise ValueError("Limit cannot exceed 5000")
        
        if not isinstance(sort, str):
            raise ValueError("Sort parameter must be a string")
        
        if not isinstance(facet, str):
            raise ValueError("Facet parameter must be a string")
        
        # Sanitize string inputs for FQL injection prevention
        if query_filter:
            query_filter = query_filter.strip().replace("'", "''")  # Escape single quotes for FQL
        
        sort = sort.strip()
        facet = facet.strip()
        
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
        
        search_results = self._handle_api_response_body(response, "search vulnerabilities")
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
        if not vulnerability_ids or not isinstance(vulnerability_ids, list):
            raise ValueError("Vulnerability IDs must be provided as a non-empty list")
        
        if not all(isinstance(vid, str) and vid.strip() for vid in vulnerability_ids):
            raise ValueError("All vulnerability IDs must be non-empty strings")
        
        if len(vulnerability_ids) > 400:  # Falcon API typical limit for batch operations
            raise ValueError("Too many vulnerability IDs provided (maximum: 400)")
        
        # Sanitize vulnerability IDs
        sanitized_ids = [vid.strip().replace("'", "''") for vid in vulnerability_ids]
        
        logger.info("getting_vulnerability_details", vulnerability_count=len(sanitized_ids))
        
        # Get vulnerability details
        response = self.vulnerabilities.getVulnerabilities(ids=sanitized_ids)
        
        resources = self._handle_api_response(response, "get vulnerability details")
        logger.info("vulnerability_details_retrieved", vulnerability_count=len(resources))
        
        return resources 