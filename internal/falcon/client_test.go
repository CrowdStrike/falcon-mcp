package falconapi

import (
	"context"
	"net/http"
	"testing"

	"golang.org/x/oauth2"

	"github.com/crowdstrike/falcon-mcp/internal/config"
)

func TestProxyHTTPClient(t *testing.T) {
	t.Parallel()
	const proxy = "http://proxy.example.com:8080"

	c, err := proxyHTTPClient(proxy)
	if err != nil {
		t.Fatalf("proxyHTTPClient: %v", err)
	}

	tr, ok := c.Transport.(*http.Transport)
	if !ok {
		t.Fatalf("transport type = %T, want *http.Transport", c.Transport)
	}
	if tr.Proxy == nil {
		t.Fatal("transport Proxy is nil, want a proxy func")
	}

	// The Proxy func should resolve any outbound request to the configured proxy.
	req, err := http.NewRequest(http.MethodGet, "https://api.crowdstrike.com/x", nil)
	if err != nil {
		t.Fatal(err)
	}
	got, err := tr.Proxy(req)
	if err != nil {
		t.Fatalf("proxy func: %v", err)
	}
	if got == nil || got.String() != proxy {
		t.Errorf("resolved proxy = %v, want %s", got, proxy)
	}
}

func TestProxyHTTPClientClonesDefaults(t *testing.T) {
	t.Parallel()
	c, err := proxyHTTPClient("http://proxy.example.com:8080")
	if err != nil {
		t.Fatalf("proxyHTTPClient: %v", err)
	}
	tr := c.Transport.(*http.Transport)
	// A clone of http.DefaultTransport keeps its connection-pool defaults rather
	// than a zero-value transport.
	if tr.MaxIdleConns == 0 {
		t.Error("MaxIdleConns = 0, want DefaultTransport's non-zero default (clone lost defaults)")
	}
	if def := http.DefaultTransport.(*http.Transport); tr == def {
		t.Error("transport is the shared DefaultTransport, want an independent clone")
	}
}

func TestProxyHTTPClientInvalid(t *testing.T) {
	t.Parallel()
	// A control character makes url.Parse fail outright.
	if _, err := proxyHTTPClient("http://\x7f"); err == nil {
		t.Fatal("expected error for unparseable proxy url")
	}
}

// TestNewWithProxy verifies the client constructs when a proxy is configured.
// HostOverride is set so gofalcon skips cloud autodiscovery (a network call at
// construction); the OAuth token exchange is deferred to first use, so this
// exercises the proxy-injection branch fully offline.
func TestNewWithProxy(t *testing.T) {
	t.Parallel()
	cfg := &config.Config{
		ClientID:     "id",
		ClientSecret: "secret",
		HostOverride: "api.us-2.crowdstrike.com",
		Proxy:        "http://proxy.example.com:8080",
	}
	c, err := New(context.Background(), cfg)
	if err != nil {
		t.Fatalf("New with proxy: %v", err)
	}
	if c == nil {
		t.Fatal("New returned nil client")
	}
}

func TestNewWithoutProxy(t *testing.T) {
	t.Parallel()
	cfg := &config.Config{
		ClientID:     "id",
		ClientSecret: "secret",
		HostOverride: "api.us-2.crowdstrike.com",
	}
	c, err := New(context.Background(), cfg)
	if err != nil {
		t.Fatalf("New without proxy: %v", err)
	}
	if c == nil {
		t.Fatal("New returned nil client")
	}
}

// TestOAuth2ContextKeyResolves documents the mechanism the proxy relies on:
// gofalcon's client-credentials path resolves its base HTTP client from the
// oauth2.HTTPClient context key. If this ever stops holding, proxy injection is
// silently broken, so assert it directly.
func TestOAuth2ContextKeyResolves(t *testing.T) {
	t.Parallel()
	want := &http.Client{}
	ctx := context.WithValue(context.Background(), oauth2.HTTPClient, want)
	got, ok := ctx.Value(oauth2.HTTPClient).(*http.Client)
	if !ok || got != want {
		t.Fatal("oauth2.HTTPClient context key did not round-trip an *http.Client")
	}
}
