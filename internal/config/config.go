// Package config loads falcon-mcp server configuration from command-line
// flags and environment variables. Precedence is flag > env > default,
// matching the Python implementation's argparse+os.environ cascade.
package config

import (
	"flag"
	"fmt"
	"os"
	"strings"
)

// Config holds all runtime configuration for the Falcon MCP server.
type Config struct {
	// Falcon API credentials and connection.
	ClientID     string
	ClientSecret string
	BaseURL      string
	MemberCID    string
	ProxyURL     string

	// MCP server behavior.
	Transport        string // stdio | sse | streamable-http
	Modules          []string
	Debug            bool
	UserAgentComment string
	Dynamic          bool

	// HTTP transport.
	Host          string
	Port          int
	StatelessHTTP bool
	APIKey        string
	MultiTenant   bool
}

// validTransports enumerates the supported transport protocols.
var validTransports = map[string]bool{
	"stdio":           true,
	"sse":             true,
	"streamable-http": true,
}

// envOr returns the environment variable value for key, or def if unset.
func envOr(key, def string) string {
	if v, ok := os.LookupEnv(key); ok {
		return v
	}
	return def
}

// envBool reports whether the environment variable equals "true" (case-insensitive),
// matching the Python `.lower() == "true"` check.
func envBool(key string) bool {
	return strings.EqualFold(os.Getenv(key), "true")
}

// Load parses configuration from the given argument slice (typically os.Args[1:])
// and the process environment. It returns the resolved Config or an error if the
// arguments are invalid. A request for --version is signaled via the returned
// showVersion bool.
func Load(args []string) (cfg *Config, showVersion bool, err error) {
	fs := flag.NewFlagSet("falcon-mcp", flag.ContinueOnError)

	var (
		versionFlag = fs.Bool("version", false, "Print version and exit")
		transport   = fs.String("transport", envOr("FALCON_MCP_TRANSPORT", "stdio"),
			"Transport protocol: stdio, sse, or streamable-http (env: FALCON_MCP_TRANSPORT)")
		modules = fs.String("modules", envOr("FALCON_MCP_MODULES", ""),
			"Comma-separated list of modules to enable (default: all, env: FALCON_MCP_MODULES)")
		debug = fs.Bool("debug", envBool("FALCON_MCP_DEBUG"),
			"Enable debug logging (env: FALCON_MCP_DEBUG)")
		baseURL = fs.String("base-url", os.Getenv("FALCON_BASE_URL"),
			"Falcon API base URL (env: FALCON_BASE_URL)")
		host = fs.String("host", envOr("FALCON_MCP_HOST", "127.0.0.1"),
			"Host to bind for HTTP transports (env: FALCON_MCP_HOST)")
		port = fs.Int("port", 0,
			"Port for HTTP transports (default: 8000, env: FALCON_MCP_PORT)")
		userAgentComment = fs.String("user-agent-comment", os.Getenv("FALCON_MCP_USER_AGENT_COMMENT"),
			"Additional User-Agent comment (env: FALCON_MCP_USER_AGENT_COMMENT)")
		statelessHTTP = fs.Bool("stateless-http", envBool("FALCON_MCP_STATELESS_HTTP"),
			"Enable stateless HTTP mode for horizontal scaling (env: FALCON_MCP_STATELESS_HTTP)")
		apiKey = fs.String("api-key", os.Getenv("FALCON_MCP_API_KEY"),
			"API key for HTTP transport authentication via x-api-key (env: FALCON_MCP_API_KEY)")
		memberCID = fs.String("member-cid", os.Getenv("FALCON_MEMBER_CID"),
			"Child CID for Flight Control (MSSP) support (env: FALCON_MEMBER_CID)")
		proxy = fs.String("proxy", os.Getenv("FALCON_PROXY_URL"),
			"HTTP/HTTPS proxy URL for outbound Falcon API connections (env: FALCON_PROXY_URL)")
		dynamic = fs.Bool("dynamic", envBool("FALCON_MCP_DYNAMIC"),
			"Enable dynamic mode: 3 meta-tools instead of all module tools (env: FALCON_MCP_DYNAMIC)")
		multiTenant = fs.Bool("multi-tenant", envBool("FALCON_MCP_MULTI_TENANT"),
			"Enable multi-tenant mode: per-request credentials from headers (env: FALCON_MCP_MULTI_TENANT)")
	)

	// Register single-character aliases matching the Python CLI.
	fs.BoolVar(versionFlag, "V", *versionFlag, "Print version and exit (alias)")
	fs.StringVar(transport, "t", *transport, "Transport protocol (alias)")
	fs.StringVar(modules, "m", *modules, "Modules to enable (alias)")
	fs.BoolVar(debug, "d", *debug, "Enable debug logging (alias)")
	fs.IntVar(port, "p", *port, "Port for HTTP transports (alias)")

	if err := fs.Parse(args); err != nil {
		return nil, false, err
	}
	if *versionFlag {
		return nil, true, nil
	}

	if !validTransports[*transport] {
		return nil, false, fmt.Errorf("invalid transport %q: must be stdio, sse, or streamable-http", *transport)
	}

	// Port: flag > env > default(8000). A 0 flag value means "unset".
	resolvedPort := *port
	if resolvedPort == 0 {
		resolvedPort = 8000
		if v := os.Getenv("FALCON_MCP_PORT"); v != "" {
			var p int
			if _, e := fmt.Sscanf(v, "%d", &p); e == nil {
				resolvedPort = p
			}
		}
	}

	cfg = &Config{
		ClientID:         os.Getenv("FALCON_CLIENT_ID"),
		ClientSecret:     os.Getenv("FALCON_CLIENT_SECRET"),
		BaseURL:          *baseURL,
		MemberCID:        *memberCID,
		ProxyURL:         *proxy,
		Transport:        *transport,
		Modules:          parseModules(*modules),
		Debug:            *debug,
		UserAgentComment: *userAgentComment,
		Dynamic:          *dynamic,
		Host:             *host,
		Port:             resolvedPort,
		StatelessHTTP:    *statelessHTTP,
		APIKey:           *apiKey,
		MultiTenant:      *multiTenant,
	}
	return cfg, false, nil
}

// parseModules splits a comma-separated module list, trimming whitespace and
// dropping empty entries. An empty input yields nil (meaning "all modules").
func parseModules(s string) []string {
	if strings.TrimSpace(s) == "" {
		return nil
	}
	var out []string
	for _, m := range strings.Split(s, ",") {
		if m = strings.TrimSpace(m); m != "" {
			out = append(out, m)
		}
	}
	return out
}
