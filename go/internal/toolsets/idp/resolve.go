package idp

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"strings"

	fal "github.com/crowdstrike/falcon-mcp/internal/falcon"
)

// resolveEntities ports _resolve_entities: it combines every supplied
// identifier into a single AND-logic GraphQL query, returning the union of
// directly-supplied entity IDs and any resolved from the query. All
// interpolated values are sanitized. A non-nil *fal.Error signals an API
// failure.
func (h *handlers) resolveEntities(ctx context.Context, in investigateEntityInput) ([]string, *fal.Error) {
	resolved := append([]string(nil), in.EntityIDs...)

	// Email (USER) and IP (ENDPOINT) cannot be combined; email takes precedence.
	hasUser := in.EmailAddresses != ""
	ipAddresses := in.IPAddresses
	if hasUser && len(ipAddresses) > 0 {
		ipAddresses = nil
	}

	var filters, fields []string
	if in.EntityNames != "" {
		filters = append(filters, fmt.Sprintf("primaryDisplayNamePattern: %s", jsonString(in.EntityNames)))
		fields = append(fields, "primaryDisplayName")
	}
	if in.EmailAddresses != "" {
		filters = append(filters, fmt.Sprintf("secondaryDisplayNamePattern: %s", jsonString(in.EmailAddresses)))
		filters = append(filters, "types: [USER]")
		fields = append(fields, "primaryDisplayName", "secondaryDisplayName")
	}
	if len(ipAddresses) > 0 {
		filters = append(filters, fmt.Sprintf("primaryDisplayNames: %s", jsonStringSlice(ipAddresses)))
		filters = append(filters, "types: [ENDPOINT]")
		fields = append(fields, "primaryDisplayName")
	}
	if len(in.DomainNames) > 0 {
		filters = append(filters, fmt.Sprintf("domains: %s", jsonStringSlice(in.DomainNames)))
		fields = append(fields, "primaryDisplayName", "secondaryDisplayName")
	}

	if len(filters) > 0 {
		fieldsStr := strings.Join(dedupe(fields), "\n")
		if len(in.DomainNames) > 0 {
			fieldsStr += "\naccounts {\n... on ActiveDirectoryAccountDescriptor {\ndomain\nsamAccountName\n}\n}"
		}
		limit := in.Limit
		if limit == 0 {
			limit = defaultLimit
		}
		query := fmt.Sprintf(`
query {
    entities(%s, first: %d) {
        nodes {
            entityId
            %s
        }
    }
}`, strings.Join(filters, ", "), limit, fieldsStr)

		body, apiErr := fal.GraphQL(ctx, h.c, query, scopeIdentityRead)
		if apiErr != nil {
			return nil, apiErr
		}
		for _, node := range entityNodes(body) {
			if id, ok := node["entityId"].(string); ok {
				resolved = append(resolved, id)
			}
		}
	}

	return dedupe(resolved), nil
}

// jsonString sanitizes s and renders it as a JSON string literal for safe
// interpolation into a GraphQL query.
func jsonString(s string) string {
	b, _ := json.Marshal(fal.SanitizeInput(s))
	return string(b)
}

// jsonStringSlice sanitizes each element and renders the slice as a JSON array
// literal.
func jsonStringSlice(ss []string) string {
	out := make([]string, len(ss))
	for i, s := range ss {
		out[i] = fal.SanitizeInput(s)
	}
	b, _ := json.Marshal(out)
	return string(b)
}

// dedupe returns the unique elements of in, sorted for deterministic output.
func dedupe(in []string) []string {
	seen := make(map[string]bool, len(in))
	var out []string
	for _, s := range in {
		if !seen[s] {
			seen[s] = true
			out = append(out, s)
		}
	}
	sort.Strings(out)
	return out
}

// entityNodes extracts data.entities.nodes from a GraphQL response body,
// returning nil when the path is absent.
func entityNodes(body map[string]any) []map[string]any {
	data, _ := body["data"].(map[string]any)
	entities, _ := data["entities"].(map[string]any)
	rawNodes, _ := entities["nodes"].([]any)
	nodes := make([]map[string]any, 0, len(rawNodes))
	for _, n := range rawNodes {
		if m, ok := n.(map[string]any); ok {
			nodes = append(nodes, m)
		}
	}
	return nodes
}
