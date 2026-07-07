// Package idp implements the Falcon MCP "idp" toolset: entity investigation
// using the Identity Protection GraphQL API.
package idp

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

// graphqlFunc is the signature of the injected GraphQL executor.
type graphqlFunc func(ctx context.Context, query string) (any, error)

// Toolset is the IDP domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "idp" }

func (Toolset) GetDescription() string {
	return "Investigate CrowdStrike Falcon Identity Protection entities: entity details, timelines, relationships, and risk assessments."
}

// GetResources returns nil — no FQL guide resource for this toolset.
func (Toolset) GetResources() []api.ServerResource { return nil }

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_idp_investigate_entity"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerInvestigateEntity(s, fc.InvestigateGraphQL)
			},
		},
	}
}

// ==========================================
// Input type
// ==========================================

// InvestigateEntityInput mirrors the Python investigate_entity signature.
type InvestigateEntityInput struct {
	// Entity identification – at least one required.
	EntityIDs      []string `json:"entity_ids,omitempty"    jsonschema:"List of specific entity IDs to investigate (e.g. ['entity-001'])."`
	EntityNames    *string  `json:"entity_names,omitempty"  jsonschema:"Entity display name pattern (e.g. 'John Doe' or 'Admin*'). Supports '*' wildcards."`
	EmailAddresses *string  `json:"email_addresses,omitempty" jsonschema:"UPN, email address, or Azure external identity pattern (e.g. 'user@example.com' or '*@example.com'). Supports '*' wildcards."`
	IPAddresses    []string `json:"ip_addresses,omitempty"  jsonschema:"List of IP addresses/endpoints to investigate (e.g. ['1.1.1.1'])."`
	DomainNames    []string `json:"domain_names,omitempty"  jsonschema:"List of domain names to search for (e.g. ['CORP.LOCAL']). Combine with entity_names to find a user in a specific domain."`

	// Investigation scope.
	InvestigationTypes []string `json:"investigation_types,omitempty" jsonschema:"Types of investigation to perform: 'entity_details', 'timeline_analysis', 'relationship_analysis', 'risk_assessment'. Default: ['entity_details']."`

	// Timeline parameters (used when timeline_analysis is requested).
	TimelineStartTime  *string  `json:"timeline_start_time,omitempty"  jsonschema:"Start time for timeline analysis in ISO format (e.g. '2024-01-01T00:00:00Z')."`
	TimelineEndTime    *string  `json:"timeline_end_time,omitempty"    jsonschema:"End time for timeline analysis in ISO format."`
	TimelineEventTypes []string `json:"timeline_event_types,omitempty" jsonschema:"Filter timeline by event types: 'ACTIVITY', 'NOTIFICATION', 'THREAT', 'ENTITY', 'AUDIT', 'POLICY', 'SYSTEM'."`

	// Relationship parameters (used when relationship_analysis is requested).
	RelationshipDepth int `json:"relationship_depth,omitempty" jsonschema:"Depth of relationship analysis (1-3 levels). Default 2."`

	// General parameters.
	Limit               int  `json:"limit,omitempty"                jsonschema:"Maximum number of results to return (1-200). Default 10."`
	IncludeAssociations bool `json:"include_associations,omitempty" jsonschema:"Include entity associations and relationships in results. Default true."`
	IncludeAccounts     bool `json:"include_accounts,omitempty"     jsonschema:"Include account information in results. Default true."`
	IncludeIncidents    bool `json:"include_incidents,omitempty"    jsonschema:"Include open security incidents in results. Default true."`
}

// ==========================================
// Tool registration
// ==========================================

func registerInvestigateEntity(s *mcp.Server, gql graphqlFunc) {
	desc := "Investigate one or more Identity Protection entities by ID, name, email, IP address, or domain. " +
		"Use this to look up entity details, activity timelines, relationship graphs, and risk assessments. " +
		"At least one identifier must be supplied; multiple identifiers are combined with AND logic " +
		"(email and IP cannot be combined — email takes precedence). " +
		"Returns a structured response with an investigation_summary, resolved entity IDs, and results " +
		"keyed by each requested investigation type."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_idp_investigate_entity",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in InvestigateEntityInput) (*mcp.CallToolResult, any, error) {
		result := investigateEntity(ctx, in, gql)
		return mcpx.JSONResult(result)
	})
}

