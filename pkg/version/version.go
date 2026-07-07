// Package version exposes the falcon-mcp version string and builds the
// RFC-compliant User-Agent header sent to the Falcon API.
package version

import (
	"fmt"
	"runtime"
	"strings"

	"github.com/crowdstrike/gofalcon/falcon"
)

// Version is the falcon-mcp release version. It is overridable at build time
// via -ldflags "-X github.com/crowdstrike/falcon-mcp-go/pkg/version.Version=x.y.z".
var Version = "0.13.0"

// String returns the current falcon-mcp version.
func String() string {
	return Version
}

// UserAgent builds an RFC-compliant User-Agent string in the form:
//
//	falcon-mcp/VERSION (comment; gofalcon/VERSION; Go/VERSION; OS/Arch)
//
// The optional comment mirrors the Python --user-agent-comment flag.
func UserAgent(comment string) string {
	parts := make([]string, 0, 4)
	if c := strings.TrimSpace(comment); c != "" {
		parts = append(parts, c)
	}
	parts = append(parts,
		fmt.Sprintf("gofalcon/%s", falcon.Version.String()),
		fmt.Sprintf("Go/%s", strings.TrimPrefix(runtime.Version(), "go")),
		fmt.Sprintf("%s/%s", runtime.GOOS, runtime.GOARCH),
	)
	return fmt.Sprintf("falcon-mcp/%s (%s)", Version, strings.Join(parts, "; "))
}
