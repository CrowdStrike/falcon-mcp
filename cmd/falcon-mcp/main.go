// Command falcon-mcp is the CrowdStrike Falcon MCP server. It exposes the
// Falcon platform to MCP clients over stdio, SSE, or streamable-HTTP transports.
package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/config"
	"github.com/crowdstrike/falcon-mcp-go/internal/dotenv"
	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/internal/logging"
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

	srv, toolCount, resourceCount, err := server.Build(fc, server.Options{
		Enabled: cfg.Modules,
		Dynamic: cfg.Dynamic,
	})
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
		// HTTP transports are wired in Phase 2 (pkg/http).
		return fmt.Errorf("transport %q not yet implemented", cfg.Transport)
	default:
		return fmt.Errorf("unknown transport %q", cfg.Transport)
	}
}