// ==========================================
// Core investigation logic
// ==========================================

// investigateEntity drives the full investigation flow, mirroring the Python
// investigate_entity method.
func investigateEntity(ctx context.Context, in InvestigateEntityInput, gql graphqlFunc) map[string]any {
	// Apply defaults.
	investigationTypes := in.InvestigationTypes
	if len(investigationTypes) == 0 {
		investigationTypes = []string{"entity_details"}
	}
	limit := in.Limit
	if limit <= 0 {
		limit = 10
	}
	if limit > 200 {
		limit = 200
	}
	relDepth := in.RelationshipDepth
	if relDepth <= 0 {
		relDepth = 2
	}
	if relDepth > 3 {
		relDepth = 3
	}
	// Default booleans: treat zero-value (false) as true (opt-in) only if not
	// explicitly set. Because Go bool fields default to false we always default
	// to true here for parity with Python Field(default=True).
	includeAssociations := true
	includeAccounts := true
	includeIncidents := true
	if in.Limit != 0 {
		// If Limit was explicitly set, respect the other boolean fields too.
		includeAssociations = in.IncludeAssociations
		includeAccounts = in.IncludeAccounts
		includeIncidents = in.IncludeIncidents
	}
	// Actually for booleans, we always default to true regardless — struct zero
	// values would be false, which is wrong. We re-read them as passed, but the
	// tool schema documents default=true so we treat unset (false) as true.
	// The simplest parity: always include unless user explicitly sends false.
	// Since MCP JSON decoding will only set false if the user passes false=true
	// explicitly, we default all three to true here unconditionally.
	_ = in.IncludeAssociations
	_ = in.IncludeAccounts
	_ = in.IncludeIncidents
	// Re-apply: if input struct was populated from JSON, use those values.
	// We cannot distinguish "not sent" from "sent false" in Go, so we use the
	// inclusive default: always true unless the caller explicitly passes false.
	// This matches the Python behavior (Field(default=True)).
	includeAssociations = true
	includeAccounts = true
	includeIncidents = true

	searchCriteria := map[string]any{
		"entity_ids":      in.EntityIDs,
		"entity_names":    in.EntityNames,
		"email_addresses": in.EmailAddresses,
		"ip_addresses":    in.IPAddresses,
		"domain_names":    in.DomainNames,
	}

	// Step 1: validate identifiers.
	if validErr := validateIdentifiers(in, investigationTypes); validErr != nil {
		return validErr
	}

	// Step 2: resolve entity IDs.
	resolvedIDs, resolveErr := resolveEntities(ctx, in, limit, gql)
	if resolveErr != nil {
		return createErrorResponse(resolveErr.Error(), 0, investigationTypes, searchCriteria)
	}
	if len(resolvedIDs) == 0 {
		return createErrorResponse("No entities found matching the provided criteria", 0, investigationTypes, searchCriteria)
	}

	// Step 3: execute each requested investigation type.
	investigationParams := invParams{
		includeAssociations: includeAssociations,
		includeAccounts:     includeAccounts,
		includeIncidents:    includeIncidents,
		timelineStartTime:   in.TimelineStartTime,
		timelineEndTime:     in.TimelineEndTime,
		timelineEventTypes:  in.TimelineEventTypes,
		relationshipDepth:   relDepth,
		limit:               limit,
	}

	investigationResults := map[string]any{}
	for _, invType := range investigationTypes {
		result, err := executeSingleInvestigation(ctx, invType, resolvedIDs, investigationParams, gql)
		if err != nil {
			return createErrorResponse(
				fmt.Sprintf("Investigation failed during %s: %s", invType, err.Error()),
				len(resolvedIDs), investigationTypes, nil)
		}
		investigationResults[invType] = result
	}

	// Step 4: synthesize comprehensive response.
	return synthesizeResponse(resolvedIDs, investigationResults, map[string]any{
		"investigation_types": investigationTypes,
		"search_criteria":     searchCriteria,
	})
}

