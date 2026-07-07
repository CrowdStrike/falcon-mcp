package cloud

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/cloud_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/cloud_security_assets"
	"github.com/crowdstrike/gofalcon/falcon/client/cloud_security_detections"
	"github.com/crowdstrike/gofalcon/falcon/client/container_vulnerabilities"
	"github.com/crowdstrike/gofalcon/falcon/client/kubernetes_protection"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

type mockK8sAPI struct {
	combinedResp *kubernetes_protection.ContainerCombinedOK
	combinedErr  error
	countResp    *kubernetes_protection.ContainerCountOK
	countErr     error
}

func (m *mockK8sAPI) ContainerCombined(p *kubernetes_protection.ContainerCombinedParams, _ ...kubernetes_protection.ClientOption) (*kubernetes_protection.ContainerCombinedOK, error) {
	return m.combinedResp, m.combinedErr
}

func (m *mockK8sAPI) ContainerCount(p *kubernetes_protection.ContainerCountParams, _ ...kubernetes_protection.ClientOption) (*kubernetes_protection.ContainerCountOK, error) {
	return m.countResp, m.countErr
}

type mockContainerVulnAPI struct {
	resp *container_vulnerabilities.ReadCombinedVulnerabilitiesOK
	err  error
}

func (m *mockContainerVulnAPI) ReadCombinedVulnerabilities(p *container_vulnerabilities.ReadCombinedVulnerabilitiesParams, _ ...container_vulnerabilities.ClientOption) (*container_vulnerabilities.ReadCombinedVulnerabilitiesOK, error) {
	return m.resp, m.err
}

type mockCSPMAssetsAPI struct {
	queryResp    *cloud_security_assets.CloudSecurityAssetsQueriesOK
	queryErr     error
	entitiesResp *cloud_security_assets.CloudSecurityAssetsEntitiesGetOK
	entitiesErr  error
	entitiesGot  []string // IDs passed to entities call
}

func (m *mockCSPMAssetsAPI) CloudSecurityAssetsQueries(p *cloud_security_assets.CloudSecurityAssetsQueriesParams, _ ...cloud_security_assets.ClientOption) (*cloud_security_assets.CloudSecurityAssetsQueriesOK, error) {
	return m.queryResp, m.queryErr
}

func (m *mockCSPMAssetsAPI) CloudSecurityAssetsEntitiesGet(p *cloud_security_assets.CloudSecurityAssetsEntitiesGetParams, _ ...cloud_security_assets.ClientOption) (*cloud_security_assets.CloudSecurityAssetsEntitiesGetOK, error) {
	m.entitiesGot = append(m.entitiesGot, p.Ids...)
	return m.entitiesResp, m.entitiesErr
}

type mockIOMAPI struct {
	queryResp    *cloud_security_detections.CspmEvaluationsIomQueriesOK
	queryErr     error
	entitiesResp *cloud_security_detections.CspmEvaluationsIomEntitiesOK
	entitiesErr  error
}

func (m *mockIOMAPI) CspmEvaluationsIomQueries(p *cloud_security_detections.CspmEvaluationsIomQueriesParams, _ ...cloud_security_detections.ClientOption) (*cloud_security_detections.CspmEvaluationsIomQueriesOK, error) {
	return m.queryResp, m.queryErr
}

func (m *mockIOMAPI) CspmEvaluationsIomEntities(p *cloud_security_detections.CspmEvaluationsIomEntitiesParams, _ ...cloud_security_detections.ClientOption) (*cloud_security_detections.CspmEvaluationsIomEntitiesOK, error) {
	return m.entitiesResp, m.entitiesErr
}

type mockCloudPoliciesAPI struct {
	queryResp  *cloud_policies.QuerySuppressionRulesOK
	queryErr   error
	getResp    *cloud_policies.GetSuppressionRulesOK
	getErr     error
	createResp *cloud_policies.CreateSuppressionRuleOK
	createErr  error
	deleteResp *cloud_policies.DeleteSuppressionRulesOK
	deleteErr  error
}

func (m *mockCloudPoliciesAPI) QuerySuppressionRules(p *cloud_policies.QuerySuppressionRulesParams, _ ...cloud_policies.ClientOption) (*cloud_policies.QuerySuppressionRulesOK, error) {
	return m.queryResp, m.queryErr
}

