package idp

import (
	"context"
	"errors"
	"strings"
	"testing"
)

// ==========================================
// Helpers for building stub graphql funcs
// ==========================================

// captureFunc returns a graphqlFunc that captures the query string into *got
// and returns the provided response.
func captureFunc(got *string, resp any, err error) graphqlFunc {
	return func(_ context.Context, query string) (any, error) {
		*got = query
		return resp, err
	}
}

// allCaptureFunc returns a graphqlFunc that appends every query to *got
// and always returns the same response. Use this when you need to assert
// on the resolve query (first call) rather than the investigation query (last call).
func allCaptureFunc(got *[]string, resp any, err error) graphqlFunc {
	return func(_ context.Context, query string) (any, error) {
		*got = append(*got, query)
		return resp, err
	}
}

// containsAny reports whether any element of queries contains sub.
func containsAny(queries []string, sub string) bool {
	for _, q := range queries {
		if strings.Contains(q, sub) {
			return true
		}
	}
	return false
}

// fakeEntitiesResponse builds the minimal GraphQL response shape that the code
// expects: {"data":{"entities":{"nodes":[...]}}}
func fakeEntitiesResponse(nodes []map[string]any) map[string]any {
	anyNodes := make([]any, len(nodes))
	for i, n := range nodes {
		anyNodes[i] = n
	}
	return map[string]any{
		"data": map[string]any{
			"entities": map[string]any{
				"nodes": anyNodes,
			},
		},
	}
}

// fakeTimelineResponse builds a GraphQL response for a timeline query.
func fakeTimelineResponse(nodes []any, hasNextPage bool) map[string]any {
	return map[string]any{
		"data": map[string]any{
			"timeline": map[string]any{
				"nodes": nodes,
				"pageInfo": map[string]any{
					"hasNextPage": hasNextPage,
					"endCursor":   nil,
				},
			},
		},
	}
}

// ==========================================
// Query-builder unit tests
// ==========================================

func TestBuildEntityDetailsQuery_ContainsEntityFilter(t *testing.T) {
	ids := []string{"entity-001", "entity-002"}
	query := buildEntityDetailsQuery(ids, true, true, true, true)

	// Must contain the entity IDs as a JSON array.
	if !strings.Contains(query, `"entity-001"`) {
		t.Errorf("query missing entity-001: %s", query)
	}
	if !strings.Contains(query, `"entity-002"`) {
		t.Errorf("query missing entity-002: %s", query)
	}
	// Must use the entities(...) field.
	if !strings.Contains(query, "entities(entityIds:") {
		t.Errorf("query missing entities(entityIds: %s", query)
	}
	// Core fields must be present.
	for _, field := range []string{"entityId", "primaryDisplayName", "riskScore", "riskScoreSeverity"} {
		if !strings.Contains(query, field) {
			t.Errorf("query missing field %q: %s", field, query)
		}
	}
	// Optional sections included.
	if !strings.Contains(query, "riskFactors") {
		t.Errorf("query missing riskFactors")
	}
	if !strings.Contains(query, "associations") {
		t.Errorf("query missing associations")
	}
	if !strings.Contains(query, "openIncidents") {
		t.Errorf("query missing openIncidents")
	}
	if !strings.Contains(query, "accounts") {
		t.Errorf("query missing accounts")
	}
}

func TestBuildEntityDetailsQuery_OptionalFieldsOmitted(t *testing.T) {
	query := buildEntityDetailsQuery([]string{"e1"}, false, false, false, false)

	for _, section := range []string{"riskFactors", "associations", "openIncidents", "accounts"} {
		if strings.Contains(query, section) {
			t.Errorf("query should NOT contain %q when include=false: %s", section, query)
		}
	}
}

