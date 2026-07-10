// Package cli owns the falcon-mcp command-line interface. It is the sole owner
// of cobra and a local viper instance: it resolves configuration values
// (precedence flag > env > config file > default), applies INI/falcon_-prefix
// normalization, and produces a plain config.Input. It imports config but
// config never imports cli — viper/cobra do not leak into the domain package.
package cli

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"path/filepath"
	"strings"

	"github.com/go-viper/encoding/ini"
	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	"github.com/crowdstrike/falcon-mcp/internal/config"
)

// Execute is the process entry point for falcon-mcp. It installs a baseline
// JSON logger so any pre-config error (flag parsing, or the final error log
// below) is captured, derives a context cancelled on os.Interrupt (so http/sse
// transports drain gracefully on Ctrl+C), builds the root command, and serves
// until interrupted. preRunE reinstalls the logger at the configured level.
// Errors are logged once here; the command is configured to stay silent so
// failures are not printed twice.
func Execute() error {
	slog.SetDefault(newLogger(slog.LevelInfo))

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	if err := newRootCmd().ExecuteContext(ctx); err != nil {
		slog.Error("server exited with error", "err", err)
		return err
	}
	return nil
}

// newLogger returns the process's JSON logger emitting to stderr at level.
func newLogger(level slog.Level) *slog.Logger {
	return slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: level}))
}

// newRootCmd builds the falcon-mcp root command. preRunE resolves the config
// once; runE serves it. cfg is the only state shared between the two phases —
// a single local held here and passed to each phase keeps it off package
// globals (CFG-2) without a wrapper type or double indirection.
func newRootCmd() *cobra.Command {
	var cfg *config.Config

	cmd := &cobra.Command{
		Use:   "falcon-mcp",
		Short: "CrowdStrike Falcon MCP server",
		// Execute logs errors once via slog; don't let cobra print them too.
		SilenceErrors: true,
		PreRunE: func(cmd *cobra.Command, _ []string) error {
			c, err := preRunE(cmd)
			cfg = c
			return err
		},
		RunE: func(cmd *cobra.Command, _ []string) error {
			return runE(cmd.Context(), cfg)
		},
	}

	registerFlags(cmd)
	return cmd
}

// preRunE resolves configuration: when --debug is set it reinstalls the logger
// at debug level, then builds a fresh viper from cmd's flags and the
// environment, reads any config file (explicit --config or discovery),
// normalizes falcon_-prefixed keys, and loads the validated config. viper is
// scoped to this call so each invocation is independent (hermetic tests). Flags
// have parsed cleanly by PreRunE, so any error here is a config error, not a
// usage error — silence usage output.
func preRunE(cmd *cobra.Command) (*config.Config, error) {
	if debug, _ := cmd.Flags().GetBool("debug"); debug {
		slog.SetDefault(newLogger(slog.LevelDebug))
	}

	v, err := newViper()
	if err != nil {
		return nil, err
	}
	bindFlags(v, cmd)
	bindEnv(v)

	cfgFile, _ := cmd.Flags().GetString("config")
	if err := readConfigFile(v, cfgFile); err != nil {
		return nil, err
	}

	// Merge ./.env after the config file: ReadInConfig replaces viper's config
	// map, so .env must be merged onto it rather than before it. Merging (not
	// replacing) lets .env and a discovered config file coexist.
	if err := mergeDotEnv(v); err != nil {
		return nil, err
	}
	normalizeFalconPrefix(v)

	cfg, err := config.Load(resolve(v))
	if err != nil {
		return nil, err
	}

	if cfg.Hosted {
		slog.Warn("hosted mode not yet implemented; serving with single credential set",
			"transport", cfg.Transport)
	}
	return cfg, nil
}

// runE serves the config that preRunE resolved over the configured transport.
func runE(ctx context.Context, cfg *config.Config) error {
	return serve(ctx, cfg)
}

