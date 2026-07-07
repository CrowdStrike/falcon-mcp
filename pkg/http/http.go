// Package http hosts the Falcon MCP server over HTTP transports
// (streamable-http and sse), wrapping the MCP SDK's streamable handler with the
// three ported middlewares (strip-trailing-slash, content-type normalization,
// optional x-api-key auth) plus /healthz and /readyz probes and graceful
// shutdown.
package http

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
)

// Options configures the HTTP server.
type Options struct {
	Addr      string // host:port to listen on
	APIKey    string // optional x-api-key; empty disables auth
	Stateless bool   // MCP stateless mode for horizontal scaling
	SSE       bool   // serve the SSE transport instead of streamable-http
	// Ready probes Falcon token reachability for /readyz. It should be cheap
	// and must not block indefinitely.
	Ready func(ctx context.Context) error
	// MultiTenant, when true, wraps the handler with requireTLSMiddleware so
	// credential-bearing requests over plaintext are rejected with a clear 400.
	MultiTenant bool
}

// Serve builds and runs the HTTP server until ctx is cancelled, then shuts down
// gracefully (10s timeout). getServer returns the MCP server bound to a request
// — the multi-tenancy hook. For single-tenant mode it returns the same server
// for every request.
func Serve(ctx context.Context, getServer func(*http.Request) *mcp.Server, opts Options) error {
	mux := http.NewServeMux()

	// Health probes: plain HTTP, no OAuth, registered before the MCP handler.
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})
	mux.HandleFunc("/readyz", func(w http.ResponseWriter, r *http.Request) {
		if opts.Ready != nil {
			rctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
			defer cancel()
			if err := opts.Ready(rctx); err != nil {
				http.Error(w, "not ready: "+err.Error(), http.StatusServiceUnavailable)
				return
			}
		}
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ready"))
	})

	// The MCP transport handler.
	var mcpHandler http.Handler
	if opts.SSE {
		mcpHandler = mcp.NewSSEHandler(func(r *http.Request) *mcp.Server { return getServer(r) }, nil)
	} else {
		mcpHandler = mcp.NewStreamableHTTPHandler(
			func(r *http.Request) *mcp.Server { return getServer(r) },
			&mcp.StreamableHTTPOptions{Stateless: opts.Stateless},
		)
	}
	mux.Handle("/", mcpHandler)

	// Compose middleware (outermost first): strip slash → normalize CT →
	// [require-TLS for multi-tenant] → auth.
	var chain http.Handler = mux
	chain = apiKeyAuth(chain, opts.APIKey)
	if opts.MultiTenant {
		chain = requireTLSMiddleware(chain)
	}
	handler := stripTrailingSlash(normalizeContentType(chain))

	srv := &http.Server{
		Addr:              opts.Addr,
		Handler:           handler,
		ReadHeaderTimeout: 10 * time.Second,
	}

	errCh := make(chan error, 1)
	go func() {
		slog.Info("HTTP server listening", "addr", opts.Addr, "sse", opts.SSE, "stateless", opts.Stateless)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- err
		}
	}()

	select {
	case <-ctx.Done():
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		slog.Info("shutting down HTTP server")
		return srv.Shutdown(shutdownCtx)
	case err := <-errCh:
		return fmt.Errorf("HTTP server error: %w", err)
	}
}

// SingleTenantReady returns a /readyz probe that checks the given client's
// Falcon token reachability.
func SingleTenantReady(fc *falcon.FalconClient) func(context.Context) error {
	return fc.Connectivity
}
