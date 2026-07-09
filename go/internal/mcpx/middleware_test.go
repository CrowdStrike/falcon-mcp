package mcpx

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

// echoHandler records the path and content-type it received so middleware
// effects can be asserted, and returns 200.
func echoHandler(gotPath, gotCT *string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		*gotPath = r.URL.Path
		*gotCT = r.Header.Get("Content-Type")
		w.WriteHeader(http.StatusOK)
	})
}

func TestAuthMiddleware(t *testing.T) {
	tests := []struct {
		name     string
		apiKey   string
		provided string
		wantCode int
	}{
		{"no key configured passes through", "", "", http.StatusOK},
		{"no key configured ignores header", "", "whatever", http.StatusOK},
		{"correct key passes", "secret", "secret", http.StatusOK},
		{"wrong key rejected", "secret", "nope", http.StatusUnauthorized},
		{"missing key rejected", "secret", "", http.StatusUnauthorized},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var path, ct string
			h := WrapHTTP(echoHandler(&path, &ct), HTTPMiddleware{APIKey: tt.apiKey})
			req := httptest.NewRequest(http.MethodPost, "/mcp", nil)
			if tt.provided != "" {
				req.Header.Set("x-api-key", tt.provided)
			}
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if rec.Code != tt.wantCode {
				t.Fatalf("code = %d, want %d", rec.Code, tt.wantCode)
			}
		})
	}
}

func TestContentTypeNormalize(t *testing.T) {
	tests := []struct {
		in   string
		want string
	}{
		{"application/json-rpc", "application/json"},
		{"application/json-rpc; charset=utf-8", "application/json; charset=utf-8"},
		{"application/json", "application/json"},
		{"text/plain", "text/plain"},
		{"", ""},
	}
	for _, tt := range tests {
		t.Run(tt.in, func(t *testing.T) {
			var path, ct string
			h := WrapHTTP(echoHandler(&path, &ct), HTTPMiddleware{})
			req := httptest.NewRequest(http.MethodPost, "/mcp", nil)
			if tt.in != "" {
				req.Header.Set("Content-Type", tt.in)
			}
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if ct != tt.want {
				t.Fatalf("Content-Type seen by handler = %q, want %q", ct, tt.want)
			}
		})
	}
}

func TestTrailingSlashStrip(t *testing.T) {
	tests := []struct {
		in   string
		want string
	}{
		{"/mcp/", "/mcp"},
		{"/mcp", "/mcp"},
		{"/", "/"},
		{"/a/b/", "/a/b"},
	}
	for _, tt := range tests {
		t.Run(tt.in, func(t *testing.T) {
			var path, ct string
			h := WrapHTTP(echoHandler(&path, &ct), HTTPMiddleware{})
			req := httptest.NewRequest(http.MethodPost, tt.in, nil)
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if path != tt.want {
				t.Fatalf("path seen by handler = %q, want %q", path, tt.want)
			}
		})
	}
}

// TestAuthRejectsBeforeHandler proves a bad key never reaches the wrapped
// handler (no side effects on reject).
func TestAuthRejectsBeforeHandler(t *testing.T) {
	reached := false
	h := WrapHTTP(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		reached = true
	}), HTTPMiddleware{APIKey: "secret"})
	req := httptest.NewRequest(http.MethodPost, "/mcp", nil)
	req.Header.Set("x-api-key", "wrong")
	h.ServeHTTP(httptest.NewRecorder(), req)
	if reached {
		t.Fatal("handler was reached despite failed auth")
	}
}
