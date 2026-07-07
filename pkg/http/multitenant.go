package http

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
)

// Credential header names for multi-tenant mode. Per-request Falcon API
// credentials are supplied via these headers (best practice: only over TLS).
const (
	headerClientID     = "X-Falcon-Client-Id"
	headerClientSecret = "X-Falcon-Client-Secret"
	headerMemberCID    = "X-Falcon-Member-Cid"
	headerBaseURL      = "X-Falcon-Base-Url"
)

// credentialsFromRequest extracts per-request Falcon credentials from the
// X-Falcon-* headers. It returns ok=false if the required client id/secret are
// absent. It never logs secret values.
func credentialsFromRequest(r *http.Request) (falcon.Credentials, bool) {
	id := strings.TrimSpace(r.Header.Get(headerClientID))
	secret := strings.TrimSpace(r.Header.Get(headerClientSecret))
	if id == "" || secret == "" {
		return falcon.Credentials{}, false
	}
	return falcon.Credentials{
		ClientID:     id,
		ClientSecret: secret,
		MemberCID:    strings.TrimSpace(r.Header.Get(headerMemberCID)),
		BaseURL:      strings.TrimSpace(r.Header.Get(headerBaseURL)),
	}, true
}

// MultiTenantServerFunc returns a getServer callback for
// mcp.NewStreamableHTTPHandler that builds a per-request MCP server bound to the
// credentials supplied in the request headers, reusing cached clients from pool.
//
// buildServer constructs the MCP server for a given client (typically a closure
// over server.Build with the enabled modules + dynamic flag). requireTLS, when
// true, rejects credential-bearing requests that did not arrive over TLS
// (either a direct TLS connection or X-Forwarded-Proto: https), since sending
// API secrets in cleartext is unsafe.
func MultiTenantServerFunc(
	pool *falcon.Pool,
	buildServer func(fc *falcon.FalconClient) (*mcp.Server, error),
	requireTLS bool,
) func(*http.Request) *mcp.Server {
	return func(r *http.Request) *mcp.Server {
		if requireTLS && !isTLS(r) {
			// getServer returning nil yields a 400; the client should retry over
			// HTTPS. We cannot write a custom body from here.
			return nil
		}
		creds, ok := credentialsFromRequest(r)
		if !ok {
			return nil
		}
		fc, err := pool.Get(r.Context(), creds)
		if err != nil {
			return nil
		}
		srv, err := buildServer(fc)
		if err != nil {
			return nil
		}
		return srv
	}
}

// isTLS reports whether the request arrived over a secure transport, either
// directly (r.TLS set) or via a trusted proxy (X-Forwarded-Proto: https).
func isTLS(r *http.Request) bool {
	if r.TLS != nil {
		return true
	}
	return strings.EqualFold(r.Header.Get("X-Forwarded-Proto"), "https")
}

// requireTLSMiddleware rejects credential-bearing requests that are not over
// TLS with a clear 400 (getServer's nil-return path yields a bare 400 with no
// body). Health probes are exempt. This wraps the handler so the client gets an
// actionable error rather than a generic bad-request.
func requireTLSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/healthz" || r.URL.Path == "/readyz" {
			next.ServeHTTP(w, r)
			return
		}
		hasCreds := r.Header.Get(headerClientID) != "" || r.Header.Get(headerClientSecret) != ""
		if hasCreds && !isTLS(r) {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusBadRequest)
			_, _ = fmt.Fprint(w, `{"error": "Falcon credentials must be sent over TLS (HTTPS)"}`)
			return
		}
		next.ServeHTTP(w, r)
	})
}
