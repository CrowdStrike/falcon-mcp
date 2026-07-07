package http

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
)

func TestCredentialsFromRequest(t *testing.T) {
	r := httptest.NewRequest(http.MethodPost, "/mcp", nil)
	r.Header.Set(headerClientID, "cid")
	r.Header.Set(headerClientSecret, "csecret")
	r.Header.Set(headerMemberCID, "member1")
	creds, ok := credentialsFromRequest(r)
	if !ok {
		t.Fatal("expected credentials to be extracted")
	}
	if creds.ClientID != "cid" || creds.ClientSecret != "csecret" || creds.MemberCID != "member1" {
		t.Errorf("wrong credentials: %+v", creds)
	}

	// Missing secret → not ok.
	r2 := httptest.NewRequest(http.MethodPost, "/mcp", nil)
	r2.Header.Set(headerClientID, "cid")
	if _, ok := credentialsFromRequest(r2); ok {
		t.Error("expected ok=false when secret is missing")
	}
}

func TestMultiTenantServerFuncBuildsPerTenant(t *testing.T) {
	pool := falcon.NewPool(falcon.PoolOptions{Salt: []byte("s")})
	built := map[*falcon.FalconClient]bool{}
	getServer := MultiTenantServerFunc(pool, func(fc *falcon.FalconClient) (*mcp.Server, error) {
		built[fc] = true
		return mcp.NewServer(&mcp.Implementation{Name: "t", Version: "0"}, nil), nil
	}, false /* requireTLS off for this unit test */)

	req := func(id string) *http.Request {
		r := httptest.NewRequest(http.MethodPost, "/mcp", nil)
		r.Header.Set(headerClientID, id)
		r.Header.Set(headerClientSecret, "secret-"+id)
		r.Header.Set(headerBaseURL, "https://api.us-2.crowdstrike.com")
		return r.WithContext(context.Background())
	}

	if s := getServer(req("tenant-a")); s == nil {
		t.Fatal("expected a server for tenant-a")
	}
	if s := getServer(req("tenant-b")); s == nil {
		t.Fatal("expected a server for tenant-b")
	}
	// Two distinct tenants → two distinct clients built.
	if len(built) != 2 {
		t.Errorf("expected 2 distinct clients built, got %d", len(built))
	}

	// Missing credentials → nil (yields 400 at the transport layer).
	noCreds := httptest.NewRequest(http.MethodPost, "/mcp", nil)
	if s := getServer(noCreds.WithContext(context.Background())); s != nil {
		t.Error("expected nil server when credentials are absent")
	}
}

func TestMultiTenantRequiresTLS(t *testing.T) {
	pool := falcon.NewPool(falcon.PoolOptions{Salt: []byte("s")})
	getServer := MultiTenantServerFunc(pool, func(fc *falcon.FalconClient) (*mcp.Server, error) {
		return mcp.NewServer(&mcp.Implementation{Name: "t", Version: "0"}, nil), nil
	}, true /* requireTLS */)

	// Plaintext request with credentials → rejected (nil server).
	plain := httptest.NewRequest(http.MethodPost, "/mcp", nil)
	plain.Header.Set(headerClientID, "cid")
	plain.Header.Set(headerClientSecret, "csecret")
	if s := getServer(plain.WithContext(context.Background())); s != nil {
		t.Error("expected nil server for plaintext credential request under requireTLS")
	}

	// X-Forwarded-Proto: https satisfies the TLS requirement (proxy TLS termination).
	fwd := httptest.NewRequest(http.MethodPost, "/mcp", nil)
	fwd.Header.Set(headerClientID, "cid")
	fwd.Header.Set(headerClientSecret, "csecret")
	fwd.Header.Set(headerBaseURL, "https://api.us-2.crowdstrike.com")
	fwd.Header.Set("X-Forwarded-Proto", "https")
	if s := getServer(fwd.WithContext(context.Background())); s == nil {
		t.Error("expected a server when X-Forwarded-Proto is https")
	}
}

func TestRequireTLSMiddleware(t *testing.T) {
	next := http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(http.StatusOK) })
	h := requireTLSMiddleware(next)

	// Plaintext + credentials → 400.
	rec := httptest.NewRecorder()
	r := httptest.NewRequest(http.MethodPost, "/mcp", nil)
	r.Header.Set(headerClientID, "cid")
	h.ServeHTTP(rec, r)
	if rec.Code != http.StatusBadRequest {
		t.Errorf("plaintext creds = %d, want 400", rec.Code)
	}

	// Health probe exempt even without TLS.
	rec2 := httptest.NewRecorder()
	h.ServeHTTP(rec2, httptest.NewRequest(http.MethodGet, "/healthz", nil))
	if rec2.Code != http.StatusOK {
		t.Errorf("healthz = %d, want 200 (exempt)", rec2.Code)
	}
}
