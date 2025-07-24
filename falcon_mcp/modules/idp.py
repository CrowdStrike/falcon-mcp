# pylint: disable=too-many-arguments,too-many-positional-arguments,redefined-builtin
"""
Identity Protection (IDP) module for Falcon MCP Server

This module provides tool for accessing and managing CrowdStrike Falcon Identity Protection capabilities.
Core use cases:
1. Entity Lookup & Investigation
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from pydantic import Field

from falcon_mcp.common.errors import handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import sanitize_input
from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)


class IdpModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon Identity Protection."""

    def register_tools(self, server: FastMCP) -> None:
        """Register IDP tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Entity Investigation Tool
        self._add_tool(server, self.investigate_entity, name="idp_investigate_entity")

    # ==========================================
    #  Entity Investigation Tool
    # ==========================================

    def investigate_entity(
        self,
        # Entity Identification (Required - at least one)
        entity_ids: Optional[List[str]] = Field(
            default=None,
            description="List of specific entity IDs to investigate (e.g., ['entity-001'])",
        ),
        entity_names: Optional[List[str]] = Field(
            default=None,
            description="List of entity names to search for (e.g., ['Administrator', 'John Doe']). When combined with other parameters, uses AND logic.",
        ),
        email_addresses: Optional[List[str]] = Field(
            default=None,
            description="List of email addresses to investigate (e.g., ['user@example.com']). When combined with other parameters, uses AND logic.",
        ),
        ip_addresses: Optional[List[str]] = Field(
            default=None,
            description="List of IP addresses/endpoints to investigate (e.g., ['1.1.1.1']). When combined with other parameters, uses AND logic.",
        ),
        domain_names: Optional[List[str]] = Field(
            default=None,
            description="List of domain names to search for (e.g., ['XDRHOLDINGS.COM', 'CORP.LOCAL']). When combined with other parameters, uses AND logic. Example: entity_names=['Administrator'] + domain_names=['DOMAIN.COM'] finds Administrator user in that specific domain.",
        ),
        # Investigation Scope Control
        investigation_types: Optional[List[str]] = Field(
            default=["entity_details"],
            description="Types of investigation to perform: 'entity_details', 'timeline_analysis', 'relationship_analysis', 'risk_assessment'. Use multiple for comprehensive analysis.",
        ),
        # Timeline Parameters (when timeline_analysis is included)
        timeline_start_time: Optional[str] = Field(
            default=None,
            description="Start time for timeline analysis in ISO format (e.g., '2024-01-01T00:00:00Z')",
        ),
        timeline_end_time: Optional[str] = Field(
            default=None, description="End time for timeline analysis in ISO format"
        ),
        timeline_event_types: Optional[List[str]] = Field(
            default=None,
            description="Filter timeline by event types: 'ACTIVITY', 'NOTIFICATION', 'THREAT', 'ENTITY', 'AUDIT', 'POLICY', 'SYSTEM'",
        ),
        # Relationship Parameters (when relationship_analysis is included)
        relationship_depth: Optional[int] = Field(
            default=2,
            ge=1,
            le=3,
            description="Depth of relationship analysis (1-3 levels)",
        ),
        # General Parameters
        limit: Optional[int] = Field(
            default=50, ge=1, le=200, description="Maximum number of results to return"
        ),
        include_associations: Optional[bool] = Field(
            default=True,
            description="Include entity associations and relationships in results",
        ),
        include_accounts: Optional[bool] = Field(
            default=True, description="Include account information in results"
        ),
        include_incidents: Optional[bool] = Field(
            default=True, description="Include open security incidents in results"
        ),
    ) -> Dict[str, Any]:
        """Comprehensive entity investigation tool.

        This tool provides complete entity investigation capabilities including:
        - Entity search and details lookup
        - Activity timeline analysis
        - Relationship and association mapping
        - Risk assessment
        """
        logger.debug("Starting comprehensive entity investigation")

        # Step 1: Validate inputs
        validation_error = self._validate_entity_identifiers(
            entity_ids,
            entity_names,
            email_addresses,
            ip_addresses,
            domain_names,
            investigation_types,
        )
        if validation_error:
            return validation_error

        # Step 2: Entity Resolution - Find entities from various identifiers
        logger.debug("Resolving entities from provided identifiers")
        search_criteria = {
            "entity_ids": entity_ids,
            "entity_names": entity_names,
            "email_addresses": email_addresses,
            "ip_addresses": ip_addresses,
            "domain_names": domain_names,
        }

        resolved_entity_ids = self._resolve_entities(
            {
                "entity_ids": entity_ids if entity_ids is not None else None,
                "entity_names": entity_names if entity_names is not None else None,
                "email_addresses": email_addresses
                if email_addresses is not None
                else None,
                "ip_addresses": ip_addresses if ip_addresses is not None else None,
                "domain_names": domain_names if domain_names is not None else None,
                "limit": limit,
            }
        )

        # Check if entity resolution failed
        if isinstance(resolved_entity_ids, dict) and "error" in resolved_entity_ids:
            return self._create_error_response(
                resolved_entity_ids["error"], 0, investigation_types, search_criteria
            )

        if not resolved_entity_ids:
            return self._create_error_response(
                "No entities found matching the provided criteria",
                0,
                investigation_types,
                search_criteria,
            )

        logger.debug(f"Resolved {len(resolved_entity_ids)} entities for investigation")

        # Step 3: Execute investigations based on requested types
        investigation_results = {}
        investigation_params = {
            "include_associations": include_associations,
            "include_accounts": include_accounts,
            "include_incidents": include_incidents,
            "timeline_start_time": timeline_start_time,
            "timeline_end_time": timeline_end_time,
            "timeline_event_types": timeline_event_types,
            "relationship_depth": relationship_depth,
            "limit": limit,
        }

        for investigation_type in investigation_types:
            result = self._execute_single_investigation(
                investigation_type, resolved_entity_ids, investigation_params
            )
            if "error" in result:
                return self._create_error_response(
                    f"Investigation failed during {investigation_type}: {result['error']}",
                    len(resolved_entity_ids),
                    investigation_types,
                )
            investigation_results[investigation_type] = result

        # Step 4: Synthesize comprehensive response
        return self._synthesize_investigation_response(
            resolved_entity_ids,
            investigation_results,
            {
                "investigation_types": investigation_types,
                "search_criteria": search_criteria,
            },
        )

    # ==========================================
    # Investigation Helper Methods
    # ==========================================

    def _validate_entity_identifiers(
        self,
        entity_ids,
        entity_names,
        email_addresses,
        ip_addresses,
        domain_names,
        investigation_types,
    ):
        """Validate that at least one entity identifier is provided."""
        if not any(
            [entity_ids, entity_names, email_addresses, ip_addresses, domain_names]
        ):
            return {
                "error": "At least one entity identifier must be provided (entity_ids, entity_names, email_addresses, ip_addresses, or domain_names)",
                "investigation_summary": {
                    "entity_count": 0,
                    "investigation_types": investigation_types,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "failed",
                },
            }
        return None

    def _create_error_response(
        self, error_message, entity_count, investigation_types, search_criteria=None
    ):
        """Create a standardized error response."""
        response = {
            "error": error_message,
            "investigation_summary": {
                "entity_count": entity_count,
                "investigation_types": investigation_types,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "failed",
            },
        }
        if search_criteria:
            response["search_criteria"] = search_criteria
        return response

    def _execute_single_investigation(
        self, investigation_type, resolved_entity_ids, params
    ):
        """Execute a single investigation type and return results or error."""
        logger.debug(f"Executing {investigation_type} investigation")

        if investigation_type == "entity_details":
            return self._get_entity_details_batch(
                resolved_entity_ids,
                {
                    "include_associations": params.get("include_associations", True),
                    "include_accounts": params.get("include_accounts", True),
                    "include_incidents": params.get("include_incidents", True),
                },
            )
        if investigation_type == "timeline_analysis":
            return self._get_entity_timelines_batch(
                resolved_entity_ids,
                {
                    "start_time": params.get("timeline_start_time"),
                    "end_time": params.get("timeline_end_time"),
                    "event_types": params.get("timeline_event_types"),
                    "limit": params.get("limit", 50),
                },
            )
        if investigation_type == "relationship_analysis":
            return self._analyze_relationships_batch(
                resolved_entity_ids,
                {
                    "relationship_depth": params.get("relationship_depth", 2),
                    "include_risk_context": True,
                    "limit": params.get("limit", 50),
                },
            )
        if investigation_type == "risk_assessment":
            return self._assess_risks_batch(
                resolved_entity_ids, {"include_risk_factors": True}
            )

        logger.warning(f"Unknown investigation type: {investigation_type}")
        return {"error": f"Unknown investigation type: {investigation_type}"}

    # ==========================================
    # GraphQL Query Building Helper Methods
    # ==========================================

    def _build_entity_details_query(
        self,
        entity_ids: List[str],
        include_risk_factors: bool,
        include_associations: bool,
        include_incidents: bool,
        include_accounts: bool,
    ) -> str:
        """Build GraphQL query for detailed entity information."""
        entity_ids_json = json.dumps(entity_ids)

        # Start with minimal safe fields
        fields = [
            "entityId",
            "primaryDisplayName",
            "secondaryDisplayName",
            "type",
            "riskScore",
            "riskScoreSeverity",
        ]

        if include_risk_factors:
            fields.append("""
                riskFactors {
                    type
                    severity
                }
            """)

        if include_associations:
            fields.append("""
                associations {
                    bindingType
                    ... on EntityAssociation {
                        entity {
                            entityId
                            primaryDisplayName
                            secondaryDisplayName
                            type
                        }
                    }
                    ... on LocalAdminLocalUserAssociation {
                        accountName
                    }
                    ... on LocalAdminDomainEntityAssociation {
                        entityType
                        entity {
                            entityId
                            primaryDisplayName
                            secondaryDisplayName
                        }
                    }
                }
            """)

        if include_incidents:
            fields.append("""
                openIncidents(first: 10) {
                    nodes {
                        type
                        startTime
                        endTime
                        compromisedEntities {
                            entityId
                            primaryDisplayName
                        }
                    }
                }
            """)

        if include_accounts:
            fields.append("""
                accounts {
                    ... on ActiveDirectoryAccountDescriptor {
                        domain
                        samAccountName
                        ou
                        servicePrincipalNames
                        passwordAttributes {
                            lastChange
                            strength
                        }
                        expirationTime
                    }
                    ... on SsoUserAccountDescriptor {
                        dataSource
                        mostRecentActivity
                        title
                        creationTime
                        passwordAttributes {
                            lastChange
                        }
                    }
                    ... on AzureCloudServiceAdapterDescriptor {
                        registeredTenantType
                        appOwnerOrganizationId
                        publisherDomain
                        signInAudience
                    }
                    ... on CloudServiceAdapterDescriptor {
                        dataSourceParticipantIdentifier
                    }
                }
            """)

        fields_string = "\n".join(fields)

        return f"""
        query {{
            entities(entityIds: {entity_ids_json}, first: 50) {{
                nodes {{
                    {fields_string}
                }}
            }}
        }}
        """

    def _build_timeline_query(
        self,
        entity_id: str,
        start_time: Optional[str],
        end_time: Optional[str],
        event_types: Optional[List[str]],
        limit: int,
    ) -> str:
        """Build GraphQL query for entity timeline."""
        filters = [f'sourceEntityQuery: {{entityIds: ["{entity_id}"]}}']

        if start_time and isinstance(start_time, str):
            filters.append(f'startTime: "{start_time}"')
        if end_time and isinstance(end_time, str):
            filters.append(f'endTime: "{end_time}"')
        if event_types and isinstance(event_types, list):
            # Format event types as unquoted GraphQL enums
            categories_str = "[" + ", ".join(event_types) + "]"
            filters.append(f"categories: {categories_str}")

        filter_string = ", ".join(filters)

        return f"""
        query {{
            timeline({filter_string}, first: {limit}) {{
                nodes {{
                    eventId
                    eventType
                    eventSeverity
                    timestamp
                    ... on TimelineUserOnEndpointActivityEvent {{
                        sourceEntity {{
                            entityId
                            primaryDisplayName
                        }}
                        targetEntity {{
                            entityId
                            primaryDisplayName
                        }}
                    }}
                    ... on TimelineAuthenticationEvent {{
                        sourceEntity {{
                            entityId
                            primaryDisplayName
                        }}
                        targetEntity {{
                            entityId
                            primaryDisplayName
                        }}
                    }}
                    ... on TimelineAlertEvent {{
                        sourceEntity {{
                            entityId
                            primaryDisplayName
                        }}
                    }}
                    ... on TimelineDceRpcEvent {{
                        sourceEntity {{
                            entityId
                            primaryDisplayName
                        }}
                        targetEntity {{
                            entityId
                            primaryDisplayName
                        }}
                    }}
                    ... on TimelineFailedAuthenticationEvent {{
                        sourceEntity {{
                            entityId
                            primaryDisplayName
                        }}
                        targetEntity {{
                            entityId
                            primaryDisplayName
                        }}
                    }}
                    ... on TimelineFileOperationEvent {{
                        targetEntity {{
                            entityId
                            primaryDisplayName
                        }}
                    }}
                    ... on TimelineConnectorConfigurationEvent {{
                        category
                    }}
                    ... on TimelineConnectorConfigurationAddedEvent {{
                        category
                    }}
                    ... on TimelineConnectorConfigurationDeletedEvent {{
                        category
                    }}
                    ... on TimelineConnectorConfigurationModifiedEvent {{
                        category
                    }}
                }}
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
            }}
        }}
        """

    def _build_relationship_analysis_query(
        self,
        entity_id: str,
        relationship_depth: int,
        include_risk_context: bool,
        limit: int,
    ) -> str:
        """Build GraphQL query for relationship analysis."""
        risk_fields = ""
        if include_risk_context:
            risk_fields = """
                riskScore
                riskScoreSeverity
                riskFactors {
                    type
                    severity
                }
            """

        # Build nested association fields based on relationship_depth
        def build_association_fields(depth: int) -> str:
            if depth <= 0:
                return ""

            nested_associations = ""
            if depth > 1:
                nested_associations = build_association_fields(depth - 1)

            return f"""
                associations {{
                    bindingType
                    ... on EntityAssociation {{
                        entity {{
                            entityId
                            primaryDisplayName
                            secondaryDisplayName
                            type
                            {risk_fields}
                            {nested_associations}
                        }}
                    }}
                    ... on LocalAdminLocalUserAssociation {{
                        accountName
                    }}
                    ... on LocalAdminDomainEntityAssociation {{
                        entityType
                        entity {{
                            entityId
                            primaryDisplayName
                            secondaryDisplayName
                            type
                            {risk_fields}
                            {nested_associations}
                        }}
                    }}
                }}
            """

        association_fields = build_association_fields(relationship_depth)

        return f"""
        query {{
            entities(entityIds: ["{entity_id}"], first: {limit}) {{
                nodes {{
                    entityId
                    primaryDisplayName
                    secondaryDisplayName
                    type
                    {risk_fields}
                    {association_fields}
                }}
            }}
        }}
        """

    def _build_risk_assessment_query(
        self, entity_ids: List[str], include_risk_factors: bool
    ) -> str:
        """Build GraphQL query for risk assessment."""
        entity_ids_json = json.dumps(entity_ids)

        risk_fields = """
            riskScore
            riskScoreSeverity
        """

        if include_risk_factors:
            risk_fields += """
                riskFactors {
                    type
                    severity
                }
            """

        return f"""
        query {{
            entities(entityIds: {entity_ids_json}, first: 50) {{
                nodes {{
                    entityId
                    primaryDisplayName
                    {risk_fields}
                }}
            }}
        }}
        """

    def _resolve_entities(
        self, identifiers: Dict[str, Any]
    ) -> List[str] | Dict[str, Any]:
        """Resolve entity IDs from various identifier types using unified AND-based query.

        All provided identifiers are combined using AND logic in a single GraphQL query.
        For example: entity_names=["Administrator"] + domain_names=["XDRHOLDINGS.COM"]
        will find entities that match BOTH criteria.

        Returns:
            List[str]: List of resolved entity IDs on success
            Dict[str, Any]: Error response on failure
        """
        resolved_ids = []

        # Direct entity IDs - no resolution needed
        entity_ids = identifiers.get("entity_ids")
        if entity_ids and isinstance(entity_ids, list):
            resolved_ids.extend(entity_ids)

        # Check if we have conflicting entity types (USER vs ENDPOINT)
        email_addresses = identifiers.get("email_addresses")
        ip_addresses = identifiers.get("ip_addresses")
        has_user_criteria = bool(email_addresses)
        has_endpoint_criteria = bool(ip_addresses)

        # If we have both USER and ENDPOINT criteria, we need separate queries
        if has_user_criteria and has_endpoint_criteria:
            # This is a conflict - cannot search for both USER and ENDPOINT in same query
            # For now, prioritize USER entities (emails) over ENDPOINT entities (IPs)
            logger.warning(
                "Cannot combine email addresses (USER) and IP addresses (ENDPOINT) in single query. Prioritizing USER entities."
            )
            ip_addresses = None

        # Build unified GraphQL query with AND logic
        query_filters = []
        query_fields = []

        # Add entity names filter
        self._add_entity_filters(identifiers, query_fields, query_filters)
        # Add email addresses filter (USER entities)
        self._add_email_filter(email_addresses, query_fields, query_filters)
        # Add IP addresses filter (ENDPOINT entities) - only if no USER criteria
        self._add_ip_filter(
            has_user_criteria, ip_addresses, query_fields, query_filters
        )
        # Add domain names filter
        domain_names = self._add_domain_filter(identifiers, query_fields, query_filters)

        # If we have filters to apply, execute unified query
        if query_filters:
            # Remove duplicates from fields
            query_fields = list(set(query_fields))
            fields_string = "\n".join(query_fields)

            # Add account information for domain context
            if domain_names:
                fields_string += """
                    accounts {
                        ... on ActiveDirectoryAccountDescriptor {
                            domain
                            samAccountName
                        }
                    }"""

            filters_string = ", ".join(query_filters)
            limit = identifiers.get("limit", 50)

            query = f"""
            query {{
                entities({filters_string}, first: {limit}) {{
                    nodes {{
                        entityId
                        {fields_string}
                    }}
                }}
            }}
            """

            response = self.client.command(
                "api_preempt_proxy_post_graphql", body={"query": query}
            )
            result = handle_api_response(
                response,
                operation="api_preempt_proxy_post_graphql",
                error_message="Failed to resolve entities with combined filters",
                default_result=None,
            )
            if self._is_error(result):
                return result

            # Extract entities from GraphQL response structure
            data = response.get("body", {}).get("data", {})
            entities = data.get("entities", {}).get("nodes", [])
            resolved_ids.extend([entity["entityId"] for entity in entities])

        # Remove duplicates and return
        return list(set(resolved_ids))

    def _add_domain_filter(self, identifiers, query_fields, query_filters):
        domain_names = identifiers.get("domain_names")
        if domain_names and isinstance(domain_names, list):
            sanitized_domains = [sanitize_input(domain) for domain in domain_names]
            domains_json = json.dumps(sanitized_domains)
            query_filters.append(f"domains: {domains_json}")
            query_fields.extend(["primaryDisplayName", "secondaryDisplayName"])
        return domain_names

    def _add_ip_filter(
        self, has_user_criteria, ip_addresses, query_fields, query_filters
    ):
        if ip_addresses and isinstance(ip_addresses, list) and not has_user_criteria:
            sanitized_ips = [sanitize_input(ip) for ip in ip_addresses]
            ips_json = json.dumps(sanitized_ips)
            query_filters.append(f"primaryDisplayNames: {ips_json}")
            query_filters.append("types: [ENDPOINT]")
            query_fields.append("primaryDisplayName")

    def _add_email_filter(self, email_addresses, query_fields, query_filters):
        if email_addresses and isinstance(email_addresses, list):
            sanitized_emails = [sanitize_input(email) for email in email_addresses]
            emails_json = json.dumps(sanitized_emails)
            query_filters.append(f"secondaryDisplayNames: {emails_json}")
            query_filters.append("types: [USER]")
            query_fields.extend(["primaryDisplayName", "secondaryDisplayName"])

    def _add_entity_filters(self, identifiers, query_fields, query_filters):
        entity_names = identifiers.get("entity_names")
        if entity_names and isinstance(entity_names, list):
            sanitized_names = [sanitize_input(name) for name in entity_names]
            names_json = json.dumps(sanitized_names)
            query_filters.append(f"primaryDisplayNames: {names_json}")
            query_fields.append("primaryDisplayName")

    def _get_entity_details_batch(
        self, entity_ids: List[str], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get detailed entity information for multiple entities."""
        graphql_query = self._build_entity_details_query(
            entity_ids=entity_ids,
            include_risk_factors=True,
            include_associations=options.get("include_associations", True),
            include_incidents=options.get("include_incidents", True),
            include_accounts=options.get("include_accounts", True),
        )

        response = self.client.command(
            "api_preempt_proxy_post_graphql", body={"query": graphql_query}
        )
        result = handle_api_response(
            response,
            operation="api_preempt_proxy_post_graphql",
            error_message="Failed to get entity details",
            default_result=None,
        )
        if self._is_error(result):
            return result

        # Extract entities from GraphQL response structure
        data = response.get("body", {}).get("data", {})
        entities = data.get("entities", {}).get("nodes", [])
        return {"entities": entities, "entity_count": len(entities)}

    def _get_entity_timelines_batch(
        self, entity_ids: List[str], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get timeline analysis for multiple entities."""
        timeline_results = []

        for entity_id in entity_ids:
            graphql_query = self._build_timeline_query(
                entity_id=entity_id,
                start_time=options.get("start_time"),
                end_time=options.get("end_time"),
                event_types=options.get("event_types"),
                limit=options.get("limit", 50),
            )

            response = self.client.command(
                "api_preempt_proxy_post_graphql", body={"query": graphql_query}
            )
            result = handle_api_response(
                response,
                operation="api_preempt_proxy_post_graphql",
                error_message=f"Failed to get timeline for entity '{entity_id}'",
                default_result=None,
            )
            if self._is_error(result):
                return result

            # Extract timeline from GraphQL response structure
            data = response.get("body", {}).get("data", {})
            timeline_data = data.get("timeline", {})
            timeline_results.append(
                {
                    "entity_id": entity_id,
                    "timeline": timeline_data.get("nodes", []),
                    "page_info": timeline_data.get("pageInfo", {}),
                }
            )

        return {"timelines": timeline_results, "entity_count": len(entity_ids)}

    def _analyze_relationships_batch(
        self, entity_ids: List[str], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze relationships for multiple entities."""
        relationship_results = []

        for entity_id in entity_ids:
            # Handle FieldInfo objects - extract the actual value
            relationship_depth = options.get("relationship_depth", 2)
            if hasattr(relationship_depth, "default"):
                relationship_depth = relationship_depth.default

            graphql_query = self._build_relationship_analysis_query(
                entity_id=entity_id,
                relationship_depth=relationship_depth,
                include_risk_context=options.get("include_risk_context", True),
                limit=options.get("limit", 50),
            )

            response = self.client.command(
                "api_preempt_proxy_post_graphql", body={"query": graphql_query}
            )
            result = handle_api_response(
                response,
                operation="api_preempt_proxy_post_graphql",
                error_message=f"Failed to analyze relationships for entity '{entity_id}'",
                default_result=None,
            )
            if self._is_error(result):
                return result

            # Extract entities from GraphQL response structure
            data = response.get("body", {}).get("data", {})
            entities = data.get("entities", {}).get("nodes", [])
            if entities:
                entity_data = entities[0]
                relationship_results.append(
                    {
                        "entity_id": entity_id,
                        "associations": entity_data.get("associations", []),
                        "relationship_count": len(entity_data.get("associations", [])),
                    }
                )
            else:
                relationship_results.append(
                    {
                        "entity_id": entity_id,
                        "associations": [],
                        "relationship_count": 0,
                    }
                )

        return {"relationships": relationship_results, "entity_count": len(entity_ids)}

    def _assess_risks_batch(
        self, entity_ids: List[str], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform risk assessment for multiple entities."""
        graphql_query = self._build_risk_assessment_query(
            entity_ids=entity_ids,
            include_risk_factors=options.get("include_risk_factors", True),
        )

        response = self.client.command(
            "api_preempt_proxy_post_graphql", body={"query": graphql_query}
        )
        result = handle_api_response(
            response,
            operation="api_preempt_proxy_post_graphql",
            error_message="Failed to assess risks",
            default_result=None,
        )
        if self._is_error(result):
            return result

        # Extract entities from GraphQL response structure
        data = response.get("body", {}).get("data", {})
        entities = data.get("entities", {}).get("nodes", [])
        risk_assessments = []

        for entity in entities:
            risk_assessments.append(
                {
                    "entityId": entity.get("entityId"),
                    "primaryDisplayName": entity.get("primaryDisplayName"),
                    "riskScore": entity.get("riskScore", 0),
                    "riskScoreSeverity": entity.get("riskScoreSeverity", "LOW"),
                    "riskFactors": entity.get("riskFactors", []),
                }
            )

        return {
            "risk_assessments": risk_assessments,
            "entity_count": len(risk_assessments),
        }

    def _synthesize_investigation_response(
        self,
        entity_ids: List[str],
        investigation_results: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize comprehensive investigation response from multiple API results."""

        # Build investigation summary
        investigation_summary = {
            "entity_count": len(entity_ids),
            "resolved_entity_ids": entity_ids,
            "investigation_types": metadata.get("investigation_types", []),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
        }

        # Add search criteria to summary
        search_criteria = metadata.get("search_criteria", {})
        if any(search_criteria.values()):
            investigation_summary["search_criteria"] = search_criteria

        # Start building comprehensive response
        response = {
            "investigation_summary": investigation_summary,
            "entities": entity_ids,
        }

        # Add investigation results based on what was requested
        for investigation_type, results in investigation_results.items():
            response[investigation_type] = results

        # Generate cross-investigation insights
        insights = self._generate_investigation_insights(
            investigation_results, entity_ids
        )
        if insights:
            response["cross_investigation_insights"] = insights

        return response

    def _generate_investigation_insights(
        self, investigation_results: Dict[str, Any], entity_ids: List[str]
    ) -> Dict[str, Any]:
        """Generate insights by analyzing results across different investigation types."""
        insights = {}

        # Timeline and relationship correlation
        if (
            "timeline_analysis" in investigation_results
            and "relationship_analysis" in investigation_results
        ):
            insights["activity_relationship_correlation"] = (
                self._analyze_activity_relationships(
                    investigation_results["timeline_analysis"],
                    investigation_results["relationship_analysis"],
                )
            )

        # Multi-entity patterns (if investigating multiple entities)
        if len(entity_ids) > 1:
            insights["multi_entity_patterns"] = self._analyze_multi_entity_patterns(
                investigation_results, entity_ids
            )

        return insights

    def _analyze_activity_relationships(
        self, timeline_analysis: Dict[str, Any], relationship_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze correlation between timeline activities and entity relationships."""
        correlation = {"related_entity_activities": [], "suspicious_patterns": []}

        # This would involve complex analysis of timeline events and relationships
        # For now, provide basic structure
        timelines = timeline_analysis.get("timelines", [])
        relationships = relationship_analysis.get("relationships", [])

        correlation["timeline_count"] = len(timelines)
        correlation["relationship_count"] = len(relationships)

        return correlation

    def _analyze_multi_entity_patterns(
        self, investigation_results: Dict[str, Any], entity_ids: List[str]
    ) -> Dict[str, Any]:
        """Analyze patterns across multiple entities being investigated."""
        patterns = {
            "common_risk_factors": [],
            "shared_relationships": [],
            "coordinated_activities": [],
        }

        # Analyze common risk factors across entities
        if "risk_assessment" in investigation_results:
            risk_assessments = investigation_results["risk_assessment"].get(
                "risk_assessments", []
            )
            risk_factor_counts = {}

            for assessment in risk_assessments:
                for risk_factor in assessment.get("riskFactors", []):
                    risk_type = risk_factor.get("type")
                    if risk_type in risk_factor_counts:
                        risk_factor_counts[risk_type] += 1
                    else:
                        risk_factor_counts[risk_type] = 1

            # Find common risk factors (present in multiple entities)
            for risk_type, count in risk_factor_counts.items():
                if count > 1:
                    patterns["common_risk_factors"].append(
                        {
                            "risk_type": risk_type,
                            "entity_count": count,
                            "percentage": round((count / len(entity_ids)) * 100, 1),
                        }
                    )

        return patterns
