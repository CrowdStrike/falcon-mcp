package cli

import (
	"io"
	"os"
	"strings"
	"testing"

	"github.com/crowdstrike/falcon-mcp/internal/toolsets"

	// Blank import registers the hosts module in the default registry.
	_ "github.com/crowdstrike/falcon-mcp/internal/toolsets/hosts"
)

func TestResolveConfig_Precedence(t *testing.T) {
	// env overrides default; changed flag overrides env.
	t.Setenv("FALCON_MCP_TRANSPORT", "streamable-http")
	t.Setenv("FALCON_CLIENT_ID", "env-id")
	t.Setenv("FALCON_CLIENT_SECRET", "env-secret")

	root := newRootCmd()
	root.SetArgs([]string{"--transport", "sse"})
	if err := root.ParseFlags([]string{"--transport", "sse"}); err != nil {
		t.Fatalf("parse: %v", err)
	}

	cfg := resolveConfig(root)
	if cfg.Transport != "sse" {
		t.Fatalf("changed flag should win over env: transport = %q, want sse", cfg.Transport)
	}
	if cfg.ClientID != "env-id" {
		t.Fatalf("env credential not applied: %q", cfg.ClientID)
	}
}

func TestResolveConfig_EnvOverDefault(t *testing.T) {
	t.Setenv("FALCON_BASE_URL", "https://api.us-2.crowdstrike.com")
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "secret")

	root := newRootCmd()
	_ = root.ParseFlags(nil)
	cfg := resolveConfig(root)
	if cfg.BaseURL != "https://api.us-2.crowdstrike.com" {
		t.Fatalf("env base URL not applied: %q", cfg.BaseURL)
	}
}

func TestResolveConfig_DefaultWhenUnset(t *testing.T) {
	root := newRootCmd()
	_ = root.ParseFlags(nil)
	cfg := resolveConfig(root)
	if cfg.Transport != "stdio" {
		t.Fatalf("default transport = %q, want stdio", cfg.Transport)
	}
}

func TestResolveConfig_ReadOnlyFlag(t *testing.T) {
	root := newRootCmd()
	_ = root.ParseFlags([]string{"--read-only"})
	cfg := resolveConfig(root)
	if !cfg.ReadOnly {
		t.Fatal("--read-only flag not applied")
	}
}

// TestHTTPConfig_MapsHostPortStateless asserts the run() switch feeds the HTTP
// transports a correctly-joined address and the stateless toggle.
func TestHTTPConfig_MapsHostPortStateless(t *testing.T) {
	root := newRootCmd()
	_ = root.ParseFlags([]string{"--host", "0.0.0.0", "--port", "9123", "--stateless-http"})
	cfg := resolveConfig(root)
	hc := httpConfig(cfg)
	if hc.Addr != "0.0.0.0:9123" {
		t.Fatalf("Addr = %q, want 0.0.0.0:9123", hc.Addr)
	}
	if !hc.Stateless {
		t.Fatal("Stateless not propagated from --stateless-http")
	}
}

// TestHostsRegisteredSlug asserts the hosts module registers under the exact
// slug agents/configs depend on.
func TestHostsRegisteredSlug(t *testing.T) {
	slugs := toolsets.Default().Slugs()
	found := false
	for _, s := range slugs {
		if s == "hosts" {
			found = true
		}
	}
	if !found {
		t.Fatalf("hosts not registered; slugs = %v", slugs)
	}
}

func TestReadOnlyDropsWriteTools(t *testing.T) {
	// hosts is all read-only, so a read-only build keeps both tools; this
	// asserts the filter path runs without dropping read tools.
	sets := toolsets.Default().Build(nil, []string{"hosts"}, true)
	if len(sets) != 1 {
		t.Fatalf("want 1 toolset, got %d", len(sets))
	}
	if len(sets[0].Tools) != 2 {
		t.Fatalf("hosts read-only build should keep both read tools, got %d", len(sets[0].Tools))
	}
}

func TestConfigureLogging_WritesToStderrNotStdout(t *testing.T) {
	// Redirect both streams so we can prove log output lands on stderr and
	// stdout stays clean (stdio transport owns stdout; HTTP must not pollute it).
	origOut, origErr := os.Stdout, os.Stderr
	outR, outW, _ := os.Pipe()
	errR, errW, _ := os.Pipe()
	os.Stdout, os.Stderr = outW, errW
	t.Cleanup(func() { os.Stdout, os.Stderr = origOut, origErr })

	logger := configureLogging(true)
	if logger == nil {
		t.Fatal("configureLogging returned nil")
	}
	logger.Info("probe-line")

	_ = outW.Close()
	_ = errW.Close()
	outBuf, _ := io.ReadAll(outR)
	errBuf, _ := io.ReadAll(errR)

	if strings.Contains(string(outBuf), "probe-line") {
		t.Fatalf("log line leaked to stdout: %q", outBuf)
	}
	if !strings.Contains(string(errBuf), "probe-line") {
		t.Fatalf("log line not found on stderr: %q", errBuf)
	}
}
