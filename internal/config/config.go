// Package config parses and validates falcon-mcp server configuration. It
// validates resolved input values and returns a normalized Config; it never
// reads the environment or stores config in a package-level global. Env/flag/
// file resolution lives in the internal/cli package.
package config

import (
	"errors"
	"fmt"
	"net/url"
	"regexp"
	"strings"

	"github.com/crowdstrike/falcon-mcp/internal/version"
)

// defaultDetailFetchConcurrency bounds concurrent detail-fetch requests. The
// workload is network/API-bound (Falcon rate limits), not CPU-bound, so this is
// a small fixed default rather than a function of runtime.NumCPU().
const defaultDetailFetchConcurrency = 4

// Sentinel errors returned by Load. Use errors.Is for control flow.
var (
	// ErrMissingCredentials is returned when client id/secret are absent.
	ErrMissingCredentials = errors.New("config: client id and client secret are required")
	// ErrInvalidTransport is returned when the transport is not one of the
	// supported values.
	ErrInvalidTransport = errors.New("config: transport must be stdio, http, or sse")
	// ErrStatelessRequiresHTTP is returned when stateless-http is set but the
	// transport is not http. Stateless mode is a streamable-HTTP-only feature.
	ErrStatelessRequiresHTTP = errors.New("config: stateless-http requires the http transport")
	// ErrAPIKeyRequiresHTTP is returned when api-key is set but the transport is
	// not http or sse. A static endpoint secret only guards a network transport;
	// it is meaningless for stdio.
	ErrAPIKeyRequiresHTTP = errors.New("config: api-key requires the http or sse transport")
	// ErrInvalidProxy is returned when a non-empty proxy value is not a usable
	// proxy URL (unparseable, missing scheme/host, or an unsupported scheme).
	ErrInvalidProxy = errors.New("config: invalid proxy url")
)

// Validation patterns, compiled once at package scope (PERF-2).
var (
	cloudRE     = regexp.MustCompile(`^(autodiscover|us-?1|us-?2|us-?3|eu-?1|us-?gov-?1|us-?gov-?2|gov-?1|gov-?2)$`)
	memberCIDRE = regexp.MustCompile(`^[0-9a-fA-F]{32}(-[0-9a-fA-F]{2})?$`)
)

// Config is the server configuration. The cli package populates it from flags,
// env, and config files, then passes it to Load for validation and default
// normalization. Treat it as immutable after Load returns.
type Config struct {
	ClientID     string
	ClientSecret string
	Cloud        string
	HostOverride string
	MemberCID    string
	// Proxy is an optional outbound HTTP/HTTPS proxy URL for Falcon API calls.
	// When set it forces both the OAuth token exchange and all API traffic
	// through the proxy. When empty, the default transport is used, which honors
	// the HTTPS_PROXY/HTTP_PROXY/NO_PROXY environment variables.
	Proxy     string
	Transport string
	HTTPAddr  string
	Hosted    bool
	// UserAgent is an optional caller-supplied string appended to the API
	// User-Agent header. Load composes the final value; see composeUserAgent.
	UserAgent string
	// Dynamic exposes only the three meta-tools (falcon_search_tools,
	// falcon_execute_tool, falcon_list_enabled_modules) instead of every
	// module's tools, so clients discover tools on demand and pay each tool's
	// schema cost only when they call it. Off by default.
	Dynamic bool
	// StatelessHTTP runs the http transport in stateless mode: no
	// Mcp-Session-Id tracking, a fresh temporary session per request. Intended
	// for horizontally-scaled deployments. Only meaningful with transport "http".
	StatelessHTTP          bool
	DetailFetchConcurrency int
	// APIKey is an optional static shared secret. When non-empty, the http and
	// sse transports require it in the x-api-key request header; empty disables
	// endpoint auth. It authenticates clients to this server and is unrelated to
	// the Falcon OAuth credentials (ClientID/ClientSecret), which authenticate
	// this server to CrowdStrike.
	APIKey string
	// Modules is an allowlist of module names to enable; empty enables all.
	// config normalizes this list but does not validate names against the real
	// module set — that authority belongs to the mcpserver package.
	Modules []string
}

