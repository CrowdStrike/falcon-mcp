// Package cloud implements the Falcon MCP "cloud" toolset: Kubernetes container
// inventory, container image vulnerability search, CSPM asset/IOM search, and
// CSPM suppression rule management.
package cloud

import (
	"context"
	"encoding/json"

	"github.com/crowdstrike/gofalcon/falcon/client/cloud_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/cloud_security_assets"
	"github.com/crowdstrike/gofalcon/falcon/client/cloud_security_detections"
	"github.com/crowdstrike/gofalcon/falcon/client/container_vulnerabilities"
	"github.com/crowdstrike/gofalcon/falcon/client/kubernetes_protection"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	k8sContainersFQLGuideURI   = "falcon://cloud/kubernetes-containers/fql-guide"
	imagesVulnFQLGuideURI      = "falcon://cloud/images-vulnerabilities/fql-guide"
	cspmAssetsFQLGuideURI      = "falcon://cloud/cspm-assets/fql-guide"
	cspmIOMFindingsFQLGuideURI = "falcon://cloud/cspm-iom-findings/fql-guide"

	cspmAssetsBatchSize  = 100
	iomEntitiesBatchSize = 100
)

// KubernetesProtectionAPI is the narrow slice of the gofalcon kubernetes_protection
// client this toolset uses.
type KubernetesProtectionAPI interface {
	ContainerCombined(*kubernetes_protection.ContainerCombinedParams, ...kubernetes_protection.ClientOption) (*kubernetes_protection.ContainerCombinedOK, error)
	ContainerCount(*kubernetes_protection.ContainerCountParams, ...kubernetes_protection.ClientOption) (*kubernetes_protection.ContainerCountOK, error)
}

// ContainerVulnerabilitiesAPI is the narrow slice of the gofalcon
// container_vulnerabilities client this toolset uses.
type ContainerVulnerabilitiesAPI interface {
	ReadCombinedVulnerabilities(*container_vulnerabilities.ReadCombinedVulnerabilitiesParams, ...container_vulnerabilities.ClientOption) (*container_vulnerabilities.ReadCombinedVulnerabilitiesOK, error)
}

// CloudSecurityAssetsAPI is the narrow slice of the gofalcon
// cloud_security_assets client this toolset uses.
type CloudSecurityAssetsAPI interface {
	CloudSecurityAssetsQueries(*cloud_security_assets.CloudSecurityAssetsQueriesParams, ...cloud_security_assets.ClientOption) (*cloud_security_assets.CloudSecurityAssetsQueriesOK, error)
	CloudSecurityAssetsEntitiesGet(*cloud_security_assets.CloudSecurityAssetsEntitiesGetParams, ...cloud_security_assets.ClientOption) (*cloud_security_assets.CloudSecurityAssetsEntitiesGetOK, error)
}

// CloudSecurityDetectionsAPI is the narrow slice of the gofalcon
// cloud_security_detections client this toolset uses.
type CloudSecurityDetectionsAPI interface {
	CspmEvaluationsIomQueries(*cloud_security_detections.CspmEvaluationsIomQueriesParams, ...cloud_security_detections.ClientOption) (*cloud_security_detections.CspmEvaluationsIomQueriesOK, error)
	CspmEvaluationsIomEntities(*cloud_security_detections.CspmEvaluationsIomEntitiesParams, ...cloud_security_detections.ClientOption) (*cloud_security_detections.CspmEvaluationsIomEntitiesOK, error)
}

// CloudPoliciesAPI is the narrow slice of the gofalcon cloud_policies client
// this toolset uses.
type CloudPoliciesAPI interface {
	QuerySuppressionRules(*cloud_policies.QuerySuppressionRulesParams, ...cloud_policies.ClientOption) (*cloud_policies.QuerySuppressionRulesOK, error)
	GetSuppressionRules(*cloud_policies.GetSuppressionRulesParams, ...cloud_policies.ClientOption) (*cloud_policies.GetSuppressionRulesOK, error)
	CreateSuppressionRule(*cloud_policies.CreateSuppressionRuleParams, ...cloud_policies.ClientOption) (*cloud_policies.CreateSuppressionRuleOK, error)
	DeleteSuppressionRules(*cloud_policies.DeleteSuppressionRulesParams, ...cloud_policies.ClientOption) (*cloud_policies.DeleteSuppressionRulesOK, error)
}

