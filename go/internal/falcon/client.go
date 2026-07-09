package falcon

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
	"runtime"
	"strings"

	"github.com/crowdstrike/gofalcon/falcon"
	"github.com/crowdstrike/gofalcon/falcon/client"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/clientcredentials"

	"github.com/crowdstrike/falcon-mcp/internal/version"
)

// gofalconVersion is the pinned gofalcon SDK version, reported in the user
// agent. Keep in sync with the require directive in go.mod.
// TODO(release): guard this against go.mod drift in CI (read
// runtime/debug.BuildInfo) so a stale value fails the build, not just the UA.
const gofalconVersion = "v0.21.0"

// Config holds the settings needed to build an authenticated Falcon client.
type Config struct {
	ClientID         string
	ClientSecret     string
	BaseURL          string // Full URL (-> HostOverride) or a cloud name (us-1, eu-1, ...).
	MemberCID        string // MSSP / Flight Control child CID.
	Proxy            string
	UserAgentComment string
	Debug            bool
}

// NewClient builds an authenticated gofalcon client and verifies the
// credentials before returning. gofalcon authenticates lazily on the first API
// call, so NewClient runs a scope-independent OAuth2 probe to fail fast on bad
// credentials, matching the Python server's eager login.
func NewClient(ctx context.Context, cfg Config) (*client.CrowdStrikeAPISpecification, error) {
	ctx, err := withProxy(ctx, cfg.Proxy)
	if err != nil {
		return nil, err
	}

	ac, err := apiConfigFor(ctx, cfg)
	if err != nil {
		return nil, err
	}

	if err := authProbe(ctx, authProbeConfig{
		ClientID:     cfg.ClientID,
		ClientSecret: cfg.ClientSecret,
		MemberCID:    cfg.MemberCID,
		TokenURL:     "https://" + ac.Host() + "/oauth2/token",
	}); err != nil {
		return nil, err
	}

	return falcon.NewClient(ac)
}

// apiConfigFor assembles the gofalcon ApiConfig from cfg, resolving BaseURL to
// either a HostOverride (when it is a full URL) or a cloud name.
func apiConfigFor(ctx context.Context, cfg Config) (*falcon.ApiConfig, error) {
	if cfg.ClientID == "" || cfg.ClientSecret == "" {
		return nil, fmt.Errorf("falcon: client ID and secret are required")
	}

	ac := &falcon.ApiConfig{
		ClientId:          cfg.ClientID,
		ClientSecret:      cfg.ClientSecret,
		MemberCID:         cfg.MemberCID,
		Context:           ctx,
		UserAgentOverride: userAgent(cfg.UserAgentComment),
		Debug:             cfg.Debug,
	}

	// A parseable URL with a host is a direct host override; anything else is
	// treated as a cloud region name.
	if u, err := url.Parse(cfg.BaseURL); err == nil && u.Host != "" {
		ac.HostOverride = u.Host
	} else if cfg.BaseURL != "" {
		cloud, err := falcon.CloudValidate(cfg.BaseURL)
		if err != nil {
			return nil, fmt.Errorf("falcon: invalid base URL %q: %w", cfg.BaseURL, err)
		}
		ac.Cloud = cloud
	}

	return ac, nil
}

// withProxy returns a context carrying an *http.Client whose transport proxies
// through proxyURL. The proxied client is installed on the oauth2.HTTPClient
// context key so it becomes gofalcon's base transport for both the token
// exchange and API calls, while gofalcon's own retry/rate-limit/user-agent
// layers still wrap on top. Setting a base *http.Transport via
// ApiConfig.TransportDecorator would instead replace the oauth2 token-injecting
// transport and send every request unauthenticated. An empty proxyURL is a
// no-op so HTTP(S)_PROXY environment variables keep working for free.
func withProxy(ctx context.Context, proxyURL string) (context.Context, error) {
	if proxyURL == "" {
		return ctx, nil
	}
	u, err := url.Parse(proxyURL)
	if err != nil {
		return nil, fmt.Errorf("falcon: invalid proxy URL %q: %w", proxyURL, err)
	}
	proxied := &http.Client{Transport: &http.Transport{Proxy: http.ProxyURL(u)}}
	return context.WithValue(ctx, oauth2.HTTPClient, proxied), nil
}

// authProbeConfig configures a scope-independent credential check.
type authProbeConfig struct {
	ClientID     string
	ClientSecret string
	MemberCID    string
	TokenURL     string
	HTTPClient   *http.Client // Optional; for tests. Falls back to the context client.
}

// authProbe performs an OAuth2 client-credentials token exchange to validate
// credentials without requiring any API scope. A failed exchange is a fatal
// startup error.
func authProbe(ctx context.Context, cfg authProbeConfig) error {
	conf := clientcredentials.Config{
		ClientID:     cfg.ClientID,
		ClientSecret: cfg.ClientSecret,
		TokenURL:     cfg.TokenURL,
	}
	if cfg.MemberCID != "" {
		conf.EndpointParams = url.Values{"member_cid": []string{cfg.MemberCID}}
	}
	if cfg.HTTPClient != nil {
		ctx = context.WithValue(ctx, oauth2.HTTPClient, cfg.HTTPClient)
	}
	if _, err := conf.Token(ctx); err != nil {
		return fmt.Errorf("falcon: authentication failed: %w", err)
	}
	return nil
}

// userAgent builds the RFC-format user agent string, mirroring the Python
// client: falcon-mcp/<ver> (<comment>; gofalcon/<ver>; Go/<ver>; <os>/<arch>).
// An empty comment is omitted cleanly.
func userAgent(comment string) string {
	parts := make([]string, 0, 4)
	if comment != "" {
		parts = append(parts, comment)
	}
	parts = append(parts,
		"gofalcon/"+gofalconVersion,
		"Go/"+runtime.Version(),
		runtime.GOOS+"/"+runtime.GOARCH,
	)
	return fmt.Sprintf("falcon-mcp/%s (%s)", version.Version, strings.Join(parts, "; "))
}
