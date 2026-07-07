package falcon

import (
	"context"
	"fmt"
	"net/url"

	"github.com/crowdstrike/gofalcon/falcon"
	"github.com/crowdstrike/gofalcon/falcon/client"
	"golang.org/x/oauth2/clientcredentials"
)

// FalconClient wraps the gofalcon generated API client. Toolsets obtain the
// concrete gofalcon sub-clients through the typed domain accessors defined in
// accessors.go; each toolset declares a narrow interface over only the ops it
// uses, which keeps handlers unit-testable with hand-written mocks.
//
// The underlying client's OAuth token refresh is mutex-protected by
// golang.org/x/oauth2/clientcredentials, so a single FalconClient is safe for
// concurrent use across goroutines with no additional locking.
type FalconClient struct {
	api   *client.CrowdStrikeAPISpecification
	creds Credentials
}

// NewClient builds a FalconClient from the given credentials and options.
// It eagerly constructs the gofalcon client (which autodiscovers the cloud
// when no base URL is set); it does not by itself guarantee a valid token —
// use Connectivity to verify reachability.
func NewClient(ctx context.Context, creds Credentials, debug bool, userAgentComment string) (*FalconClient, error) {
	ac, err := buildAPIConfig(ctx, creds, factoryOptions{debug: debug, userAgentComment: userAgentComment})
	if err != nil {
		return nil, err
	}
	api, err := falcon.NewClient(ac)
	if err != nil {
		return nil, err
	}
	return &FalconClient{api: api, creds: creds}, nil
}

// API returns the underlying gofalcon client. Prefer the typed domain
// accessors (Hosts, Detects, ...) over reaching into this directly.
func (c *FalconClient) API() *client.CrowdStrikeAPISpecification { return c.api }

// Connectivity verifies that the configured credentials can obtain an OAuth2
// token from the Falcon API. It returns nil on success.
func (c *FalconClient) Connectivity(ctx context.Context) error {
	host := "api.crowdstrike.com"
	if c.creds.BaseURL != "" {
		if h, err := hostFromBaseURL(c.creds.BaseURL); err == nil {
			host = h
		}
	}

	cfg := clientcredentials.Config{
		ClientID:     c.creds.ClientID,
		ClientSecret: c.creds.ClientSecret,
		TokenURL:     "https://" + host + "/oauth2/token",
	}
	if c.creds.MemberCID != "" {
		cfg.EndpointParams = url.Values{"member_cid": []string{c.creds.MemberCID}}
	}

	if _, err := cfg.Token(ctx); err != nil {
		return fmt.Errorf("Falcon token request failed: %w", err)
	}
	return nil
}
