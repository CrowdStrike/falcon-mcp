package detections

import (
	"context"
	"fmt"
	"strconv"

	"github.com/crowdstrike/gofalcon/falcon/client/alerts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/modules/base"
)

// validStatuses are the accepted detection statuses for update_detections.
var validStatuses = map[string]bool{
	"new": true, "in_progress": true, "reopened": true, "closed": true,
}

// resolutionTags mark a detection's resolution; closing without one triggers a
// hint in the response.
var resolutionTags = map[string]bool{
	"true_positive": true, "false_positive": true, "ignored": true,
}

// UpdateInput is the input for falcon_update_detections. All fields except IDs
// are optional; several are mutually exclusive (validated before the API call).
type UpdateInput struct {
	IDs                []string `json:"ids" jsonschema:"composite IDs of the detections to update"`
	Status             string   `json:"status,omitempty" jsonschema:"new, in_progress, reopened, or closed"`
	AssignToUUID       string   `json:"assign_to_uuid,omitempty" jsonschema:"assign to a user by UUID"`
	AssignToUserID     string   `json:"assign_to_user_id,omitempty" jsonschema:"assign to a user by user id"`
	AssignToName       string   `json:"assign_to_name,omitempty" jsonschema:"assign to a user by name"`
	Unassign           bool     `json:"unassign,omitempty" jsonschema:"remove the current assignment"`
	AppendComment      string   `json:"append_comment,omitempty" jsonschema:"append a comment"`
	ShowInUI           *bool    `json:"show_in_ui,omitempty" jsonschema:"show or hide in the UI"`
	AddTags            []string `json:"add_tags,omitempty" jsonschema:"tags to add"`
	RemoveTags         []string `json:"remove_tags,omitempty" jsonschema:"tags to remove"`
	RemoveTagsByPrefix string   `json:"remove_tags_by_prefix,omitempty" jsonschema:"remove all tags with this prefix"`
}

func (m *Module) updateDetections(ctx context.Context, _ *mcp.CallToolRequest, in UpdateInput) (*mcp.CallToolResult, base.ActionResult, error) {
	actions, err := in.actionParameters()
	if err != nil {
		return nil, base.ActionResult{}, err
	}
	// Log the shape of the update, not comment text (which may carry sensitive
	// content): id count, status, assignment intent, and action count.
	m.Logger.Debug("update_detections",
		"ids", len(in.IDs),
		"status", in.Status,
		"unassign", in.Unassign,
		"assigning", in.AssignToUUID != "" || in.AssignToUserID != "" || in.AssignToName != "",
		"actions", len(actions),
	)

	params := alerts.NewUpdateV3ParamsWithContext(ctx)
	params.Body = &models.DetectsapiPatchEntitiesAlertsV3Request{
		CompositeIds:     in.IDs,
		ActionParameters: actions,
	}
	resp, err := m.API.UpdateV3(params)
	if e := base.APIError(err, resp, scopeAlertsWrite); e != nil {
		return nil, base.ActionResult{}, e
	}

	// Advise when closing a detection without a resolution tag.
	if in.Status == "closed" && !in.hasResolutionTag() {
		return nil, base.ActionResult{
			Ok:   true,
			Hint: "Detection closed without a resolution tag (true_positive/false_positive/ignored). Consider adding one via add_tags.",
		}, nil
	}
	return nil, base.ActionResult{Ok: true}, nil
}

// actionParameters validates the input and builds the ordered gofalcon action
// parameters. The Falcon API rejects JSON booleans for show_in_ui/unassign, so
// those are stringified here at the param boundary (they stay Go bool everywhere
// else).
func (in UpdateInput) actionParameters() ([]*models.MsaspecActionParameter, error) {
	if len(in.IDs) == 0 {
		return nil, fmt.Errorf("update detections: %w: ids must not be empty", errInvalidInput)
	}
	if err := in.validate(); err != nil {
		return nil, err
	}

	var actions []*models.MsaspecActionParameter
	add := func(name, value string) {
		actions = append(actions, &models.MsaspecActionParameter{Name: ptr(name), Value: ptr(value)})
	}

	if in.Status != "" {
		add("update_status", in.Status)
	}
	switch {
	case in.Unassign:
		add("unassign", "true")
	case in.AssignToUUID != "":
		add("assign_to_uuid", in.AssignToUUID)
	case in.AssignToUserID != "":
		add("assign_to_user_id", in.AssignToUserID)
	case in.AssignToName != "":
		add("assign_to_name", in.AssignToName)
	}
	if in.AppendComment != "" {
		add("append_comment", in.AppendComment)
	}
	if in.ShowInUI != nil {
		add("show_in_ui", strconv.FormatBool(*in.ShowInUI))
	}
	for _, t := range in.AddTags {
		if t != "" {
			add("add_tag", t)
		}
	}
	for _, t := range in.RemoveTags {
		if t != "" {
			add("remove_tag", t)
		}
	}
	if in.RemoveTagsByPrefix != "" {
		add("remove_tags_by_prefix", in.RemoveTagsByPrefix)
	}

	if len(actions) == 0 {
		return nil, fmt.Errorf("update detections: %w: no update fields provided", errInvalidInput)
	}
	return actions, nil
}

// validate enforces the client-side constraints on an update request.
func (in UpdateInput) validate() error {
	if in.Status != "" && !validStatuses[in.Status] {
		return fmt.Errorf("update detections: %w: invalid status %q", errInvalidInput, in.Status)
	}

	assignCount := 0
	for _, v := range []string{in.AssignToUUID, in.AssignToUserID, in.AssignToName} {
		if v != "" {
			assignCount++
		}
	}
	if assignCount > 1 {
		return fmt.Errorf("update detections: %w: assign_to_uuid, assign_to_user_id, and assign_to_name are mutually exclusive", errInvalidInput)
	}
	if in.Unassign && assignCount > 0 {
		return fmt.Errorf("update detections: %w: unassign cannot be combined with an assignment", errInvalidInput)
	}
	return nil
}

// hasResolutionTag reports whether the added tags include a resolution tag.
func (in UpdateInput) hasResolutionTag() bool {
	for _, t := range in.AddTags {
		if resolutionTags[t] {
			return true
		}
	}
	return false
}

func ptr[T any](v T) *T { return &v }
