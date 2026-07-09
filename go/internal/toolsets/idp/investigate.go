package idp

import (
	"context"
	"fmt"
	"maps"
	"strings"

	fal "github.com/crowdstrike/falcon-mcp/internal/falcon"
)

// validEventTypes is the set of timeline event categories the API accepts.
// Interpolated enum tokens are restricted to this set because they are not
// quoted string literals and so bypass SanitizeInput's escaping.
var validEventTypes = map[string]bool{
	"ACTIVITY":     true,
	"NOTIFICATION": true,
	"THREAT":       true,
	"ENTITY":       true,
	"AUDIT":        true,
	"POLICY":       true,
	"SYSTEM":       true,
}

// boolOpt resolves an optional bool pointer to its value, defaulting to true
// (the Python default for the include_* flags).
func boolOpt(p *bool) bool {
	if p == nil {
		return true
	}
	return *p
}

// runInvestigation dispatches a single investigation type against the resolved
// entity IDs, returning the result fragment or a *fal.Error.
func (h *handlers) runInvestigation(ctx context.Context, kind string, ids []string, in investigateEntityInput) (map[string]any, *fal.Error) {
	switch kind {
	case "entity_details":
		return h.entityDetails(ctx, ids, in)
	case "timeline_analysis":
		return h.timelineAnalysis(ctx, ids, in)
	case "relationship_analysis":
		return h.relationshipAnalysis(ctx, ids, in)
	case "risk_assessment":
		return h.riskAssessment(ctx, ids)
	default:
		return nil, &fal.Error{Message: fmt.Sprintf("Unknown investigation type: %s", kind)}
	}
}

func (h *handlers) entityDetails(ctx context.Context, ids []string, in investigateEntityInput) (map[string]any, *fal.Error) {
	var fields []string
	fields = append(fields,
		"entityId", "primaryDisplayName", "secondaryDisplayName", "type",
		"riskScore", "riskScoreSeverity",
		"riskFactors {\ntype\nseverity\n}")
	if boolOpt(in.IncludeAssociations) {
		fields = append(fields, associationsFragment)
	}
	if boolOpt(in.IncludeIncidents) {
		fields = append(fields, incidentsFragment)
	}
	if boolOpt(in.IncludeAccounts) {
		fields = append(fields, accountsFragment)
	}
	query := fmt.Sprintf(`
query {
    entities(entityIds: %s, first: 50) {
        nodes {
            %s
        }
    }
}`, jsonStringSlice(ids), strings.Join(fields, "\n"))

	body, apiErr := fal.GraphQL(ctx, h.c, query, scopeIdentityRead)
	if apiErr != nil {
		return nil, apiErr
	}
	nodes := entityNodes(body)
	return map[string]any{"entities": toAnySlice(nodes), "entity_count": len(nodes)}, nil
}

func (h *handlers) timelineAnalysis(ctx context.Context, ids []string, in investigateEntityInput) (map[string]any, *fal.Error) {
	limit := in.Limit
	if limit == 0 {
		limit = defaultLimit
	}
	results := make([]any, 0, len(ids))
	for _, id := range ids {
		filters := []string{fmt.Sprintf(`sourceEntityQuery: {entityIds: [%s]}`, jsonString(id))}
		if in.TimelineStartTime != "" {
			filters = append(filters, fmt.Sprintf(`startTime: %s`, jsonString(in.TimelineStartTime)))
		}
		if in.TimelineEndTime != "" {
			filters = append(filters, fmt.Sprintf(`endTime: %s`, jsonString(in.TimelineEndTime)))
		}
		if len(in.TimelineEventTypes) > 0 {
			// Event types are interpolated as unquoted GraphQL enums, which
			// SanitizeInput's string-literal rules do not protect. Restrict to
			// the documented enum values so no caller token reaches the query
			// verbatim.
			var cats []string
			for _, c := range in.TimelineEventTypes {
				if validEventTypes[c] {
					cats = append(cats, c)
				}
			}
			if len(cats) > 0 {
				filters = append(filters, fmt.Sprintf("categories: [%s]", strings.Join(cats, ", ")))
			}
		}
		query := fmt.Sprintf(`
query {
    timeline(%s, first: %d) {
        nodes {
            eventId
            eventType
            eventSeverity
            timestamp
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}`, strings.Join(filters, ", "), limit)

		body, apiErr := fal.GraphQL(ctx, h.c, query, scopeIdentityRead)
		if apiErr != nil {
			return nil, apiErr
		}
		data, _ := body["data"].(map[string]any)
		timeline, _ := data["timeline"].(map[string]any)
		nodes, _ := timeline["nodes"].([]any)
		pageInfo, _ := timeline["pageInfo"].(map[string]any)
		if nodes == nil {
			nodes = []any{}
		}
		results = append(results, map[string]any{
			"entity_id": id,
			"timeline":  nodes,
			"page_info": pageInfo,
		})
	}
	return map[string]any{"timelines": results, "entity_count": len(ids)}, nil
}