func (m *mockCloudPoliciesAPI) GetSuppressionRules(p *cloud_policies.GetSuppressionRulesParams, _ ...cloud_policies.ClientOption) (*cloud_policies.GetSuppressionRulesOK, error) {
	return m.getResp, m.getErr
}

func (m *mockCloudPoliciesAPI) CreateSuppressionRule(p *cloud_policies.CreateSuppressionRuleParams, _ ...cloud_policies.ClientOption) (*cloud_policies.CreateSuppressionRuleOK, error) {
	return m.createResp, m.createErr
}

func (m *mockCloudPoliciesAPI) DeleteSuppressionRules(p *cloud_policies.DeleteSuppressionRulesParams, _ ...cloud_policies.ClientOption) (*cloud_policies.DeleteSuppressionRulesOK, error) {
	return m.deleteResp, m.deleteErr
}

// ---------------------------------------------------------------------------
// Test helper
// ---------------------------------------------------------------------------

func callTool(t *testing.T, register func(*mcp.Server), name string, args map[string]any) (string, bool) {
	t.Helper()
	srv := mcp.NewServer(&mcp.Implementation{Name: "test", Version: "0"}, nil)
	register(srv)

	clientT, serverT := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, serverT, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil).Connect(ctx, clientT, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	defer cs.Close()

	res, err := cs.CallTool(ctx, &mcp.CallToolParams{Name: name, Arguments: args})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	tc, ok := res.Content[0].(*mcp.TextContent)
	if !ok {
		t.Fatalf("expected TextContent, got %T", res.Content[0])
	}
	return tc.Text, res.IsError
}

func contains(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return true
		}
	}
	return false
}

// ---------------------------------------------------------------------------
// falcon_search_kubernetes_containers tests
// ---------------------------------------------------------------------------

