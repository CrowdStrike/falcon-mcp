package falcon

import "testing"

func TestScopeStrings(t *testing.T) {
	tests := []struct {
		name  string
		scope Scope
		want  []string
	}{
		{"read only", Scope{Name: "Hosts", Read: true}, []string{"Hosts:read"}},
		{"write only", Scope{Name: "Hosts", Write: true}, []string{"Hosts:write"}},
		{"read and write", Scope{Name: "Hosts", Read: true, Write: true}, []string{"Hosts:read", "Hosts:write"}},
		{"neither yields empty", Scope{Name: "Hosts"}, nil},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.scope.Strings()
			if len(got) != len(tt.want) {
				t.Fatalf("Strings() = %v, want %v", got, tt.want)
			}
			for i := range got {
				if got[i] != tt.want[i] {
					t.Fatalf("Strings()[%d] = %q, want %q", i, got[i], tt.want[i])
				}
			}
		})
	}
}
