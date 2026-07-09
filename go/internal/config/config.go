// Package config defines the falcon-mcp server configuration and its
// precedence rules: defaults are overridden by environment variables, which are
// overridden by explicitly-set command-line flags.
package config

import (
	"fmt"
	"strings"
)

// Config holds all server settings. It is populated once at startup and is
// immutable thereafter.
type Config struct {
	Transport        string
	Modules          []string
	Debug            bool
	BaseURL          string
	Host             string
	Port             int
	UserAgentComment string
	StatelessHTTP    bool
	APIKey           string
	MemberCID        string
	Proxy            string
	Dynamic          bool
	ReadOnly         bool

	ClientID     string
	ClientSecret string
}

// Defaults returns a Config populated with the built-in default values, before
// any environment or flag overrides are applied.
func Defaults() Config {
	return Config{
		Transport: "stdio",
		BaseURL:   "https://api.crowdstrike.com",
		Host:      "127.0.0.1",
		Port:      8000,
	}
}

// Validate checks that required fields are present. Credentials are mandatory.
func (c *Config) Validate() error {
	if c.ClientID == "" || c.ClientSecret == "" {
		return fmt.Errorf("falcon: API credentials are required: set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET (or pass --client-id/--client-secret)")
	}
	return nil
}

// ParseModules splits a comma-separated module list into slugs, trimming
// whitespace and dropping empty entries. An empty string yields nil (meaning
// "all modules").
func ParseModules(s string) []string {
	if strings.TrimSpace(s) == "" {
		return nil
	}
	var out []string
	for part := range strings.SplitSeq(s, ",") {
		if slug := strings.TrimSpace(part); slug != "" {
			out = append(out, slug)
		}
	}
	return out
}
