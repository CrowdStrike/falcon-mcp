// Package detections implements the Falcon MCP "detections" toolset: search
// and detail retrieval for detections (alerts) across all Falcon products
// (EPP, IDP, XDR, OverWatch, NG-SIEM), plus updating detection status,
// assignment, visibility, comments, and tags.
package detections

import (
	"context"
	"sort"
	"strings"

	"github.com/crowdstrike/gofalcon/falcon/client/alerts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://detections/search/fql-guide"
)

// validStatuses are the allowed values for the update_detections status
// field, matching the Python module's _valid_statuses set.
var validStatuses = map[string]struct{}{
	"new":         {},
	"in_progress": {},
	"reopened":    {},
	"closed":      {},
}

// resolutionTags are the conventional resolution tags the Falcon console's
// Resolution view keys off of.
var resolutionTags = map[string]struct{}{
	"true_positive":  {},
	"false_positive": {},
	"ignored":        {},
}

// AlertsAPI is the narrow slice of the gofalcon alerts client this toolset
// uses. Declaring it here (rather than depending on the full ClientService)
// keeps the handlers unit-testable with a hand-written mock.
type AlertsAPI interface {
	QueryV2(*alerts.QueryV2Params, ...alerts.ClientOption) (*alerts.QueryV2OK, error)
	GetV2(*alerts.GetV2Params, ...alerts.ClientOption) (*alerts.GetV2OK, error)
	UpdateV3(*alerts.UpdateV3Params, ...alerts.ClientOption) (*alerts.UpdateV3OK, error)
}

// Toolset is the detections domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "detections" }

func (Toolset) GetDescription() string {
	return "Access and manage CrowdStrike Falcon detections (alerts)."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_detections_fql_guide",
			"Contains the guide for the `filter` param of the `falcon_search_detections` tool.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_detections"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchDetections(s, fc.Alerts())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_get_detection_details"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerGetDetectionDetails(s, fc.Alerts())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_update_detections"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerUpdateDetections(s, fc.Alerts())
			},
		},
	}
}

// --- falcon_search_detections ---

// SearchDetectionsInput mirrors the Python search_detections signature.
// Optional fields use pointers so the inferred JSON Schema marks them
// optional.
type SearchDetectionsInput struct {
	Filter        *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://detections/search/fql-guide for syntax. Examples: status:'new'+severity_name:'High', device.hostname:'DC*'."`
	Limit         int64   `json:"limit,omitempty" jsonschema:"The maximum number of detections to return in this response [1-9999]. Default 10. Use with the offset parameter to manage pagination of results."`
	Offset        *int64  `json:"offset,omitempty" jsonschema:"The first detection to return, where 0 is the latest detection. Use with the limit parameter to manage pagination of results."`
	Q             *string `json:"q,omitempty" jsonschema:"Search all detection metadata for the provided string."`
	Sort          *string `json:"sort,omitempty" jsonschema:"Sort detections. Fields: timestamp, created_timestamp, updated_timestamp, severity, confidence, agent_id. Sort asc or desc; both 'severity.desc' and 'severity|desc' are supported. Examples: severity.desc, timestamp.desc."`
	IncludeHidden *bool   `json:"include_hidden,omitempty" jsonschema:"Whether to include previously hidden detections. Default true."`
}