func TestSearchKubernetesContainersSuccess(t *testing.T) {
	containerName := "web-server"
	container := &models.ModelsContainer{ContainerName: &containerName}
	mock := &mockK8sAPI{
		combinedResp: &kubernetes_protection.ContainerCombinedOK{
			Payload: &models.ModelsContainerEntityResponse{
				Resources: []*models.ModelsContainer{container},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchKubernetesContainers(s, mock) },
		"falcon_search_kubernetes_containers",
		map[string]any{"filter": "cloud:'AWS'"},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 container, got %d", len(got))
	}
	if got[0]["container_name"] != containerName {
		t.Errorf("expected container_name=%q, got %v", containerName, got[0]["container_name"])
	}
}

func TestSearchKubernetesContainersEmpty(t *testing.T) {
	mock := &mockK8sAPI{
		combinedResp: &kubernetes_protection.ContainerCombinedOK{
			Payload: &models.ModelsContainerEntityResponse{
				Resources: []*models.ModelsContainer{},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchKubernetesContainers(s, mock) },
		"falcon_search_kubernetes_containers",
		map[string]any{},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v", err)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
}

func TestSearchKubernetesContainersFQLError(t *testing.T) {
	mock := &mockK8sAPI{
		combinedErr: runtime.NewAPIError("ContainerCombined", "bad filter", 400),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchKubernetesContainers(s, mock) },
		"falcon_search_kubernetes_containers",
		map[string]any{"filter": "bogus=="},
	)
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v", err)
	}
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
	if guide, _ := got["fql_guide"].(string); len(guide) < 100 {
		t.Errorf("fql_guide too short/empty: %q", guide)
	}
}

// ---------------------------------------------------------------------------
// falcon_count_kubernetes_containers tests
// ---------------------------------------------------------------------------

func TestCountKubernetesContainersSuccess(t *testing.T) {
	count := int64(42)
	mock := &mockK8sAPI{
		countResp: &kubernetes_protection.ContainerCountOK{
			Payload: &models.CommonCountResponse{
				Resources: []*models.CommonCountAsResource{
					{Count: &count},
				},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerCountKubernetesContainers(s, mock) },
		"falcon_count_kubernetes_containers",
		map[string]any{},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got float64
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a number: %v (%s)", err, text)
	}
	if got != 42 {
		t.Errorf("expected count 42, got %v", got)
	}
}

func TestCountKubernetesContainersError(t *testing.T) {
	mock := &mockK8sAPI{
		countErr: errors.New("connection refused"),
	}

	text, _ := callTool(t,
		func(s *mcp.Server) { registerCountKubernetesContainers(s, mock) },
		"falcon_count_kubernetes_containers",
		map[string]any{},
	)
	if !contains(text, "Failed to count Kubernetes containers") {
		t.Errorf("expected error message, got %s", text)
	}
}

// ---------------------------------------------------------------------------
// falcon_search_images_vulnerabilities tests
// ---------------------------------------------------------------------------

func TestSearchImagesVulnerabilitiesSuccess(t *testing.T) {
	cveID := "CVE-2025-1234"
	vuln := &models.ModelsAPIVulnerabilityCombined{CveID: &cveID}
	mock := &mockContainerVulnAPI{
		resp: &container_vulnerabilities.ReadCombinedVulnerabilitiesOK{
			Payload: &models.VulnerabilitiesAPICombinedVulnerability{
				Resources: []*models.ModelsAPIVulnerabilityCombined{vuln},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchImagesVulnerabilities(s, mock) },
		"falcon_search_images_vulnerabilities",
		map[string]any{"filter": "cvss_score:>5"},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 result, got %d", len(got))
	}
	if got[0]["cve_id"] != cveID {
		t.Errorf("expected cve_id=%q, got %v", cveID, got[0]["cve_id"])
	}
}

// ---------------------------------------------------------------------------
// falcon_search_cspm_assets tests (with slimming assertion)
// ---------------------------------------------------------------------------

func TestSearchCSPMAssetsTwoStepWithSlimming(t *testing.T) {
	// Build a fake ResourcesCloudResource with both keep and drop fields. The
	// bloated fields (e.g. raw config JSON, compliance data) should be absent
	// from the response; the KEEP_TOP_LEVEL fields should be retained.
	resourceID := "aws-ec2-i-0123456789"
	cloudProvider := "AWS"
	region := "us-east-1"

	asset := &models.ResourcesCloudResource{
		ResourceID:    resourceID,
		CloudProvider: cloudProvider,
		Region:        region,
		// Cid is NOT in the KEEP_TOP_LEVEL allowlist.
		Cid: "some-cid-value",
	}

	queryMeta := &models.AssetsGetResourceIDsResponse{
		Resources: []string{"id-1"},
	}
	entitiesPayload := &models.AssetsGetResourcesResponse{
		Resources: []*models.ResourcesCloudResource{asset},
	}

	mock := &mockCSPMAssetsAPI{
		queryResp: &cloud_security_assets.CloudSecurityAssetsQueriesOK{
			Payload: queryMeta,
		},
		entitiesResp: &cloud_security_assets.CloudSecurityAssetsEntitiesGetOK{
			Payload: entitiesPayload,
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchCSPMAssets(s, mock) },
		"falcon_search_cspm_assets",
		map[string]any{"filter": "cloud_provider:'AWS'"},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 asset, got %d", len(got))
	}

	asset0 := got[0]

	// Retained fields must be present.
	if asset0["resource_id"] != resourceID {
		t.Errorf("expected resource_id=%q, got %v", resourceID, asset0["resource_id"])
	}
	if asset0["cloud_provider"] != cloudProvider {
		t.Errorf("expected cloud_provider=%q, got %v", cloudProvider, asset0["cloud_provider"])
	}
	if asset0["region"] != region {
		t.Errorf("expected region=%q, got %v", region, asset0["region"])
	}

	// Bloated/internal field must be dropped.
	if _, ok := asset0["cid"]; ok {
		t.Errorf("bloated field 'cid' should have been stripped from slimmed asset, but was present")
	}

	// The entities call must have received the ID from the query call.
	if len(mock.entitiesGot) != 1 || mock.entitiesGot[0] != "id-1" {
		t.Errorf("entities call got IDs %v, expected [id-1]", mock.entitiesGot)
	}
}

func TestSearchCSPMAssetsEmpty(t *testing.T) {
	mock := &mockCSPMAssetsAPI{
		queryResp: &cloud_security_assets.CloudSecurityAssetsQueriesOK{
			Payload: &models.AssetsGetResourceIDsResponse{
				Resources: []string{},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchCSPMAssets(s, mock) },
		"falcon_search_cspm_assets",
		map[string]any{},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v", err)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
	// Entities should never be called when query returns no IDs.
	if len(mock.entitiesGot) != 0 {
		t.Errorf("entities call should not happen on empty query; got %v", mock.entitiesGot)
	}
}

func TestSearchCSPMAssetsFQLError(t *testing.T) {
	mock := &mockCSPMAssetsAPI{
		queryErr: runtime.NewAPIError("CloudSecurityAssetsQueries", "bad filter", 400),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchCSPMAssets(s, mock) },
		"falcon_search_cspm_assets",
		map[string]any{"filter": "bogus=="},
	)
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v", err)
	}
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got keys %v", keysOf(got))
	}
}

// ---------------------------------------------------------------------------
// CSPM asset slimming unit tests
// ---------------------------------------------------------------------------

func TestSlimCSPMAssetKeepsAllowlistedFields(t *testing.T) {
	asset := &models.ResourcesCloudResource{
		ID:            "test-id",
		Arn:           "arn:aws:ec2:us-east-1:123:instance/i-123",
		ResourceID:    "i-123",
		ResourceName:  "my-instance",
		ResourceType:  "AWS::EC2::Instance",
		AccountID:     "123456789",
		AccountName:   "prod-account",
		Region:        "us-east-1",
		CloudProvider: "AWS",
		Active:        true,
		// Bloated fields not in allowlist:
		Cid:         "should-be-stripped",
		ClusterID:   "should-be-stripped",
		ClusterName: "should-be-stripped",
	}

	result := slimCSPMAsset(asset)

	// Allowlisted fields must be present.
	for _, key := range []string{"id", "arn", "resource_id", "resource_name", "resource_type",
		"account_id", "account_name", "region", "cloud_provider", "active"} {
		if _, ok := result[key]; !ok {
			t.Errorf("expected field %q to be retained, but it was dropped", key)
		}
	}

	// Bloated fields must be absent.
	for _, key := range []string{"cid", "cluster_id", "cluster_name"} {
		if _, ok := result[key]; ok {
			t.Errorf("expected field %q to be stripped, but it was retained", key)
		}
	}
}

func TestSlimCloudContextKeepsSecurityFields(t *testing.T) {
	ctx := map[string]any{
		"cspm_license":     "full",
		"publicly_exposed": true,
		"managed_by":       "aws",
		// Should be dropped:
		"raw_config":      map[string]any{"very": "bloated"},
		"compliance_data": []any{"tons", "of", "data"},
		"detections": map[string]any{
			"iom_counts":       42,
			"ioa_counts":       7,
			"severities":       map[string]any{"critical": 1},
			"highest_severity": "critical",
			"resource_url":     "https://example.com",
			// Should be stripped from detections:
			"rule_ids":       []string{"rule-1"},
			"benchmark_objs": []any{"lots", "of", "data"},
		},
		"insights": map[string]any{
			"external": map[string]any{"internet_exposed": true},
			// verbose details should be dropped since we only keep "external"
		},
	}

	result := slimCloudContext(ctx)

	if result["cspm_license"] != "full" {
		t.Errorf("expected cspm_license, got %v", result["cspm_license"])
	}
	if result["publicly_exposed"] != true {
		t.Errorf("expected publicly_exposed=true")
	}
	if _, ok := result["raw_config"]; ok {
		t.Error("raw_config should be stripped")
	}
	if _, ok := result["compliance_data"]; ok {
		t.Error("compliance_data should be stripped")
	}

	// Check detections keep/drop.
	det, ok := result["detections"].(map[string]any)
	if !ok {
		t.Fatal("expected detections map")
	}
	if _, ok := det["iom_counts"]; !ok {
		t.Error("iom_counts should be retained in detections")
	}
	if _, ok := det["rule_ids"]; ok {
		t.Error("rule_ids should be stripped from detections")
	}
	if _, ok := det["benchmark_objs"]; ok {
		t.Error("benchmark_objs should be stripped from detections")
	}

	// Check insights.
	insights, ok := result["insights"].(map[string]any)
	if !ok {
		t.Fatal("expected insights map")
	}
	if _, ok := insights["external"]; !ok {
		t.Error("external should be retained in insights")
	}
}

// ---------------------------------------------------------------------------
// falcon_search_iom_findings tests
// ---------------------------------------------------------------------------

func TestSearchIOMFindingsTwoStep(t *testing.T) {
	entityID := "iom-entity-abc"
	entity := &models.EvaluationsEvaluation{ID: entityID}

	mock := &mockIOMAPI{
		queryResp: &cloud_security_detections.CspmEvaluationsIomQueriesOK{
			Payload: &models.EvaluationsQueryIOMsResponse{
				Resources: []string{"iom-id-1"},
			},
		},
		entitiesResp: &cloud_security_detections.CspmEvaluationsIomEntitiesOK{
			Payload: &models.EvaluationsGetIOMsResponse{
				Resources: []*models.EvaluationsEvaluation{entity},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchIOMFindings(s, mock) },
		"falcon_search_iom_findings",
		map[string]any{"filter": "severity:'critical'"},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 finding, got %d", len(got))
	}
	if got[0]["id"] != entityID {
		t.Errorf("expected id=%q, got %v", entityID, got[0]["id"])
	}
}

func TestSearchIOMFindingsEmpty(t *testing.T) {
	mock := &mockIOMAPI{
		queryResp: &cloud_security_detections.CspmEvaluationsIomQueriesOK{
			Payload: &models.EvaluationsQueryIOMsResponse{
				Resources: []string{},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchIOMFindings(s, mock) },
		"falcon_search_iom_findings",
		map[string]any{},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v", err)
	}
	if got["total"].(float64) != 0 {
		t.Errorf("expected total 0, got %v", got["total"])
	}
}

func TestSearchIOMFindingsFQLError(t *testing.T) {
	mock := &mockIOMAPI{
		queryErr: runtime.NewAPIError("CspmEvaluationsIomQueries", "bad filter", 400),
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchIOMFindings(s, mock) },
		"falcon_search_iom_findings",
		map[string]any{"filter": "bogus=="},
	)
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}

	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON object: %v", err)
	}
	if _, ok := got["fql_guide"]; !ok {
		t.Errorf("expected fql_guide in 400 response, got %v", keysOf(got))
	}
}

// ---------------------------------------------------------------------------
// falcon_search_cspm_suppression_rules tests
// ---------------------------------------------------------------------------

func TestSearchCSPMSuppressionRulesTwoStep(t *testing.T) {
	ruleID := "rule-abc-123"
	rule := &models.ApimodelsSuppressionRule{}

	mock := &mockCloudPoliciesAPI{
		queryResp: &cloud_policies.QuerySuppressionRulesOK{
			Payload: &models.SuppressionrulesQuerySuppressionRulesResponse{
				Resources: []string{ruleID},
			},
		},
		getResp: &cloud_policies.GetSuppressionRulesOK{
			Payload: &models.SuppressionrulesGetSuppressionRulesResponse{
				Resources: []*models.ApimodelsSuppressionRule{rule},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchCSPMSuppressionRules(s, mock) },
		"falcon_search_cspm_suppression_rules",
		map[string]any{},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 rule, got %d", len(got))
	}
}

func TestSearchCSPMSuppressionRulesEmpty(t *testing.T) {
	mock := &mockCloudPoliciesAPI{
		queryResp: &cloud_policies.QuerySuppressionRulesOK{
			Payload: &models.SuppressionrulesQuerySuppressionRulesResponse{
				Resources: []string{},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerSearchCSPMSuppressionRules(s, mock) },
		"falcon_search_cspm_suppression_rules",
		map[string]any{},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}
	if text != "[]" {
		t.Errorf("expected empty array, got %s", text)
	}
}

// ---------------------------------------------------------------------------
// falcon_create_cspm_suppression_rule tests
// ---------------------------------------------------------------------------

func TestCreateCSPMSuppressionRuleSuccess(t *testing.T) {
	createdID := "new-rule-456"
	rule := &models.ApimodelsSuppressionRule{}

	mock := &mockCloudPoliciesAPI{
		createResp: &cloud_policies.CreateSuppressionRuleOK{
			Payload: &models.SuppressionrulesCreateSuppressionRuleResponse{
				Resources: []string{createdID},
			},
		},
		getResp: &cloud_policies.GetSuppressionRulesOK{
			Payload: &models.SuppressionrulesGetSuppressionRulesResponse{
				Resources: []*models.ApimodelsSuppressionRule{rule},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerCreateCSPMSuppressionRule(s, mock) },
		"falcon_create_cspm_suppression_rule",
		map[string]any{
			"name":               "Test rule",
			"suppression_reason": "accept-risk",
			"rule_severities":    []any{"low"},
		},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON array: %v (%s)", err, text)
	}
	if len(got) != 1 {
		t.Fatalf("expected 1 rule, got %d", len(got))
	}
}

func TestCreateCSPMSuppressionRuleInvalidReason(t *testing.T) {
	mock := &mockCloudPoliciesAPI{}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerCreateCSPMSuppressionRule(s, mock) },
		"falcon_create_cspm_suppression_rule",
		map[string]any{
			"name":               "Bad rule",
			"suppression_reason": "not-valid",
			"rule_ids":           []any{"r1"},
		},
	)
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "Invalid suppression_reason") {
		t.Errorf("expected validation error, got %s", text)
	}
}

func TestCreateCSPMSuppressionRuleMissingRuleSelection(t *testing.T) {
	mock := &mockCloudPoliciesAPI{}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerCreateCSPMSuppressionRule(s, mock) },
		"falcon_create_cspm_suppression_rule",
		map[string]any{
			"name":               "No scope",
			"suppression_reason": "accept-risk",
			// No rule_ids, rule_names, or rule_severities
		},
	)
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "At least one rule selection") {
		t.Errorf("expected rule selection error, got %s", text)
	}
}

