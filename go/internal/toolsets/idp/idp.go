// Package idp provides the Identity Protection entity investigation tool. It is
// the reference GraphQL module: unlike the REST two-step modules, its single
// tool builds GraphQL queries by string interpolation (gofalcon's
// SwaggerGraphQLQuery has no variables field), so every interpolated value is
// run through falcon.SanitizeInput, and the response body is read via the raw
// falcon.GraphQL executor because the typed gofalcon OK type discards it.
package idp

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/crowdstrike/gofalcon/falcon/client"
	"github.com/google/jsonschema-go/jsonschema"

	fal "github.com/crowdstrike/falcon-mcp/internal/falcon"
	"github.com/crowdstrike/falcon-mcp/internal/toolsets"
)

// scopeIdentityRead is the API scope the GraphQL investigation operation
// requires.
var scopeIdentityRead = fal.Scope{Name: "Identity Protection Entities", Read: true}

const (
	defaultLimit             = 10
	defaultRelationshipDepth = 2
)

func init() { toolsets.Register("idp", New) }

type investigateEntityInput struct {
	EntityIDs           []string `json:"entity_ids,omitempty"           jsonschema:"List of specific entity IDs to investigate (e.g., ['entity-001'])."`
	EntityNames         string   `json:"entity_names,omitempty"         jsonschema:"Entity display name pattern (e.g., 'John Doe' or 'Admin*'). Supports '*' wildcards. Combined with other parameters using AND logic."`
	EmailAddresses      string   `json:"email_addresses,omitempty"      jsonschema:"UPN or email pattern (e.g., 'user@example.com', '*@example.com'). Supports '*' wildcards. Email and IP cannot be combined; email takes precedence."`
	IPAddresses         []string `json:"ip_addresses,omitempty"         jsonschema:"List of IP addresses/endpoints to investigate (e.g., ['1.1.1.1'])."`
	DomainNames         []string `json:"domain_names,omitempty"         jsonschema:"List of domain names to search for (e.g., ['CORP.LOCAL'])."`
	InvestigationTypes  []string `json:"investigation_types,omitempty"  jsonschema:"Investigation types: 'entity_details', 'timeline_analysis', 'relationship_analysis', 'risk_assessment'."`
	TimelineStartTime   string   `json:"timeline_start_time,omitempty"  jsonschema:"Start time for timeline analysis in ISO format (e.g., '2024-01-01T00:00:00Z')."`
	TimelineEndTime     string   `json:"timeline_end_time,omitempty"    jsonschema:"End time for timeline analysis in ISO format."`
	TimelineEventTypes  []string `json:"timeline_event_types,omitempty" jsonschema:"Filter timeline by event types: 'ACTIVITY', 'NOTIFICATION', 'THREAT', 'ENTITY', 'AUDIT', 'POLICY', 'SYSTEM'."`
	RelationshipDepth   int64    `json:"relationship_depth,omitempty"   jsonschema:"Depth of relationship analysis (1-3 levels)."`
	Limit               int64    `json:"limit,omitempty"                jsonschema:"Maximum number of results to return. [1-200]"`
	IncludeAssociations *bool    `json:"include_associations,omitempty" jsonschema:"Include entity associations and relationships in results."`
	IncludeAccounts     *bool    `json:"include_accounts,omitempty"     jsonschema:"Include account information in results."`
	IncludeIncidents    *bool    `json:"include_incidents,omitempty"    jsonschema:"Include open security incidents in results."`
}

var _ toolsets.Constrainer = investigateEntityInput{}

// ApplyConstraints sets the numeric bounds/defaults the Python tool declares,
// which jsonschema struct tags cannot express.
func (investigateEntityInput) ApplyConstraints(schema *jsonschema.Schema) {
	if lim := schema.Properties["limit"]; lim != nil {
		lo, hi := 1.0, 200.0
		lim.Minimum = &lo
		lim.Maximum = &hi
		lim.Default = json.RawMessage("10")
	}
	if depth := schema.Properties["relationship_depth"]; depth != nil {
		lo, hi := 1.0, 3.0
		depth.Minimum = &lo
		depth.Maximum = &hi
		depth.Default = json.RawMessage("2")
	}
}

// New builds the idp toolset from an authenticated Falcon client.
func New(c *client.CrowdStrikeAPISpecification) *toolsets.Toolset {
	h := &handlers{c: c}
	return &toolsets.Toolset{
		Name:        "idp",
		Description: "Investigate CrowdStrike Falcon Identity Protection entities.",
		Tools: []toolsets.Tool{
			toolsets.NewTool("idp_investigate_entity", investigateEntityDescription, toolsets.ReadOnly(), h.investigateEntity),
		},
	}
}