func registerSearchDetections(s *mcp.Server, api AlertsAPI) {
	desc := "Find detections (also called alerts) by criteria and return their complete details. " +
		"Use this to discover detections by severity, status, hostname, time range, or other " +
		"attributes — this is the tool for general alert and detection queries. Covers alerts " +
		"across all Falcon products: endpoint (EPP), identity (IDP), XDR, OverWatch, and " +
		"NG-SIEM. Consult falcon://detections/search/fql-guide before constructing filter " +
		"expressions. Returns full alert records including process context, device info, " +
		"tactic/technique details, and threat classification."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_detections",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchDetectionsInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)
		includeHidden := includeHiddenOrDefault(in.IncludeHidden)

		// Step 1: query matching composite IDs.
		qp := alerts.NewQueryV2ParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Q = in.Q
		qp.Sort = in.Sort
		qp.IncludeHidden = &includeHidden

		queryResp, err := api.QueryV2(qp)
		if err != nil {
			return searchErr("GetQueriesAlertsV2", "Failed to search detections", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full details for the matched IDs.
		details, err := fetchDetails(ctx, api, ids, includeHidden)
		if err != nil {
			resp := falcon.NormalizeError("PostEntitiesAlertsV2", "Failed to get detection details", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(details)
	})
}

// --- falcon_get_detection_details ---

// GetDetectionDetailsInput takes explicit composite detection IDs.
type GetDetectionDetailsInput struct {
	IDs           []string `json:"ids" jsonschema:"Composite ID(s) to retrieve detection details for."`
	IncludeHidden *bool    `json:"include_hidden,omitempty" jsonschema:"Whether to include hidden detections. Default true. When true, shows all detections including previously hidden ones for comprehensive visibility."`
}

func registerGetDetectionDetails(s *mcp.Server, api AlertsAPI) {
	desc := "Retrieve details for detection IDs you already have. Use when you have specific " +
		"composite detection ID(s). For discovering detections by criteria (severity, status, " +
		"hostname, etc.), use falcon_search_detections instead. Returns full detection records."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_get_detection_details",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in GetDetectionDetailsInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 {
			return mcpx.JSONResult([]any{})
		}
		includeHidden := includeHiddenOrDefault(in.IncludeHidden)
		details, err := fetchDetails(ctx, api, in.IDs, includeHidden)
		if err != nil {
			resp := falcon.NormalizeError("PostEntitiesAlertsV2", "Failed to get detection details", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(details)
	})
}

// --- falcon_update_detections ---

// UpdateDetectionsInput mirrors the Python update_detections signature.
type UpdateDetectionsInput struct {
	IDs                []string `json:"ids" jsonschema:"Composite ID(s) of the detection(s) to update."`
	Status             *string  `json:"status,omitempty" jsonschema:"New status for the detection(s). Allowed values: new, in_progress, reopened, closed."`
	AssignToUUID       *string  `json:"assign_to_uuid,omitempty" jsonschema:"UUID of the user to assign the detection(s) to. Example: '00000000-0000-0000-0000-000000000000'."`
	AssignToUserID     *string  `json:"assign_to_user_id,omitempty" jsonschema:"Email address of the user to assign the detection(s) to. Example: 'analyst@example.com'."`
	AssignToName       *string  `json:"assign_to_name,omitempty" jsonschema:"Full name of the user to assign the detection(s) to. Example: 'Jane Smith'."`
	Unassign           *bool    `json:"unassign,omitempty" jsonschema:"Pass true to remove the current assignee. false is a no-op; only true has any effect."`
	AppendComment      *string  `json:"append_comment,omitempty" jsonschema:"Comment to append to the detection(s). Comments are visible in the Falcon console. Must be a non-empty, non-whitespace string."`
	ShowInUI           *bool    `json:"show_in_ui,omitempty" jsonschema:"Whether to show the detection(s) in the Falcon UI. Set to false to hide."`
	AddTags            []string `json:"add_tags,omitempty" jsonschema:"Tags to add to the detection(s). Tags are free-form strings; any value is accepted. true_positive, false_positive, and ignored are the conventional resolution tags the Falcon console surfaces in its Resolution column — use them when recording a resolution, but they are guidance, not an enforced set."`
	RemoveTags         []string `json:"remove_tags,omitempty" jsonschema:"Tags to remove from the detection(s). Each value must match an existing tag exactly."`
	RemoveTagsByPrefix *string  `json:"remove_tags_by_prefix,omitempty" jsonschema:"Remove all tags on the detection(s) that start with this prefix (e.g. 'fc/')."`
}

func registerUpdateDetections(s *mcp.Server, api AlertsAPI) {
	desc := "Update the status, assignment, visibility, comments, and tags of one or more " +
		"detections. Use to change status (new, in_progress, reopened, closed), assign to a " +
		"user by UUID, email address, or full name, unassign, append a comment, hide/show " +
		"detections in the UI, or add/remove tags. Resolution is tag-based: applying the " +
		"conventional tags true_positive, false_positive, or ignored is what populates the " +
		"console's Resolution view. At least one update parameter must be provided. Returns " +
		"`[]` (empty list) on success, or `{\"result\": [], \"hint\": \"...\"}` when closing " +
		"without adding a resolution tag in this call; returns an error dict on failure."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_update_detections",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in UpdateDetectionsInput) (*mcp.CallToolResult, any, error) {
		// Validate mutually exclusive assignment parameters.
		assignmentCount := 0
		for _, p := range []*string{in.AssignToUUID, in.AssignToUserID, in.AssignToName} {
			if p != nil {
				assignmentCount++
			}
		}
		if assignmentCount > 1 {
			return mcpx.JSONResult(map[string]string{
				"error": "Provide at most one of assign_to_uuid, assign_to_user_id, assign_to_name.",
			})
		}

		if in.Unassign != nil && *in.Unassign && assignmentCount > 0 {
			return mcpx.JSONResult(map[string]string{
				"error": "Cannot combine unassign with an assignment parameter.",
			})
		}

		if in.AppendComment != nil && strings.TrimSpace(*in.AppendComment) == "" {
			return mcpx.JSONResult(map[string]string{"error": "append_comment must not be empty."})
		}

		for _, tag := range in.AddTags {
			if strings.TrimSpace(tag) == "" {
				return mcpx.JSONResult(map[string]string{
					"error": "add_tags must not contain empty or whitespace-only strings.",
				})
			}
		}

		for _, tag := range in.RemoveTags {
			if strings.TrimSpace(tag) == "" {
				return mcpx.JSONResult(map[string]string{
					"error": "remove_tags must not contain empty or whitespace-only strings.",
				})
			}
		}

		if in.RemoveTagsByPrefix != nil && strings.TrimSpace(*in.RemoveTagsByPrefix) == "" {
			return mcpx.JSONResult(map[string]string{
				"error": "remove_tags_by_prefix must not be empty or whitespace-only.",
			})
		}

		if in.Status != nil {
			if _, ok := validStatuses[*in.Status]; !ok {
				return mcpx.JSONResult(map[string]string{
					"error": "status must be one of: " + strings.Join(sortedKeys(validStatuses), ", ") + ".",
				})
			}
		}

		if len(in.IDs) == 0 {
			return mcpx.JSONResult(map[string]string{"error": "At least one detection ID must be provided."})
		}

		var actionParameters []*models.MsaspecActionParameter
		addParam := func(name, value string) {
			n, v := name, value
			actionParameters = append(actionParameters, &models.MsaspecActionParameter{Name: &n, Value: &v})
		}

		if in.Status != nil {
			addParam("update_status", *in.Status)
		}
		if in.AssignToUUID != nil {
			addParam("assign_to_uuid", *in.AssignToUUID)
		}
		if in.AssignToUserID != nil {
			addParam("assign_to_user_id", *in.AssignToUserID)
		}
		if in.AssignToName != nil {
			addParam("assign_to_name", *in.AssignToName)
		}
		if in.AppendComment != nil {
			addParam("append_comment", *in.AppendComment)
		}
		// show_in_ui and unassign must be sent as strings — the API rejects JSON booleans.
		if in.ShowInUI != nil {
			addParam("show_in_ui", boolString(*in.ShowInUI))
		}
		if in.Unassign != nil && *in.Unassign {
			addParam("unassign", "true")
		}
		for _, tag := range in.AddTags {
			addParam("add_tag", tag)
		}
		for _, tag := range in.RemoveTags {
			addParam("remove_tag", tag)
		}
		if in.RemoveTagsByPrefix != nil {
			addParam("remove_tags_by_prefix", *in.RemoveTagsByPrefix)
		}

		if len(actionParameters) == 0 {
			return mcpx.JSONResult(map[string]string{"error": "At least one update parameter must be provided."})
		}

		up := alerts.NewUpdateV3ParamsWithContext(ctx)
		up.Body = &models.DetectsapiPatchEntitiesAlertsV3Request{
			CompositeIds:     in.IDs,
			ActionParameters: actionParameters,
		}

		_, err := api.UpdateV3(up)
		if err != nil {
			resp := falcon.NormalizeError("PatchEntitiesAlertsV3", "Failed to update detections", err)
			return mcpx.JSONResult([]any{resp})
		}

		result := []any{}

		// Soft hint: closing without adding a resolution tag in this call may leave the
		// detection out of the console's Resolution view. Non-fatal — only wraps the success
		// case. We only know this call's add_tags, not any resolution tag set previously.
		if in.Status != nil && *in.Status == "closed" && !hasResolutionTag(in.AddTags) {
			return mcpx.JSONResult(map[string]any{
				"result": result,
				"hint": "No resolution tag was added in this update call. The console convention is to " +
					"add true_positive, false_positive, or ignored when closing a detection so it " +
					"appears in the Resolution view (skip if a resolution tag was already set).",
			})
		}

		return mcpx.JSONResult(result)
	})
}

