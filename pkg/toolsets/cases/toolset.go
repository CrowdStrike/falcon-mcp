// Package cases implements the Falcon MCP "cases" toolset: searching, creating,
// updating, and managing evidence and tags for CrowdStrike cases. Templates are
// served by a separate sub-client (case_management) which requires the lead to
// add a CaseManagement() accessor to FalconClient before wiring that tool; all
// seven remaining tools are fully operational via fc.Cases().
package cases

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/case_management"
	"github.com/crowdstrike/gofalcon/falcon/client/cases"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const fqlGuideURI = "falcon://cases/search/fql-guide"

// CasesAPI is the narrow slice of the gofalcon cases client this toolset uses.
type CasesAPI interface {
	QueriesCasesGetV1(*cases.QueriesCasesGetV1Params, ...cases.ClientOption) (*cases.QueriesCasesGetV1OK, error)
	EntitiesCasesPostV2(*cases.EntitiesCasesPostV2Params, ...cases.ClientOption) (*cases.EntitiesCasesPostV2OK, error)
	EntitiesCasesPutV2(*cases.EntitiesCasesPutV2Params, ...cases.ClientOption) (*cases.EntitiesCasesPutV2Created, error)
	EntitiesCasesPatchV2(*cases.EntitiesCasesPatchV2Params, ...cases.ClientOption) (*cases.EntitiesCasesPatchV2OK, error)
	EntitiesAlertEvidencePostV1(*cases.EntitiesAlertEvidencePostV1Params, ...cases.ClientOption) (*cases.EntitiesAlertEvidencePostV1OK, error)
	EntitiesEventEvidencePostV1(*cases.EntitiesEventEvidencePostV1Params, ...cases.ClientOption) (*cases.EntitiesEventEvidencePostV1OK, error)
	EntitiesCaseTagsPostV1(*cases.EntitiesCaseTagsPostV1Params, ...cases.ClientOption) (*cases.EntitiesCaseTagsPostV1OK, error)
	EntitiesCaseTagsDeleteV1(*cases.EntitiesCaseTagsDeleteV1Params, ...cases.ClientOption) (*cases.EntitiesCaseTagsDeleteV1OK, error)
}

// CaseManagementAPI is the narrow slice of the case_management client used for
// template listing. This sub-client is not yet accessible via an fc.CaseManagement()
// accessor; the lead must add it before list_case_templates can be wired.
type CaseManagementAPI interface {
	QueriesTemplatesGetV1(*case_management.QueriesTemplatesGetV1Params, ...case_management.ClientOption) (*case_management.QueriesTemplatesGetV1OK, error)
	EntitiesTemplatesGetV1(*case_management.EntitiesTemplatesGetV1Params, ...case_management.ClientOption) (*case_management.EntitiesTemplatesGetV1OK, error)
}

// Toolset is the cases domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "cases" }

func (Toolset) GetDescription() string {
	return "Manage CrowdStrike Falcon cases: search, create, update, attach evidence, manage tags, and list templates."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_cases_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_cases` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_cases"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchCases(s, fc.Cases())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_cases"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetCases(s, fc.Cases())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_create_case"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerCreateCase(s, fc.Cases())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_update_case"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerUpdateCase(s, fc.Cases())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_add_case_alert_evidence"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerAddCaseAlertEvidence(s, fc.Cases())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_add_case_event_evidence"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerAddCaseEventEvidence(s, fc.Cases())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_manage_case_tags"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerManageCaseTags(s, fc.Cases())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_list_case_templates"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerListCaseTemplates(s, fc.CaseManagement())
			},
		},
	}
}

// --- falcon_search_cases (two-step: query IDs → fetch details) ---

type searchCasesInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://cases/search/fql-guide for syntax. Examples: status:'new'+severity:>70, assigned_to_name:'Alice'."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of cases to return [1-500]. Default 10."`
	Offset *int64  `json:"offset,omitempty" jsonschema:"Starting index for pagination."`
	Q      *string `json:"q,omitempty" jsonschema:"Free-text search across all case metadata."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort order. Fields: created_timestamp, updated_timestamp, severity, status, name, reference_id. Formats: 'field.desc', 'field|asc'. Example: 'created_timestamp.desc'."`
}