func TestBuildTimelineQuery_Basic(t *testing.T) {
	entityID := "entity-abc"
	query := buildTimelineQuery(entityID, nil, nil, nil, 25)

	if !strings.Contains(query, `"entity-abc"`) {
		t.Errorf("timeline query missing entity ID")
	}
	if !strings.Contains(query, "sourceEntityQuery:") {
		t.Errorf("timeline query missing sourceEntityQuery filter")
	}
	if !strings.Contains(query, "first: 25") {
		t.Errorf("timeline query missing first: 25")
	}
	// Should not contain time filters.
	if strings.Contains(query, "startTime:") {
		t.Errorf("unexpected startTime filter")
	}
	if strings.Contains(query, "categories:") {
		t.Errorf("unexpected categories filter")
	}
	// Must include the inline fragment types.
	if !strings.Contains(query, "TimelineAuthenticationEvent") {
		t.Errorf("timeline query missing TimelineAuthenticationEvent")
	}
}

func TestBuildTimelineQuery_WithFilters(t *testing.T) {
	start := "2024-01-01T00:00:00Z"
	end := "2024-01-31T23:59:59Z"
	query := buildTimelineQuery("e1", &start, &end, []string{"ACTIVITY", "THREAT"}, 100)

	if !strings.Contains(query, `startTime: "2024-01-01T00:00:00Z"`) {
		t.Errorf("missing startTime filter")
	}
	if !strings.Contains(query, `endTime: "2024-01-31T23:59:59Z"`) {
		t.Errorf("missing endTime filter")
	}
	if !strings.Contains(query, "categories: [ACTIVITY, THREAT]") {
		t.Errorf("missing categories filter, got: %s", query)
	}
}

func TestBuildRelationshipAnalysisQuery(t *testing.T) {
	query := buildRelationshipAnalysisQuery("entity-x", 2, true, 50)

	if !strings.Contains(query, `"entity-x"`) {
		t.Errorf("missing entity ID in relationship query")
	}
	if !strings.Contains(query, "associations") {
		t.Errorf("missing associations in relationship query")
	}
	if !strings.Contains(query, "riskScore") {
		t.Errorf("missing riskScore in relationship query")
	}
	if !strings.Contains(query, "riskFactors") {
		t.Errorf("missing riskFactors in relationship query")
	}
}

func TestBuildRiskAssessmentQuery(t *testing.T) {
	query := buildRiskAssessmentQuery([]string{"e1", "e2"}, true)

	if !strings.Contains(query, `"e1"`) || !strings.Contains(query, `"e2"`) {
		t.Errorf("risk query missing entity IDs")
	}
	if !strings.Contains(query, "riskScore") {
		t.Errorf("risk query missing riskScore")
	}
	if !strings.Contains(query, "riskFactors") {
		t.Errorf("risk query missing riskFactors")
	}
}

// ==========================================
// Integration-style: investigateEntity with stubbed graphql
// ==========================================

func TestInvestigateEntity_EntityDetails(t *testing.T) {
	var capturedQuery string
	fakeNode := map[string]any{
		"entityId":           "entity-001",
		"primaryDisplayName": "John Doe",
		"riskScore":          float64(75),
		"riskScoreSeverity":  "HIGH",
	}
	resp := fakeEntitiesResponse([]map[string]any{fakeNode})

	gql := captureFunc(&capturedQuery, resp, nil)

	in := InvestigateEntityInput{
		EntityIDs:          []string{"entity-001"},
		InvestigationTypes: []string{"entity_details"},
	}
	result := investigateEntity(context.Background(), in, gql)

	// Must have investigation_summary.
	summary, ok := result["investigation_summary"].(map[string]any)
	if !ok {
		t.Fatalf("missing investigation_summary, got: %v", result)
	}
	if summary["status"] != "completed" {
		t.Errorf("unexpected status: %v", summary["status"])
	}
	if summary["entity_count"] != 1 {
		t.Errorf("unexpected entity_count: %v", summary["entity_count"])
	}

	// Must have entity_details key.
	details, ok := result["entity_details"].(map[string]any)
	if !ok {
		t.Fatalf("missing entity_details key in result: %v", result)
	}
	if details["entity_count"] != 1 {
		t.Errorf("unexpected entity_count in details: %v", details["entity_count"])
	}

	// The generated query must contain the entity IDs and expected fields.
	if !strings.Contains(capturedQuery, `"entity-001"`) {
		t.Errorf("generated query missing entity ID, got: %s", capturedQuery)
	}
	if !strings.Contains(capturedQuery, "entityId") {
		t.Errorf("generated query missing entityId field")
	}
}

