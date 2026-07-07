// Package fql embeds the Falcon Query Language guide documents and serves them
// as MCP resources. The guide text is copied verbatim (at build time, via a
// generator) from the Python falcon_mcp/resources/*.py constants; each guide is
// exposed at its falcon://<module>/<path>/fql-guide URI.
package fql

import (
	"embed"
	"fmt"
	"io/fs"
	"strings"
)

//go:embed guides/*.md
var guidesFS embed.FS

// uriToFilename converts a resource URI to its embedded filename, matching the
// generator's scheme: "falcon://hosts/search/fql-guide" ->
// "guides/hosts_search_fql-guide.md".
func uriToFilename(uri string) string {
	rest := strings.TrimPrefix(uri, "falcon://")
	return "guides/" + strings.ReplaceAll(rest, "/", "_") + ".md"
}

// Guide returns the embedded guide text for the given resource URI.
func Guide(uri string) (string, error) {
	data, err := guidesFS.ReadFile(uriToFilename(uri))
	if err != nil {
		return "", fmt.Errorf("fql guide not found for %q: %w", uri, err)
	}
	return string(data), nil
}

// MustGuide returns the guide text for uri, panicking if it is missing. It is
// intended for use at toolset-registration time with compile-time-known URIs.
func MustGuide(uri string) string {
	text, err := Guide(uri)
	if err != nil {
		panic(err)
	}
	return text
}

// URIs returns the resource URIs of all embedded guides, for validation/tests.
func URIs() ([]string, error) {
	entries, err := fs.ReadDir(guidesFS, "guides")
	if err != nil {
		return nil, err
	}
	uris := make([]string, 0, len(entries))
	for _, e := range entries {
		name := strings.TrimSuffix(e.Name(), ".md")
		uris = append(uris, "falcon://"+strings.ReplaceAll(name, "_", "/"))
	}
	return uris, nil
}
