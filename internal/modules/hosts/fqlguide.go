package hosts

import _ "embed"

//go:generate go run github.com/crowdstrike/falcon-mcp/tools/genfqlguide -in fql_guide.md

// fqlGuide is the FQL documentation for searching hosts, served as the hosts
// FQL guide resource. Whitespace in fql_guide.md is normalized by
// `go generate` (see the directive above).
//
//go:embed fql_guide.md
var fqlGuide string
