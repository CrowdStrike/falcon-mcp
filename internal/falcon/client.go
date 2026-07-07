// Package falconapi builds the shared gofalcon API client from validated
// configuration. It isolates region/MSSP wiring so the rest of the server can
// depend on the concrete *client.CrowdStrikeAPISpecification.
package falconapi

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"net/url"

	"github.com/crowdstrike/gofalcon/falcon"
	"github.com/crowdstrike/gofalcon/falcon/client"
	"golang.org/x/oauth2"

	"github.com/crowdstrike/falcon-mcp/internal/config"
)

// New constructs a gofalcon client from cfg. The context is used only for the
// OAuth2 token exchange during construction (per gofalcon's ApiConfig
// contract); per-call cancellation is supplied separately on each API call.
//
// When cfg.Proxy is set, the context carries a proxied *http.Client under the
// oauth2.HTTPClient key. gofalcon resolves its base transport from that key
// (via clientcredentials -> oauth2.NewClient), so both the token exchange and
// all API calls route through the proxy. This is the correct injection point:
// ApiConfig.TransportDecorator wraps gofalcon's outermost round-tripper (above
// the OAuth transport), so using it to swap in a proxied transport would strip
// the Authorization layer and break auth. When cfg.Proxy is empty the context
// is left untouched, so gofalcon uses http.DefaultTransport, which honors the
// HTTPS_PROXY/HTTP_PROXY/NO_PROXY environment variables.
func New(ctx context.Context, cfg *config.Config) (*client.CrowdStrikeAPISpecification, error) {
	if cfg.Proxy != "" {
		proxyClient, err := proxyHTTPClient(cfg.Proxy)
		if err != nil {
			return nil, err
		}
		ctx = context.WithValue(ctx, oauth2.HTTPClient, proxyClient)
	}

	c, err := falcon.NewClient(&falcon.ApiConfig{
		ClientId:          cfg.ClientID,
		ClientSecret:      cfg.ClientSecret,
		MemberCID:         cfg.MemberCID,
		Cloud:             falcon.Cloud(cfg.Cloud),
		HostOverride:      cfg.HostOverride,
		UserAgentOverride: cfg.UserAgent,
		Context:           ctx,
	})
	if err != nil {
		return nil, err
	}
	// Log the client shape at construction, never the secret (SEC-2). MemberCID
	// is reported only by presence; the proxy URL is reported only by presence
	// because it can embed credentials in userinfo.
	slog.Default().Debug("falcon client constructed",
		"cloud", cfg.Cloud,
		"host_override", cfg.HostOverride,
		"member_cid_set", cfg.MemberCID != "",
		"user_agent", cfg.UserAgent,
		"proxy_set", cfg.Proxy != "",
	)
	return c, nil
}

// proxyHTTPClient builds an *http.Client whose transport routes requests through
// proxy. It clones http.DefaultTransport to keep its connection-pool and timeout
// defaults, overriding only the proxy. proxy is validated by config.Load; it is
// re-parsed here rather than threaded through as a *url.URL to keep config.Config
// free of net/url types.
func proxyHTTPClient(proxy string) (*http.Client, error) {
	u, err := url.Parse(proxy)
	if err != nil {
		return nil, fmt.Errorf("parse proxy url %q: %w", proxy, err)
	}
	tr := http.DefaultTransport.(*http.Transport).Clone()
	tr.Proxy = http.ProxyURL(u)
	return &http.Client{Transport: tr}, nil
}