// registerFlags declares the falcon-mcp flags on cmd. --config is intentionally
// not bound to a viper key: it names the file to read, it is not a config value.
func registerFlags(cmd *cobra.Command) {
	f := cmd.Flags()
	f.String("config", "", "path to a config file (yaml, json, or ini); overrides discovery")
	f.BoolP("debug", "d", false, "enable debug-level logging")
	f.String("client-id", "", "Falcon OAuth2 client id (env FALCON_CLIENT_ID)")
	f.String("client-secret", "", "Falcon OAuth2 client secret (env FALCON_CLIENT_SECRET)")
	f.String("cloud", "", "Falcon cloud region: autodiscover, us-1, us-2, eu-1, us-gov-1, ... (env FALCON_CLOUD). Overridden by FALCON_BASE_URL, which sets the API host directly (bare FQDN; any scheme/path is stripped)")
	f.String("member-cid", "", "MSSP member CID selector")
	f.String("proxy", "", "outbound HTTP/HTTPS proxy URL for Falcon API calls; empty honors HTTPS_PROXY/NO_PROXY (env FALCON_MCP_PROXY)")
	f.String("transport", "stdio", "transport: stdio, http, or sse. Note: http/sse serve a single credential set, not multi-tenant (env FALCON_MCP_TRANSPORT)")
	f.String("http-addr", ":8080", "listen address for the http and sse transports (env FALCON_MCP_HTTP_ADDR)")
	f.Bool("hosted", false, "reserved; logs a warning and proceeds as single-credential (not yet implemented)")
	f.String("user-agent", "", "user agent comment appended to API requests (alias --user-agent-comment; env FALCON_USER_AGENT or FALCON_USER_AGENT_COMMENT)")
	// --dynamic maps to env FALCON_MCP_DYNAMIC. Operational settings use the
	// FALCON_MCP_ prefix (see bindEnv), matching upstream falcon-mcp; credentials
	// keep the gofalcon-standard FALCON_ prefix.
	f.Bool("dynamic", false, "expose only the 3 meta-tools (falcon_search_tools/execute_tool/list_enabled_modules) instead of all tools (env FALCON_MCP_DYNAMIC)")
	f.Bool("stateless-http", false, "run the http transport in stateless mode: a fresh session per request, no session tracking, for scalable deployments (env FALCON_MCP_STATELESS_HTTP)")
	f.String("api-key", "", "static secret required in the x-api-key header for http/sse clients; empty disables auth (env FALCON_MCP_API_KEY)")
	f.StringSlice("modules", nil, "modules to enable (comma-separated); empty enables all")
	f.Duration("keep-alive", 0, "interval to ping idle sessions and hold long-lived http/sse connections open; 0 disables; ignored by stdio (env FALCON_MCP_KEEP_ALIVE)")

	// Alias --user-agent-comment to the canonical --user-agent flag. Normalizing
	// the input name (rather than declaring a second flag) means bindFlags's
	// VisitAll still sees only user-agent, so viper binding is unchanged. This
	// matches upstream falcon-mcp's --user-agent-comment naming.
	f.SetNormalizeFunc(func(_ *pflag.FlagSet, name string) pflag.NormalizedName {
		if name == "user-agent-comment" {
			name = "user-agent"
		}
		return pflag.NormalizedName(name)
	})
}

// bindFlags binds every flag on cmd to a viper key, converting dashes to
// underscores (client-id -> client_id). This gives flags highest precedence
// while env/file resolution flows through the same keys, all on the local viper
// instance. --config and --debug are excluded: they select behavior, not config
// values.
func bindFlags(v *viper.Viper, cmd *cobra.Command) {
	cmd.Flags().VisitAll(func(f *pflag.Flag) {
		if f.Name == "config" || f.Name == "debug" {
			return
		}
		key := strings.ReplaceAll(f.Name, "-", "_")
		_ = v.BindPFlag(key, f)
	})
}

// bindEnv wires each viper key to its explicit environment variable name(s).
// It replaces viper's AutomaticEnv/SetEnvPrefix mechanism because that supports
// only a single prefix, whereas this command splits env vars across two: the
// gofalcon-standard FALCON_ prefix for credentials and connection settings, and
// FALCON_MCP_ for this server's own operational settings. When BindEnv is given
// explicit names, viper uses them verbatim and ignores any configured prefix, so
// the two families coexist. FALCON_USER_AGENT wins over the upstream
// FALCON_USER_AGENT_COMMENT alias when both are set (first name listed wins).
func bindEnv(v *viper.Viper) {
	// Credentials and connection settings keep the gofalcon-standard FALCON_
	// prefix that users and CI already export.
	_ = v.BindEnv("client_id", "FALCON_CLIENT_ID")
	_ = v.BindEnv("client_secret", "FALCON_CLIENT_SECRET")
	_ = v.BindEnv("cloud", "FALCON_CLOUD")
	_ = v.BindEnv("member_cid", "FALCON_MEMBER_CID")
	_ = v.BindEnv("base_url", "FALCON_BASE_URL")
	_ = v.BindEnv("user_agent", "FALCON_USER_AGENT", "FALCON_USER_AGENT_COMMENT")

	// This server's own operational settings live under FALCON_MCP_, matching
	// upstream falcon-mcp (e.g. FALCON_MCP_DYNAMIC).
	_ = v.BindEnv("transport", "FALCON_MCP_TRANSPORT")
	_ = v.BindEnv("http_addr", "FALCON_MCP_HTTP_ADDR")
	_ = v.BindEnv("hosted", "FALCON_MCP_HOSTED")
	_ = v.BindEnv("dynamic", "FALCON_MCP_DYNAMIC")
	_ = v.BindEnv("stateless_http", "FALCON_MCP_STATELESS_HTTP")
	_ = v.BindEnv("api_key", "FALCON_MCP_API_KEY")
	_ = v.BindEnv("modules", "FALCON_MCP_MODULES")
	_ = v.BindEnv("proxy", "FALCON_MCP_PROXY")
	_ = v.BindEnv("keep_alive", "FALCON_MCP_KEEP_ALIVE")
}