const investigateEntityDescription = "Investigate one or more Identity Protection entities by ID, name, email, IP, or domain.\n\n" +
	"Use this to look up entity details, activity timelines, relationship graphs, and risk " +
	"assessments; at least one identifier must be supplied, and multiple identifiers are " +
	"combined with AND logic (email and IP cannot be combined — email takes precedence). " +
	"Returns a structured response with an investigation_summary, resolved entity IDs, and " +
	"results keyed by each requested investigation type."

type handlers struct {
	c *client.CrowdStrikeAPISpecification
}

// investigationTypes returns the requested types, defaulting to entity_details.
func (in investigateEntityInput) investigationTypes() []string {
	if len(in.InvestigationTypes) == 0 {
		return []string{"entity_details"}
	}
	return in.InvestigationTypes
}

// investigateEntity orchestrates entity resolution and the requested
// investigations, returning a synthesized response.
func (h *handlers) investigateEntity(ctx context.Context, in investigateEntityInput) (any, error) {
	if errResp := validateIdentifiers(in); errResp != nil {
		return errResp, nil
	}

	types := in.investigationTypes()
	searchCriteria := map[string]any{
		"entity_ids":      in.EntityIDs,
		"entity_names":    in.EntityNames,
		"email_addresses": in.EmailAddresses,
		"ip_addresses":    in.IPAddresses,
		"domain_names":    in.DomainNames,
	}

	ids, apiErr := h.resolveEntities(ctx, in)
	if apiErr != nil {
		return errorResponse(apiErr.Message, 0, types, searchCriteria), nil
	}
	if len(ids) == 0 {
		return errorResponse("No entities found matching the provided criteria", 0, types, searchCriteria), nil
	}

	results := make(map[string]any, len(types))
	for _, kind := range types {
		r, e := h.runInvestigation(ctx, kind, ids, in)
		if e != nil {
			return errorResponse(
				fmt.Sprintf("Investigation failed during %s: %s", kind, e.Message),
				len(ids), types, nil), nil
		}
		results[kind] = r
	}

	return synthesizeResponse(ids, results, types, searchCriteria), nil
}

// nowUTC renders the current time in the microsecond ISO format the Python
// server used (datetime.utcnow().isoformat()).
func nowUTC() string {
	return time.Now().UTC().Format("2006-01-02T15:04:05.000000")
}

// validateIdentifiers ports _validate_entity_identifiers: at least one
// identifier is required, and entity_names/email_addresses cannot be a bare
// wildcard. It returns a failed-status error response, or nil when valid.
func validateIdentifiers(in investigateEntityInput) map[string]any {
	if len(in.EntityIDs) == 0 && in.EntityNames == "" && in.EmailAddresses == "" &&
		len(in.IPAddresses) == 0 && len(in.DomainNames) == 0 {
		return errorResponse(
			"At least one entity identifier must be provided (entity_ids, entity_names, "+
				"email_addresses, ip_addresses, or domain_names)",
			0, in.investigationTypes(), nil)
	}
	if isBareWildcard(in.EntityNames) || isBareWildcard(in.EmailAddresses) {
		return errorResponse(
			"entity_names/email_addresses cannot be a bare wildcard ('*'). Provide a more "+
				"specific pattern (e.g., 'Admin*') or narrow the search.",
			0, in.investigationTypes(), nil)
	}
	return nil
}

// isBareWildcard reports whether s is non-empty but contains only '*' and
// spaces, matching the Python strip("* ") == "" check.
func isBareWildcard(s string) bool {
	if s == "" {
		return false
	}
	for _, r := range s {
		if r != '*' && r != ' ' {
			return false
		}
	}
	return true
}

// errorResponse ports _create_error_response: a standardized failed-status
// envelope, optionally carrying the search criteria.
func errorResponse(message string, entityCount int, investigationTypes []string, searchCriteria map[string]any) map[string]any {
	resp := map[string]any{
		"error": message,
		"investigation_summary": map[string]any{
			"entity_count":        entityCount,
			"investigation_types": investigationTypes,
			"timestamp":           nowUTC(),
			"status":              "failed",
		},
	}
	if searchCriteria != nil {
		resp["search_criteria"] = searchCriteria
	}
	return resp
}