// Toolset is the cloud domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "cloud" }

func (Toolset) GetDescription() string {
	return "Access and analyze CrowdStrike Falcon cloud resources: Kubernetes containers, " +
		"container image vulnerabilities, CSPM assets, IOM findings, and suppression rules."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			k8sContainersFQLGuideURI,
			"falcon_kubernetes_containers_fql_filter_guide",
			"Contains the guide for the `filter` param of the `falcon_search_kubernetes_containers` and `falcon_count_kubernetes_containers` tools.",
		),
		fql.Resource(
			imagesVulnFQLGuideURI,
			"falcon_images_vulnerabilities_fql_filter_guide",
			"Contains the guide for the `filter` param of the `falcon_search_images_vulnerabilities` tool.",
		),
		fql.Resource(
			cspmAssetsFQLGuideURI,
			"falcon_search_cspm_assets_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_cspm_assets` tool.",
		),
		fql.Resource(
			cspmIOMFindingsFQLGuideURI,
			"falcon_search_iom_findings_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_iom_findings` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_kubernetes_containers"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchKubernetesContainers(s, fc.KubernetesProtection())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_count_kubernetes_containers"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCountKubernetesContainers(s, fc.KubernetesProtection())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_images_vulnerabilities"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchImagesVulnerabilities(s, fc.ContainerVulnerabilities())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_cspm_assets"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchCSPMAssets(s, fc.CloudSecurityAssets())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_iom_findings"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchIOMFindings(s, fc.CloudSecurityDetections())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_search_cspm_suppression_rules"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchCSPMSuppressionRules(s, fc.CloudPolicies())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_create_cspm_suppression_rule"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCreateCSPMSuppressionRule(s, fc.CloudPolicies())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_delete_cspm_suppression_rules"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDeleteCSPMSuppressionRules(s, fc.CloudPolicies())
			},
		},
	}
}

// --- falcon_search_kubernetes_containers ---

type searchKubernetesContainersInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://cloud/kubernetes-containers/fql-guide for syntax. Examples: cloud:'AWS', cluster_name:'prod'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum containers to return [1-9999]. Default 10."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return containers."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort expression. Fields: cloud_name, cloud_region, cluster_name, container_name, namespace, last_seen, first_seen, running_status, image_vulnerability_count. Direction: .asc or .desc. Examples: 'container_name.desc', 'last_seen.desc'."`
}

func registerSearchKubernetesContainers(s *mcp.Server, api KubernetesProtectionAPI) {
	desc := "Search for Kubernetes containers in your CrowdStrike container inventory. " +
		"Use this to find containers by cluster, namespace, image, or cloud provider. " +
		"Consult falcon://cloud/kubernetes-containers/fql-guide before constructing filter " +
		"expressions. Returns full container details including image, status, and vulnerabilities."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_kubernetes_containers",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchKubernetesContainersInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeContainerLimit(in.Limit)

		p := kubernetes_protection.NewContainerCombinedParamsWithContext(ctx)
		p.Filter = in.Filter
		p.Limit = &limit
		p.Offset = in.Offset
		p.Sort = in.Sort

		resp, err := api.ContainerCombined(p)
		if err != nil {
			return fqlSearchErr("ReadContainerCombined", "Failed to search Kubernetes containers", in.Filter, k8sContainersFQLGuideURI, err)
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_count_kubernetes_containers ---

type countKubernetesContainersInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://cloud/kubernetes-containers/fql-guide for syntax. Examples: cloud:'Azure', container_name:'service'."`
}

func registerCountKubernetesContainers(s *mcp.Server, api KubernetesProtectionAPI) {
	desc := "Count Kubernetes containers matching filter criteria. " +
		"Use this for aggregate counts without returning full container details. " +
		"Consult falcon://cloud/kubernetes-containers/fql-guide before constructing filter " +
		"expressions. Returns the matching container count as an integer."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_count_kubernetes_containers",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in countKubernetesContainersInput) (*mcp.CallToolResult, any, error) {
		p := kubernetes_protection.NewContainerCountParamsWithContext(ctx)
		p.Filter = in.Filter

		resp, err := api.ContainerCount(p)
		if err != nil {
			e := falcon.NormalizeError("ReadContainerCount", "Failed to count Kubernetes containers", err)
			return mcpx.JSONResult([]any{e})
		}

		resources := resp.GetPayload().Resources
		if len(resources) > 0 && resources[0] != nil && resources[0].Count != nil {
			return mcpx.JSONResult(*resources[0].Count)
		}
		return mcpx.JSONResult(int64(0))
	})
}

