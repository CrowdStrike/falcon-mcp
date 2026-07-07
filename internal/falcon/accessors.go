package falcon

import (
	"github.com/crowdstrike/gofalcon/falcon/client/alerts"
	"github.com/crowdstrike/gofalcon/falcon/client/cases"
	"github.com/crowdstrike/gofalcon/falcon/client/correlation_rules"
	"github.com/crowdstrike/gofalcon/falcon/client/data_protection_configuration"
	"github.com/crowdstrike/gofalcon/falcon/client/discover"
	"github.com/crowdstrike/gofalcon/falcon/client/host_group"
	"github.com/crowdstrike/gofalcon/falcon/client/hosts"
	"github.com/crowdstrike/gofalcon/falcon/client/intel"
	"github.com/crowdstrike/gofalcon/falcon/client/ioc"
	"github.com/crowdstrike/gofalcon/falcon/client/quarantine"
	"github.com/crowdstrike/gofalcon/falcon/client/recon"
	"github.com/crowdstrike/gofalcon/falcon/client/report_executions"
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

// ReportExecutions returns the Report Executions service client.
func (c *FalconClient) ReportExecutions() report_executions.ClientService {
	return c.api.ReportExecutions
}

// Intel returns the Intel service client.
func (c *FalconClient) Intel() intel.ClientService { return c.api.Intel }

// Alerts returns the Alerts service client (used by the detections toolset).
func (c *FalconClient) Alerts() alerts.ClientService { return c.api.Alerts }

// IOC returns the IOC (indicator) service client.
func (c *FalconClient) IOC() ioc.ClientService { return c.api.Ioc }

// Quarantine returns the Quarantine service client.
func (c *FalconClient) Quarantine() quarantine.ClientService { return c.api.Quarantine }

// HostGroup returns the Host Group service client.
func (c *FalconClient) HostGroup() host_group.ClientService { return c.api.HostGroup }

// Cases returns the Cases service client.
func (c *FalconClient) Cases() cases.ClientService { return c.api.Cases }

// CorrelationRules returns the Correlation Rules service client.
func (c *FalconClient) CorrelationRules() correlation_rules.ClientService {
	return c.api.CorrelationRules
}

// DataProtectionConfiguration returns the Data Protection Configuration service client.
func (c *FalconClient) DataProtectionConfiguration() data_protection_configuration.ClientService {
	return c.api.DataProtectionConfiguration
}