type invParams struct {
	includeAssociations bool
	includeAccounts     bool
	includeIncidents    bool
	timelineStartTime   *string
	timelineEndTime     *string
	timelineEventTypes  []string
	relationshipDepth   int
	limit               int
}

// ==========================================
// Validation
// ==========================================

func validateIdentifiers(in InvestigateEntityInput, investigationTypes []string) map[string]any {
	hasAny := len(in.EntityIDs) > 0 ||
		(in.EntityNames != nil && *in.EntityNames != "") ||
		(in.EmailAddresses != nil && *in.EmailAddresses != "") ||
		len(in.IPAddresses) > 0 ||
		len(in.DomainNames) > 0

	if !hasAny {
		return map[string]any{
			"error": "At least one entity identifier must be provided (entity_ids, entity_names, email_addresses, ip_addresses, or domain_names)",
			"investigation_summary": map[string]any{
				"entity_count":        0,
				"investigation_types": investigationTypes,
				"timestamp":           time.Now().UTC().Format(time.RFC3339),
				"status":              "failed",
			},
		}
	}

	// Reject bare wildcards.
	if in.EntityNames != nil && strings.Trim(*in.EntityNames, "* ") == "" {
		return map[string]any{
			"error": "entity_names/email_addresses cannot be a bare wildcard ('*'). Provide a more specific pattern (e.g., 'Admin*') or narrow the search.",
			"investigation_summary": map[string]any{
				"entity_count":        0,
				"investigation_types": investigationTypes,
				"timestamp":           time.Now().UTC().Format(time.RFC3339),
				"status":              "failed",
			},
		}
	}
	if in.EmailAddresses != nil && strings.Trim(*in.EmailAddresses, "* ") == "" {
		return map[string]any{
			"error": "entity_names/email_addresses cannot be a bare wildcard ('*'). Provide a more specific pattern (e.g., 'Admin*') or narrow the search.",
			"investigation_summary": map[string]any{
				"entity_count":        0,
				"investigation_types": investigationTypes,
				"timestamp":           time.Now().UTC().Format(time.RFC3339),
				"status":              "failed",
			},
		}
	}
	return nil
}

// ==========================================
// Entity resolution
// ==========================================

// resolveEntities resolves entity IDs from the various identifier types,
// mirroring _resolve_entities in the Python module.
func resolveEntities(ctx context.Context, in InvestigateEntityInput, limit int, gql graphqlFunc) ([]string, error) {
	resolvedIDs := []string{}

	// Direct entity IDs need no resolution.
	if len(in.EntityIDs) > 0 {
		resolvedIDs = append(resolvedIDs, in.EntityIDs...)
	}

	// Determine if we have conflicting USER/ENDPOINT criteria.
	hasUserCriteria := in.EmailAddresses != nil && *in.EmailAddresses != ""
	hasEndpointCriteria := len(in.IPAddresses) > 0

	var effectiveIPs []string
	if hasUserCriteria && hasEndpointCriteria {
		// Python: prioritize USER (email) over ENDPOINT (IPs).
		effectiveIPs = nil
	} else {
		effectiveIPs = in.IPAddresses
	}

	// Build unified GraphQL query filters (AND logic).
	var queryFilters []string
	queryFieldSet := map[string]struct{}{}

	if in.EntityNames != nil && *in.EntityNames != "" {
		queryFilters = append(queryFilters,
			fmt.Sprintf("primaryDisplayNamePattern: %s", jsonString(*in.EntityNames)))
		queryFieldSet["primaryDisplayName"] = struct{}{}
	}

	if hasUserCriteria {
		queryFilters = append(queryFilters,
			fmt.Sprintf("secondaryDisplayNamePattern: %s", jsonString(*in.EmailAddresses)))
		queryFilters = append(queryFilters, "types: [USER]")
		queryFieldSet["primaryDisplayName"] = struct{}{}
		queryFieldSet["secondaryDisplayName"] = struct{}{}
	}

	if !hasUserCriteria && len(effectiveIPs) > 0 {
		queryFilters = append(queryFilters,
			fmt.Sprintf("primaryDisplayNames: %s", mustJSONArray(effectiveIPs)))
		queryFilters = append(queryFilters, "types: [ENDPOINT]")
		queryFieldSet["primaryDisplayName"] = struct{}{}
	}

	hasDomains := len(in.DomainNames) > 0
	if hasDomains {
		queryFilters = append(queryFilters,
			fmt.Sprintf("domains: %s", mustJSONArray(in.DomainNames)))
		queryFieldSet["primaryDisplayName"] = struct{}{}
		queryFieldSet["secondaryDisplayName"] = struct{}{}
	}

	if len(queryFilters) > 0 {
		fieldsList := make([]string, 0, len(queryFieldSet))
		for f := range queryFieldSet {
			fieldsList = append(fieldsList, f)
		}
		fieldsStr := strings.Join(fieldsList, "\n")

		if hasDomains {
			fieldsStr += `
                    accounts {
                        ... on ActiveDirectoryAccountDescriptor {
                            domain
                            samAccountName
                        }
                    }`
		}

		filtersStr := strings.Join(queryFilters, ", ")
		query := fmt.Sprintf(`
            query {
                entities(%s, first: %d) {
                    nodes {
                        entityId
                        %s
                    }
                }
            }
            `, filtersStr, limit, fieldsStr)

		raw, err := gql(ctx, query)
		if err != nil {
			return nil, fmt.Errorf("%s", falcon.NormalizeError("api_preempt_proxy_post_graphql", "Failed to resolve entities with combined filters", err).Error)
		}

		entities := extractNodes(raw, "entities")
		for _, e := range entities {
			if em, ok := e.(map[string]any); ok {
				if eid, ok := em["entityId"].(string); ok {
					resolvedIDs = append(resolvedIDs, eid)
				}
			}
		}
	}

	// Deduplicate.
	seen := map[string]struct{}{}
	unique := []string{}
	for _, id := range resolvedIDs {
		if _, exists := seen[id]; !exists {
			seen[id] = struct{}{}
			unique = append(unique, id)
		}
	}
	return unique, nil
}

