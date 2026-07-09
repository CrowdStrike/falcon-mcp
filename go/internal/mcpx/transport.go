package mcpx

import (
	"context"
	"errors"
	"net/http"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// RunStdio serves the MCP server over stdio, blocking until the context is
// canceled or the transport closes. stdio requires that no diagnostic output
// goes to stdout; logging is configured to stderr elsewhere.
func RunStdio(ctx context.Context, srv *mcp.Server) error {
	return srv.Run(ctx, &mcp.StdioTransport{})
}

// HTTPConfig holds the settings for the HTTP-based transports.
type HTTPConfig struct {
	// Addr is the host:port to bind, e.g. "127.0.0.1:8000".
	Addr string
	// Stateless maps to StreamableHTTPOptions.Stateless; ignored by SSE.
	Stateless bool
	// Handler, when set, wraps the MCP handler (used for auth/logging middleware).
	Handler func(http.Handler) http.Handler
}

// RunStreamableHTTP serves the MCP server over the streamable-http transport on
// cfg.Addr, blocking until ctx is canceled. The single shared server is reused
// across requests via the getServer closure; cfg.Stateless toggles stateless
// mode on the handler. Shutdown is graceful on context cancellation.
func RunStreamableHTTP(ctx context.Context, cfg HTTPConfig, srv *mcp.Server) error {
	handler := mcp.NewStreamableHTTPHandler(
		func(*http.Request) *mcp.Server { return srv },
		&mcp.StreamableHTTPOptions{Stateless: cfg.Stateless},
	)
	return serve(ctx, cfg, handler)
}

// RunSSE serves the MCP server over the legacy SSE transport on cfg.Addr,
// blocking until ctx is canceled. The single shared server is reused across
// requests. Shutdown is graceful on context cancellation.
func RunSSE(ctx context.Context, cfg HTTPConfig, srv *mcp.Server) error {
	handler := mcp.NewSSEHandler(func(*http.Request) *mcp.Server { return srv }, nil)
	return serve(ctx, cfg, handler)
}

// readHeaderTimeout bounds how long a client may take to send request headers,
// preventing a slow-client (Slowloris) connection from tying up a server
// goroutine indefinitely. Bodies and SSE streams are unbounded by design.
const readHeaderTimeout = 10 * time.Second

// serve runs an http.Server with the given handler (optionally wrapped by
// cfg.Handler middleware) and shuts it down gracefully when ctx is canceled.
func serve(ctx context.Context, cfg HTTPConfig, h http.Handler) error {
	if cfg.Handler != nil {
		h = cfg.Handler(h)
	}
	hs := &http.Server{
		Addr:              cfg.Addr,
		Handler:           h,
		ReadHeaderTimeout: readHeaderTimeout,
	}

	errc := make(chan error, 1)
	go func() { errc <- hs.ListenAndServe() }()

	select {
	case <-ctx.Done():
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		return hs.Shutdown(shutdownCtx)
	case err := <-errc:
		if errors.Is(err, http.ErrServerClosed) {
			return nil
		}
		return err
	}
}
