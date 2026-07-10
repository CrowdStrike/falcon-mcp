package cli

import (
	"context"
	"log/slog"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/spf13/viper"

	"github.com/crowdstrike/falcon-mcp/internal/config"
	"github.com/crowdstrike/falcon-mcp/internal/version"
)

// resolveArgs builds the root command, parses args onto it, and runs PreRunE to
// resolve the config. It stops short of RunE so tests never live-serve.
func resolveArgs(t *testing.T, args []string) (*config.Config, error) {
	t.Helper()
	cmd := newRootCmd()
	if err := cmd.ParseFlags(args); err != nil {
		t.Fatalf("parse flags: %v", err)
	}
	var cfg *config.Config
	cfg, err := preRunE(cmd)
	return cfg, err
}

func TestExecuteResolvesFlags(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "")
	t.Setenv("FALCON_CLIENT_SECRET", "")

	cfg, err := resolveArgs(t, []string{"--client-id", "id", "--client-secret", "s"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.ClientID != "id" {
		t.Fatalf("cfg not resolved: %+v", cfg)
	}
	if cfg.ClientSecret != "s" {
		t.Errorf("ClientSecret = %q, want s", cfg.ClientSecret)
	}
	if cfg.Transport != "stdio" {
		t.Errorf("Transport = %q, want stdio (default)", cfg.Transport)
	}
}

// TestExecuteDebugFlag verifies --debug reinstalls the default logger at Debug
// level during PreRunE. It mutates the global default logger, so it must not run
// in parallel; it restores the original logger via t.Cleanup.
func TestExecuteDebugFlag(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	orig := slog.Default()
	t.Cleanup(func() { slog.SetDefault(orig) })
	slog.SetDefault(newLogger(slog.LevelInfo))

	if _, err := resolveArgs(t, []string{"-d"}); err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if !slog.Default().Enabled(context.Background(), slog.LevelDebug) {
		t.Errorf("default logger not enabled at Debug after --debug")
	}
}

func TestExecuteResolvesEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "e")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.ClientID != "e" {
		t.Fatalf("cfg not resolved from env: %+v", cfg)
	}
}

func TestExecuteFlagBeatsEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "envval")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{"--client-id", "flagval"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.ClientID != "flagval" {
		t.Fatalf("flag should beat env: got %+v", cfg)
	}
}

