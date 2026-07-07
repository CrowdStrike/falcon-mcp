package falcon

import (
	"github.com/crowdstrike/gofalcon/falcon/client/certificate_based_exclusions"
	"github.com/crowdstrike/gofalcon/falcon/client/content_update_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/custom_ioa"
	"github.com/crowdstrike/gofalcon/falcon/client/device_control_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/firewall_management"
	"github.com/crowdstrike/gofalcon/falcon/client/firewall_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/ioa_exclusions"
	"github.com/crowdstrike/gofalcon/falcon/client/ml_exclusions"
	"github.com/crowdstrike/gofalcon/falcon/client/prevention_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/real_time_response"
	"github.com/crowdstrike/gofalcon/falcon/client/real_time_response_admin"
	"github.com/crowdstrike/gofalcon/falcon/client/real_time_response_audit"
	"github.com/crowdstrike/gofalcon/falcon/client/response_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/sensor_update_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/sensor_visibility_exclusions"
)

// Tier-3 accessors: exclusions (4 sub-clients), firewall (2), policies (6),
// custom_ioa, and RTR (3). Grouped in this file to keep accessors.go focused.

// IoaExclusions returns the IOA Exclusions service client.
func (c *FalconClient) IoaExclusions() ioa_exclusions.ClientService { return c.api.IoaExclusions }

// MlExclusions returns the ML Exclusions service client.
func (c *FalconClient) MlExclusions() ml_exclusions.ClientService { return c.api.MlExclusions }

// SensorVisibilityExclusions returns the Sensor Visibility Exclusions service client.
func (c *FalconClient) SensorVisibilityExclusions() sensor_visibility_exclusions.ClientService {
	return c.api.SensorVisibilityExclusions
}

// CertificateBasedExclusions returns the Certificate-Based Exclusions service client.
func (c *FalconClient) CertificateBasedExclusions() certificate_based_exclusions.ClientService {
	return c.api.CertificateBasedExclusions
}

// FirewallManagement returns the Firewall Management service client.
func (c *FalconClient) FirewallManagement() firewall_management.ClientService {
	return c.api.FirewallManagement
}

// FirewallPolicies returns the Firewall Policies service client.
func (c *FalconClient) FirewallPolicies() firewall_policies.ClientService {
	return c.api.FirewallPolicies
}

// PreventionPolicies returns the Prevention Policies service client.
func (c *FalconClient) PreventionPolicies() prevention_policies.ClientService {
	return c.api.PreventionPolicies
}

// SensorUpdatePolicies returns the Sensor Update Policies service client.
func (c *FalconClient) SensorUpdatePolicies() sensor_update_policies.ClientService {
	return c.api.SensorUpdatePolicies
}

// DeviceControlPolicies returns the Device Control Policies service client.
func (c *FalconClient) DeviceControlPolicies() device_control_policies.ClientService {
	return c.api.DeviceControlPolicies
}

// ResponsePolicies returns the Response Policies service client.
func (c *FalconClient) ResponsePolicies() response_policies.ClientService {
	return c.api.ResponsePolicies
}

// ContentUpdatePolicies returns the Content Update Policies service client.
func (c *FalconClient) ContentUpdatePolicies() content_update_policies.ClientService {
	return c.api.ContentUpdatePolicies
}

// CustomIOA returns the Custom IOA service client.
func (c *FalconClient) CustomIOA() custom_ioa.ClientService { return c.api.CustomIoa }

// RealTimeResponse returns the Real Time Response service client (read-only session ops).
func (c *FalconClient) RealTimeResponse() real_time_response.ClientService {
	return c.api.RealTimeResponse
}

// RealTimeResponseAdmin returns the RTR Admin service client (command execution).
func (c *FalconClient) RealTimeResponseAdmin() real_time_response_admin.ClientService {
	return c.api.RealTimeResponseAdmin
}

// RealTimeResponseAudit returns the RTR Audit service client.
func (c *FalconClient) RealTimeResponseAudit() real_time_response_audit.ClientService {
	return c.api.RealTimeResponseAudit
}
