// Package quarantine implements the Falcon MCP "quarantine" toolset: searching
// quarantined files, previewing action counts, and applying or deleting
// quarantine records.
package quarantine

import (
	"context"

	"github.com/crowdstrike/gofalcon/falcon/client/quarantine"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/fql"
	"github.com/crowdstrike/falcon-mcp-go/pkg/api"
	"github.com/crowdstrike/falcon-mcp-go/pkg/mcpx"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"
)

const (
	fqlGuideURI = "falcon://quarantine/files/search/fql-guide"
)

// QuarantineAPI is the narrow slice of the gofalcon quarantine client this
// toolset uses. Declaring it here keeps the handlers unit-testable with a
// hand-written mock.
type QuarantineAPI interface {
	QueryQuarantineFiles(*quarantine.QueryQuarantineFilesParams, ...quarantine.ClientOption) (*quarantine.QueryQuarantineFilesOK, error)
	GetQuarantineFiles(*quarantine.GetQuarantineFilesParams, ...quarantine.ClientOption) (*quarantine.GetQuarantineFilesOK, error)
	ActionUpdateCount(*quarantine.ActionUpdateCountParams, ...quarantine.ClientOption) (*quarantine.ActionUpdateCountOK, error)
	UpdateQuarantinedDetectsByIds(*quarantine.UpdateQuarantinedDetectsByIdsParams, ...quarantine.ClientOption) (*quarantine.UpdateQuarantinedDetectsByIdsOK, error)
	UpdateQfByQuery(*quarantine.UpdateQfByQueryParams, ...quarantine.ClientOption) (*quarantine.UpdateQfByQueryOK, error)
}

// Toolset is the quarantine domain module.
type Toolset struct{}

func init() { toolsets.Register(&Toolset{}) }

func (Toolset) GetName() string { return "quarantine" }

func (Toolset) GetDescription() string {
	return "Investigate and manage CrowdStrike Falcon quarantined files."
}

func (Toolset) GetResources() []api.ServerResource {
	return []api.ServerResource{
		fql.Resource(
			fqlGuideURI,
			"falcon_search_quarantined_files_fql_guide",
			"Contains the guide for the `filter` param of quarantine search and filter-based action tools.",
		),
	}
}

func (t Toolset) GetTools(fc *falcon.FalconClient) []api.ServerTool {
	return []api.ServerTool{
		{
			Tool: &mcp.Tool{Name: "falcon_search_quarantined_files"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerSearchQuarantinedFiles(s, fc.Quarantine())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_preview_quarantine_actions"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerPreviewQuarantineActions(s, fc.Quarantine())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_update_quarantined_files"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerUpdateQuarantinedFiles(s, fc.Quarantine())
			},
		},
		{
			Tool: &mcp.Tool{Name: "falcon_delete_quarantined_files"},
			Register: func(s *mcp.Server, fc *falcon.FalconClient) {
				registerDeleteQuarantinedFiles(s, fc.Quarantine())
			},
		},
	}
}

// --- falcon_search_quarantined_files ---

type searchQuarantinedFilesInput struct {
	Filter *string `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://quarantine/files/search/fql-guide for syntax."`
	Limit  int64   `json:"limit,omitempty" jsonschema:"Maximum number of quarantine file IDs to return [1-500]. Default 10."`
	Offset *string `json:"offset,omitempty" jsonschema:"Starting index of overall result set from which to return IDs."`
	Sort   *string `json:"sort,omitempty" jsonschema:"Sort quarantined files using FQL syntax such as date_updated|desc or hostname|asc."`
}

func registerSearchQuarantinedFiles(s *mcp.Server, api QuarantineAPI) {
	desc := "Search quarantined files and return full quarantine metadata. " +
		"Use this to discover quarantine records by host, hash, user, or state. " +
		"Consult falcon://quarantine/files/search/fql-guide before constructing " +
		"filter expressions. Returns full quarantine details including hostname, " +
		"sha256, paths, state, and associated alert and detection IDs."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_search_quarantined_files",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in searchQuarantinedFilesInput) (*mcp.CallToolResult, any, error) {
		limit := normalizeLimit(in.Limit)

		// Step 1: query matching quarantine file IDs.
		qp := quarantine.NewQueryQuarantineFilesParamsWithContext(ctx)
		qp.Filter = in.Filter
		qp.Limit = &limit
		qp.Offset = in.Offset
		qp.Sort = in.Sort

		queryResp, err := api.QueryQuarantineFiles(qp)
		if err != nil {
			return searchErr("QueryQuarantineFiles", "Failed to search quarantined files", in.Filter, err)
		}

		ids := queryResp.GetPayload().Resources
		if len(ids) == 0 {
			return mcpx.JSONResult(falcon.FormatEmptyResponse(in.Filter))
		}

		// Step 2: fetch full details for the matched IDs.
		dp := quarantine.NewGetQuarantineFilesParamsWithContext(ctx)
		dp.Body = &models.MsaIdsRequest{Ids: ids}

		detailsResp, err := api.GetQuarantineFiles(dp)
		if err != nil {
			resp := falcon.NormalizeError("GetQuarantineFiles", "Failed to get quarantined file details", err)
			return mcpx.JSONResult([]any{resp})
		}
		return mcpx.JSONResult(detailsResp.GetPayload().Resources)
	})
}

