package hosts

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/crowdstrike/falcon-mcp/internal/parity"
)

// TestParity_SearchHosts is the reference parity fixture for the Go rewrite.
// It runs the real hosts handler against a fake transport and asserts the
// output matches the expected Python-server shape structurally (D4: key order
// ignored) and, for the ordering case, in the fixed sort-correct sequence (D5:
// array order preserved, asserting the *fixed* behavior not Python's buggy
// order). Phase 4 modules plug into this same table-driven pattern.
func TestParity_SearchHosts(t *testing.T) {
	tests := []struct {
		name      string
		queryIDs  []string
		detailIDs []string
		input     searchHostsInput
		wantJSON  string   // expected canonical parity payload
		wantOrder []string // fixed sort-correct device_id order (nil to skip)
	}{
		{
			name:      "success two hosts",
			queryIDs:  []string{"a", "b"},
			detailIDs: []string{"a", "b"},
			input:     searchHostsInput{Filter: "platform_name:'Windows'", Sort: "hostname.asc"},
			wantJSON:  `[{"device_id":"a","hostname":"host-a"},{"device_id":"b","hostname":"host-b"}]`,
			wantOrder: []string{"a", "b"},
		},
		{
			name:      "sort order restored when details endpoint scrambles",
			queryIDs:  []string{"c", "a", "b"},
			detailIDs: []string{"a", "b", "c"}, // details returns a different order
			input:     searchHostsInput{Filter: "x"},
			wantJSON:  `[{"device_id":"c","hostname":"host-c"},{"device_id":"a","hostname":"host-a"},{"device_id":"b","hostname":"host-b"}]`,
			wantOrder: []string{"c", "a", "b"}, // the FIXED order (matches query step), not Python's buggy scramble
		},
		{
			name:      "empty search returns bare list",
			queryIDs:  []string{},
			detailIDs: []string{},
			input:     searchHostsInput{Filter: "nomatch"},
			wantJSON:  `[]`,
			wantOrder: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var captured []capturedRequest
			c := newTestClient(t, tt.queryIDs, detailsResponse(tt.detailIDs...), &captured)
			h := &handlers{c: c}

			out, err := h.searchHosts(context.Background(), tt.input)
			if err != nil {
				t.Fatalf("searchHosts: %v", err)
			}
			got, err := json.Marshal(out)
			if err != nil {
				t.Fatalf("marshal output: %v", err)
			}

			// D4 tier-1: semantic payload parity — key order ignored, and
			// gofalcon's null-valued optional fields treated as absent to match
			// FalconPy's omitted keys.
			if d, err := parity.DiffSemantic([]byte(tt.wantJSON), got); err != nil {
				t.Fatalf("parity diff error: %v", err)
			} else if d != "" {
				t.Fatalf("parity mismatch:\n%s", d)
			}

			// D5: fixed sort-correct ordering asserted independently.
			if tt.wantOrder != nil {
				order, err := parity.OrderOf(got, "device_id")
				if err != nil {
					t.Fatalf("order-of: %v", err)
				}
				if len(order) != len(tt.wantOrder) {
					t.Fatalf("order length = %d, want %d (%v)", len(order), len(tt.wantOrder), order)
				}
				for i := range tt.wantOrder {
					if order[i] != tt.wantOrder[i] {
						t.Fatalf("sort order = %v, want %v", order, tt.wantOrder)
					}
				}
			}
		})
	}
}