// --- falcon_search_images_vulnerabilities ---

type searchImagesVulnerabilitiesInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://cloud/images-vulnerabilities/fql-guide for syntax. Examples: cve_id:*'*2025*', cvss_score:>5."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum records to return [1-9999]. Default 10."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return results."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort expression. Fields: cps_current_rating, cve_id, cvss_score, images_impacted. Direction: .asc or .desc. Examples: 'cvss_score.desc', 'cps_current_rating.asc'."`
}

func registerSearchImagesVulnerabilities(s *mcp.Server, api ContainerVulnerabilitiesAPI) {
	desc := "Search for container image vulnerabilities in CrowdStrike Image Assessments. " +
		"Use this to find CVEs affecting container images by severity, CVSS score, or CVE ID. " +
		"Consult falcon://cloud/images-vulnerabilities/fql-guide before constructing filter " +
		"expressions. Returns vulnerability details including CVE IDs, scores, and impacted image counts."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_images_vulnerabilities",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchImagesVulnerabilitiesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeContainerLimit(in.Limit)

		p := container_vulnerabilities.NewReadCombinedVulnerabilitiesParamsWithContext(ctx)
		p.Filter = in.Filter
		p.Limit = &limit
		p.Offset = in.Offset
		p.Sort = in.Sort

		resp, err := api.ReadCombinedVulnerabilities(p)
		if err != nil {
			return fqlSearchErr("ReadCombinedVulnerabilities", "Failed to search images vulnerabilities", in.Filter, imagesVulnFQLGuideURI, err)
		}

		resources := resp.GetPayload().Resources
		if len(resources) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}
		return mcpx.JSONResult(resources)
	})
}

// --- falcon_search_cspm_assets ---

type searchCSPMAssetsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://cloud/cspm-assets/fql-guide for syntax. Examples: cloud_provider:'AWS', tag_key:'Environment'+tag_value:'Production'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum assets to return [1-1000]. Default 100."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return assets."`
	After  *string `json:"after,omitempty" jsonschema:"Pagination cursor token from a previous response. Use instead of offset for cursor-based pagination."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort expression. Fields: cloud_provider, account_id, account_name, resource_type, region, creation_time, updated_at. Direction: .asc or .desc. Examples: 'updated_at.desc', 'resource_type.asc'."`
}

func registerSearchCSPMAssets(s *mcp.Server, api CloudSecurityAssetsAPI) {
	desc := "Search for cloud assets in your CrowdStrike CSPM inventory. " +
		"Use this to find cloud resources (EC2, VPCs, S3, etc.) by provider, region, resource type, " +
		"or tags. Consult falcon://cloud/cspm-assets/fql-guide before constructing filter expressions. " +
		"Returns slimmed asset details with security posture context (IOM/IOA counts, exposure, severity)."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_cspm_assets",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchCSPMAssetsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeCSPMAssetsLimit(in.Limit)

		// Step 1: query for asset IDs.
		qp := cloud_security_assets.NewCloudSecurityAssetsQueriesParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.After = in.After
		qp.Sort = in.Sort

		queryResp, err := api.CloudSecurityAssetsQueries(qp)
		if err != nil {
			normalized := falcon.NormalizeError("cloud_security_assets_queries", "Failed to query CSPM assets", err)
			if falcon.IsFQLError(normalized.StatusCode) {
				return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, in.Filter, fql.MustGuide(cspmAssetsFQLGuideURI)))
			}
			return mcpx.JSONResult([]any{normalized})
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: batch-fetch full asset details (API limit: 100 IDs per request).
		allAssets := make([]*models.ResourcesCloudResource, 0, len(ids))
		for i := 0; i < len(ids); i += cspmAssetsBatchSize {
			end := i + cspmAssetsBatchSize
			if end > len(ids) {
				end = len(ids)
			}
			batch := ids[i:end]

			dp := cloud_security_assets.NewCloudSecurityAssetsEntitiesGetParamsWithContext(ctx)
			dp.Ids = batch

			detailResp, err := api.CloudSecurityAssetsEntitiesGet(dp)
			if err != nil {
				e := falcon.NormalizeError("cloud_security_assets_entities_get", "Failed to get CSPM asset details", err)
				return mcpx.JSONResult([]any{e})
			}
			allAssets = append(allAssets, detailResp.GetPayload().Resources...)
		}

		// Slim each asset to drop bloated fields before returning.
		slimmed := make([]map[string]any, 0, len(allAssets))
		for _, asset := range allAssets {
			slimmed = append(slimmed, slimCSPMAsset(asset))
		}
		return mcpx.JSONResult(slimmed)
	})
}