func TestInvestigateEntity_MultipleTypes(t *testing.T) {
	callCount := 0
	// For entity_details and risk_assessment both use the entities query.
	gql := func(_ context.Context, query string) (any, error) {
		callCount++
		return fakeEntitiesResponse([]map[string]any{
			{"entityId": "e1", "primaryDisplayName": "Alice", "riskScore": float64(50), "riskScoreSeverity": "MEDIUM"},
		}), nil
	}

	in := InvestigateEntityInput{
		EntityIDs:          []string{"e1"},
		InvestigationTypes: []string{"entity_details", "risk_assessment"},
	}
	result := investigateEntity(context.Background(), in, gql)

	if _, ok := result["entity_details"]; !ok {
		t.Errorf("missing entity_details key")
	}
	if _, ok := result["risk_assessment"]; !ok {
		t.Errorf("missing risk_assessment key")
	}

	// Two queries: one for entity_details, one for risk_assessment.
	if callCount != 2 {
		t.Errorf("expected 2 graphql calls, got %d", callCount)
	}
}

func TestInvestigateEntity_TimelineAnalysis(t *testing.T) {
	var capturedQuery string
	gql := func(_ context.Context, query string) (any, error) {
		capturedQuery = query
		return fakeTimelineResponse([]any{
			map[string]any{"eventId": "evt-1", "eventType": "AUTH", "timestamp": "2024-01-15T10:00:00Z"},
		}, false), nil
	}

	start := "2024-01-01T00:00:00Z"
	in := InvestigateEntityInput{
		EntityIDs:          []string{"e1"},
		InvestigationTypes: []string{"timeline_analysis"},
		TimelineStartTime:  &start,
	}
	result := investigateEntity(context.Background(), in, gql)

	ta, ok := result["timeline_analysis"].(map[string]any)
	if !ok {
		t.Fatalf("missing timeline_analysis in result: %v", result)
	}
	timelines, _ := ta["timelines"].([]map[string]any)
	if len(timelines) != 1 {
		t.Errorf("expected 1 timeline entry, got %d", len(timelines))
	}
	if timelines[0]["entity_id"] != "e1" {
		t.Errorf("wrong entity_id: %v", timelines[0]["entity_id"])
	}
	if !strings.Contains(capturedQuery, `startTime: "2024-01-01T00:00:00Z"`) {
		t.Errorf("timeline query missing startTime filter: %s", capturedQuery)
	}
}

func TestInvestigateEntity_GraphQLError(t *testing.T) {
	gql := func(_ context.Context, _ string) (any, error) {
		return nil, errors.New("API connection refused")
	}

	in := InvestigateEntityInput{
		EntityIDs:          []string{"e1"},
		InvestigationTypes: []string{"entity_details"},
	}
	result := investigateEntity(context.Background(), in, gql)

	if _, hasErr := result["error"]; !hasErr {
		t.Errorf("expected error key in result, got: %v", result)
	}
	summary, ok := result["investigation_summary"].(map[string]any)
	if !ok {
		t.Fatalf("missing investigation_summary")
	}
	if summary["status"] != "failed" {
		t.Errorf("expected status=failed, got %v", summary["status"])
	}
}

func TestInvestigateEntity_NoIdentifiers(t *testing.T) {
	var called bool
	gql := func(_ context.Context, _ string) (any, error) {
		called = true
		return nil, nil
	}

	in := InvestigateEntityInput{
		InvestigationTypes: []string{"entity_details"},
	}
	result := investigateEntity(context.Background(), in, gql)

	if called {
		t.Error("graphql should not be called when no identifiers provided")
	}
	if _, hasErr := result["error"]; !hasErr {
		t.Errorf("expected error key, got: %v", result)
	}
	errMsg, _ := result["error"].(string)
	if !strings.Contains(errMsg, "At least one entity identifier") {
		t.Errorf("unexpected error message: %s", errMsg)
	}
}

