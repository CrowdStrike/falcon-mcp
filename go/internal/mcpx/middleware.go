package mcpx

import (
	"crypto/subtle"
	"log/slog"
	"net/http"
	"strings"
)

// HTTPMiddleware configures the net/http middleware applied to the HTTP-based
// transports. Its zero value applies content-type normalization, trailing-slash
// stripping, and request logging but no authentication.
type HTTPMiddleware struct {
	// APIKey, when non-empty, requires a matching x-api-key header; requests
	// without it are rejected with 401 before reaching the handler.
	APIKey string
}

// WrapHTTP wraps h with the configured middleware. The layers run
// outermost-first: logging, then auth, then content-type normalization, then
// trailing-slash stripping, then the handler. This mirrors the Python server's
// composition while ensuring rejected requests are still logged.
func (m HTTPMiddleware) wrap(h http.Handler) http.Handler {
	h = stripTrailingSlash(h)
	h = normalizeContentType(h)
	if m.APIKey != "" {
		h = requireAPIKey(h, m.APIKey)
	}
	h = logRequests(h)
	return h
}

// WrapHTTP applies the configured middleware to h. It is the exported entry
// point used when wiring the HTTP transports.
func WrapHTTP(h http.Handler, m HTTPMiddleware) http.Handler {
	return m.wrap(h)
}

// requireAPIKey rejects requests whose x-api-key header does not match key,
// comparing in constant time to avoid leaking the key via timing.
func requireAPIKey(next http.Handler, key string) http.Handler {
	want := []byte(key)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		got := []byte(r.Header.Get("x-api-key"))
		if subtle.ConstantTimeCompare(got, want) != 1 {
			http.Error(w, `{"error":"Unauthorized"}`, http.StatusUnauthorized)
			return
		}
		next.ServeHTTP(w, r)
	})
}

// normalizeContentType rewrites an application/json-rpc content type to
// application/json, preserving any parameters (e.g. "; charset=utf-8"). Some
// clients send the json-rpc media type, which the MCP handler does not accept.
func normalizeContentType(next http.Handler) http.Handler {
	const jsonRPC = "application/json-rpc"
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if ct := r.Header.Get("Content-Type"); strings.HasPrefix(strings.ToLower(ct), jsonRPC) {
			r.Header.Set("Content-Type", "application/json"+ct[len(jsonRPC):])
		}
		next.ServeHTTP(w, r)
	})
}

// stripTrailingSlash removes a trailing slash from the request path (except for
// the root "/") so routes match regardless of a trailing slash.
func stripTrailingSlash(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if p := r.URL.Path; p != "/" && strings.HasSuffix(p, "/") {
			r.URL.Path = strings.TrimRight(p, "/")
			if r.URL.RawPath != "" {
				r.URL.RawPath = strings.TrimRight(r.URL.RawPath, "/")
			}
		}
		next.ServeHTTP(w, r)
	})
}

// logRequests emits a debug log line per request via the default slog logger.
func logRequests(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		slog.Debug("http request", "method", r.Method, "path", r.URL.Path, "remote", r.RemoteAddr)
		next.ServeHTTP(w, r)
	})
}