func TestExecuteUserAgentCommentFlagAlias(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")
	t.Setenv("FALCON_USER_AGENT", "")
	t.Setenv("FALCON_USER_AGENT_COMMENT", "")

	cfg, err := resolveArgs(t, []string{"--user-agent-comment", "my-tool/1.0"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	want := "falcon-mcp/" + version.Version + " my-tool/1.0"
	if cfg == nil || cfg.UserAgent != want {
		t.Fatalf("UserAgent = %q, want %q", cfgUserAgent(cfg), want)
	}
}

func TestExecuteUserAgentCommentEnvAlias(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")
	t.Setenv("FALCON_USER_AGENT", "")
	t.Setenv("FALCON_USER_AGENT_COMMENT", "env-tool/2.0")

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	want := "falcon-mcp/" + version.Version + " env-tool/2.0"
	if cfg == nil || cfg.UserAgent != want {
		t.Fatalf("UserAgent = %q, want %q", cfgUserAgent(cfg), want)
	}
}

// TestExecuteUserAgentEnvWinsOverComment documents precedence: BindEnv lists
// FALCON_USER_AGENT first, so it wins when both env vars are set.
func TestExecuteUserAgentEnvWinsOverComment(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")
	t.Setenv("FALCON_USER_AGENT", "primary/1.0")
	t.Setenv("FALCON_USER_AGENT_COMMENT", "secondary/2.0")

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	want := "falcon-mcp/" + version.Version + " primary/1.0"
	if cfg == nil || cfg.UserAgent != want {
		t.Fatalf("UserAgent = %q, want %q", cfgUserAgent(cfg), want)
	}
}

// cfgUserAgent safely reads UserAgent for failure messages when cfg may be nil.
func cfgUserAgent(c *config.Config) string {
	if c == nil {
		return "<nil>"
	}
	return c.UserAgent
}

func TestExecuteDynamicFlag(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{"--dynamic"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || !cfg.Dynamic {
		t.Fatalf("Dynamic = false, want true from --dynamic: %+v", cfg)
	}
}

func TestExecuteDynamicEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")
	t.Setenv("FALCON_MCP_DYNAMIC", "true")

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || !cfg.Dynamic {
		t.Fatalf("Dynamic = false, want true from FALCON_MCP_DYNAMIC: %+v", cfg)
	}
}

func TestExecuteDynamicDefaultsFalse(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.Dynamic {
		t.Fatalf("Dynamic = true, want false by default: %+v", cfg)
	}
}

func TestExecuteStatelessHTTPFlag(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{"--transport", "http", "--http-addr", ":8080", "--stateless-http"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || !cfg.StatelessHTTP {
		t.Fatalf("StatelessHTTP = false, want true from --stateless-http: %+v", cfg)
	}
}

func TestExecuteKeepAliveFlag(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{"--transport", "http", "--http-addr", ":8080", "--keep-alive", "30s"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.KeepAlive != 30*time.Second {
		t.Fatalf("KeepAlive = %v, want 30s from --keep-alive: %+v", cfgKeepAlive(cfg), cfg)
	}
}

func TestExecuteKeepAliveEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")
	t.Setenv("FALCON_MCP_KEEP_ALIVE", "45s")

	cfg, err := resolveArgs(t, []string{"--transport", "http", "--http-addr", ":8080"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.KeepAlive != 45*time.Second {
		t.Fatalf("KeepAlive = %v, want 45s from FALCON_MCP_KEEP_ALIVE: %+v", cfgKeepAlive(cfg), cfg)
	}
}

func TestExecuteKeepAliveDefaultsZero(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, nil)
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.KeepAlive != 0 {
		t.Fatalf("KeepAlive = %v, want 0 by default: %+v", cfgKeepAlive(cfg), cfg)
	}
}

func TestExecuteStatelessHTTPEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")
	t.Setenv("FALCON_MCP_STATELESS_HTTP", "true")

	cfg, err := resolveArgs(t, []string{"--transport", "http", "--http-addr", ":8080"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || !cfg.StatelessHTTP {
		t.Fatalf("StatelessHTTP = false, want true from FALCON_MCP_STATELESS_HTTP: %+v", cfg)
	}
}

func TestExecuteStatelessHTTPDefaultsFalse(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.StatelessHTTP {
		t.Fatalf("StatelessHTTP = true, want false by default: %+v", cfg)
	}
}

func TestExecuteHTTPTransport(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "")
	t.Setenv("FALCON_CLIENT_SECRET", "")

	cfg, err := resolveArgs(t, []string{
		"--transport", "http", "--http-addr", ":9000",
		"--client-id", "id", "--client-secret", "s",
	})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.Transport != "http" || cfg.HTTPAddr != ":9000" {
		t.Fatalf("http transport not resolved: %+v", cfg)
	}
}

func TestExecuteAPIKeyFlag(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{"--transport", "http", "--http-addr", ":8080", "--api-key", "secret"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.APIKey != "secret" {
		t.Fatalf("APIKey = %q, want secret from --api-key: %+v", cfgAPIKey(cfg), cfg)
	}
}

func TestExecuteAPIKeyEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")
	t.Setenv("FALCON_MCP_API_KEY", "envsecret")

	cfg, err := resolveArgs(t, []string{"--transport", "http", "--http-addr", ":8080"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.APIKey != "envsecret" {
		t.Fatalf("APIKey = %q, want envsecret from FALCON_MCP_API_KEY: %+v", cfgAPIKey(cfg), cfg)
	}
}

func TestExecuteAPIKeyRejectedWithStdio(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{"--api-key", "secret"})
	if err == nil {
		t.Fatal("expected error for --api-key with stdio transport")
	}
	if cfg != nil {
		t.Fatal("cfg should be nil when config invalid")
	}
}

// cfgAPIKey safely reads APIKey for failure messages when cfg may be nil.
func cfgAPIKey(c *config.Config) string {
	if c == nil {
		return "<nil>"
	}
	return c.APIKey
}

// cfgKeepAlive safely reads KeepAlive for failure messages when cfg may be nil.
func cfgKeepAlive(c *config.Config) time.Duration {
	if c == nil {
		return -1
	}
	return c.KeepAlive
}

func TestExecuteProxyFlag(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{"--proxy", "http://proxy.example.com:8080"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.Proxy != "http://proxy.example.com:8080" {
		t.Fatalf("Proxy not resolved from --proxy: %+v", cfg)
	}
}

func TestExecuteProxyEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")
	t.Setenv("FALCON_MCP_PROXY", "http://envproxy.example.com:3128")

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.Proxy != "http://envproxy.example.com:3128" {
		t.Fatalf("Proxy not resolved from FALCON_MCP_PROXY: %+v", cfg)
	}
}

func TestExecuteProxyFlagBeatsEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")
	t.Setenv("FALCON_MCP_PROXY", "http://envproxy.example.com:3128")

	cfg, err := resolveArgs(t, []string{"--proxy", "http://flagproxy.example.com:8080"})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.Proxy != "http://flagproxy.example.com:8080" {
		t.Fatalf("--proxy should beat FALCON_MCP_PROXY: %+v", cfg)
	}
}

func TestExecuteProxyDefaultsEmpty(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.Proxy != "" {
		t.Fatalf("Proxy = %q, want empty by default: %+v", cfg.Proxy, cfg)
	}
}

func TestExecuteProxyInvalidErrors(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{"--proxy", "not-a-url"})
	if err == nil {
		t.Fatal("expected error for invalid --proxy")
	}
	if cfg != nil {
		t.Fatal("cfg should be nil when config invalid")
	}
}

func TestExecuteMissingCredsErrors(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "")
	t.Setenv("FALCON_CLIENT_SECRET", "")

	cfg, err := resolveArgs(t, []string{})
	if err == nil {
		t.Fatal("expected error for missing credentials")
	}
	if cfg != nil {
		t.Fatal("cfg should be nil when config invalid")
	}
}

func TestExecuteMissingConfigFileErrors(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "id")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	cfg, err := resolveArgs(t, []string{"--config", filepath.Join(t.TempDir(), "nope.yaml")})
	if err == nil {
		t.Fatal("expected error for missing config file")
	}
	if cfg != nil {
		t.Fatal("cfg should be nil when config file missing")
	}
}

func TestExecuteReadsConfigFile(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "")
	t.Setenv("FALCON_CLIENT_SECRET", "")

	dir := t.TempDir()
	path := filepath.Join(dir, "cfg.yaml")
	if err := os.WriteFile(path, []byte("client_id: fromfile\nclient_secret: s\n"), 0o600); err != nil {
		t.Fatal(err)
	}

	cfg, err := resolveArgs(t, []string{"--config", path})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.ClientID != "fromfile" {
		t.Fatalf("config file not read: %+v", cfg)
	}
}

