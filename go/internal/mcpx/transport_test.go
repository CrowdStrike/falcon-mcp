package mcpx

import (
	"context"
	"encoding/json"
	"errors"
	"net"
	"net/http"
	"sync"
	"testing"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp/internal/toolsets"
)

var errConcurrentCall = errors.New("concurrent tool call returned IsError")

// serveHTTP starts the given transport runner on a random loopback port and
// returns the base URL, cancelling and waiting for shutdown via t.Cleanup.
func serveHTTP(t *testing.T, run func(ctx context.Context, addr string, srv *mcp.Server) error) string {
	t.Helper()
	srv := NewServer("test-version")
	Register(srv, []*toolsets.Toolset{testToolset()})

	// Bind a random port first so the test knows the address before serving.
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("listen: %v", err)
	}
	addr := ln.Addr().String()
	_ = ln.Close()

	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() { done <- run(ctx, addr, srv) }()
	t.Cleanup(func() {
		cancel()
		select {
		case <-done:
		case <-time.After(5 * time.Second):
			t.Error("transport did not shut down within 5s")
		}
	})

	// Wait for the listener to accept connections.
	deadline := time.Now().Add(3 * time.Second)
	for time.Now().Before(deadline) {
		c, err := net.Dial("tcp", addr)
		if err == nil {
			_ = c.Close()
			return "http://" + addr
		}
		time.Sleep(10 * time.Millisecond)
	}
	t.Fatalf("server never became reachable at %s", addr)
	return ""
}

func TestRunStreamableHTTP_ServesMCP(t *testing.T) {
	base := serveHTTP(t, func(ctx context.Context, addr string, srv *mcp.Server) error {
		return RunStreamableHTTP(ctx, HTTPConfig{Addr: addr}, srv)
	})

	ctx := context.Background()
	client := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil)
	cs, err := client.Connect(ctx, &mcp.StreamableClientTransport{Endpoint: base}, nil)
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })

	res, err := cs.CallTool(ctx, &mcp.CallToolParams{
		Name:      "falcon_search_hosts",
		Arguments: map[string]any{"filter": "x"},
	})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	tc, ok := res.Content[0].(*mcp.TextContent)
	if !ok {
		t.Fatalf("content is %T", res.Content[0])
	}
	var payload []map[string]any
	if err := json.Unmarshal([]byte(tc.Text), &payload); err != nil {
		t.Fatalf("bad payload: %v", err)
	}
	if payload[0]["device_id"] != "abc" {
		t.Fatalf("unexpected payload: %v", payload)
	}
}

func TestRunSSE_ServesMCP(t *testing.T) {
	base := serveHTTP(t, func(ctx context.Context, addr string, srv *mcp.Server) error {
		return RunSSE(ctx, HTTPConfig{Addr: addr}, srv)
	})

	ctx := context.Background()
	client := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil)
	cs, err := client.Connect(ctx, &mcp.SSEClientTransport{Endpoint: base}, nil)
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	t.Cleanup(func() { _ = cs.Close() })

	tools, err := cs.ListTools(ctx, nil)
	if err != nil {
		t.Fatalf("ListTools: %v", err)
	}
	var found bool
	for _, tl := range tools.Tools {
		if tl.Name == "falcon_search_hosts" {
			found = true
		}
	}
	if !found {
		t.Fatal("falcon_search_hosts not served over SSE")
	}
}

func TestRunStreamableHTTP_MiddlewareRejectsBadAPIKey(t *testing.T) {
	base := serveHTTP(t, func(ctx context.Context, addr string, srv *mcp.Server) error {
		mw := HTTPMiddleware{APIKey: "secret"}
		return RunStreamableHTTP(ctx, HTTPConfig{
			Addr:    addr,
			Handler: func(h http.Handler) http.Handler { return WrapHTTP(h, mw) },
		}, srv)
	})

	// A raw POST without the key must be rejected 401 before reaching MCP.
	resp, err := http.Post(base, "application/json", nil)
	if err != nil {
		t.Fatalf("post: %v", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusUnauthorized {
		t.Fatalf("status = %d, want 401", resp.StatusCode)
	}
}

// TestRunStreamableHTTP_ConcurrentToolCalls drives many tool calls in parallel
// through the streamable-http server (which serves requests concurrently),
// proving the shared server and its handlers are safe under load (R6). Run under
// -race to catch data races across the concurrent request path.
func TestRunStreamableHTTP_ConcurrentToolCalls(t *testing.T) {
	base := serveHTTP(t, func(ctx context.Context, addr string, srv *mcp.Server) error {
		return RunStreamableHTTP(ctx, HTTPConfig{Addr: addr}, srv)
	})

	const clients = 16
	var wg sync.WaitGroup
	wg.Add(clients)
	errs := make(chan error, clients)
	for range clients {
		go func() {
			defer wg.Done()
			ctx := context.Background()
			cl := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil)
			cs, err := cl.Connect(ctx, &mcp.StreamableClientTransport{Endpoint: base}, nil)
			if err != nil {
				errs <- err
				return
			}
			defer cs.Close()
			res, err := cs.CallTool(ctx, &mcp.CallToolParams{
				Name:      "falcon_search_hosts",
				Arguments: map[string]any{"filter": "x"},
			})
			if err != nil {
				errs <- err
				return
			}
			if res.IsError {
				errs <- errConcurrentCall
			}
		}()
	}
	wg.Wait()
	close(errs)
	for err := range errs {
		t.Fatalf("concurrent tool call failed: %v", err)
	}
}

func TestRunStreamableHTTP_GracefulShutdownOnContextCancel(t *testing.T) {
	srv := NewServer("test-version")
	Register(srv, []*toolsets.Toolset{testToolset()})

	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("listen: %v", err)
	}
	addr := ln.Addr().String()
	_ = ln.Close()

	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() { done <- RunStreamableHTTP(ctx, HTTPConfig{Addr: addr}, srv) }()

	// Let it start, then cancel and expect a clean (nil) return.
	time.Sleep(100 * time.Millisecond)
	cancel()
	select {
	case err := <-done:
		if err != nil && err != http.ErrServerClosed {
			t.Fatalf("shutdown returned %v, want nil/ErrServerClosed", err)
		}
	case <-time.After(5 * time.Second):
		t.Fatal("server did not shut down after context cancel")
	}
}