// --- falcon_preview_quarantine_actions ---

type previewQuarantineActionsInput struct {
	Filter string `json:"filter" jsonschema:"FQL filter expression. See falcon://quarantine/files/search/fql-guide for syntax."`
}

func registerPreviewQuarantineActions(s *mcp.Server, api QuarantineAPI) {
	desc := "Estimate how many quarantine records each action would affect for a given filter. " +
		"Use this read-only tool before calling a mutating quarantine action to " +
		"understand the blast radius of a release, unrelease, or delete request. " +
		"Consult falcon://quarantine/files/search/fql-guide before constructing " +
		"filter expressions. Returns a list of action counts keyed by action name."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_preview_quarantine_actions",
		Description: desc,
		Annotations: mcpx.ReadOnly(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in previewQuarantineActionsInput) (*mcp.CallToolResult, any, error) {
		if in.Filter == "" {
			e := falcon.ErrorResponse{Error: "Provide a non-empty FQL `filter` for falcon_preview_quarantine_actions."}
			return mcpx.JSONResult([]any{e})
		}

		ap := quarantine.NewActionUpdateCountParamsWithContext(ctx)
		ap.Filter = in.Filter

		resp, err := api.ActionUpdateCount(ap)
		if err != nil {
			e := falcon.NormalizeError("ActionUpdateCount", "Failed to count quarantine actions", err)
			return mcpx.JSONResult([]any{e})
		}
		return mcpx.JSONResult(resp.GetPayload().Resources)
	})
}

// --- falcon_update_quarantined_files ---

type updateQuarantinedFilesInput struct {
	Action  string   `json:"action" jsonschema:"Reversible action to apply. Supported values are release and unrelease."`
	IDs     []string `json:"ids,omitempty" jsonschema:"Quarantine file ID(s) to update. Provide ids OR filter (not both)."`
	Filter  *string  `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://quarantine/files/search/fql-guide for syntax."`
	Comment *string  `json:"comment,omitempty" jsonschema:"Optional audit comment describing why the action is being taken."`
}

func registerUpdateQuarantinedFiles(s *mcp.Server, api QuarantineAPI) {
	desc := "Apply a reversible quarantine action to records selected by IDs or filter. " +
		"Use this to release or unrelease quarantined files. Provide `ids` for " +
		"specific records, or `filter` to select by query. Consult " +
		"falcon://quarantine/files/search/fql-guide before constructing filter " +
		"expressions. Returns an empty list on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_update_quarantined_files",
		Description: desc,
		Annotations: mcpx.Mutating(),
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in updateQuarantinedFilesInput) (*mcp.CallToolResult, any, error) {
		normalized, ok := normalizeRestoreAction(in.Action)
		if !ok {
			e := falcon.ErrorResponse{Error: "Unsupported quarantine `action`. Use `release` or `unrelease`."}
			return mcpx.JSONResult([]any{e})
		}

		if len(in.IDs) == 0 && in.Filter == nil {
			e := falcon.ErrorResponse{Error: "Provide either `ids` or `filter` when updating quarantined files."}
			return mcpx.JSONResult([]any{e})
		}

		if len(in.IDs) > 0 {
			return applyActionByIDs(ctx, api, in.IDs, normalized, in.Comment,
				"Failed to update quarantined files by IDs")
		}
		return applyActionByQuery(ctx, api, normalized, *in.Filter, in.Comment,
			"Failed to update quarantined files by query")
	})
}

// --- falcon_delete_quarantined_files ---