// newTestViper builds a viper for tests, failing the test if codec registration
// errors (it does not in practice).
func newTestViper(t *testing.T) *viper.Viper {
	t.Helper()
	v, err := newViper()
	if err != nil {
		t.Fatalf("newViper: %v", err)
	}
	return v
}

func TestResolvePrecedence(t *testing.T) {
	t.Parallel()
	v := newTestViper(t)
	v.Set("client_id", "flagval") // simulates a bound flag value (highest)
	v.Set("client_secret", "sekret")
	v.SetDefault("transport", "stdio")
	v.Set("hosted", true)
	in := resolve(v)
	if in.ClientID != "flagval" {
		t.Errorf("ClientID = %q, want flagval", in.ClientID)
	}
	if in.ClientSecret != "sekret" {
		t.Errorf("ClientSecret = %q, want sekret", in.ClientSecret)
	}
	if in.Transport != "stdio" {
		t.Errorf("Transport = %q, want stdio", in.Transport)
	}
	if !in.Hosted {
		t.Errorf("Hosted = false, want true")
	}
}

func TestResolveMapsAllKeys(t *testing.T) {
	t.Parallel()
	v := newTestViper(t)
	v.Set("client_id", "id")
	v.Set("client_secret", "s")
	v.Set("cloud", "us-1")
	v.Set("base_url", "https://example.test")
	v.Set("member_cid", "abc")
	v.Set("transport", "http")
	v.Set("http_addr", ":9000")
	v.Set("user_agent", "my-tool/1.0")
	v.Set("api_key", "secret")
	v.Set("proxy", "http://proxy.example.com:8080")
	in := resolve(v)
	if in.Cloud != "us-1" || in.HostOverride != "https://example.test" ||
		in.MemberCID != "abc" || in.Transport != "http" || in.HTTPAddr != ":9000" ||
		in.UserAgent != "my-tool/1.0" || in.APIKey != "secret" ||
		in.Proxy != "http://proxy.example.com:8080" {
		t.Errorf("resolve mapped keys incorrectly: %+v", in)
	}
}

