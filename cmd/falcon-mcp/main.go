// Command falcon-mcp is the CrowdStrike Falcon MCP server. It exposes the
// Falcon platform to MCP clients over stdio, SSE, or streamable-HTTP transports.
package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/config"
	"github.com/crowdstrike/falcon-mcp-go/internal/dotenv"
	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/logging"
	falconhttp "github.com/crowdstrike/falcon-mcp-go/pkg/http"
	"github.com/crowdstrike/falcon-mcp-go/pkg/server"
	"github.com/crowdstrike/falcon-mcp-go/pkg/version"

	// Blank-import every toolset so its init() registers it with the registry.
	// (Toolset packages are added in later phases.)
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/all"
)

func main() {
	dotenv.Load()

	cfg, showVersion, err := config.Load(os.Args[1:])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	if showVersion {
		fmt.Printf("falcon-mcp %s\n", version.String())
		return
	}

	logging.Configure(cfg.Debug)
	slog.Info("Initializing Falcon MCP Server", "version", version.String())

	if err := run(cfg); err != nil {
		slog.Error("fatal", "err", err)
		os.Exit(1)
	}
}

func run(cfg *config.Config) error {
	// Root context cancelled on SIGINT/SIGTERM for graceful shutdown.
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	buildServer := func(fc *falcon.FalconClient) (*mcp.Server, error) {
		srv, _, _, err := server.Build(fc, server.Options{Enabled: cfg.Modules, Dynamic: cfg.Dynamic})
		return srv, err
	}

	// Multi-tenant mode: no process-wide credentials; each request supplies its
	// own via headers, served from an LRU+TTL client pool. Only valid for HTTP
	// transports.
	if cfg.MultiTenant {
		if cfg.Transport == "stdio" {
			return fmt.Errorf("--multi-tenant requires an HTTP transport (streamable-http or sse), not stdio")
		}
		pool := falcon.NewPool(falcon.PoolOptions{Debug: cfg.Debug, UserAgentComment: cfg.UserAgentComment})
		getServer := falconhttp.MultiTenantServerFunc(pool, buildServer, true /* requireTLS */)
		slog.Info("Falcon MCP ready (multi-tenant)",
			"version", version.String(), "transport", cfg.Transport, "dynamic", cfg.Dynamic)
		return falconhttp.Serve(ctx, getServer, falconhttp.Options{
			Addr:        fmt.Sprintf("%s:%d", cfg.Host, cfg.Port),
			APIKey:      cfg.APIKey,
			Stateless:   cfg.StatelessHTTP,
			SSE:         cfg.Transport == "sse",
			MultiTenant: true,
			// No readiness probe against a specific tenant; liveness only.
		})
	}

	// Single-tenant: one shared, thread-safe client from env/flags.
	fc, err := falcon.NewClient(ctx, falcon.Credentials{
		ClientID:     cfg.ClientID,
		ClientSecret: cfg.ClientSecret,
		BaseURL:      cfg.BaseURL,
		MemberCID:    cfg.MemberCID,
		ProxyURL:     cfg.ProxyURL,
	}, cfg.Debug, cfg.UserAgentComment)
	if err != nil {
		return err
	}

	// Verify credentials up front (matches the Python startup auth check).
	if err := fc.Connectivity(ctx); err != nil {
		return fmt.Errorf("failed to authenticate with the Falcon API: %w", err)
	}

	srv, toolCount, resourceCount, err := buildServerWithCounts(fc, cfg)
	if err != nil {
		return err
	}
	slog.Info("Falcon MCP ready",
		"version", version.String(),
		"tools", toolCount,
		"resources", resourceCount,
		"transport", cfg.Transport,
		"dynamic", cfg.Dynamic,
	)

	switch cfg.Transport {
	case "stdio":
		return srv.Run(ctx, &mcp.StdioTransport{})
	case "streamable-http", "sse":
		return falconhttp.Serve(ctx, func(*http.Request) *mcp.Server { return srv }, falconhttp.Options{
			Addr:      fmt.Sprintf("%s:%d", cfg.Host, cfg.Port),
			APIKey:    cfg.APIKey,
			Stateless: cfg.StatelessHTTP,
			SSE:       cfg.Transport == "sse",
			Ready:     falconhttp.SingleTenantReady(fc),
		})
	default:
		return fmt.Errorf("unknown transport %q", cfg.Transport)
	}
}

// buildServerWithCounts builds the server and returns tool/resource counts for
// the startup log line.
func buildServerWithCounts(fc *falcon.FalconClient, cfg *config.Config) (*mcp.Server, int, int, error) {
	return server.Build(fc, server.Options{Enabled: cfg.Modules, Dynamic: cfg.Dynamic})
}
