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
        filter: Optional[str] = Field(default=None, examples={"agent_id:'77d11725xxxxxxxxxxxxxxxxxxxxc48ca19'", "status:'new'"}),
        limit: Optional[int] = Field(default=100, ge=1, le=9999),
        offset: Optional[int] = Field(default=0, ge=0),
        q: Optional[str] = Field(default=None),
        sort: Optional[str] = Field(default=None, examples={"severity.desc", "timestamp.desc"}),
        include_hidden: Optional[bool] = Field(default=True),
    ) -> List[Dict[str, Any]]:
        """Search for detections in your CrowdStrike environment.

        Args:
            filter: Filter detections using a query in Falcon Query Language (FQL) An asterisk wildcard * includes all results. You must use FQL and never use JSON.
            limit: The maximum number of detections to return in this response (default: 100; max: 9999). Use with the offset parameter to manage pagination of results.
            offset: The first detection to return, where 0 is the latest detection. Use with the limit parameter to manage pagination of results.
            q: Search all detection metadata for the provided string.
            sort: Sort detections using these options:
                timestamp: Timestamp when the alert occurred
                created_timestamp: When the alert was created
                updated_timestamp: When the alert was last modified
                severity: Severity level of the alert (1-100, recommended when filtering by severity)
                confidence: Confidence level of the alert (1-100)
                agent_id: Agent ID associated with the alert

                Sort either asc (ascending) or desc (descending).
                Both formats are supported: 'severity.desc' or 'severity|desc'

                When searching for high severity alerts, use 'severity.desc' to get the highest severity alerts first.
                For chronological ordering, use 'timestamp.desc' for most recent alerts first.

                Examples: 'severity.desc', 'timestamp.desc'
            include_hidden: Whether to include hidden detections (default: True). When True, shows all detections including previously hidden ones for comprehensive visibility.

    🎯 FALCON QUERY LANGUAGE (FQL) COMPREHENSIVE GUIDE FOR DETECTIONS:

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

    🚨 DETECTION PROPERTIES (Complete List):

    === IDENTIFICATION & CORE ===
    • composite_id: Unique detection identifier
    • aggregate_id: Related detection group identifier
    • cid: Customer ID
    • agent_id: Falcon agent identifier
    • pattern_id: Detection pattern identifier

    === ASSIGNMENT & WORKFLOW ===
    • assigned_to_name: Person assigned to this detection
    • assigned_to_uid: Assigned user identifier
    • assigned_to_uuid: Assigned user UUID
    • status: Detection status (new, in_progress, closed, reopened)

    === TIMESTAMPS ===
    • created_timestamp: When detection was created
    • updated_timestamp: Last modification time
    • timestamp: Detection occurrence timestamp

    === THREAT INTELLIGENCE ===
    • confidence: Confidence level (1-100)
    • severity: Detection severity level
    • tactic: MITRE ATT&CK tactic
    • tactic_id: MITRE ATT&CK tactic ID
    • technique: MITRE ATT&CK technique
    • technique_id: MITRE ATT&CK technique ID
    • objective: Attack objective description

    === DETECTION METADATA ===
    • name: Detection name/title
    • display_name: Human-readable detection name
    • description: Detection description
    • type: Detection type classification
    • scenario: Detection scenario

    === SYSTEM & PLATFORM ===
    • platform: Operating system platform
    • show_in_ui: Whether detection appears in UI (true/false)
    • data_domains: Data classification domains

    === PRODUCT FILTERING ===
    • product: Source Falcon product
        - 'epp' (Endpoint Protection)
        - 'idp' (Identity Protection)
        - 'mobile' (Falcon for Mobile)
        - 'xdr' (Falcon XDR)
        - 'overwatch' (OverWatch)
        - 'cwpp' (Cloud Workload Protection)
        - 'ngsiem' (Next-Gen SIEM)
        - 'thirdparty' (Third party data)
        - 'data-protection' (Data Protection)

    === SOURCE INFORMATION ===
    • source_products: Products that generated this detection
    • source_vendors: Vendor sources for the detection

    === TAGS & CLASSIFICATION ===
    • tags: Detection classification tags

    💡 PRACTICAL DETECTION SEARCH EXAMPLES:

    === STATUS-BASED SEARCHES ===
    Find new detections:
    status:'new'

    Find detections in progress:
    status:'in_progress'

    Find closed detections:
    status:'closed'

    Find reopened detections:
    status:'reopened'

    === PRODUCT-SPECIFIC SEARCHES ===
    Find endpoint protection detections:
    product:'epp'

    Find identity protection detections:
    product:'idp'

    Find XDR detections:
    product:'xdr'

    Find OverWatch detections:
    product:'overwatch'

    === SEVERITY & CONFIDENCE SEARCHES ===
    Find high confidence detections:
    confidence:>80

    Find medium to high confidence:
    confidence:>=50

    🔥 SEVERITY NUMERIC MAPPING (Critical for Proper Filtering):
    Based on CrowdStrike Falcon API data:
    • Critical: severity:>=90 (or severity:90 exactly)
    • High: severity:>=70 (or severity:70 exactly)
    • Medium: severity:>=50 (or severity:50 exactly)
    • Low: severity:>=20 (covers range 20-40)
    • Informational: severity:<=10 (covers range 2-5)

    Find critical severity detections only:
    severity:>=90

    Find high severity detections (includes critical):
    severity:>=70

    Find medium severity and above (includes high & critical):
    severity:>=50

    Find high severity detections only (excludes critical):
    severity:70

    Find informational detections:
    severity:<=10

    === ASSIGNMENT SEARCHES ===
    Find unassigned detections:
    assigned_to_name:!*

    Find detections assigned to specific analyst:
    assigned_to_name:'john.doe'

    === TIME-BASED SEARCHES ===
    Find recent detections (last 24 hours):
    created_timestamp:>'2024-01-20T00:00:00Z'

    Find detections from specific date range:
    created_timestamp:>='2024-01-15T00:00:00Z'+created_timestamp:<='2024-01-20T00:00:00Z'

    Find recently updated detections:
    updated_timestamp:>'2024-01-19T00:00:00Z'

    === THREAT INTELLIGENCE SEARCHES ===
    Find detections with specific tactic:
    tactic:'Persistence'

    Find detections with technique ID:
    technique_id:'T1055'

    Find detections with specific objective:
    objective:'*credential*'

    === ADVANCED COMBINED SEARCHES ===
    Find new high-confidence endpoint detections:
    status:'new'+confidence:>75+product:'epp'

    Find assigned XDR detections that are in progress:
    product:'xdr'+status:'in_progress'+assigned_to_name:*

    Find recent high-severity unassigned detections:
    created_timestamp:>'2024-01-18T00:00:00Z'+assigned_to_name:!*+confidence:>80

    Find OverWatch detections with persistence tactics:
    product:'overwatch'+tactic:'Persistence'

    === BULK FILTERING SEARCHES ===
    Find detections from multiple products:
    (product:'epp'),(product:'xdr'),(product:'idp')

    Find detections in various active states:
    (status:'new'),(status:'in_progress')

    Find detections needing attention (new or reopened):
    (status:'new'),(status:'reopened')

    === INVESTIGATION-FOCUSED SEARCHES ===
    Find detections with specific pattern:
    pattern_id:'12345'

    Find related detections by aggregate:
    aggregate_id:'agg-67890'

    Find detections with specific tags:
    tags:'malware'

    Find detections that show in UI:
    show_in_ui:true

    🚀 USAGE EXAMPLES:

    # Find new endpoint protection detections sorted by severity
    search_detections("status:'new'+product:'epp'", limit=50, sort="severity.desc")

    # Find high-confidence XDR detections from last week
    search_detections("product:'xdr'+confidence:>80+created_timestamp:>'2024-01-15T00:00:00Z'", limit=25)

    # Find unassigned detections across all products
    search_detections("assigned_to_name:!*", limit=100, sort="timestamp.desc")

    # Find OverWatch detections with specific tactics
    search_detections("product:'overwatch'+tactic:'Initial Access'", limit=50)

    # Find detections that need immediate attention
    search_detections("(status:'new'),(status:'reopened')+confidence:>75", sort="timestamp.desc")

    ⚠️ IMPORTANT NOTES:
    • Use single quotes around string values: 'value'
    • Use square brackets for exact matches: ['exact_value']
    • Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
    • Status values are: new, in_progress, closed, reopened
    • Product filtering enables product-specific detection analysis
    • Confidence values range from 1-100
    • Complex queries may take longer to execute
    • include_hidden parameter shows previously hidden detections

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

        # Define the operation name - migrated from QueryDetects to GetQueriesAlertsV2
        operation = "GetQueriesAlertsV2"

        logger.debug("Searching detections with params: %s", params)

        # Make the API request
        response = self.client.command(operation, parameters=params)

        # Use handle_api_response to get detection IDs (now composite_ids)
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
            # Use the enhanced base method with composite_ids and include_hidden
            details = self._base_get_by_ids(
                operation="PostEntitiesAlertsV2",
                ids=detection_ids,
                id_key="composite_ids",
                include_hidden=include_hidden
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
        include_hidden: Optional[bool] = Field(default=True),
    ) -> List[Dict[str, Any]]|Dict[str, Any]:
        """View information about detections. Gets detailed information about a specific detection.

        Args:
            ids: ID(s) of the detections to retrieve. View key attributes of detections, including the associated host, disposition, objective/tactic/technique, adversary, and more. Specify one or more detection IDs (max 1000 per request). Find detection IDs with the search_detections operation, the Falcon console, or the Streaming API.
            include_hidden: Whether to include hidden detections (default: True). When True, shows all detections including previously hidden ones for comprehensive visibility.

        Returns:
            Detection details
        """
        logger.debug("Getting detection details for ID: %s", ids)

        # Use the enhanced base method - composite_ids parameter matches ids for backward compatibility
        return self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=ids,
            id_key="composite_ids",
            include_hidden=include_hidden,
        )