func TestInvestigateEntity_BareWildcardRejected(t *testing.T) {
	wildcard := "*"
	in := InvestigateEntityInput{
		EntityNames:        &wildcard,
		InvestigationTypes: []string{"entity_details"},
	}
	result := investigateEntity(context.Background(), in, func(_ context.Context, _ string) (any, error) {
		return nil, nil
	})
	errMsg, _ := result["error"].(string)
	if !strings.Contains(errMsg, "bare wildcard") {
		t.Errorf("expected bare wildcard error, got: %s", errMsg)
	}
}

func TestInvestigateEntity_NoEntitiesFound(t *testing.T) {
	// GraphQL returns empty nodes — no entities match.
	gql := captureFunc(new(string), fakeEntitiesResponse(nil), nil)

	name := "NonExistent"
	in := InvestigateEntityInput{
		EntityNames:        &name,
		InvestigationTypes: []string{"entity_details"},
	}
	result := investigateEntity(context.Background(), in, gql)

	errMsg, _ := result["error"].(string)
	if !strings.Contains(errMsg, "No entities found") {
		t.Errorf("expected 'No entities found' error, got: %s", errMsg)
	}
}

func TestInvestigateEntity_EmailFilter(t *testing.T) {
	var capturedQueries []string
	gql := allCaptureFunc(&capturedQueries, fakeEntitiesResponse([]map[string]any{
		{"entityId": "u1", "primaryDisplayName": "User One"},
	}), nil)

	email := "user@example.com"
	in := InvestigateEntityInput{
		EmailAddresses:     &email,
		InvestigationTypes: []string{"entity_details"},
	}
	result := investigateEntity(context.Background(), in, gql)

	// The resolve-entities query (first call) must use secondaryDisplayNamePattern and USER type.
	if !containsAny(capturedQueries, "secondaryDisplayNamePattern") {
		t.Errorf("no query contained secondaryDisplayNamePattern, queries: %v", capturedQueries)
	}
	if !containsAny(capturedQueries, "types: [USER]") {
		t.Errorf("no query contained types: [USER], queries: %v", capturedQueries)
	}
	// The result should not be an error.
	if _, hasErr := result["error"]; hasErr {
		t.Errorf("unexpected error: %v", result["error"])
	}
}

func TestInvestigateEntity_IPFilter(t *testing.T) {
	var capturedQueries []string
	gql := allCaptureFunc(&capturedQueries, fakeEntitiesResponse([]map[string]any{
		{"entityId": "ep1", "primaryDisplayName": "1.1.1.1"},
	}), nil)

	in := InvestigateEntityInput{
		IPAddresses:        []string{"1.1.1.1"},
		InvestigationTypes: []string{"entity_details"},
	}
	result := investigateEntity(context.Background(), in, gql)

	if !containsAny(capturedQueries, "primaryDisplayNames:") {
		t.Errorf("no query contained primaryDisplayNames, queries: %v", capturedQueries)
	}
	if !containsAny(capturedQueries, "types: [ENDPOINT]") {
		t.Errorf("no query contained types: [ENDPOINT], queries: %v", capturedQueries)
	}
	if _, hasErr := result["error"]; hasErr {
		t.Errorf("unexpected error: %v", result["error"])
	}
}

func TestInvestigateEntity_EmailIPConflict_EmailWins(t *testing.T) {
	var capturedQueries []string
	gql := allCaptureFunc(&capturedQueries, fakeEntitiesResponse([]map[string]any{
		{"entityId": "u1"},
	}), nil)

	email := "user@example.com"
	in := InvestigateEntityInput{
		EmailAddresses:     &email,
		IPAddresses:        []string{"1.1.1.1"},
		InvestigationTypes: []string{"entity_details"},
	}
	investigateEntity(context.Background(), in, gql)

	// The resolve query must use USER type, not ENDPOINT.
	if !containsAny(capturedQueries, "types: [USER]") {
		t.Errorf("expected USER type somewhere in queries: %v", capturedQueries)
	}
	// No query should contain ENDPOINT type.
	if containsAny(capturedQueries, "types: [ENDPOINT]") {
		t.Errorf("should not contain ENDPOINT type when email takes precedence: %v", capturedQueries)
	}
}