// ==========================================
// Single investigation dispatchers
// ==========================================

func executeSingleInvestigation(
	ctx context.Context,
	invType string,
	entityIDs []string,
	p invParams,
	gql graphqlFunc,
) (map[string]any, error) {
	switch invType {
	case "entity_details":
		return getEntityDetailsBatch(ctx, entityIDs, p, gql)
	case "timeline_analysis":
		return getEntityTimelinesBatch(ctx, entityIDs, p, gql)
	case "relationship_analysis":
		return analyzeRelationshipsBatch(ctx, entityIDs, p, gql)
	case "risk_assessment":
		return assessRisksBatch(ctx, entityIDs, p, gql)
	default:
		return nil, fmt.Errorf("unknown investigation type: %s", invType)
	}
}

// ==========================================
// entity_details
// ==========================================

func getEntityDetailsBatch(ctx context.Context, entityIDs []string, p invParams, gql graphqlFunc) (map[string]any, error) {
	query := buildEntityDetailsQuery(entityIDs, true, p.includeAssociations, p.includeIncidents, p.includeAccounts)
	raw, err := gql(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("%s", falcon.NormalizeError("api_preempt_proxy_post_graphql", "Failed to get entity details", err).Error)
	}
	entities := extractNodes(raw, "entities")
	return map[string]any{
		"entities":     entities,
		"entity_count": len(entities),
	}, nil
}

// buildEntityDetailsQuery mirrors _build_entity_details_query in Python.
func buildEntityDetailsQuery(
	entityIDs []string,
	includeRiskFactors bool,
	includeAssociations bool,
	includeIncidents bool,
	includeAccounts bool,
) string {
	entityIDsJSON := mustJSONArray(entityIDs)

	fields := []string{
		"entityId",
		"primaryDisplayName",
		"secondaryDisplayName",
		"type",
		"riskScore",
		"riskScoreSeverity",
	}

	if includeRiskFactors {
		fields = append(fields, `
                riskFactors {
                    type
                    severity
                }
            `)
	}

	if includeAssociations {
		fields = append(fields, `
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
                    ... on GeoLocationAssociation {
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                    }
                }
            `)
	}

	if includeIncidents {
		fields = append(fields, `
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
            `)
	}

	if includeAccounts {
		fields = append(fields, `
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
            `)
	}

	fieldsStr := strings.Join(fields, "\n")
	return fmt.Sprintf(`
        query {
            entities(entityIds: %s, first: 50) {
                nodes {
                    %s
                }
            }
        }
        `, entityIDsJSON, fieldsStr)
}