// --- CSPM asset slimming (ported from Python _slim_cspm_asset / _slim_cloud_context) ---

// keepTopLevel is the allowlist of top-level fields to retain on each CSPM
// asset record. All other fields (raw config blobs, compliance benchmarks, etc.)
// are dropped to reduce response size. Ported verbatim from the Python module.
var keepTopLevel = map[string]bool{
	"id":                 true,
	"arn":                true,
	"resource_id":        true,
	"resource_name":      true,
	"resource_type":      true,
	"resource_type_name": true,
	"account_id":         true,
	"account_name":       true,
	"region":             true,
	"zone":               true,
	"cloud_provider":     true,
	"service":            true,
	"service_category":   true,
	"active":             true,
	"first_seen":         true,
	"updated_at":         true,
	"creation_time":      true,
	"tags":               true,
	"resource_url":       true,
	"relationships":      true,
}

// slimCSPMAsset strips bloated fields from a CSPM asset record. It is a faithful
// port of the Python _slim_cspm_asset method: keep KEEP_TOP_LEVEL fields, plus
// a slimmed cloud_context via slimCloudContext.
func slimCSPMAsset(asset *models.ResourcesCloudResource) map[string]any {
	if asset == nil {
		return map[string]any{}
	}

	// Marshal the full asset to a generic map so we can apply the allowlist.
	raw := resourceCloudResourceToMap(asset)

	slimmed := make(map[string]any, len(keepTopLevel)+1)
	for k, v := range raw {
		if keepTopLevel[k] {
			slimmed[k] = v
		}
	}

	// Handle cloud_context separately with its own slimming logic.
	if ctx, ok := raw["cloud_context"]; ok {
		if ctxMap, ok := ctx.(map[string]any); ok {
			slimmed["cloud_context"] = slimCloudContext(ctxMap)
		}
	}

	return slimmed
}

// slimCloudContext keeps security-relevant summary fields from cloud_context,
// dropping benchmark bloat. Ported from Python _slim_cloud_context.
func slimCloudContext(ctx map[string]any) map[string]any {
	slimmed := make(map[string]any)

	// Scalar fields worth keeping.
	for _, key := range []string{
		"cspm_license",
		"publicly_exposed",
		"managed_by",
		"has_tags",
		"instance_id",
		"instance_state",
		"open_cloud_risks",
		"scan_type",
		"data_classifications",
	} {
		if v, ok := ctx[key]; ok {
			slimmed[key] = v
		}
	}

	// Host info (platform, OS, state) — small and useful.
	if v, ok := ctx["host"]; ok {
		slimmed["host"] = v
	}

	// Detections — keep counts/severity, strip rule IDs and benchmark objects.
	if detections, ok := ctx["detections"].(map[string]any); ok {
		det := make(map[string]any)
		for _, k := range []string{
			"iom_counts",
			"ioa_counts",
			"severities",
			"highest_severity",
			"resource_url",
		} {
			if v, ok := detections[k]; ok {
				det[k] = v
			}
		}
		slimmed["detections"] = det
	}

	// Insights — keep external boolean flags, drop verbose details.
	if insights, ok := ctx["insights"].(map[string]any); ok {
		if external, ok := insights["external"]; ok && external != nil {
			slimmed["insights"] = map[string]any{"external": external}
		}
	}

	return slimmed
}

// resourceCloudResourceToMap converts a *models.ResourcesCloudResource to a
// generic map[string]any by round-tripping through JSON. This is the simplest
// correct approach for a large, heterogeneous struct with many optional fields.
func resourceCloudResourceToMap(r *models.ResourcesCloudResource) map[string]any {
	data, err := json.Marshal(r)
	if err != nil {
		return map[string]any{}
	}
	var m map[string]any
	if err := json.Unmarshal(data, &m); err != nil {
		return map[string]any{}
	}
	return m
}

