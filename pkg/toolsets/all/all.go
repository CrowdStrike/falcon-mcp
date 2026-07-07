// Package all blank-imports every Falcon toolset package so that their init()
// functions register them with the toolsets registry. cmd/falcon-mcp imports
// this single package instead of listing each toolset individually.
//
// Toolset imports are added here as each module is implemented in later phases.
package all

import (
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/correlation_rules"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/data_protection"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/detections"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/discover"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/host_groups"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/hosts"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/intel"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/ioc"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/quarantine"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/recon"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/scheduled_reports"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/sensor_usage"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/serverless"
	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/spotlight"
)
