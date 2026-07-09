// Package cli wires the cobra command, flag/environment binding, and server
// startup for falcon-mcp.
package cli

import (
	"context"
	"fmt"
	"io"
	"log/slog"
	"net"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"

	"github.com/spf13/cobra"

	"github.com/crowdstrike/falcon-mcp/internal/config"
	fal "github.com/crowdstrike/falcon-mcp/internal/falcon"
	"github.com/crowdstrike/falcon-mcp/internal/mcpx"
	"github.com/crowdstrike/falcon-mcp/internal/toolsets"
	"github.com/crowdstrike/falcon-mcp/internal/version"
)

// Execute builds and runs the root command. It first loads a .env file from the
// working directory (if present) so its values participate in the
// defaults < env < flag precedence, mirroring the Python server.
func Execute() error {
	config.LoadDotEnv(".env")
	return newRootCmd().Execute()
}

func newRootCmd() *cobra.Command {
	def := config.Defaults()

	cmd := &cobra.Command{
		Use:           "falcon-mcp",
		Short:         "CrowdStrike Falcon MCP Server",
		Version:       version.Version,
		SilenceUsage:  true,
		SilenceErrors: true,
		RunE: func(c *cobra.Command, _ []string) error {
			return run(c)
		},
	}

	f := cmd.Flags()
	f.StringP("transport", "t", def.Transport, "Transport: stdio, streamable-http, or sse")
	f.StringP("modules", "m", "", "Comma-separated modules to enable (default: all)")
	f.BoolP("debug", "d", false, "Enable debug logging")
	f.String("base-url", def.BaseURL, "Falcon API base URL or cloud name")
	f.String("host", def.Host, "Bind host for HTTP transports")
	f.IntP("port", "p", def.Port, "Bind port for HTTP transports")
	f.String("user-agent-comment", "", "Additional User-Agent comment")
	f.Bool("stateless-http", false, "Use stateless streamable-http")
	f.String("api-key", "", "API key for x-api-key auth on HTTP transports")
	f.String("member-cid", "", "Member CID for MSSP / Flight Control")
	f.String("proxy", "", "HTTP/HTTPS proxy URL")
	f.Bool("dynamic", false, "Enable dynamic mode (3 meta-tools)")
	f.Bool("read-only", false, "Register only read-only tools")
	f.String("client-id", "", "Falcon API client ID")
	f.String("client-secret", "", "Falcon API client secret")

	return cmd
}

// resolveConfig applies precedence defaults < env < explicit flags. A flag
// value is used only when the user changed it; otherwise the env var (if set)
// wins over the built-in default.
func resolveConfig(cmd *cobra.Command) config.Config {
	cfg := config.Defaults()
	f := cmd.Flags()

	str := func(name, env string) string {
		if f.Changed(name) {
			v, _ := f.GetString(name)
			return v
		}
		if v, ok := os.LookupEnv(env); ok {
			return v
		}
		v, _ := f.GetString(name)
		return v
	}
	boolVal := func(name, env string) bool {
		if f.Changed(name) {
			v, _ := f.GetBool(name)
			return v
		}
		if v, ok := os.LookupEnv(env); ok {
			b, _ := strconv.ParseBool(v)
			return b
		}
		v, _ := f.GetBool(name)
		return v
	}

	cfg.Transport = str("transport", "FALCON_MCP_TRANSPORT")
	cfg.Modules = config.ParseModules(str("modules", "FALCON_MCP_MODULES"))
	cfg.BaseURL = str("base-url", "FALCON_BASE_URL")
	cfg.Host = str("host", "FALCON_MCP_HOST")
	cfg.UserAgentComment = str("user-agent-comment", "FALCON_MCP_USER_AGENT_COMMENT")
	cfg.APIKey = str("api-key", "FALCON_MCP_API_KEY")
	cfg.MemberCID = str("member-cid", "FALCON_MEMBER_CID")
	cfg.Proxy = str("proxy", "FALCON_PROXY_URL")
	cfg.ClientID = str("client-id", "FALCON_CLIENT_ID")
	cfg.ClientSecret = str("client-secret", "FALCON_CLIENT_SECRET")

	cfg.Debug = boolVal("debug", "FALCON_MCP_DEBUG")
	cfg.StatelessHTTP = boolVal("stateless-http", "FALCON_MCP_STATELESS_HTTP")
	cfg.Dynamic = boolVal("dynamic", "FALCON_MCP_DYNAMIC")
	cfg.ReadOnly = boolVal("read-only", "FALCON_MCP_READ_ONLY")

	// port (int) resolved explicitly; cfg.Port already holds the default.
	if f.Changed("port") {
		cfg.Port, _ = f.GetInt("port")
	} else if v, ok := os.LookupEnv("FALCON_MCP_PORT"); ok {
		if p, err := strconv.Atoi(v); err == nil {
			cfg.Port = p
		}
	}

	return cfg
}

// configureLogging returns a slog.Logger writing to stderr (required for the
// stdio transport, which owns stdout).
func configureLogging(debug bool) *slog.Logger {
	level := slog.LevelInfo
	if debug {
		level = slog.LevelDebug
	}
	var w io.Writer = os.Stderr
	return slog.New(slog.NewTextHandler(w, &slog.HandlerOptions{Level: level}))
}

func run(cmd *cobra.Command) error {
	cfg := resolveConfig(cmd)
	logger := configureLogging(cfg.Debug)
	slog.SetDefault(logger)

	if err := cfg.Validate(); err != nil {
		return err
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	client, err := fal.NewClient(ctx, fal.Config{
		ClientID:         cfg.ClientID,
		ClientSecret:     cfg.ClientSecret,
		BaseURL:          cfg.BaseURL,
		MemberCID:        cfg.MemberCID,
		Proxy:            cfg.Proxy,
		UserAgentComment: cfg.UserAgentComment,
		Debug:            cfg.Debug,
	})
	if err != nil {
		return err
	}

	sets := toolsets.Default().Build(client, cfg.Modules, cfg.ReadOnly)
	if cfg.Dynamic {
		// Dynamic mode collapses the full surface into 3 discovery meta-tools.
		// Building the facade from the already-filtered sets carries read-only
		// filtering through: dropped write tools are absent from search/execute.
		sets = []*toolsets.Toolset{toolsets.Dynamic(sets)}
	}
	srv := mcpx.NewServer(version.Version)
	mcpx.Register(srv, sets)

	logger.Info("starting falcon-mcp",
		"version", version.Version, "transport", cfg.Transport,
		"modules", len(sets), "read_only", cfg.ReadOnly)

	switch cfg.Transport {
	case "stdio":
		return mcpx.RunStdio(ctx, srv)
	case "streamable-http":
		return mcpx.RunStreamableHTTP(ctx, httpConfig(cfg), srv)
	case "sse":
		return mcpx.RunSSE(ctx, httpConfig(cfg), srv)
	default:
		return fmt.Errorf("unknown transport %q: want stdio, streamable-http, or sse", cfg.Transport)
	}
}

// httpConfig builds the HTTP transport settings from cfg, including the
// middleware chain (api-key auth, content-type normalization, trailing-slash
// stripping, request logging).
func httpConfig(cfg config.Config) mcpx.HTTPConfig {
	mw := mcpx.HTTPMiddleware{APIKey: cfg.APIKey}
	return mcpx.HTTPConfig{
		Addr:      net.JoinHostPort(cfg.Host, strconv.Itoa(cfg.Port)),
		Stateless: cfg.StatelessHTTP,
		Handler:   func(h http.Handler) http.Handler { return mcpx.WrapHTTP(h, mw) },
	}
}
