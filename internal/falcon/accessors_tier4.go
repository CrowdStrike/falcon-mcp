package falcon

import (
	"github.com/crowdstrike/gofalcon/falcon/client/cloud_policies"
	"github.com/crowdstrike/gofalcon/falcon/client/cloud_security_assets"
	"github.com/crowdstrike/gofalcon/falcon/client/cloud_security_detections"
	"github.com/crowdstrike/gofalcon/falcon/client/container_vulnerabilities"
	"github.com/crowdstrike/gofalcon/falcon/client/identity_protection"
	"github.com/crowdstrike/gofalcon/falcon/client/kubernetes_protection"
	"github.com/crowdstrike/gofalcon/falcon/client/ngsiem"
	"github.com/crowdstrike/gofalcon/falcon/client/saas_security"
)

// Tier-4 accessors: cloud (5 sub-clients), ngsiem, idp.

// KubernetesProtection returns the Kubernetes Protection service client.
func (c *FalconClient) KubernetesProtection() kubernetes_protection.ClientService {
	return c.api.KubernetesProtection
}

// ContainerVulnerabilities returns the Container Vulnerabilities service client.
func (c *FalconClient) ContainerVulnerabilities() container_vulnerabilities.ClientService {
	return c.api.ContainerVulnerabilities
}

// CloudSecurityAssets returns the Cloud Security Assets (CSPM assets) service client.
func (c *FalconClient) CloudSecurityAssets() cloud_security_assets.ClientService {
	return c.api.CloudSecurityAssets
}

// CloudSecurityDetections returns the Cloud Security Detections (CSPM IOM) service client.
func (c *FalconClient) CloudSecurityDetections() cloud_security_detections.ClientService {
	return c.api.CloudSecurityDetections
}

// CloudPolicies returns the Cloud Policies service client (CSPM suppression rules).
func (c *FalconClient) CloudPolicies() cloud_policies.ClientService { return c.api.CloudPolicies }

// Ngsiem returns the NGSIEM service client.
func (c *FalconClient) Ngsiem() ngsiem.ClientService { return c.api.Ngsiem }

// IdentityProtection returns the Identity Protection service client (GraphQL).
func (c *FalconClient) IdentityProtection() identity_protection.ClientService {
	return c.api.IdentityProtection
}

// SaasSecurity returns the SaaS Security (Shield) service client.
func (c *FalconClient) SaasSecurity() saas_security.ClientService { return c.api.SaasSecurity }