func (h *handlers) relationshipAnalysis(ctx context.Context, ids []string, in investigateEntityInput) (map[string]any, *fal.Error) {
	limit := in.Limit
	if limit == 0 {
		limit = defaultLimit
	}
	depth := in.RelationshipDepth
	if depth == 0 {
		depth = defaultRelationshipDepth
	}
	results := make([]any, 0, len(ids))
	for _, id := range ids {
		query := fmt.Sprintf(`
query {
    entities(entityIds: [%s], first: %d) {
        nodes {
            entityId
            primaryDisplayName
            secondaryDisplayName
            type
            riskScore
            riskScoreSeverity
            riskFactors {
                type
                severity
            }
            %s
        }
    }
}`, jsonString(id), limit, associationFieldsForDepth(int(depth)))

		body, apiErr := fal.GraphQL(ctx, h.c, query, scopeIdentityRead)
		if apiErr != nil {
			return nil, apiErr
		}
		nodes := entityNodes(body)
		if len(nodes) > 0 {
			assoc, _ := nodes[0]["associations"].([]any)
			results = append(results, map[string]any{
				"entity_id":          id,
				"associations":       assoc,
				"relationship_count": len(assoc),
			})
		} else {
			results = append(results, map[string]any{
				"entity_id":          id,
				"associations":       []any{},
				"relationship_count": 0,
			})
		}
	}
	return map[string]any{"relationships": results, "entity_count": len(ids)}, nil
}

func (h *handlers) riskAssessment(ctx context.Context, ids []string) (map[string]any, *fal.Error) {
	query := fmt.Sprintf(`
query {
    entities(entityIds: %s, first: 50) {
        nodes {
            entityId
            primaryDisplayName
            riskScore
            riskScoreSeverity
            riskFactors {
                type
                severity
            }
        }
    }
}`, jsonStringSlice(ids))

	body, apiErr := fal.GraphQL(ctx, h.c, query, scopeIdentityRead)
	if apiErr != nil {
		return nil, apiErr
	}
	nodes := entityNodes(body)
	assessments := make([]any, 0, len(nodes))
	for _, n := range nodes {
		assessments = append(assessments, map[string]any{
			"entityId":           n["entityId"],
			"primaryDisplayName": n["primaryDisplayName"],
			"riskScore":          n["riskScore"],
			"riskScoreSeverity":  n["riskScoreSeverity"],
			"riskFactors":        n["riskFactors"],
		})
	}
	return map[string]any{"risk_assessments": assessments, "entity_count": len(assessments)}, nil
}

// associationFieldsForDepth builds the nested associations selection to the
// given relationship depth, mirroring the Python recursive builder.
func associationFieldsForDepth(depth int) string {
	if depth <= 0 {
		return ""
	}
	nested := ""
	if depth > 1 {
		nested = associationFieldsForDepth(depth - 1)
	}
	return fmt.Sprintf(`associations {
        bindingType
        ... on EntityAssociation {
            entity {
                entityId
                primaryDisplayName
                secondaryDisplayName
                type
                riskScore
                riskScoreSeverity
                %s
            }
        }
        ... on LocalAdminDomainEntityAssociation {
            entityType
            entity {
                entityId
                primaryDisplayName
                secondaryDisplayName
                type
                %s
            }
        }
    }`, nested, nested)
}

func toAnySlice(nodes []map[string]any) []any {
	out := make([]any, len(nodes))
	for i, n := range nodes {
		out[i] = n
	}
	return out
}

// synthesizeResponse ports _synthesize_investigation_response: it assembles the
// investigation_summary, resolved entity IDs, and per-type results.
func synthesizeResponse(ids []string, results map[string]any, investigationTypes []string, searchCriteria map[string]any) map[string]any {
	summary := map[string]any{
		"entity_count":        len(ids),
		"resolved_entity_ids": ids,
		"investigation_types": investigationTypes,
		"timestamp":           nowUTC(),
		"status":              "completed",
	}
	if anyCriteria(searchCriteria) {
		summary["search_criteria"] = searchCriteria
	}
	resp := map[string]any{
		"investigation_summary": summary,
		"entities":              ids,
	}
	maps.Copy(resp, results)
	return resp
}

// anyCriteria reports whether the search-criteria map has at least one non-empty
// value, matching Python's any(search_criteria.values()).
func anyCriteria(c map[string]any) bool {
	for _, v := range c {
		switch val := v.(type) {
		case nil:
		case string:
			if val != "" {
				return true
			}
		case []string:
			if len(val) > 0 {
				return true
			}
		default:
			return true
		}
	}
	return false
}

const associationsFragment = `associations {
    bindingType
    ... on EntityAssociation {
        entity {
            entityId
            primaryDisplayName
            secondaryDisplayName
            type
        }
    }
    ... on GeoLocationAssociation {
        geoLocation {
            country
            city
        }
    }
}`

const incidentsFragment = `openIncidents(first: 10) {
    nodes {
        type
        startTime
        endTime
    }
}`

const accountsFragment = `accounts {
    ... on ActiveDirectoryAccountDescriptor {
        domain
        samAccountName
    }
    ... on SsoUserAccountDescriptor {
        dataSource
        title
    }
}`
