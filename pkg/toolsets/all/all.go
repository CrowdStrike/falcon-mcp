// Package all blank-imports every Falcon toolset package so that their init()
// functions register them with the toolsets registry. cmd/falcon-mcp imports
// this single package instead of listing each toolset individually.
//
// Toolset imports are added here as each module is implemented in later phases.
package all

import (
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/hosts"
)