// ---------------------------------------------------------------------------
// falcon_delete_cspm_suppression_rules tests
// ---------------------------------------------------------------------------

func TestDeleteCSPMSuppressionRulesSuccess(t *testing.T) {
	rule := &models.ApimodelsSuppressionRule{}
	mock := &mockCloudPoliciesAPI{
		deleteResp: &cloud_policies.DeleteSuppressionRulesOK{
			Payload: &models.SuppressionrulesDeleteSuppressionRulesResponse{
				Resources: []*models.ApimodelsSuppressionRule{rule},
			},
		},
	}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerDeleteCSPMSuppressionRules(s, mock) },
		"falcon_delete_cspm_suppression_rules",
		map[string]any{"ids": []any{"rule-id-1"}},
	)
	if isErr {
		t.Fatalf("unexpected error: %s", text)
	}

	var got []map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not a JSON array: %v (%s)", err, text)
	}
}

func TestDeleteCSPMSuppressionRulesEmptyIDs(t *testing.T) {
	mock := &mockCloudPoliciesAPI{}

	text, isErr := callTool(t,
		func(s *mcp.Server) { registerDeleteCSPMSuppressionRules(s, mock) },
		"falcon_delete_cspm_suppression_rules",
		map[string]any{"ids": []any{}},
	)
	if isErr {
		t.Fatalf("unexpected protocol error: %s", text)
	}
	if !contains(text, "ids") {
		t.Errorf("expected ids validation error, got %s", text)
	}
}