func TestInvestigateEntity_UnknownType(t *testing.T) {
	gql := captureFunc(new(string), nil, nil)

	in := InvestigateEntityInput{
		EntityIDs:          []string{"e1"},
		InvestigationTypes: []string{"nonexistent_type"},
	}
	result := investigateEntity(context.Background(), in, gql)

	errMsg, _ := result["error"].(string)
	if !strings.Contains(errMsg, "unknown investigation type") {
		t.Errorf("expected 'unknown investigation type' error, got: %s", errMsg)
	}
}

func TestInvestigateEntity_RiskAssessment(t *testing.T) {
	var capturedQuery string
	gql := captureFunc(&capturedQuery, fakeEntitiesResponse([]map[string]any{
		{
			"entityId":           "e1",
			"primaryDisplayName": "Alice",
			"riskScore":          float64(80),
			"riskScoreSeverity":  "HIGH",
			"riskFactors": []any{
				map[string]any{"type": "PASSWORD_NEVER_EXPIRES", "severity": "HIGH"},
			},
		},
	}), nil)

	in := InvestigateEntityInput{
		EntityIDs:          []string{"e1"},
		InvestigationTypes: []string{"risk_assessment"},
	}
	result := investigateEntity(context.Background(), in, gql)

	ra, ok := result["risk_assessment"].(map[string]any)
	if !ok {
		t.Fatalf("missing risk_assessment key: %v", result)
	}
	assessments, ok := ra["risk_assessments"].([]map[string]any)
	if !ok || len(assessments) == 0 {
		t.Fatalf("expected risk_assessments slice, got: %v", ra)
	}
	if assessments[0]["riskScoreSeverity"] != "HIGH" {
		t.Errorf("wrong riskScoreSeverity: %v", assessments[0]["riskScoreSeverity"])
	}
	// Query must contain riskFactors.
	if !strings.Contains(capturedQuery, "riskFactors") {
		t.Errorf("risk query missing riskFactors field")
	}
}

func TestInvestigateEntity_RelationshipAnalysis(t *testing.T) {
	var capturedQuery string
	gql := captureFunc(&capturedQuery, fakeEntitiesResponse([]map[string]any{
		{
			"entityId":           "e1",
			"primaryDisplayName": "Bob",
			"associations": []any{
				map[string]any{"bindingType": "MEMBER_OF"},
			},
		},
	}), nil)

	in := InvestigateEntityInput{
		EntityIDs:          []string{"e1"},
		InvestigationTypes: []string{"relationship_analysis"},
		RelationshipDepth:  2,
	}
	result := investigateEntity(context.Background(), in, gql)

	relResult, ok := result["relationship_analysis"].(map[string]any)
	if !ok {
		t.Fatalf("missing relationship_analysis key: %v", result)
	}
	rels, ok := relResult["relationships"].([]map[string]any)
	if !ok || len(rels) == 0 {
		t.Fatalf("expected relationships slice, got: %v", relResult)
	}
	if rels[0]["relationship_count"] != 1 {
		t.Errorf("expected relationship_count=1, got: %v", rels[0]["relationship_count"])
	}
	if !strings.Contains(capturedQuery, "associations") {
		t.Errorf("relationship query missing associations")
	}
}

// ==========================================
// Toolset interface tests
// ==========================================

func TestToolsetMetadata(t *testing.T) {
	ts := &Toolset{}
	if ts.GetName() != "idp" {
		t.Errorf("expected name 'idp', got %q", ts.GetName())
	}
	if ts.GetResources() != nil {
		t.Errorf("expected nil resources, got %v", ts.GetResources())
	}
	if ts.GetDescription() == "" {
		t.Error("description must not be empty")
	}
}
