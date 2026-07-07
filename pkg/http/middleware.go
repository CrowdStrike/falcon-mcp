package http

import (
	"crypto/subtle"
	"log/slog"
	"net/http"
	"strings"
)

// stripTrailingSlash removes a trailing slash from request paths (except "/"),
// porting the Python strip_trailing_slash_middleware. Some MCP clients append a
// slash that the SDK's route matching does not expect.
func stripTrailingSlash(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" && strings.HasSuffix(r.URL.Path, "/") {
			r.URL.Path = strings.TrimRight(r.URL.Path, "/")
			if r.URL.RawPath != "" {
				r.URL.RawPath = strings.TrimRight(r.URL.RawPath, "/")
			}
		}
		next.ServeHTTP(w, r)
	})
}

// normalizeContentType rewrites an "application/json-rpc" Content-Type to
// "application/json" (preserving any parameters like "; charset=utf-8"),
// porting the Python normalize_content_type_middleware. Some clients send the
// non-standard json-rpc media type, which the SDK rejects.
func normalizeContentType(next http.Handler) http.Handler {
	const jsonRPC = "application/json-rpc"
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if ct := r.Header.Get("Content-Type"); ct != "" {
			if strings.HasPrefix(strings.ToLower(ct), jsonRPC) {
				newCT := "application/json" + ct[len(jsonRPC):]
				slog.Debug("normalized Content-Type", "from", ct, "to", newCT)
				r.Header.Set("Content-Type", newCT)
			}
		}
		next.ServeHTTP(w, r)
	})
}

// apiKeyAuth validates the x-api-key header against apiKey using a
// constant-time comparison, porting the Python auth_middleware. When apiKey is
// empty, authentication is disabled (the middleware is a passthrough). Health
// probes are exempt so orchestrators can reach them without the key.
func apiKeyAuth(next http.Handler, apiKey string) http.Handler {
	if apiKey == "" {
		return next
	}
	expected := []byte(apiKey)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/healthz" || r.URL.Path == "/readyz" {
			next.ServeHTTP(w, r)
			return
		}
		provided := []byte(r.Header.Get("x-api-key"))
		if subtle.ConstantTimeCompare(provided, expected) != 1 {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusUnauthorized)
			_, _ = w.Write([]byte(`{"error": "Unauthorized"}`))
			return
		}
		next.ServeHTTP(w, r)
	})
}
