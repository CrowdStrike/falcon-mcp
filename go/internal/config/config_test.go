package config

import (
	"testing"
	"unicode"
)

func TestParseModules(t *testing.T) {
	tests := []struct {
		in   string
		want []string
	}{
		{"", nil},
		{"hosts", []string{"hosts"}},
		{"hosts,detections", []string{"hosts", "detections"}},
		{" hosts , detections ", []string{"hosts", "detections"}}, // trims whitespace
		{"hosts,,detections", []string{"hosts", "detections"}},    // drops empties
	}
	for _, tt := range tests {
		got := ParseModules(tt.in)
		if len(got) != len(tt.want) {
			t.Fatalf("ParseModules(%q) = %v, want %v", tt.in, got, tt.want)
		}
		for i := range got {
			if got[i] != tt.want[i] {
				t.Fatalf("ParseModules(%q)[%d] = %q, want %q", tt.in, i, got[i], tt.want[i])
			}
		}
	}
}

func TestValidate_RequiresCredentials(t *testing.T) {
	if err := (&Config{ClientID: "id", ClientSecret: "secret"}).Validate(); err != nil {
		t.Fatalf("valid config rejected: %v", err)
	}
	if err := (&Config{ClientID: "id"}).Validate(); err == nil {
		t.Fatal("missing client secret should fail validation")
	}
	if err := (&Config{ClientSecret: "secret"}).Validate(); err == nil {
		t.Fatal("missing client id should fail validation")
	}
	// EC-1 / Effective Go: error strings are lower-case and unpunctuated.
	err := (&Config{}).Validate()
	if err == nil {
		t.Fatal("empty config should fail validation")
	}
	if r := []rune(err.Error()); unicode.IsUpper(r[0]) {
		t.Fatalf("error string must start lower-case, got %q", err.Error())
	}
}

func TestDefaults(t *testing.T) {
	c := Defaults()
	if c.Transport != "stdio" {
		t.Fatalf("default transport = %q, want stdio", c.Transport)
	}
	if c.BaseURL != "https://api.crowdstrike.com" {
		t.Fatalf("default base URL = %q", c.BaseURL)
	}
	if c.Port != 8000 {
		t.Fatalf("default port = %d, want 8000", c.Port)
	}
	if c.Host != "127.0.0.1" {
		t.Fatalf("default host = %q", c.Host)
	}
}
