package detections

import _ "embed"

//go:generate go run github.com/crowdstrike/falcon-mcp/tools/genfqlguide -in fql_guide.md

// fqlGuideURI is the MCP resource URI for the detections FQL guide, matching
// falcon-mcp's falcon://detections/search/fql-guide.
const fqlGuideURI = "falcon://detections/search/fql-guide"

// fqlGuide is the FQL documentation for searching detections. It is served as
// the detections FQL guide resource and also returned inline inside FQL-error
// responses to guide filter correction. Whitespace in fql_guide.md is
// normalized by `go generate` (see the directive above).
//
//go:embed fql_guide.md
var fqlGuide string