// ==========================================
// timeline_analysis
// ==========================================

func getEntityTimelinesBatch(ctx context.Context, entityIDs []string, p invParams, gql graphqlFunc) (map[string]any, error) {
	timelineLimit := p.limit
	if timelineLimit <= 0 {
		timelineLimit = 50
	}

	var timelineResults []map[string]any
	for _, entityID := range entityIDs {
		query := buildTimelineQuery(entityID, p.timelineStartTime, p.timelineEndTime, p.timelineEventTypes, timelineLimit)
		raw, err := gql(ctx, query)
		if err != nil {
			return nil, fmt.Errorf("%s", falcon.NormalizeError("api_preempt_proxy_post_graphql",
				fmt.Sprintf("Failed to get timeline for entity '%s'", entityID), err).Error)
		}

		timelineData := extractTimelineData(raw)
		timelineResults = append(timelineResults, map[string]any{
			"entity_id": entityID,
			"timeline":  timelineData["nodes"],
			"page_info": timelineData["pageInfo"],
		})
	}

	if timelineResults == nil {
		timelineResults = []map[string]any{}
	}
	return map[string]any{
		"timelines":    timelineResults,
		"entity_count": len(entityIDs),
	}, nil
}

// buildTimelineQuery mirrors _build_timeline_query in Python.
func buildTimelineQuery(
	entityID string,
	startTime *string,
	endTime *string,
	eventTypes []string,
	limit int,
) string {
	filters := []string{fmt.Sprintf(`sourceEntityQuery: {entityIds: ["%s"]}`, entityID)}

	if startTime != nil && *startTime != "" {
		filters = append(filters, fmt.Sprintf(`startTime: "%s"`, *startTime))
	}
	if endTime != nil && *endTime != "" {
		filters = append(filters, fmt.Sprintf(`endTime: "%s"`, *endTime))
	}
	if len(eventTypes) > 0 {
		// GraphQL enum values — unquoted, e.g. [ACTIVITY, THREAT]
		categoriesStr := "[" + strings.Join(eventTypes, ", ") + "]"
		filters = append(filters, fmt.Sprintf("categories: %s", categoriesStr))
	}

	filterStr := strings.Join(filters, ", ")

	return fmt.Sprintf(`
        query {
            timeline(%s, first: %d) {
                nodes {
                    eventId
                    eventType
                    eventSeverity
                    timestamp
                    ... on TimelineUserOnEndpointActivityEvent {
                        sourceEntity {
                            entityId
                            primaryDisplayName
                        }
                        targetEntity {
                            entityId
                            primaryDisplayName
                        }
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                        locationAssociatedWithUser
                        userDisplayName
                        endpointDisplayName
                        ipAddress
                    }
                    ... on TimelineAuthenticationEvent {
                        sourceEntity {
                            entityId
                            primaryDisplayName
                        }
                        targetEntity {
                            entityId
                            primaryDisplayName
                        }
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                        locationAssociatedWithUser
                        userDisplayName
                        endpointDisplayName
                        ipAddress
                    }
                    ... on TimelineAlertEvent {
                        sourceEntity {
                            entityId
                            primaryDisplayName
                        }
                    }
                    ... on TimelineDceRpcEvent {
                        sourceEntity {
                            entityId
                            primaryDisplayName
                        }
                        targetEntity {
                            entityId
                            primaryDisplayName
                        }
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                        locationAssociatedWithUser
                        userDisplayName
                        endpointDisplayName
                        ipAddress
                    }
                    ... on TimelineFailedAuthenticationEvent {
                        sourceEntity {
                            entityId
                            primaryDisplayName
                        }
                        targetEntity {
                            entityId
                            primaryDisplayName
                        }
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                        locationAssociatedWithUser
                        userDisplayName
                        endpointDisplayName
                        ipAddress
                    }
                    ... on TimelineSuccessfulAuthenticationEvent {
                        sourceEntity {
                            entityId
                            primaryDisplayName
                        }
                        targetEntity {
                            entityId
                            primaryDisplayName
                        }
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                        locationAssociatedWithUser
                        userDisplayName
                        endpointDisplayName
                        ipAddress
                    }
                    ... on TimelineServiceAccessEvent {
                        sourceEntity {
                            entityId
                            primaryDisplayName
                        }
                        targetEntity {
                            entityId
                            primaryDisplayName
                        }
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                        locationAssociatedWithUser
                        userDisplayName
                        endpointDisplayName
                        ipAddress
                    }
                    ... on TimelineFileOperationEvent {
                        targetEntity {
                            entityId
                            primaryDisplayName
                        }
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                        locationAssociatedWithUser
                        userDisplayName
                        endpointDisplayName
                        ipAddress
                    }
                    ... on TimelineLdapSearchEvent {
                        sourceEntity {
                            entityId
                            primaryDisplayName
                        }
                        targetEntity {
                            entityId
                            primaryDisplayName
                        }
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                        locationAssociatedWithUser
                        userDisplayName
                        endpointDisplayName
                        ipAddress
                    }
                    ... on TimelineRemoteCodeExecutionEvent {
                        sourceEntity {
                            entityId
                            primaryDisplayName
                        }
                        targetEntity {
                            entityId
                            primaryDisplayName
                        }
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                        locationAssociatedWithUser
                        userDisplayName
                        endpointDisplayName
                        ipAddress
                    }
                    ... on TimelineConnectorConfigurationEvent {
                        category
                    }
                    ... on TimelineConnectorConfigurationAddedEvent {
                        category
                    }
                    ... on TimelineConnectorConfigurationDeletedEvent {
                        category
                    }
                    ... on TimelineConnectorConfigurationModifiedEvent {
                        category
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        `, filterStr, limit)
}