func TestDeleteCSPMSuppressionRulesAPIError(t *testing.T) {
	mock := &mockCloudPoliciesAPI{
		deleteErr: errors.New("network error"),
	}

	text, _ := callTool(t,
		func(s *mcp.Server) { registerDeleteCSPMSuppressionRules(s, mock) },
		"falcon_delete_cspm_suppression_rules",
		map[string]any{"ids": []any{"rule-1"}},
	)
	if !contains(text, "Failed to delete suppression rules") {
		t.Errorf("expected error message, got %s", text)
	}
}

// ---------------------------------------------------------------------------
// limit normalization tests
// ---------------------------------------------------------------------------

func TestNormalizeContainerLimit(t *testing.T) {
	cases := map[int64]int64{0: 10, -5: 10, 1: 1, 10: 10, 9999: 9999, 10000: 9999}
	for in, want := range cases {
		if got := normalizeContainerLimit(in); got != want {
			t.Errorf("normalizeContainerLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

func TestNormalizeCSPMAssetsLimit(t *testing.T) {
	cases := map[int64]int64{0: 100, -1: 100, 1: 1, 100: 100, 1000: 1000, 1001: 1000}
	for in, want := range cases {
		if got := normalizeCSPMAssetsLimit(in); got != want {
			t.Errorf("normalizeCSPMAssetsLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

func TestNormalizeSuppressionRulesLimit(t *testing.T) {
	cases := map[int64]int64{0: 100, -1: 100, 1: 1, 100: 100, 500: 500, 501: 500}
	for in, want := range cases {
		if got := normalizeSuppressionRulesLimit(in); got != want {
			t.Errorf("normalizeSuppressionRulesLimit(%d) = %d, want %d", in, got, want)
		}
	}
}

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------

func keysOf(m map[string]any) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}