// --- falcon_search_iom_findings ---

type searchIOMFindingsInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://cloud/cspm-iom-findings/fql-guide for syntax. Examples: severity:'critical'+status:'open', cloud_provider:'aws'+service:'S3'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum IOM findings to return [1-1000]. Default 100."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return findings."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort expression. Fields: severity, first_detected, last_detected, cloud_provider, service, status. Direction: |asc or |desc. Examples: 'severity|desc', 'last_detected|desc'."`
}

func registerSearchIOMFindings(s *mcp.Server, api CloudSecurityDetectionsAPI) {
	desc := "Search for CSPM Indicators of Misconfiguration (IOM) findings. " +
		"Use this to find cloud misconfigurations by severity, provider, service, or suppression state. " +
		"Consult falcon://cloud/cspm-iom-findings/fql-guide before constructing filter expressions. " +
		"Returns IOM entities with cloud context, evaluation details, and resource information."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_iom_findings",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchIOMFindingsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeIOMLimit(in.Limit)

		// Step 1: query for IOM IDs.
		qp := cloud_security_detections.NewCspmEvaluationsIomQueriesParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort

		queryResp, err := api.CspmEvaluationsIomQueries(qp)
		if err != nil {
			normalized := falcon.NormalizeError("cspm_evaluations_iom_queries", "Failed to query IOM findings", err)
			if falcon.IsFQLError(normalized.StatusCode) {
				return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, in.Filter, fql.MustGuide(cspmIOMFindingsFQLGuideURI)))
			}
			return mcpx.JSONResult([]any{normalized})
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: batch-fetch IOM entity details (API limit: 100 IDs per request).
		allEntities := make([]*models.EvaluationsEvaluation, 0, len(ids))
		for i := 0; i < len(ids); i += iomEntitiesBatchSize {
			end := i + iomEntitiesBatchSize
			if end > len(ids) {
				end = len(ids)
			}
			batch := ids[i:end]

			dp := cloud_security_detections.NewCspmEvaluationsIomEntitiesParamsWithContext(ctx)
			dp.Ids = batch

			detailResp, err := api.CspmEvaluationsIomEntities(dp)
			if err != nil {
				e := falcon.NormalizeError("cspm_evaluations_iom_entities", "Failed to get IOM entity details", err)
				return mcpx.JSONResult([]any{e})
			}
			allEntities = append(allEntities, detailResp.GetPayload().Resources...)
		}

		return mcpx.JSONResult(allEntities)
	})
}

// --- falcon_search_cspm_suppression_rules ---

type searchCSPMSuppressionRulesInput struct {
	Limit  int64  `json:"limit,omitempty" jsonschema:"Maximum suppression rules to return [1-500]. Default 100."`
	Offset *int64 `json:"offset,omitempty" jsonschema:"Starting index for pagination."`
}

func registerSearchCSPMSuppressionRules(s *mcp.Server, api CloudPoliciesAPI) {
	desc := "Search for CSPM IOM suppression rules. " +
		"Use this to review existing suppressions before creating new ones. " +
		"Returns suppression rule objects including scope, reason, and expiration details. " +
		"Returns an empty list if no rules exist."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_cspm_suppression_rules",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchCSPMSuppressionRulesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeSuppressionRulesLimit(in.Limit)

		// Step 1: query for suppression rule IDs.
		qp := cloud_policies.NewQuerySuppressionRulesParamsWithContext(ctx)
		qp.Limit = &limit
		qp.Offset = in.Offset

		queryResp, err := api.QuerySuppressionRules(qp)
		if err != nil {
			e := falcon.NormalizeError("QuerySuppressionRules", "Failed to query suppression rules", err)
			return mcpx.JSONResult([]any{e})
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult([]any{})
		}

		// Step 2: fetch full suppression rule details.
		dp := cloud_policies.NewGetSuppressionRulesParamsWithContext(ctx)
		dp.Ids = ids

		detailResp, err := api.GetSuppressionRules(dp)
		if err != nil {
			e := falcon.NormalizeError("GetSuppressionRules", "Failed to get suppression rule details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(detailResp.GetPayload().Resources)
	})
}

// --- falcon_create_cspm_suppression_rule ---