func TestReadConfigFileYAML(t *testing.T) {
	t.Parallel()
	dir := t.TempDir()
	path := filepath.Join(dir, "c.yaml")
	if err := os.WriteFile(path, []byte("client_id: fileval\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	v := newTestViper(t)
	if err := readConfigFile(v, path); err != nil {
		t.Fatalf("readConfigFile: %v", err)
	}
	if got := v.GetString("client_id"); got != "fileval" {
		t.Errorf("client_id = %q, want fileval", got)
	}
}

func TestReadConfigFileINISection(t *testing.T) {
	t.Parallel()
	dir := t.TempDir()
	path := filepath.Join(dir, "c.ini")
	if err := os.WriteFile(path, []byte("[falcon]\nclient_id = fromini\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	v := newTestViper(t)
	if err := readConfigFile(v, path); err != nil {
		t.Fatalf("readConfigFile: %v", err)
	}
	normalizeFalconPrefix(v)
	if got := v.GetString("client_id"); got != "fromini" {
		t.Errorf("client_id = %q, want fromini", got)
	}
}

func TestNormalizeFalconPrefixStrips(t *testing.T) {
	t.Parallel()
	v := newTestViper(t)
	v.Set("falcon_client_id", "y")
	normalizeFalconPrefix(v)
	if got := v.GetString("client_id"); got != "y" {
		t.Errorf("client_id = %q, want y (prefix stripped)", got)
	}
}

func TestNormalizeFalconPrefixNonPrefixedWins(t *testing.T) {
	t.Parallel()
	v := newTestViper(t)
	v.Set("client_id", "a")
	v.Set("falcon_client_id", "b")
	normalizeFalconPrefix(v)
	if got := v.GetString("client_id"); got != "a" {
		t.Errorf("client_id = %q, want a (non-prefixed wins)", got)
	}
}

func TestReadConfigFileExplicitMissingIsError(t *testing.T) {
	t.Parallel()
	v := newTestViper(t)
	if err := readConfigFile(v, filepath.Join(t.TempDir(), "nope.yaml")); err == nil {
		t.Fatal("expected error for missing explicit config file")
	}
}

func TestReadConfigFileNoPathNoFileIsOK(t *testing.T) {
	dir := t.TempDir()
	// Chdir into an empty temp dir so "." search path finds nothing.
	t.Chdir(dir)
	v := newTestViper(t)
	if err := readConfigFile(v, ""); err != nil {
		t.Fatalf("readConfigFile with no path should not error, got: %v", err)
	}
}

// writeDotEnv writes a .env file into dir.
func writeDotEnv(t *testing.T, dir, content string) {
	t.Helper()
	if err := os.WriteFile(filepath.Join(dir, ".env"), []byte(content), 0o600); err != nil {
		t.Fatalf("write .env: %v", err)
	}
}

func TestMergeDotEnvLoadsKeys(t *testing.T) {
	dir := t.TempDir()
	writeDotEnv(t, dir, "FALCON_CLIENT_ID=fromdotenv\n")
	t.Chdir(dir)

	v := newTestViper(t)
	if err := mergeDotEnv(v); err != nil {
		t.Fatalf("mergeDotEnv: %v", err)
	}
	normalizeFalconPrefix(v)
	if got := v.GetString("client_id"); got != "fromdotenv" {
		t.Errorf("client_id = %q, want fromdotenv", got)
	}
}

func TestMergeDotEnvMissingIsOK(t *testing.T) {
	t.Chdir(t.TempDir()) // no .env present
	v := newTestViper(t)
	if err := mergeDotEnv(v); err != nil {
		t.Fatalf("mergeDotEnv with no .env should not error, got: %v", err)
	}
}

// TestMergeDotEnvPreservesConfigFile verifies .env merges onto a config file
// already read into viper rather than replacing it.
func TestMergeDotEnvPreservesConfigFile(t *testing.T) {
	dir := t.TempDir()
	writeDotEnv(t, dir, "FALCON_CLOUD=us-2\n")
	t.Chdir(dir)

	v := newTestViper(t)
	v.Set("client_id", "fromfile") // simulate a value from a prior config-file read
	if err := mergeDotEnv(v); err != nil {
		t.Fatalf("mergeDotEnv: %v", err)
	}
	normalizeFalconPrefix(v)
	if got := v.GetString("client_id"); got != "fromfile" {
		t.Errorf("client_id = %q, want fromfile (config file value preserved)", got)
	}
	if got := v.GetString("cloud"); got != "us-2" {
		t.Errorf("cloud = %q, want us-2 (from .env)", got)
	}
}

// TestExecuteReadsDotEnv resolves a full config from a .env file in the CWD.
func TestExecuteReadsDotEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "")
	t.Setenv("FALCON_CLIENT_SECRET", "")

	dir := t.TempDir()
	writeDotEnv(t, dir, "FALCON_CLIENT_ID=envfile\nFALCON_CLIENT_SECRET=s\n")
	t.Chdir(dir)

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.ClientID != "envfile" {
		t.Fatalf(".env not resolved: %+v", cfg)
	}
}

// TestExecuteEnvBeatsDotEnv verifies a real env var outranks a .env value,
// matching python-dotenv's non-overriding load_dotenv.
func TestExecuteEnvBeatsDotEnv(t *testing.T) {
	t.Setenv("FALCON_CLIENT_ID", "fromenv")
	t.Setenv("FALCON_CLIENT_SECRET", "s")

	dir := t.TempDir()
	writeDotEnv(t, dir, "FALCON_CLIENT_ID=fromdotenv\n")
	t.Chdir(dir)

	cfg, err := resolveArgs(t, []string{})
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if cfg == nil || cfg.ClientID != "fromenv" {
		t.Fatalf("env should beat .env: got %+v", cfg)
	}
}
