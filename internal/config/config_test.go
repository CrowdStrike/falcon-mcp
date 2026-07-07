package config

import (
	"os"
	"reflect"
	"testing"
)

func TestLoadDefaults(t *testing.T) {
	clearFalconEnv(t)

	cfg, showVersion, err := Load(nil)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if showVersion {
		t.Fatal("showVersion should be false")
	}
	if cfg.Transport != "stdio" {
		t.Errorf("Transport = %q, want stdio", cfg.Transport)
	}
	if cfg.Host != "127.0.0.1" {
		t.Errorf("Host = %q, want 127.0.0.1", cfg.Host)
	}
	if cfg.Port != 8000 {
		t.Errorf("Port = %d, want 8000", cfg.Port)
	}
	if cfg.Modules != nil {
		t.Errorf("Modules = %v, want nil (all)", cfg.Modules)
	}
}

func TestLoadFlagsOverrideEnv(t *testing.T) {
	clearFalconEnv(t)
	t.Setenv("FALCON_MCP_TRANSPORT", "sse")
	t.Setenv("FALCON_MCP_PORT", "9999")

	// Flag beats env.
	cfg, _, err := Load([]string{"--transport", "streamable-http", "--port", "1234"})
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.Transport != "streamable-http" {
		t.Errorf("Transport = %q, want streamable-http", cfg.Transport)
	}
	if cfg.Port != 1234 {
		t.Errorf("Port = %d, want 1234", cfg.Port)
	}
}

func TestLoadEnvWhenNoFlag(t *testing.T) {
	clearFalconEnv(t)
	t.Setenv("FALCON_MCP_PORT", "9999")

	cfg, _, err := Load(nil)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.Port != 9999 {
		t.Errorf("Port = %d, want 9999 (from env)", cfg.Port)
	}
}

func TestLoadInvalidTransport(t *testing.T) {
	clearFalconEnv(t)
	if _, _, err := Load([]string{"--transport", "bogus"}); err == nil {
		t.Fatal("expected error for invalid transport")
	}
}

func TestParseModules(t *testing.T) {
	tests := []struct {
		in   string
		want []string
	}{
		{"", nil},
		{"  ", nil},
		{"hosts", []string{"hosts"}},
		{"hosts, detections , ioc", []string{"hosts", "detections", "ioc"}},
		{"hosts,,ioc", []string{"hosts", "ioc"}},
	}
	for _, tt := range tests {
		if got := parseModules(tt.in); !reflect.DeepEqual(got, tt.want) {
			t.Errorf("parseModules(%q) = %v, want %v", tt.in, got, tt.want)
		}
	}
}

func TestLoadVersionFlag(t *testing.T) {
	clearFalconEnv(t)
	_, showVersion, err := Load([]string{"--version"})
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if !showVersion {
		t.Fatal("showVersion should be true for --version")
	}
}

// clearFalconEnv unsets all FALCON_MCP env vars that could bleed into tests.
func clearFalconEnv(t *testing.T) {
	t.Helper()
	for _, k := range []string{
		"FALCON_MCP_TRANSPORT", "FALCON_MCP_MODULES", "FALCON_MCP_DEBUG",
		"FALCON_BASE_URL", "FALCON_MCP_HOST", "FALCON_MCP_PORT",
		"FALCON_MCP_USER_AGENT_COMMENT", "FALCON_MCP_STATELESS_HTTP",
		"FALCON_MCP_API_KEY", "FALCON_MEMBER_CID", "FALCON_PROXY_URL",
		"FALCON_MCP_DYNAMIC", "FALCON_MCP_MULTI_TENANT",
	} {
		if _, ok := os.LookupEnv(k); ok {
			t.Setenv(k, "")
			os.Unsetenv(k)
		}
	}
}
