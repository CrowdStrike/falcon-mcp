package falcon

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"golang.org/x/oauth2"
)

func TestUserAgent_Format(t *testing.T) {
	ua := userAgent("mycomment")
	if !strings.HasPrefix(ua, "falcon-mcp/") {
		t.Fatalf("user agent must start with falcon-mcp/, got %q", ua)
	}
	for _, want := range []string{"mycomment", "gofalcon/", "Go/"} {
		if !strings.Contains(ua, want) {
			t.Fatalf("user agent %q missing %q", ua, want)
		}
	}
	if !strings.Contains(ua, "(") || !strings.Contains(ua, ")") {
		t.Fatalf("user agent %q missing RFC comment parens", ua)
	}
}

func TestUserAgent_NoComment(t *testing.T) {
	ua := userAgent("")
	// With no comment, the parenthesized section still carries gofalcon/Go/os.
	if strings.Contains(ua, "; ;") {
		t.Fatalf("empty comment should not leave a dangling separator: %q", ua)
	}
	if !strings.Contains(ua, "gofalcon/") {
		t.Fatalf("user agent %q missing gofalcon token", ua)
	}
}

func TestApiConfigFor_FullURLSetsHostOverride(t *testing.T) {
	ctx := context.Background()
	ac, err := apiConfigFor(ctx, Config{
		ClientID: "id", ClientSecret: "secret",
		BaseURL: "https://api.us-2.crowdstrike.com",
	})
	if err != nil {
		t.Fatalf("apiConfigFor: %v", err)
	}
	if ac.HostOverride != "api.us-2.crowdstrike.com" {
		t.Fatalf("HostOverride = %q, want api.us-2.crowdstrike.com", ac.HostOverride)
	}
}

func TestApiConfigFor_CloudNameSetsCloud(t *testing.T) {
	ctx := context.Background()
	ac, err := apiConfigFor(ctx, Config{
		ClientID: "id", ClientSecret: "secret",
		BaseURL: "us-2",
	})
	if err != nil {
		t.Fatalf("apiConfigFor: %v", err)
	}
	if ac.HostOverride != "" {
		t.Fatalf("cloud name should not set HostOverride, got %q", ac.HostOverride)
	}
}

func TestApiConfigFor_MissingCredentials(t *testing.T) {
	_, err := apiConfigFor(context.Background(), Config{BaseURL: "us-1"})
	if err == nil {
		t.Fatal("expected error when credentials are missing")
	}
}

func TestProxyContext_InjectsHTTPClient(t *testing.T) {
	ctx, err := withProxy(context.Background(), "http://proxy.example.com:8080")
	if err != nil {
		t.Fatalf("withProxy: %v", err)
	}
	hc, ok := ctx.Value(oauth2.HTTPClient).(*http.Client)
	if !ok || hc == nil {
		t.Fatal("withProxy did not set an *http.Client on oauth2.HTTPClient")
	}
	tr, ok := hc.Transport.(*http.Transport)
	if !ok || tr.Proxy == nil {
		t.Fatal("proxied client transport has no Proxy func")
	}
}

func TestProxyContext_EmptyIsNoop(t *testing.T) {
	ctx, err := withProxy(context.Background(), "")
	if err != nil {
		t.Fatalf("withProxy(\"\"): %v", err)
	}
	if ctx.Value(oauth2.HTTPClient) != nil {
		t.Fatal("empty proxy should not set oauth2.HTTPClient")
	}
}

func TestProxyContext_InvalidURL(t *testing.T) {
	if _, err := withProxy(context.Background(), "://not a url"); err == nil {
		t.Fatal("expected error on invalid proxy URL")
	}
}

func TestAuthProbe_SucceedsOn200(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !strings.HasSuffix(r.URL.Path, "/oauth2/token") {
			http.Error(w, "unexpected path", http.StatusNotFound)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"access_token":"tok","token_type":"bearer","expires_in":1799}`))
	}))
	defer srv.Close()

	err := authProbe(context.Background(), authProbeConfig{
		ClientID: "id", ClientSecret: "secret",
		TokenURL:   srv.URL + "/oauth2/token",
		HTTPClient: srv.Client(),
	})
	if err != nil {
		t.Fatalf("authProbe on 200: %v", err)
	}
}

func TestAuthProbe_FailsOn401(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, `{"error":"invalid_client"}`, http.StatusUnauthorized)
	}))
	defer srv.Close()

	err := authProbe(context.Background(), authProbeConfig{
		ClientID: "id", ClientSecret: "bad",
		TokenURL:   srv.URL + "/oauth2/token",
		HTTPClient: srv.Client(),
	})
	if err == nil {
		t.Fatal("authProbe should fail on 401")
	}
}
