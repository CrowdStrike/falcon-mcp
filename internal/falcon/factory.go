// Package falcon wraps the gofalcon SDK client, exposing the narrow domain
// accessors each toolset needs and centralizing credential handling, error
// normalization, and API-scope hints.
package falcon

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
	"strings"

	"github.com/crowdstrike/gofalcon/falcon"

	"github.com/crowdstrike/falcon-mcp-go/pkg/version"
)

// Credentials holds the per-tenant Falcon API credentials and connection
// options. In single-tenant mode these come from env/flags; in multi-tenant
// mode they are derived per-request from HTTP headers.
type Credentials struct {
	ClientID     string
	ClientSecret string
	// BaseURL is the full Falcon API URL (e.g. https://api.us-2.crowdstrike.com).
	// Empty means autodiscover the cloud from the credentials.
	BaseURL   string
	MemberCID string
	ProxyURL  string
}

// factoryOptions carries process-wide options that are not tenant-specific.
type factoryOptions struct {
	debug            bool
	userAgentComment string
}

// buildAPIConfig translates Credentials + options into a gofalcon ApiConfig.
func buildAPIConfig(ctx context.Context, creds Credentials, opts factoryOptions) (*falcon.ApiConfig, error) {
	if creds.ClientID == "" || creds.ClientSecret == "" {
		return nil, fmt.Errorf(
			"Falcon API credentials not provided: set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET " +
				"(or pass per-request credential headers in multi-tenant mode)")
	}

	ac := &falcon.ApiConfig{
		ClientId:          creds.ClientID,
		ClientSecret:      creds.ClientSecret,
		MemberCID:         creds.MemberCID,
		Context:           ctx,
		Debug:             opts.debug,
		UserAgentOverride: version.UserAgent(opts.userAgentComment),
	}

	// The Python config accepts a full base URL; gofalcon wants a bare host in
	// HostOverride (or a Cloud selector). Derive the host from the URL when set,
	// otherwise leave Cloud as CloudAutoDiscover.
	if creds.BaseURL != "" {
		host, err := hostFromBaseURL(creds.BaseURL)
		if err != nil {
			return nil, err
		}
		ac.HostOverride = host
	}

	if creds.ProxyURL != "" {
		decorator, err := proxyDecorator(creds.ProxyURL)
		if err != nil {
			return nil, err
		}
		ac.TransportDecorator = decorator
	}

	return ac, nil
}

// hostFromBaseURL extracts the bare host from a Falcon base URL. It accepts
// values with or without a scheme (e.g. "https://api.crowdstrike.com" or
// "api.crowdstrike.com").
func hostFromBaseURL(base string) (string, error) {
	b := strings.TrimSpace(base)
	if !strings.Contains(b, "://") {
		b = "https://" + b
	}
	u, err := url.Parse(b)
	if err != nil {
		return "", fmt.Errorf("invalid base URL %q: %w", base, err)
	}
	if u.Host == "" {
		return "", fmt.Errorf("invalid base URL %q: missing host", base)
	}
	return u.Host, nil
}

// proxyDecorator returns a TransportDecorator that routes outbound Falcon API
// traffic through the given proxy URL.
func proxyDecorator(proxyURL string) (falcon.TransportDecorator, error) {
	pu, err := url.Parse(proxyURL)
	if err != nil {
		return nil, fmt.Errorf("invalid proxy URL %q: %w", proxyURL, err)
	}
	return func(rt http.RoundTripper) http.RoundTripper {
		base, ok := rt.(*http.Transport)
		if !ok || base == nil {
			base = http.DefaultTransport.(*http.Transport).Clone()
		} else {
			base = base.Clone()
		}
		base.Proxy = http.ProxyURL(pu)
		return base
	}, nil
}
