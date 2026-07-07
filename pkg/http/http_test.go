package http

import (
	"context"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
)

// testChain builds the same middleware+mux composition Serve uses, but returns
// the handler for direct httptest exercising (no real listener).
func testChain(apiKey string, ready func(context.Context) error) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})
	mux.HandleFunc("/readyz", func(w http.ResponseWriter, r *http.Request) {
		if ready != nil {
			if err := ready(r.Context()); err != nil {
				http.Error(w, "not ready", http.StatusServiceUnavailable)
				return
			}
		}
		w.WriteHeader(http.StatusOK)
	})
	mux.HandleFunc("/mcp", func(w http.ResponseWriter, r *http.Request) {
		// Echo the normalized content-type so the test can assert it.
		_, _ = io.WriteString(w, r.Header.Get("Content-Type"))
	})
	return stripTrailingSlash(normalizeContentType(apiKeyAuth(mux, apiKey)))
}

func TestHealthz(t *testing.T) {
	srv := httptest.NewServer(testChain("", nil))
	defer srv.Close()
	resp, err := http.Get(srv.URL + "/healthz")
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		t.Errorf("healthz = %d, want 200", resp.StatusCode)
	}
}

func TestReadyz(t *testing.T) {
	// Ready succeeds.
	srv := httptest.NewServer(testChain("", func(context.Context) error { return nil }))
	defer srv.Close()
	resp, _ := http.Get(srv.URL + "/readyz")
	if resp.StatusCode != http.StatusOK {
		t.Errorf("readyz(ok) = %d, want 200", resp.StatusCode)
	}

	// Ready fails.
	srv2 := httptest.NewServer(testChain("", func(context.Context) error { return errors.New("no token") }))
	defer srv2.Close()
	resp2, _ := http.Get(srv2.URL + "/readyz")
	if resp2.StatusCode != http.StatusServiceUnavailable {
		t.Errorf("readyz(fail) = %d, want 503", resp2.StatusCode)
	}
}

func TestAPIKeyAuth(t *testing.T) {
	srv := httptest.NewServer(testChain("secret", nil))
	defer srv.Close()

	// No key → 401.
	resp, _ := http.Get(srv.URL + "/mcp")
	if resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("no key = %d, want 401", resp.StatusCode)
	}

	// Correct key → 200.
	req, _ := http.NewRequest(http.MethodGet, srv.URL+"/mcp", nil)
	req.Header.Set("x-api-key", "secret")
	resp2, _ := http.DefaultClient.Do(req)
	if resp2.StatusCode != http.StatusOK {
		t.Errorf("correct key = %d, want 200", resp2.StatusCode)
	}

	// Health endpoints exempt from auth.
	resp3, _ := http.Get(srv.URL + "/healthz")
	if resp3.StatusCode != http.StatusOK {
		t.Errorf("healthz with auth enabled = %d, want 200 (exempt)", resp3.StatusCode)
	}
}

func TestNormalizeContentType(t *testing.T) {
	srv := httptest.NewServer(testChain("", nil))
	defer srv.Close()
	req, _ := http.NewRequest(http.MethodPost, srv.URL+"/mcp", nil)
	req.Header.Set("Content-Type", "application/json-rpc; charset=utf-8")
	resp, _ := http.DefaultClient.Do(req)
	body, _ := io.ReadAll(resp.Body)
	if got := string(body); got != "application/json; charset=utf-8" {
		t.Errorf("normalized CT = %q, want application/json; charset=utf-8", got)
	}
}

func TestStripTrailingSlash(t *testing.T) {
	srv := httptest.NewServer(testChain("", nil))
	defer srv.Close()
	// /healthz/ should route to /healthz.
	resp, _ := http.Get(srv.URL + "/healthz/")
	if resp.StatusCode != http.StatusOK {
		t.Errorf("healthz/ = %d, want 200 (slash stripped)", resp.StatusCode)
	}
}