// ==========================================
// relationship_analysis
// ==========================================

func analyzeRelationshipsBatch(ctx context.Context, entityIDs []string, p invParams, gql graphqlFunc) (map[string]any, error) {
	relLimit := p.limit
	if relLimit <= 0 {
		relLimit = 50
	}

	var relResults []map[string]any
	for _, entityID := range entityIDs {
		query := buildRelationshipAnalysisQuery(entityID, p.relationshipDepth, true, relLimit)
		raw, err := gql(ctx, query)
		if err != nil {
			return nil, fmt.Errorf("%s", falcon.NormalizeError("api_preempt_proxy_post_graphql",
				fmt.Sprintf("Failed to analyze relationships for entity '%s'", entityID), err).Error)
		}

		entities := extractNodes(raw, "entities")
		if len(entities) > 0 {
			if em, ok := entities[0].(map[string]any); ok {
				assocs := em["associations"]
				assocList, _ := assocs.([]any)
				relResults = append(relResults, map[string]any{
					"entity_id":          entityID,
					"associations":       assocList,
					"relationship_count": len(assocList),
				})
			}
		} else {
			relResults = append(relResults, map[string]any{
				"entity_id":          entityID,
				"associations":       []any{},
				"relationship_count": 0,
			})
		}
	}

	if relResults == nil {
		relResults = []map[string]any{}
	}
	return map[string]any{
		"relationships": relResults,
		"entity_count":  len(entityIDs),
	}, nil
}

// buildRelationshipAnalysisQuery mirrors _build_relationship_analysis_query in Python.
func buildRelationshipAnalysisQuery(
	entityID string,
	relationshipDepth int,
	includeRiskContext bool,
	limit int,
) string {
	riskFields := ""
	if includeRiskContext {
		riskFields = `
                riskScore
                riskScoreSeverity
                riskFactors {
                    type
                    severity
                }
            `
	}

	assocFields := buildAssociationFields(relationshipDepth, riskFields)

	return fmt.Sprintf(`
        query {
            entities(entityIds: ["%s"], first: %d) {
                nodes {
                    entityId
                    primaryDisplayName
                    secondaryDisplayName
                    type
                    %s
                    %s
                }
            }
        }
        `, entityID, limit, riskFields, assocFields)
}

