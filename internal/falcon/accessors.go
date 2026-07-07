package falcon

import (
	"github.com/crowdstrike/gofalcon/falcon/client/discover"
	"github.com/crowdstrike/gofalcon/falcon/client/hosts"
	"github.com/crowdstrike/gofalcon/falcon/client/intel"
	"github.com/crowdstrike/gofalcon/falcon/client/recon"
	"github.com/crowdstrike/gofalcon/falcon/client/scheduled_reports"
	"github.com/crowdstrike/gofalcon/falcon/client/sensor_usage_api"
	"github.com/crowdstrike/gofalcon/falcon/client/serverless_vulnerabilities"
	"github.com/crowdstrike/gofalcon/falcon/client/spotlight_vulnerabilities"
)

// Domain accessors expose the concrete gofalcon sub-clients. Each toolset
// declares its own narrow interface over only the operations it calls and
// accepts the value returned here — this keeps handlers unit-testable with
// hand-written mocks while the accessor itself stays a trivial passthrough.

// Hosts returns the Hosts service client.
func (c *FalconClient) Hosts() hosts.ClientService { return c.api.Hosts }

// Discover returns the Discover service client.
func (c *FalconClient) Discover() discover.ClientService { return c.api.Discover }

// SensorUsage returns the Sensor Usage service client.
func (c *FalconClient) SensorUsage() sensor_usage_api.ClientService { return c.api.SensorUsageAPI }

// ServerlessVulnerabilities returns the Serverless Vulnerabilities service client.
func (c *FalconClient) ServerlessVulnerabilities() serverless_vulnerabilities.ClientService {
	return c.api.ServerlessVulnerabilities
}

// SpotlightVulnerabilities returns the Spotlight Vulnerabilities service client.
func (c *FalconClient) SpotlightVulnerabilities() spotlight_vulnerabilities.ClientService {
	return c.api.SpotlightVulnerabilities
}

// Recon returns the Falcon Intelligence Recon service client.
func (c *FalconClient) Recon() recon.ClientService { return c.api.Recon }

// ScheduledReports returns the Scheduled Reports service client.
func (c *FalconClient) ScheduledReports() scheduled_reports.ClientService {
	return c.api.ScheduledReports
}

// Intel returns the Intel service client.
func (c *FalconClient) Intel() intel.ClientService { return c.api.Intel }