// newViper returns a viper instance with the INI codec registered. viper v1.20+
// dropped INI/HCL/properties from core to shed third-party deps; the codec now
// lives in github.com/go-viper/encoding/ini and must be registered explicitly.
// (WHY: an INI config file may carry a [falcon] section — see hoistFalconSection.)
func newViper() (*viper.Viper, error) {
	registry := viper.NewCodecRegistry()
	if err := registry.RegisterCodec("ini", ini.Codec{}); err != nil {
		return nil, fmt.Errorf("register ini codec: %w", err)
	}
	return viper.NewWithOptions(viper.WithCodecRegistry(registry)), nil
}

// resolve reads the resolved viper keys into a config.Config. It performs no
// I/O; v must already be populated (flags bound, env enabled, file read).
func resolve(v *viper.Viper) config.Config {
	return config.Config{
		ClientID:      v.GetString("client_id"),
		ClientSecret:  v.GetString("client_secret"),
		Cloud:         v.GetString("cloud"),
		HostOverride:  v.GetString("base_url"),
		MemberCID:     v.GetString("member_cid"),
		Proxy:         v.GetString("proxy"),
		Transport:     v.GetString("transport"),
		HTTPAddr:      v.GetString("http_addr"),
		Hosted:        v.GetBool("hosted"),
		Dynamic:       v.GetBool("dynamic"),
		StatelessHTTP: v.GetBool("stateless_http"),
		APIKey:        v.GetString("api_key"),
		Modules:       v.GetStringSlice("modules"),
		UserAgent:     v.GetString("user_agent"),
		KeepAlive:     v.GetDuration("keep_alive"),
	}
}

// searchPaths returns the directories scanned for a config file named
// "falcon-mcp" when no explicit --config path is given, in precedence order.
func searchPaths() []string {
	paths := []string{"."}
	if xdg := os.Getenv("XDG_CONFIG_HOME"); xdg != "" {
		paths = append(paths, filepath.Join(xdg, "falcon-mcp"))
	} else if home, err := os.UserHomeDir(); err == nil {
		paths = append(paths, filepath.Join(home, ".config", "falcon-mcp"))
	}
	return append(paths, "/etc/falcon-mcp")
}

// readConfigFile loads a config file into v. When path is non-empty it is an
// explicit file that must exist — a missing file is an error. When path is
// empty, v searches the standard locations for a "falcon-mcp" file and a
// not-found result is not an error. After a successful read the [falcon] INI
// section (if any) is hoisted to top-level keys.
func readConfigFile(v *viper.Viper, path string) error {
	if path != "" {
		v.SetConfigFile(path)
		if err := v.ReadInConfig(); err != nil {
			return fmt.Errorf("read config %s: %w", path, err)
		}
		hoistFalconSection(v)
		return nil
	}

	v.SetConfigName("falcon-mcp")
	for _, p := range searchPaths() {
		v.AddConfigPath(p)
	}
	if err := v.ReadInConfig(); err != nil {
		var nf viper.ConfigFileNotFoundError
		if errors.As(err, &nf) {
			return nil // no config file on the search paths is fine
		}
		return fmt.Errorf("read config: %w", err)
	}
	hoistFalconSection(v)
	return nil
}

// mergeDotEnv merges ./.env (if present) into v as an "env"-format config layer.
// .env is a dotfile that viper's name-based discovery does not find, so it is
// loaded explicitly. A missing file is not an error. MergeConfig merges onto the
// existing config map rather than replacing it (as ReadInConfig would), so .env
// and a discovered config file coexist; env vars and flags still outrank both,
// matching python-dotenv's non-overriding load_dotenv.
func mergeDotEnv(v *viper.Viper) error {
	f, err := os.Open(".env")
	if err != nil {
		return nil // no .env is fine
	}
	defer f.Close()

	v.SetConfigType("env")
	if err := v.MergeConfig(f); err != nil {
		return fmt.Errorf("merge .env: %w", err)
	}
	return nil
}

// hoistFalconSection promotes an INI [falcon] section's keys to top-level
// keys, without overwriting values already set at the top level. (WHY: INI
// namespaces keys under the section header, so [falcon] client_id must be
// hoisted to client_id to resolve like every other key.)
func hoistFalconSection(v *viper.Viper) {
	sub := v.Sub("falcon")
	if sub == nil {
		return
	}
	for k, val := range sub.AllSettings() {
		if !v.IsSet(k) {
			v.Set(k, val)
		}
	}
}

// normalizeFalconPrefix strips a leading "falcon_" from any key, setting the
// stripped key only when it is not already set (non-prefixed wins). This lets a
// config file use falcon_client_id (matching the FALCON_CLIENT_ID env var)
// interchangeably with the bare client_id key.
func normalizeFalconPrefix(v *viper.Viper) {
	for k, val := range v.AllSettings() {
		stripped, ok := strings.CutPrefix(k, "falcon_")
		if !ok || stripped == "" {
			continue
		}
		if !v.IsSet(stripped) {
			v.Set(stripped, val)
		}
	}
}