// Load validates cfg, applies defaults, and returns the normalized Config. It
// fails fast when required credentials are missing or a field is malformed.
func Load(cfg Config) (*Config, error) {
	if cfg.ClientID == "" || cfg.ClientSecret == "" {
		return nil, ErrMissingCredentials
	}

	if cfg.Transport == "" {
		cfg.Transport = "stdio"
	}
	switch cfg.Transport {
	case "stdio", "http", "sse":
	default:
		return nil, ErrInvalidTransport
	}
	if cfg.Transport != "stdio" && cfg.HTTPAddr == "" {
		return nil, fmt.Errorf("config: http-addr is required for %s transport", cfg.Transport)
	}
	if cfg.StatelessHTTP && cfg.Transport != "http" {
		return nil, fmt.Errorf("%w, got %q", ErrStatelessRequiresHTTP, cfg.Transport)
	}
	if cfg.APIKey != "" && cfg.Transport == "stdio" {
		return nil, fmt.Errorf("%w, got %q", ErrAPIKeyRequiresHTTP, cfg.Transport)
	}

	if err := matchOrEmpty(cloudRE, "cloud", cfg.Cloud); err != nil {
		return nil, err
	}
	if err := matchOrEmpty(memberCIDRE, "member-cid", cfg.MemberCID); err != nil {
		return nil, err
	}

	cfg.Proxy = strings.TrimSpace(cfg.Proxy)
	if err := validateProxy(cfg.Proxy); err != nil {
		return nil, err
	}

	if cfg.DetailFetchConcurrency == 0 {
		cfg.DetailFetchConcurrency = defaultDetailFetchConcurrency
	}

	cfg.Modules = normalizeModules(cfg.Modules)

	cfg.HostOverride = normalizeHostOverride(cfg.HostOverride)

	cfg.UserAgent = composeUserAgent(cfg.UserAgent)

	return &cfg, nil
}

// normalizeHostOverride reduces a base-URL value to the bare FQDN that gofalcon's
// ApiConfig.HostOverride expects. gofalcon builds "https://" + Host() + "/oauth2/token"
// and uses Host() as the transport host, so a scheme or path in the value would
// break it. The env var is named FALCON_BASE_URL, which invites a full URL like
// "https://api.us-2.crowdstrike.com/", so we strip any scheme and path and keep
// only the host. An input that is already a bare host passes through unchanged.
func normalizeHostOverride(host string) string {
	host = strings.TrimSpace(host)
	if host == "" {
		return ""
	}
	// url.Parse only populates Host when a scheme is present; add one for a bare
	// "host/path" input so the path is stripped consistently.
	toParse := host
	if !strings.Contains(host, "://") {
		toParse = "https://" + host
	}
	if u, err := url.Parse(toParse); err == nil && u.Host != "" {
		return u.Host
	}
	return host
}

// validateProxy checks a non-empty proxy value. It must parse as an absolute URL
// with a host and one of the supported schemes (http, https, socks5). An empty
// value is valid: it selects the default transport, which honors the
// HTTPS_PROXY/NO_PROXY environment variables. The value is not stored parsed;
// falconapi re-parses it when building the client.
func validateProxy(proxy string) error {
	if proxy == "" {
		return nil
	}
	u, err := url.Parse(proxy)
	if err != nil {
		return fmt.Errorf("%w %q: %w", ErrInvalidProxy, proxy, err)
	}
	switch u.Scheme {
	case "http", "https", "socks5":
	default:
		return fmt.Errorf("%w %q: scheme must be http, https, or socks5", ErrInvalidProxy, proxy)
	}
	if u.Host == "" {
		return fmt.Errorf("%w %q: missing host", ErrInvalidProxy, proxy)
	}
	return nil
}

// composeUserAgent builds the User-Agent value sent to the Falcon API. It always// leads with falcon-mcp/<version> and appends the caller-supplied string when
// present.
func composeUserAgent(user string) string {
	if user = strings.TrimSpace(user); user != "" {
		return fmt.Sprintf("falcon-mcp/%s %s", version.Version, user)
	}
	return fmt.Sprintf("falcon-mcp/%s", version.Version)
}

// normalizeModules trims each module name and drops empty entries, returning nil
// when nothing remains. It does not validate names against the real module set:
// config must not import mcpserver, which is the sole authority on valid names.
func normalizeModules(names []string) []string {
	var out []string
	for _, n := range names {
		if n = strings.TrimSpace(n); n != "" {
			out = append(out, n)
		}
	}
	return out
}

// matchOrEmpty reports nil when s is empty or matches re, else a wrapped error
// naming field.
func matchOrEmpty(re *regexp.Regexp, field, s string) error {
	if s == "" || re.MatchString(s) {
		return nil
	}
	return fmt.Errorf("config: invalid %s %q", field, s)
}