func registerSearchCases(s *mcp.Server, api CasesAPI) {
	desc := "Find cases by criteria and return their complete details. Use this to discover cases " +
		"by status, severity, assignee, time range, or evidence attributes. Consult " +
		"falcon://cases/search/fql-guide before constructing filter expressions. Returns full " +
		"case records including status, severity, evidence, assigned user, and analysis results."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_cases",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchCasesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 500)

		qp := cases.NewQueriesCasesGetV1ParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Q = in.Q
		qp.Sort = in.Sort

		queryResp, err := api.QueriesCasesGetV1(qp)
		if err != nil {
			return searchErr("queries_cases_get_v1", "Failed to search cases", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		details, err := fetchCaseDetails(ctx, api, ids)
		if err != nil {
			resp := falcon.NormalizeError("entities_cases_post_v2", "Failed to get case details", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(details)
	})
}

// --- falcon_get_cases ---

type getCasesInput struct {
	IDs []string `json:"ids" jsonschema:"Case ID(s) to retrieve. These are opaque system IDs, not the human-readable reference_id."`
}

func registerGetCases(s *mcp.Server, api CasesAPI) {
	desc := "Retrieve details for case IDs you already have. Use when you have specific case IDs " +
		"from search results or external references. For discovering cases by criteria, use " +
		"falcon_search_cases instead. Returns full case records."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_cases",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in getCasesInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			return mcpx.JSONResult([]any{})
		}
		details, err := fetchCaseDetails(ctx, api, in.IDs)
		if err != nil {
			resp := falcon.NormalizeError("entities_cases_post_v2", "Failed to get cases", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(details)
	})
}

// --- falcon_create_case ---

type createCaseInput struct {
	Name               string   `json:"name" jsonschema:"Case name (max 256 characters)."`
	Severity           int64    `json:"severity" jsonschema:"Severity level (1-100). 1=Informational, ~25=Low, ~50=Medium, ~75=High, 100=Critical."`
	Description        *string  `json:"description,omitempty" jsonschema:"Case description (max 2048 characters)."`
	Status             *string  `json:"status,omitempty" jsonschema:"Initial status. Values: new, in_progress. Defaults to 'new' if omitted."`
	AssignedToUserUUID *string  `json:"assigned_to_user_uuid,omitempty" jsonschema:"UUID of the user to assign the case to."`
	Tags               []string `json:"tags,omitempty" jsonschema:"Tags to apply (128 combined character limit across all tags)."`
	TemplateID         *string  `json:"template_id,omitempty" jsonschema:"Template ID to apply to the case."`
	AlertIDs           []string `json:"alert_ids,omitempty" jsonschema:"Alert composite IDs to attach as evidence (from Alerts v2 API). Max 100 total evidence items."`
	EventIDs           []string `json:"event_ids,omitempty" jsonschema:"LogScale event IDs to attach as evidence (from falcon_search_ngsiem). Max 100 total evidence items."`
}

func registerCreateCase(s *mcp.Server, api CasesAPI) {
	desc := "Create a new case in CrowdStrike. Provide a name and severity at minimum. Optionally " +
		"attach alert or event evidence, assign a user, apply a template, and set tags. Returns " +
		"the created case record."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_create_case",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in createCaseInput) (*mcp.CallToolResult, any, error) {
		assignedUUID := ""
		if in.AssignedToUserUUID != nil {
			assignedUUID = *in.AssignedToUserUUID
		}
		description := ""
		if in.Description != nil {
			description = *in.Description
		}
		status := "new"
		if in.Status != nil {
			status = *in.Status
		}

		severity := in.Severity
		severityLevel := severityToLevel(severity)

		alerts := make([]*models.SdkAlertEvidenceSelector, 0, len(in.AlertIDs))
		for i := range in.AlertIDs {
			id := in.AlertIDs[i]
			alerts = append(alerts, &models.SdkAlertEvidenceSelector{ID: &id})
		}
		events := make([]*models.SdkEventEvidenceSelector, 0, len(in.EventIDs))
		for i := range in.EventIDs {
			id := in.EventIDs[i]
			events = append(events, &models.SdkEventEvidenceSelector{ID: &id})
		}

		body := &models.OperationsCreateCaseRequest{
			Name:               &in.Name,
			Severity:           &severity,
			SeverityInfo:       &models.SdkCaseSeverityInfoAssignment{Level: &severityLevel},
			Description:        &description,
			Status:             &status,
			AssignedToUserUUID: &assignedUUID,
			Tags:               in.Tags,
			Evidence: &models.OperationsCreateCaseRequestEvidence{
				Alerts: alerts,
				Events: events,
				Leads:  []*models.SdkLeadEvidenceSelector{},
			},
		}
		if in.TemplateID != nil {
			body.Template = &models.SdkTemplateSelector{ID: in.TemplateID}
		}

		pp := cases.NewEntitiesCasesPutV2ParamsWithContext(ctx)
		pp.Body = body

		resp, err := api.EntitiesCasesPutV2(pp)
		if err != nil {
			e := falcon.NormalizeError("entities_cases_put_v2", "Failed to create case", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_update_case ---

type updateCaseInput struct {
	ID                   string  `json:"id" jsonschema:"Case ID to update (the opaque system ID, not reference_id)."`
	Name                 *string `json:"name,omitempty" jsonschema:"New case name."`
	Description          *string `json:"description,omitempty" jsonschema:"New case description."`
	Status               *string `json:"status,omitempty" jsonschema:"New status. Values: new, in_progress, closed, reopened."`
	Severity             *int64  `json:"severity,omitempty" jsonschema:"New severity (1-100)."`
	AssignedToUserUUID   *string `json:"assigned_to_user_uuid,omitempty" jsonschema:"UUID of user to assign. Use remove_user_assignment=true to unassign instead."`
	RemoveUserAssignment *bool   `json:"remove_user_assignment,omitempty" jsonschema:"Set to true to remove the current user assignment."`
	TemplateID           *string `json:"template_id,omitempty" jsonschema:"Template ID to apply to the case."`
	ExpectedVersion      *int64  `json:"expected_version,omitempty" jsonschema:"Expected case version for optimistic concurrency. If provided and mismatched, the update returns 409 Conflict."`
}

func registerUpdateCase(s *mcp.Server, api CasesAPI) {
	desc := "Update an existing case's fields. Provide the case ID and any fields to change. Use " +
		"expected_version for optimistic concurrency control to prevent conflicting updates. Returns " +
		"the updated case record with incremented version."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_update_case",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in updateCaseInput) (*mcp.CallToolResult, any, error) {
		if in.Name == nil && in.Description == nil && in.Status == nil &&
			in.Severity == nil && in.AssignedToUserUUID == nil &&
			in.RemoveUserAssignment == nil && in.TemplateID == nil {
			e := falcon.ErrorResponse{Error: "Failed to update case: at least one field to update must be provided."}
			return mcpx.JSONResult([]any{e})
		}

		// OperationsCaseFieldChanges has many Required fields in the swagger model;
		// we supply zero/false values for fields we are not changing so the API
		// ignores them, matching the Python PATCH semantics.
		emptyStr := ""
		falseVal := false
		zeroSev := int64(0)
		emptyLevel := ""

		fields := &models.OperationsCaseFieldChanges{
			Name:                 &emptyStr,
			Description:          &emptyStr,
			Status:               &emptyStr,
			Severity:             &zeroSev,
			SeverityInfo:         &models.SdkCaseSeverityInfoUpdate{Level: &emptyLevel},
			AssignedToUserUUID:   &emptyStr,
			RemoveUserAssignment: &falseVal,
			CustomFields:         []*models.SdkCustomField{},
		}

		if in.Name != nil {
			fields.Name = in.Name
		}
		if in.Description != nil {
			fields.Description = in.Description
		}
		if in.Status != nil {
			fields.Status = in.Status
		}
		if in.Severity != nil {
			fields.Severity = in.Severity
			level := severityToLevel(*in.Severity)
			fields.SeverityInfo = &models.SdkCaseSeverityInfoUpdate{Level: &level}
		}
		if in.AssignedToUserUUID != nil {
			fields.AssignedToUserUUID = in.AssignedToUserUUID
		}
		if in.RemoveUserAssignment != nil {
			fields.RemoveUserAssignment = in.RemoveUserAssignment
		}
		if in.TemplateID != nil {
			fields.Template = &models.SdkTemplateSelector{ID: in.TemplateID}
		}

		body := &models.OperationsUpdateCaseRequest{
			ID:     &in.ID,
			Fields: fields,
		}
		if in.ExpectedVersion != nil {
			body.ExpectedVersion = *in.ExpectedVersion
		}

		pp := cases.NewEntitiesCasesPatchV2ParamsWithContext(ctx)
		pp.Body = body

		resp, err := api.EntitiesCasesPatchV2(pp)
		if err != nil {
			e := falcon.NormalizeError("entities_cases_patch_v2", "Failed to update case", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_add_case_alert_evidence ---

type addCaseAlertEvidenceInput struct {
	ID       string   `json:"id" jsonschema:"Case ID to add alert evidence to."`
	AlertIDs []string `json:"alert_ids" jsonschema:"Alert composite IDs to attach (from Alerts v2 API). Max 100 total evidence items per case."`
}

func registerAddCaseAlertEvidence(s *mcp.Server, api CasesAPI) {
	desc := "Attach alert evidence to an existing case. Provide alert composite_id values from the " +
		"Alerts v2 API (e.g. from falcon_search_detections). Each case supports a maximum of 100 " +
		"combined evidence items. Returns the updated case record."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_add_case_alert_evidence",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in addCaseAlertEvidenceInput) (*mcp.CallToolResult, any, error) {
		alerts := make([]*models.SdkAlertEvidenceSelector, 0, len(in.AlertIDs))
		for i := range in.AlertIDs {
			id := in.AlertIDs[i]
			alerts = append(alerts, &models.SdkAlertEvidenceSelector{ID: &id})
		}

		pp := cases.NewEntitiesAlertEvidencePostV1ParamsWithContext(ctx)
		pp.Body = &models.OperationsAddAlertsToCaseRequest{
			ID:     &in.ID,
			Alerts: alerts,
		}

		resp, err := api.EntitiesAlertEvidencePostV1(pp)
		if err != nil {
			e := falcon.NormalizeError("entities_alert_evidence_post_v1", "Failed to add alert evidence", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_add_case_event_evidence ---

type addCaseEventEvidenceInput struct {
	ID       string   `json:"id" jsonschema:"Case ID to add event evidence to."`
	EventIDs []string `json:"event_ids" jsonschema:"LogScale event IDs to attach (from falcon_search_ngsiem). Max 100 total evidence items per case."`
}

func registerAddCaseEventEvidence(s *mcp.Server, api CasesAPI) {
	desc := "Attach LogScale event evidence to an existing case. Provide event IDs obtained from " +
		"falcon_search_ngsiem or the Falcon console. Each case supports a maximum of 100 combined " +
		"evidence items. Returns the updated case record."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_add_case_event_evidence",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in addCaseEventEvidenceInput) (*mcp.CallToolResult, any, error) {
		events := make([]*models.SdkEventEvidenceSelector, 0, len(in.EventIDs))
		for i := range in.EventIDs {
			id := in.EventIDs[i]
			events = append(events, &models.SdkEventEvidenceSelector{ID: &id})
		}

		pp := cases.NewEntitiesEventEvidencePostV1ParamsWithContext(ctx)
		pp.Body = &models.OperationsAddEventsToCaseRequest{
			ID:     &in.ID,
			Events: events,
		}

		resp, err := api.EntitiesEventEvidencePostV1(pp)
		if err != nil {
			e := falcon.NormalizeError("entities_event_evidence_post_v1", "Failed to add event evidence", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_manage_case_tags ---

type manageCaseTagsInput struct {
	ID     string   `json:"id" jsonschema:"Case ID to manage tags for."`
	Action string   `json:"action" jsonschema:"Action to perform. Values: 'add' or 'remove'."`
	Tags   []string `json:"tags" jsonschema:"Tags to add or remove. 128 combined character limit across all tags on a case."`
}

func registerManageCaseTags(s *mcp.Server, api CasesAPI) {
	desc := "Add or remove tags on a case. Set action to 'add' to attach new tags, or 'remove' to " +
		"delete existing tags. Returns the updated case record."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_manage_case_tags",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in manageCaseTagsInput) (*mcp.CallToolResult, any, error) {
		switch in.Action {
		case "add":
			pp := cases.NewEntitiesCaseTagsPostV1ParamsWithContext(ctx)
			pp.Body = &models.OperationsAddTagsToCaseRequest{
				ID:   &in.ID,
				Tags: in.Tags,
			}
			resp, err := api.EntitiesCaseTagsPostV1(pp)
			if err != nil {
				e := falcon.NormalizeError("entities_case_tags_post_v1", "Failed to add case tags", err)
				return mcpx.JSONResult([]any{e})
			}
			return mcpx.JSONResult(resp.GetPayload().Resources)

		case "remove":
			pp := cases.NewEntitiesCaseTagsDeleteV1ParamsWithContext(ctx)
			pp.ID = in.ID
			pp.Tag = in.Tags
			resp, err := api.EntitiesCaseTagsDeleteV1(pp)
			if err != nil {
				e := falcon.NormalizeError("entities_case_tags_delete_v1", "Failed to remove case tags", err)
				return mcpx.JSONResult([]any{e})
			}
			return mcpx.JSONResult(resp.GetPayload().Resources)

		default:
			e := falcon.ErrorResponse{Error: "Failed to manage case tags: invalid action. Must be 'add' or 'remove'."}
			return mcpx.JSONResult([]any{e})
		}
	})
}

// --- falcon_list_case_templates ---

type listCaseTemplatesInput struct {
	Limit  int64  `json:"limit,omitempty" jsonschema:"Maximum number of templates to return [1-200]. Default 50."`
	Offset *int64 `json:"offset,omitempty" jsonschema:"Starting index for pagination."`
}

func registerListCaseTemplates(s *mcp.Server, api CaseManagementAPI) {
	desc := "List available case templates. Use to discover templates that can be applied when " +
		"creating or updating cases. Returns template details including name, custom fields, and " +
		"SLA configuration."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_list_case_templates",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in listCaseTemplatesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit, 200)
		qp := case_management.NewQueriesTemplatesGetV1ParamsWithContext(ctx)
		qp.Limit = &limit
		qp.Offset = in.Offset

		queryResp, err := api.QueriesTemplatesGetV1(qp)
		if err != nil {
			e := falcon.NormalizeError("queries_templates_get_v1", "Failed to query case templates", err)
			return mcpx.JSONResult([]any{e})
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult([]any{})
		}

		dp := case_management.NewEntitiesTemplatesGetV1ParamsWithContext(ctx)
		dp.Ids = ids

		details, err := api.EntitiesTemplatesGetV1(dp)
		if err != nil {
			e := falcon.NormalizeError("entities_templates_get_v1", "Failed to get template details", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(details.GetPayload().Resources)
	})
}

// --- helpers ---

// fetchCaseDetails calls EntitiesCasesPostV2 (the get-by-IDs operation) and
// returns the case resource list.
func fetchCaseDetails(ctx context.Context, api CasesAPI, ids []string) ([]*models.SdkCaseVM, error) {
	pp := cases.NewEntitiesCasesPostV2ParamsWithContext(ctx)
	pp.Body = &models.OperationsGetCasesByIDsRequest{Ids: ids}
	resp, err := api.EntitiesCasesPostV2(pp)
	if err != nil {
		return nil, err
	}
	return resp.GetPayload().Resources, nil
}

// searchErr normalizes a search error, surfacing the FQL guide on 400 errors.
func searchErr(operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(fqlGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeLimit clamps limit to [1, max], defaulting to 10 when unset (0).
func normalizeLimit(limit, max int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > max {
		return max
	}
	return limit
}

// severityToLevel converts a numeric severity (1-100) to a human-readable
// level string for the SeverityInfo field. Mirrors CrowdStrike's buckets.
func severityToLevel(severity int64) string {
	switch {
	case severity >= 90:
		return "critical"
	case severity >= 70:
		return "high"
	case severity >= 40:
		return "medium"
	case severity >= 20:
		return "low"
	default:
		return "informational"
	}
}