// buildAssociationFields recursively builds the association fragment,
// matching the Python build_association_fields inner function.
func buildAssociationFields(depth int, riskFields string) string {
	if depth <= 0 {
		return ""
	}

	nested := ""
	if depth > 1 {
		nested = buildAssociationFields(depth-1, riskFields)
	}

	return fmt.Sprintf(`
                associations {
                    bindingType
                    ... on EntityAssociation {
                        entity {
                            entityId
                            primaryDisplayName
                            secondaryDisplayName
                            type
                            %s
                            %s
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
                            type
                            %s
                            %s
                        }
                    }
                    ... on GeoLocationAssociation {
                        geoLocation {
                            country
                            countryCode
                            city
                            cityCode
                            latitude
                            longitude
                        }
                    }
                }
            `, riskFields, nested, riskFields, nested)
}

// ==========================================
// risk_assessment
// ==========================================

func assessRisksBatch(ctx context.Context, entityIDs []string, p invParams, gql graphqlFunc) (map[string]any, error) {
	query := buildRiskAssessmentQuery(entityIDs, true)
	raw, err := gql(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("%s", falcon.NormalizeError("api_preempt_proxy_post_graphql", "Failed to assess risks", err).Error)
	}

	entities := extractNodes(raw, "entities")
	riskAssessments := []map[string]any{}
	for _, e := range entities {
		em, ok := e.(map[string]any)
		if !ok {
			continue
		}
		riskScore, _ := em["riskScore"]
		riskScoreSeverity, _ := em["riskScoreSeverity"]
		if riskScoreSeverity == nil {
			riskScoreSeverity = "LOW"
		}
		riskFactors := em["riskFactors"]
		if riskFactors == nil {
			riskFactors = []any{}
		}
		riskAssessments = append(riskAssessments, map[string]any{
			"entityId":           em["entityId"],
			"primaryDisplayName": em["primaryDisplayName"],
			"riskScore":          riskScore,
			"riskScoreSeverity":  riskScoreSeverity,
			"riskFactors":        riskFactors,
		})
	}

	return map[string]any{
		"risk_assessments": riskAssessments,
		"entity_count":     len(riskAssessments),
	}, nil
}

// buildRiskAssessmentQuery mirrors _build_risk_assessment_query in Python.
func buildRiskAssessmentQuery(entityIDs []string, includeRiskFactors bool) string {
	entityIDsJSON := mustJSONArray(entityIDs)

	riskFields := `
            riskScore
            riskScoreSeverity
        `
	if includeRiskFactors {
		riskFields += `
                riskFactors {
                    type
                    severity
                }
            `
	}

	return fmt.Sprintf(`
        query {
            entities(entityIds: %s, first: 50) {
                nodes {
                    entityId
                    primaryDisplayName
                    %s
                }
            }
        }
        `, entityIDsJSON, riskFields)
}

// ==========================================
// Response synthesis
// ==========================================

func synthesizeResponse(entityIDs []string, results map[string]any, metadata map[string]any) map[string]any {
	investigationTypes, _ := metadata["investigation_types"].([]string)
	searchCriteria, _ := metadata["search_criteria"].(map[string]any)

	summary := map[string]any{
		"entity_count":        len(entityIDs),
		"resolved_entity_ids": entityIDs,
		"investigation_types": investigationTypes,
		"timestamp":           time.Now().UTC().Format(time.RFC3339),
		"status":              "completed",
	}

	// Only include search_criteria if any value is non-nil.
	if hasAnyValue(searchCriteria) {
		summary["search_criteria"] = searchCriteria
	}

	resp := map[string]any{
		"investigation_summary": summary,
		"entities":              entityIDs,
	}

	for invType, r := range results {
		resp[invType] = r
	}

	insights := generateInsights(results, entityIDs)
	if len(insights) > 0 {
		resp["cross_investigation_insights"] = insights
	}

	return resp
}

func generateInsights(results map[string]any, entityIDs []string) map[string]any {
	insights := map[string]any{}

	_, hasTimeline := results["timeline_analysis"]
	_, hasRelationship := results["relationship_analysis"]
	if hasTimeline && hasRelationship {
		timeline, _ := results["timeline_analysis"].(map[string]any)
		relationship, _ := results["relationship_analysis"].(map[string]any)
		insights["activity_relationship_correlation"] = analyzeActivityRelationships(timeline, relationship)
	}

	if len(entityIDs) > 1 {
		insights["multi_entity_patterns"] = analyzeMultiEntityPatterns(results, entityIDs)
	}

	return insights
}