type createCSPMSuppressionRuleInput struct {
	Name              string   `json:"name" jsonschema:"Name for the suppression rule. Should be descriptive."`
	SuppressionReason string   `json:"suppression_reason" jsonschema:"Reason for suppression. Values: 'accept-risk', 'compensating-control', 'false-positive'."`
	RuleIDs           []string `json:"rule_ids,omitempty" jsonschema:"Specific rule IDs to suppress. If not provided, use rule_severities or rule_names to scope."`
	RuleNames         []string `json:"rule_names,omitempty" jsonschema:"Rule names to suppress (supports wildcards)."`
	RuleSeverities    []string `json:"rule_severities,omitempty" jsonschema:"Rule severities to suppress. Values: 'critical', 'high', 'medium', 'low', 'informational'."`
	CloudProviders    []string `json:"cloud_providers,omitempty" jsonschema:"Limit suppression to specific cloud providers. Values: 'aws', 'azure', 'gcp'."`
	AccountIDs        []string `json:"account_ids,omitempty" jsonschema:"Limit suppression to specific cloud account IDs."`
	Regions           []string `json:"regions,omitempty" jsonschema:"Limit suppression to specific cloud regions. Ex: ['us-east-1', 'eu-west-1']."`
	ResourceIDs       []string `json:"resource_ids,omitempty" jsonschema:"Limit suppression to specific resource IDs."`
	ResourceTypes     []string `json:"resource_types,omitempty" jsonschema:"Limit suppression to specific resource types. Ex: ['AWS::S3::Bucket']."`
	ExpirationDate    *string  `json:"expiration_date,omitempty" jsonschema:"Optional expiration date in RFC 3339 format (e.g., '2025-12-31T23:59:59Z'). WARNING: Omitting this creates a PERMANENT suppression."`
}

func registerCreateCSPMSuppressionRule(s *mcp.Server, api CloudPoliciesAPI) {
	desc := "Create a CSPM IOM suppression rule to hide matching findings. " +
		"Suppressed findings are still assessed but not surfaced in compliance scores. " +
		"Requires at least one rule selection (rule_ids, rule_names, or rule_severities) and a " +
		"suppression reason. Setting an expiration_date is strongly recommended to avoid permanent " +
		"suppressions. Returns the created suppression rule object."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_create_cspm_suppression_rule",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in createCSPMSuppressionRuleInput) (*mcp.CallToolResult, any, error) {
		// Validate suppression reason.
		validReasons := map[string]bool{
			"accept-risk":          true,
			"compensating-control": true,
			"false-positive":       true,
		}
		if !validReasons[in.SuppressionReason] {
			return mcpx.JSONResult(map[string]any{
				"error":   "Invalid suppression_reason: '" + in.SuppressionReason + "'",
				"details": "Must be one of: accept-risk, compensating-control, false-positive",
			})
		}

		// Require at least one rule selection.
		if len(in.RuleIDs) == 0 && len(in.RuleNames) == 0 && len(in.RuleSeverities) == 0 {
			return mcpx.JSONResult(map[string]any{
				"error":   "At least one rule selection parameter is required",
				"details": "Provide rule_ids, rule_names, or rule_severities to scope the suppression.",
			})
		}

		// Build rule selection filter.
		ruleFilter := &models.SuppressionrulesRuleSelectionFilter{}
		if len(in.RuleIDs) > 0 {
			ruleFilter.RuleIds = in.RuleIDs
		}
		if len(in.RuleNames) > 0 {
			ruleFilter.RuleNames = in.RuleNames
		}
		if len(in.RuleSeverities) > 0 {
			ruleFilter.RuleSeverities = in.RuleSeverities
		}

		// Build scope type and asset filter.
		domain := "CSPM"
		subdomain := "IOM"
		selectionType := "rule_selection_filter"
		scopeType := "all_assets"
		var scopeAssetFilter *models.SuppressionrulesScopeAssetFilter

		hasScope := len(in.CloudProviders) > 0 || len(in.AccountIDs) > 0 ||
			len(in.Regions) > 0 || len(in.ResourceIDs) > 0 || len(in.ResourceTypes) > 0
		if hasScope {
			scopeType = "asset_filter"
			scopeAssetFilter = &models.SuppressionrulesScopeAssetFilter{}
			if len(in.CloudProviders) > 0 {
				scopeAssetFilter.CloudProviders = in.CloudProviders
			}
			if len(in.AccountIDs) > 0 {
				scopeAssetFilter.AccountIds = in.AccountIDs
			}
			if len(in.Regions) > 0 {
				scopeAssetFilter.Regions = in.Regions
			}
			if len(in.ResourceIDs) > 0 {
				scopeAssetFilter.ResourceIds = in.ResourceIDs
			}
			if len(in.ResourceTypes) > 0 {
				scopeAssetFilter.ResourceTypes = in.ResourceTypes
			}
		}

		body := &models.SuppressionrulesCreateSuppressionRuleRequest{
			Name:                &in.Name,
			Domain:              &domain,
			Subdomain:           &subdomain,
			SuppressionReason:   &in.SuppressionReason,
			RuleSelectionType:   &selectionType,
			RuleSelectionFilter: ruleFilter,
			ScopeType:           &scopeType,
			ScopeAssetFilter:    scopeAssetFilter,
		}
		if in.ExpirationDate != nil {
			body.SuppressionExpirationDate = *in.ExpirationDate
		}

		p := cloud_policies.NewCreateSuppressionRuleParamsWithContext(ctx)
		p.Body = body

		createResp, err := api.CreateSuppressionRule(p)
		if err != nil {
			e := falcon.NormalizeError("CreateSuppressionRule", "Failed to create suppression rule", err)
			return mcpx.JSONResult([]any{e})
		}

		createdIDs := createResp.GetPayload().Resources
		if len(createdIDs) == 0 {
			return mcpx.JSONResult([]any{})
		}

		// Fetch full details for the newly created rule(s).
		dp := cloud_policies.NewGetSuppressionRulesParamsWithContext(ctx)
		dp.Ids = createdIDs

		detailResp, err := api.GetSuppressionRules(dp)
		if err != nil {
			e := falcon.NormalizeError("GetSuppressionRules", "Failed to get created suppression rule details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(detailResp.GetPayload().Resources)
	})
}

