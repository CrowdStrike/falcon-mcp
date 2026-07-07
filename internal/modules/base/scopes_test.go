package base

import (
	"slices"
	"testing"
)

func TestScopeStrings(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name  string
		scope Scope
		want  []string
	}{
		{
			name:  "read only",
			scope: Scope{Name: "Hosts", Read: true},
			want:  []string{"Hosts:read"},
		},
		{
			name:  "write only",
			scope: Scope{Name: "Alerts", Write: true},
			want:  []string{"Alerts:write"},
		},
		{
			name:  "read and write",
			scope: Scope{Name: "host-group", Read: true, Write: true},
			want:  []string{"host-group:read", "host-group:write"},
		},
		{
			name:  "neither returns nil",
			scope: Scope{Name: "Hosts"},
			want:  nil,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			if got := tc.scope.Strings(); !slices.Equal(got, tc.want) {
				t.Errorf("Strings() = %v, want %v", got, tc.want)
			}
		})
	}
}