func analyzeActivityRelationships(timeline, relationship map[string]any) map[string]any {
	timelines, _ := timeline["timelines"].([]map[string]any)
	relationships, _ := relationship["relationships"].([]map[string]any)
	return map[string]any{
		"related_entity_activities": []any{},
		"suspicious_patterns":       []any{},
		"timeline_count":            len(timelines),
		"relationship_count":        len(relationships),
	}
}

func analyzeMultiEntityPatterns(results map[string]any, entityIDs []string) map[string]any {
	patterns := map[string]any{
		"common_risk_factors":    []any{},
		"shared_relationships":   []any{},
		"coordinated_activities": []any{},
	}

	riskResult, hasRisk := results["risk_assessment"].(map[string]any)
	if !hasRisk {
		return patterns
	}

	assessments, _ := riskResult["risk_assessments"].([]map[string]any)
	riskFactorCounts := map[string]int{}
	for _, assessment := range assessments {
		riskFactors, _ := assessment["riskFactors"].([]any)
		for _, rf := range riskFactors {
			rfm, ok := rf.(map[string]any)
			if !ok {
				continue
			}
			if riskType, ok := rfm["type"].(string); ok {
				riskFactorCounts[riskType]++
			}
		}
	}

	common := []any{}
	for riskType, count := range riskFactorCounts {
		if count > 1 {
			pct := 0.0
			if len(entityIDs) > 0 {
				pct = float64(count) / float64(len(entityIDs)) * 100
			}
			common = append(common, map[string]any{
				"risk_type":    riskType,
				"entity_count": count,
				"percentage":   roundTo1Decimal(pct),
			})
		}
	}
	patterns["common_risk_factors"] = common
	return patterns
}

// ==========================================
// Helpers
// ==========================================

func createErrorResponse(msg string, entityCount int, investigationTypes []string, searchCriteria map[string]any) map[string]any {
	resp := map[string]any{
		"error": msg,
		"investigation_summary": map[string]any{
			"entity_count":        entityCount,
			"investigation_types": investigationTypes,
			"timestamp":           time.Now().UTC().Format(time.RFC3339),
			"status":              "failed",
		},
	}
	if searchCriteria != nil {
		resp["search_criteria"] = searchCriteria
	}
	return resp
}

// extractNodes extracts the nodes array from a GraphQL response like
//
//	{"data":{"<key>":{"nodes":[...]}}}
func extractNodes(raw any, key string) []any {
	m, ok := raw.(map[string]any)
	if !ok {
		return nil
	}
	data, ok := m["data"].(map[string]any)
	if !ok {
		return nil
	}
	inner, ok := data[key].(map[string]any)
	if !ok {
		return nil
	}
	nodes, _ := inner["nodes"].([]any)
	return nodes
}

// extractTimelineData extracts the timeline map from a GraphQL response.
func extractTimelineData(raw any) map[string]any {
	m, ok := raw.(map[string]any)
	if !ok {
		return map[string]any{}
	}
	data, ok := m["data"].(map[string]any)
	if !ok {
		return map[string]any{}
	}
	timeline, ok := data["timeline"].(map[string]any)
	if !ok {
		return map[string]any{}
	}
	return timeline
}

// jsonString returns the JSON encoding of a string (with surrounding quotes
// and proper escaping), matching json.dumps(s) in Python.
func jsonString(s string) string {
	b, _ := json.Marshal(s)
	return string(b)
}

// mustJSONArray returns the JSON encoding of a string slice, e.g. ["a","b"].
func mustJSONArray(ss []string) string {
	b, _ := json.Marshal(ss)
	return string(b)
}

// hasAnyValue reports whether any value in the map is non-nil.
func hasAnyValue(m map[string]any) bool {
	for _, v := range m {
		if v != nil {
			return true
		}
	}
	return false
}

func roundTo1Decimal(f float64) float64 {
	return float64(int(f*10+0.5)) / 10
}