type deleteQuarantinedFilesInput struct {
	IDs     []string `json:"ids,omitempty" jsonschema:"Quarantine file ID(s) to delete. Provide ids OR filter (not both)."`
	Filter  *string  `json:"filter,omitempty" jsonschema:"FQL filter expression. See falcon://quarantine/files/search/fql-guide for syntax."`
	Comment *string  `json:"comment,omitempty" jsonschema:"Optional audit comment describing why the records are being deleted."`
}

func registerDeleteQuarantinedFiles(s *mcp.Server, api QuarantineAPI) {
	desc := "Delete quarantine records selected by IDs or filter. " +
		"This tool is destructive and should be used only when quarantine records " +
		"should be removed rather than released. Provide `ids` for specific records, " +
		"or `filter` to select by query. Consult falcon://quarantine/files/search/fql-guide " +
		"before constructing filter expressions. Returns an empty list on success."

	mcp.AddTool(s, &mcp.Tool{
		Name:        "falcon_delete_quarantined_files",
		Description: desc,
		Annotations: &mcp.ToolAnnotations{
			ReadOnlyHint:    false,
			DestructiveHint: mcpx.BoolPtr(true),
			IdempotentHint:  true,
			OpenWorldHint:   mcpx.BoolPtr(true),
		},
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in deleteQuarantinedFilesInput) (*mcp.CallToolResult, any, error) {
		if len(in.IDs) == 0 && in.Filter == nil {
			e := falcon.ErrorResponse{Error: "Provide either `ids` or `filter` when deleting quarantined files."}
			return mcpx.JSONResult([]any{e})
		}

		if len(in.IDs) > 0 {
			return applyActionByIDs(ctx, api, in.IDs, "delete", in.Comment,
				"Failed to delete quarantined files by IDs")
		}
		return applyActionByQuery(ctx, api, "delete", *in.Filter, in.Comment,
			"Failed to delete quarantined files by query")
	})
}

// --- helpers ---

// applyActionByIDs calls UpdateQuarantinedDetectsByIds with the given IDs,
// action, and optional comment.
func applyActionByIDs(ctx context.Context, api QuarantineAPI, ids []string, action string, comment *string, errorMsg string) (*mcp.CallToolResult, any, error) {
	body := &models.DomainEntitiesPatchRequest{
		Ids:    ids,
		Action: action,
	}
	if comment != nil {
		body.Comment = *comment
	}
	p := quarantine.NewUpdateQuarantinedDetectsByIdsParamsWithContext(ctx)
	p.Body = body

	_, err := api.UpdateQuarantinedDetectsByIds(p)
	if err != nil {
		e := falcon.NormalizeError("UpdateQuarantinedDetectsByIds", errorMsg, err)
		return mcpx.JSONResult([]any{e})
	}
	return mcpx.JSONResult([]any{})
}

// applyActionByQuery calls UpdateQfByQuery with the given action, filter, and
// optional comment.
func applyActionByQuery(ctx context.Context, api QuarantineAPI, action, filter string, comment *string, errorMsg string) (*mcp.CallToolResult, any, error) {
	body := &models.DomainQueriesPatchRequest{
		Action: action,
		Filter: filter,
	}
	if comment != nil {
		body.Comment = *comment
	}
	p := quarantine.NewUpdateQfByQueryParamsWithContext(ctx)
	p.Body = body

	_, err := api.UpdateQfByQuery(p)
	if err != nil {
		e := falcon.NormalizeError("UpdateQfByQuery", errorMsg, err)
		return mcpx.JSONResult([]any{e})
	}
	return mcpx.JSONResult([]any{})
}

// searchErr normalizes a search error, surfacing the FQL guide on 400 (filter
// syntax) errors and a plain normalized error otherwise.
func searchErr(operation, msg string, filter *string, err error) (*mcp.CallToolResult, any, error) {
	normalized := falcon.NormalizeError(operation, msg, err)
	if falcon.IsFQLError(normalized.StatusCode) {
		return mcpx.JSONResult(falcon.FormatFQLError([]any{normalized}, filter, fql.MustGuide(fqlGuideURI)))
	}
	return mcpx.JSONResult([]any{normalized})
}

// normalizeRestoreAction validates and normalizes a reversible quarantine action
// name. Returns the lowercased action and true on success, or empty string and
// false if invalid.
func normalizeRestoreAction(action string) (string, bool) {
	switch action {
	case "release", "unrelease":
		return action, true
	default:
		return "", false
	}
}

// normalizeLimit clamps the requested limit to [1, 500], defaulting to 10.
func normalizeLimit(limit int64) int64 {
	if limit <= 0 {
		return 10
	}
	if limit > 500 {
		return 500
	}
	return limit
}