// --- falcon_delete_cspm_suppression_rules ---

type deleteCSPMSuppressionRulesInput struct {
	IDs []string `json:"ids" jsonschema:"List of suppression rule IDs to delete. Use falcon_search_cspm_suppression_rules to find rule IDs."`
}

func registerDeleteCSPMSuppressionRules(s *mcp.Server, api CloudPoliciesAPI) {
	desc := "Delete CSPM IOM suppression rules by ID. " +
		"Deleting a suppression rule re-activates all findings that were previously suppressed by it. " +
		"Use falcon_search_cspm_suppression_rules to find rule IDs first. Returns a confirmation response."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_cspm_suppression_rules",
		Description: desc,
		Annotations: mcpx.Destructive(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deleteCSPMSuppressionRulesInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			e := falcon.ErrorResponse{Error: "Failed to delete suppression rules: `ids` must be provided"}
			return mcpx.JSONResult([]any{e})
		}

		p := cloud_policies.NewDeleteSuppressionRulesParamsWithContext(ctx)
		p.Ids = in.IDs

		resp, err := api.DeleteSuppressionRules(p)
		if err != nil {
			e := falcon.NormalizeError("DeleteSuppressionRules", "Failed to delete suppression rules", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- helpers ---

// fqlSearchErr normalizes a search error, surfacing the FQL guide on 400 errors.
func fqlSearchErr(operation, msg string, filter *string, guideURI string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(guideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeContainerLimit clamps to [1, 9999], defaulting to 10.
func normalizeContainerLimit(limit int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > 9999 {
		return 9999
	}
	return limit
}

// normalizeCSPMAssetsLimit clamps to [1, 1000], defaulting to 100.
func normalizeCSPMAssetsLimit(limit int64) int64 {
	if limit <= 0 {
		return 100
	}
	if limit > 1000 {
		return 1000
	}
	return limit
}

// normalizeIOMLimit clamps to [1, 1000], defaulting to 100.
func normalizeIOMLimit(limit int64) int64 {
	if limit <= 0 {
		return 100
	}
	if limit > 1000 {
		return 1000
	}
	return limit
}

// normalizeSuppressionRulesLimit clamps to [1, 500], defaulting to 100.
func normalizeSuppressionRulesLimit(limit int64) int64 {
	if limit <= 0 {
		return 100
	}
	if limit > 500 {
		return 500
	}
	return limit
}
