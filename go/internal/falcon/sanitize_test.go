package falcon

import "testing"

func TestSanitizeInput(t *testing.T) {
	long := make([]byte, 300)
	for i := range long {
		long[i] = 'a'
	}

	tests := []struct {
		name string
		in   string
		want string
	}{
		{name: "plain string unchanged", in: "Administrator", want: "Administrator"},
		{name: "wildcard preserved", in: "Admin*", want: "Admin*"},
		{name: "strips double quotes", in: `a"b`, want: "ab"},
		{name: "strips single quotes", in: "a'b", want: "ab"},
		{name: "strips backslash", in: `a\b`, want: "ab"},
		{name: "strips newline carriage tab", in: "a\nb\rc\td", want: "abcd"},
		{name: "strips combined injection", in: "\"; DROP\n", want: "; DROP"},
		{name: "caps at 255 chars", in: string(long), want: string(long[:255])},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := SanitizeInput(tt.in); got != tt.want {
				t.Errorf("SanitizeInput(%q) = %q, want %q", tt.in, got, tt.want)
			}
		})
	}
}