// --- helpers ---

// fetchDetails calls GetV2 (Python: PostEntitiesAlertsV2) for the given
// composite IDs and returns the alert resource list.
func fetchDetails(ctx context.Context, api AlertsAPI, ids []string, includeHidden bool) ([]*models.DetectsAlert, error) {
	dp := alerts.NewGetV2ParamsWithContext(ctx)
	dp.Body = &models.DetectsapiPostEntitiesAlertsV2Request{CompositeIds: ids}
	dp.IncludeHidden = &includeHidden
	resp, err := api.GetV2(dp)
	if err != nil {
		return nil, err
	}
	return resp.GetPayload().Resources, nil
}

// searchErr normalizes a search error, surfacing the FQL guide on 400 (filter
// syntax) errors and a plain normalized error otherwise. It always returns a
// successful tool result wrapping the error object (parity with the Python
// modules, which return error dicts rather than protocol errors).
func searchErr(operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(fqlGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeLimit clamps the requested limit to the documented [1,9999] range,
// defaulting to 10 when unset (0).
func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > 9999 {
		return 9999
	}
	return limit
}

// includeHiddenOrDefault returns *includeHidden, or true when unset — matching
// the Python module's default=True for include_hidden.
func includeHiddenOrDefault(includeHidden *bool) bool {
	if includeHidden == nil {
		return true
	}
	return *includeHidden
}

// boolString renders b as the lowercase string the API expects in place of a
// JSON boolean ("true"/"false").
func boolString(b bool) string {
	if b {
		return "true"
	}
	return "false"
}

// hasResolutionTag reports whether any of tags is a conventional resolution
// tag (true_positive, false_positive, ignored).
func hasResolutionTag(tags []string) bool {
	for _, t := range tags {
		if _, ok := resolutionTags[t]; ok {
			return true
		}
	}
	return false
}

// sortedKeys returns the keys of m in sorted order, for stable error messages.
func sortedKeys(m map[string]struct{}) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}
