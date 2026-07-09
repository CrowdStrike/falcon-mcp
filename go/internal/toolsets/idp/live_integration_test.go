//go:build integration

package idp

import (
	"context"
	"encoding/json"
	"net/url"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon"

	fal "github.com/crowdstrike/falcon-mcp/internal/falcon"
)

// loadDotEnv loads KEY=VALUE lines from the project-root .env into the process
// environment when the variables are not already set. It intentionally does not
// print values. A missing file is not an error (CI may inject env directly).
func loadDotEnv(t *testing.T) {
	t.Helper()
	_, thisFile, _, _ := runtime.Caller(0)
	// internal/toolsets/idp -> repo root is four levels up from go/.
	root := filepath.Clean(filepath.Join(filepath.Dir(thisFile), "..", "..", "..", ".."))
	data, err := os.ReadFile(filepath.Join(root, ".env"))
	if err != nil {
		return
	}
	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		k, v, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		k, v = strings.TrimSpace(k), strings.Trim(strings.TrimSpace(v), `"'`)
		if os.Getenv(k) == "" {
			t.Setenv(k, v)
		}
	}
}

// hostFromURL returns the host component of a full base URL, or the input
// unchanged when it does not parse as a URL with a host.
func hostFromURL(base string) string {
	if u, err := url.Parse(base); err == nil && u.Host != "" {
		return u.Host
	}
	return base
}

// TestLive_InvestigateEntity exercises the real Identity Protection GraphQL
// endpoint to validate the operation name, request shape, and that the raw body
// reader captures the response the typed OK type discards. It requires
// FALCON_CLIENT_ID and FALCON_CLIENT_SECRET plus the Identity Protection scope.
func TestLive_InvestigateEntity(t *testing.T) {
	loadDotEnv(t)
	id, secret := os.Getenv("FALCON_CLIENT_ID"), os.Getenv("FALCON_CLIENT_SECRET")
	if id == "" || secret == "" {
		t.Skip("live test requires FALCON_CLIENT_ID and FALCON_CLIENT_SECRET")
	}

	ctx := context.Background()
	apiCfg := &falcon.ApiConfig{ClientId: id, ClientSecret: secret, Context: ctx}
	if base := os.Getenv("FALCON_BASE_URL"); base != "" {
		apiCfg.HostOverride = hostFromURL(base)
	}
	c, err := falcon.NewClient(apiCfg)
	if err != nil {
		t.Fatalf("build live client: %v", err)
	}

	// A minimal well-formed query: resolve up to a few USER entities. Even a
	// zero-result response proves the op name, path, auth, and body reader.
	query := `
query {
    entities(types: [USER], first: 1) {
        nodes { entityId primaryDisplayName }
    }
}`
	body, apiErr := fal.GraphQL(ctx, c, query, scopeIdentityRead)
	if apiErr != nil {
		t.Fatalf("live GraphQL call failed: %s (scopes=%v)", apiErr.Message, apiErr.RequiredScopes)
	}
	if _, ok := body["data"]; !ok {
		// GraphQL returns errors in the body; surface them for diagnosis.
		b, _ := json.Marshal(body)
		t.Fatalf("live response has no data field: %s", b)
	}
	b, _ := json.MarshalIndent(body, "", "  ")
	t.Logf("live GraphQL data captured (%d bytes)", len(b))
}
