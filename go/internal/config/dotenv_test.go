package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadDotEnv_LoadsMissingVarsWithoutOverriding(t *testing.T) {
	dir := t.TempDir()
	envPath := filepath.Join(dir, ".env")
	content := "# a comment\n" +
		"FALCON_MCP_TEST_NEW=fromfile\n" +
		"FALCON_MCP_TEST_EXISTING=fromfile\n" +
		"\n" +
		"FALCON_MCP_TEST_QUOTED=\"quoted value\"\n"
	if err := os.WriteFile(envPath, []byte(content), 0o600); err != nil {
		t.Fatalf("write .env: %v", err)
	}

	// An already-set variable must not be overridden by the file.
	t.Setenv("FALCON_MCP_TEST_EXISTING", "fromenv")

	// Ensure the "new" var starts unset within this test's scope.
	t.Setenv("FALCON_MCP_TEST_NEW", "")
	_ = os.Unsetenv("FALCON_MCP_TEST_NEW")
	t.Cleanup(func() {
		_ = os.Unsetenv("FALCON_MCP_TEST_NEW")
		_ = os.Unsetenv("FALCON_MCP_TEST_QUOTED")
	})

	LoadDotEnv(envPath)

	if got := os.Getenv("FALCON_MCP_TEST_NEW"); got != "fromfile" {
		t.Fatalf("new var = %q, want fromfile", got)
	}
	if got := os.Getenv("FALCON_MCP_TEST_EXISTING"); got != "fromenv" {
		t.Fatalf("existing var = %q, want fromenv (must not be overridden)", got)
	}
	if got := os.Getenv("FALCON_MCP_TEST_QUOTED"); got != "quoted value" {
		t.Fatalf("quoted var = %q, want 'quoted value'", got)
	}
}

func TestLoadDotEnv_MissingFileIsNoError(t *testing.T) {
	// Must not panic or fail when the file is absent (CI injects env directly).
	LoadDotEnv(filepath.Join(t.TempDir(), "does-not-exist.env"))
}
