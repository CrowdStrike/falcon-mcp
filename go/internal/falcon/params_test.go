package falcon

import "testing"

func TestOptString(t *testing.T) {
	tests := []struct {
		name    string
		in      string
		wantNil bool
	}{
		{"empty string yields nil", "", true},
		{"non-empty string yields pointer", "platform_name:'Windows'", false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := Opt(tt.in)
			if tt.wantNil {
				if got != nil {
					t.Fatalf("Opt(%q) = %v, want nil", tt.in, *got)
				}
				return
			}
			if got == nil {
				t.Fatalf("Opt(%q) = nil, want pointer", tt.in)
			}
			if *got != tt.in {
				t.Fatalf("*Opt(%q) = %q, want %q", tt.in, *got, tt.in)
			}
		})
	}
}

func TestOptInt64(t *testing.T) {
	if got := Opt(int64(0)); got != nil {
		t.Fatalf("Opt(int64(0)) = %v, want nil (zero conflated with unset, matches Python)", *got)
	}
	got := Opt(int64(50))
	if got == nil || *got != 50 {
		t.Fatalf("Opt(int64(50)) = %v, want pointer to 50", got)
	}
}

func TestOptBool(t *testing.T) {
	if got := Opt(false); got != nil {
		t.Fatalf("Opt(false) = %v, want nil", *got)
	}
	got := Opt(true)
	if got == nil || *got != true {
		t.Fatalf("Opt(true) = %v, want pointer to true", got)
	}
}
