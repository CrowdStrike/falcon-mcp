package config

import (
	"errors"
	"strings"
	"testing"

	"github.com/crowdstrike/falcon-mcp/internal/version"
)

func TestLoad(t *testing.T) {
	t.Parallel()
	valid := Config{ClientID: "id", ClientSecret: "secret"}
	tests := []struct {
		name      string
		in        Config
		wantErr   error  // sentinel to errors.Is against; nil means "no error"
		errSubstr string // substring the error message must contain (when wantErr is nil but an error is expected)
		check     func(t *testing.T, c *Config)
	}{
		{
			name:    "missing client id",
			in:      Config{ClientSecret: "secret"},
			wantErr: ErrMissingCredentials,
		},
		{
			name:    "missing client secret",
			in:      Config{ClientID: "id"},
			wantErr: ErrMissingCredentials,
		},
		{
			name: "defaults applied",
			in:   valid,
			check: func(t *testing.T, c *Config) {
				if c.Transport != "stdio" {
					t.Errorf("transport = %q, want stdio", c.Transport)
				}
				if c.DetailFetchConcurrency != defaultDetailFetchConcurrency {
					t.Errorf("detailFetchConcurrency = %d, want %d", c.DetailFetchConcurrency, defaultDetailFetchConcurrency)
				}
			},
		},
		{
			name:    "invalid transport",
			in:      Config{ClientID: "id", ClientSecret: "s", Transport: "grpc"},
			wantErr: ErrInvalidTransport,
		},
		{
			name:      "http transport requires addr",
			in:        Config{ClientID: "id", ClientSecret: "s", Transport: "http"},
			errSubstr: "http-addr",
		},
		{
			name: "sse transport with addr",
			in:   Config{ClientID: "id", ClientSecret: "s", Transport: "sse", HTTPAddr: ":8080"},
			check: func(t *testing.T, c *Config) {
				if c.Transport != "sse" {
					t.Errorf("transport = %q, want sse", c.Transport)
				}
				if c.HTTPAddr != ":8080" {
					t.Errorf("http addr = %q, want :8080", c.HTTPAddr)
				}
			},
		},
		{
			name:      "invalid cloud",
			in:        Config{ClientID: "id", ClientSecret: "s", Cloud: "mars"},
			errSubstr: "cloud",
		},
		{
			name:      "invalid member cid",
			in:        Config{ClientID: "id", ClientSecret: "s", MemberCID: "xyz"},
			errSubstr: "member",
		},
		{
			name: "hosted is inert",
			in:   Config{ClientID: "id", ClientSecret: "s", Hosted: true},
			check: func(t *testing.T, c *Config) {
				if !c.Hosted {
					t.Errorf("hosted = false, want true")
				}
			},
		},
		{
			name: "dynamic passes through",
			in:   Config{ClientID: "id", ClientSecret: "s", Dynamic: true},
			check: func(t *testing.T, c *Config) {
				if !c.Dynamic {
					t.Errorf("dynamic = false, want true")
				}
			},
		},
		{
			name: "stateless-http with http transport",
			in:   Config{ClientID: "id", ClientSecret: "s", Transport: "http", HTTPAddr: ":8080", StatelessHTTP: true},
			check: func(t *testing.T, c *Config) {
				if !c.StatelessHTTP {
					t.Errorf("statelessHTTP = false, want true")
				}
			},
		},
		{
			name:    "stateless-http rejected with stdio transport",
			in:      Config{ClientID: "id", ClientSecret: "s", StatelessHTTP: true},
			wantErr: ErrStatelessRequiresHTTP,
		},
		{
			name:    "stateless-http rejected with sse transport",
			in:      Config{ClientID: "id", ClientSecret: "s", Transport: "sse", HTTPAddr: ":8080", StatelessHTTP: true},
			wantErr: ErrStatelessRequiresHTTP,
		},
		{
			name:    "api-key rejected with stdio transport",
			in:      Config{ClientID: "id", ClientSecret: "s", APIKey: "secret"},
			wantErr: ErrAPIKeyRequiresHTTP,
		},
		{
			name: "api-key accepted with http transport",
			in:   Config{ClientID: "id", ClientSecret: "s", Transport: "http", HTTPAddr: ":8080", APIKey: "secret"},
			check: func(t *testing.T, c *Config) {
				if c.APIKey != "secret" {
					t.Errorf("apiKey = %q, want secret", c.APIKey)
				}
			},
		},
		{
			name: "api-key accepted with sse transport",
			in:   Config{ClientID: "id", ClientSecret: "s", Transport: "sse", HTTPAddr: ":8080", APIKey: "secret"},
			check: func(t *testing.T, c *Config) {
				if c.APIKey != "secret" {
					t.Errorf("apiKey = %q, want secret", c.APIKey)
				}
			},
		},
		{
			name: "empty api-key allowed with stdio transport",
			in:   valid,
			check: func(t *testing.T, c *Config) {
				if c.APIKey != "" {
					t.Errorf("apiKey = %q, want empty", c.APIKey)
				}
			},
		},
		{
			name: "modules normalized: trimmed and empties dropped",
			in:   Config{ClientID: "id", ClientSecret: "s", Modules: []string{" hosts ", "", "  ", "detections"}},
			check: func(t *testing.T, c *Config) {
				want := []string{"hosts", "detections"}
				if len(c.Modules) != len(want) {
					t.Fatalf("modules = %v, want %v", c.Modules, want)
				}
				for i, m := range want {
					if c.Modules[i] != m {
						t.Errorf("modules[%d] = %q, want %q", i, c.Modules[i], m)
					}
				}
			},
		},
		{
			name: "modules all empty normalized to nil",
			in:   Config{ClientID: "id", ClientSecret: "s", Modules: []string{"", "   "}},
			check: func(t *testing.T, c *Config) {
				if c.Modules != nil {
					t.Errorf("modules = %v, want nil", c.Modules)
				}
			},
		},
		{
			name: "user agent absent gets versioned prefix only",
			in:   valid,
			check: func(t *testing.T, c *Config) {
				want := "falcon-mcp/" + version.Version
				if c.UserAgent != want {
					t.Errorf("userAgent = %q, want %q", c.UserAgent, want)
				}
			},
		},
		{
			name: "user agent appended after versioned prefix and trimmed",
			in:   Config{ClientID: "id", ClientSecret: "s", UserAgent: "  my-tool/1.2  "},
			check: func(t *testing.T, c *Config) {
				want := "falcon-mcp/" + version.Version + " my-tool/1.2"
				if c.UserAgent != want {
					t.Errorf("userAgent = %q, want %q", c.UserAgent, want)
				}
			},
		},
		{
			name: "host override bare fqdn passes through",
			in:   Config{ClientID: "id", ClientSecret: "s", HostOverride: "api.us-2.crowdstrike.com"},
			check: func(t *testing.T, c *Config) {
				if c.HostOverride != "api.us-2.crowdstrike.com" {
					t.Errorf("hostOverride = %q, want bare fqdn", c.HostOverride)
				}
			},
		},
		{
			name: "host override strips scheme and path",
			in:   Config{ClientID: "id", ClientSecret: "s", HostOverride: "https://api.us-2.crowdstrike.com/some/path"},
			check: func(t *testing.T, c *Config) {
				if c.HostOverride != "api.us-2.crowdstrike.com" {
					t.Errorf("hostOverride = %q, want api.us-2.crowdstrike.com", c.HostOverride)
				}
			},
		},
		{
			name: "host override strips trailing slash",
			in:   Config{ClientID: "id", ClientSecret: "s", HostOverride: "  https://api.us-2.crowdstrike.com/  "},
			check: func(t *testing.T, c *Config) {
				if c.HostOverride != "api.us-2.crowdstrike.com" {
					t.Errorf("hostOverride = %q, want api.us-2.crowdstrike.com", c.HostOverride)
				}
			},
		},
		{
			name: "host override empty stays empty",
			in:   valid,
			check: func(t *testing.T, c *Config) {
				if c.HostOverride != "" {
					t.Errorf("hostOverride = %q, want empty", c.HostOverride)
				}
			},
		},
		{
			name: "proxy empty stays empty",
			in:   valid,
			check: func(t *testing.T, c *Config) {
				if c.Proxy != "" {
					t.Errorf("proxy = %q, want empty", c.Proxy)
				}
			},
		},
		{
			name: "proxy http accepted and trimmed",
			in:   Config{ClientID: "id", ClientSecret: "s", Proxy: "  http://proxy.example.com:8080  "},
			check: func(t *testing.T, c *Config) {
				if c.Proxy != "http://proxy.example.com:8080" {
					t.Errorf("proxy = %q, want trimmed http url", c.Proxy)
				}
			},
		},
		{
			name: "proxy https accepted",
			in:   Config{ClientID: "id", ClientSecret: "s", Proxy: "https://proxy.example.com:8443"},
			check: func(t *testing.T, c *Config) {
				if c.Proxy != "https://proxy.example.com:8443" {
					t.Errorf("proxy = %q, want https url", c.Proxy)
				}
			},
		},
		{
			name: "proxy socks5 accepted",
			in:   Config{ClientID: "id", ClientSecret: "s", Proxy: "socks5://proxy.example.com:1080"},
			check: func(t *testing.T, c *Config) {
				if c.Proxy != "socks5://proxy.example.com:1080" {
					t.Errorf("proxy = %q, want socks5 url", c.Proxy)
				}
			},
		},
		{
			name: "proxy with userinfo accepted",
			in:   Config{ClientID: "id", ClientSecret: "s", Proxy: "http://user:pass@proxy.example.com:8080"},
			check: func(t *testing.T, c *Config) {
				if c.Proxy != "http://user:pass@proxy.example.com:8080" {
					t.Errorf("proxy = %q, want url with userinfo", c.Proxy)
				}
			},
		},
		{
			name:    "proxy missing scheme rejected",
			in:      Config{ClientID: "id", ClientSecret: "s", Proxy: "proxy.example.com:8080"},
			wantErr: ErrInvalidProxy,
		},
		{
			name:    "proxy unsupported scheme rejected",
			in:      Config{ClientID: "id", ClientSecret: "s", Proxy: "ftp://proxy.example.com:8080"},
			wantErr: ErrInvalidProxy,
		},
		{
			name:    "proxy missing host rejected",
			in:      Config{ClientID: "id", ClientSecret: "s", Proxy: "http://"},
			wantErr: ErrInvalidProxy,
		},
		{
			name:    "proxy unparseable rejected",
			in:      Config{ClientID: "id", ClientSecret: "s", Proxy: "http://[::1"},
			wantErr: ErrInvalidProxy,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			c, err := Load(tt.in)
			if tt.wantErr != nil {
				if !errors.Is(err, tt.wantErr) {
					t.Fatalf("err = %v, want %v", err, tt.wantErr)
				}
				return
			}
			if tt.errSubstr != "" {
				if err == nil {
					t.Fatalf("expected error containing %q, got nil", tt.errSubstr)
				}
				if !strings.Contains(err.Error(), tt.errSubstr) {
					t.Fatalf("err = %v, want substring %q", err, tt.errSubstr)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected err: %v", err)
			}
			if tt.check != nil {
				tt.check(t, c)
			}
		})
	}
}
