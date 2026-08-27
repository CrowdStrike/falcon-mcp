<!-- meta:title Module Overview -->
<!-- meta:description Overview of all available Falcon MCP modules with API scopes. -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:0 -->

The Falcon MCP Server provides the following modules. Each module requires specific CrowdStrike API scopes.

| Module | API Scopes | Description |
|--------|-------------------|-------------|
| [AgentWorks](/falcon-mcp/modules/agentworks/) | `Charlotte AI Agent Definition:read`, `Charlotte AI Agent Definition:write` | Calling, listing, and observing CrowdStrike AgentWorks (agentic-studio) Charlotte AI agents and their execution traces |
| [Case Management](/falcon-mcp/modules/cases/) | `Case Templates:read`, `Cases:read`, `Cases:write` | Managing CrowdStrike cases, including searching, creating, updating, and managing evidence and tags |
| [Cloud Security](/falcon-mcp/modules/cloud/) | `Cloud Groups V2:read`, `Cloud Security API Assets:read`, `Cloud Security API Detections:read`, `Cloud Security API Risks:read`, `Cloud Security Policies:read`, `Falcon Container Image:read`, `Cloud Security Policies:write` | Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets, IOM Findings, CSPM Suppression Rules, Cloud Risks, Cloud Groups, and Cloud Insights |
| [Correlation Rules](/falcon-mcp/modules/correlationrules/) | `Correlation Rules:read`, `Correlation Rules:write` | Correlation Rules module for CrowdStrike Falcon. |
| [Custom IOA](/falcon-mcp/modules/custom-ioa/) | `Custom IOA Rules:read`, `Custom IOA Rules:write` | Searching, creating, updating, and deleting Custom IOA (Indicators of Attack) behavioral rules and rule groups using Falcon Custom IOA Service Collection endpoints |
| [Data Protection](/falcon-mcp/modules/data-protection/) | `Data Protection:read` | Provides read-only access to Data Protection configuration data — classifications, policies, and content patterns — so an LLM can reason about why a Data Protection detection fired |
| [Detections](/falcon-mcp/modules/detections/) | `Alerts:read`, `Alerts:write` | Accessing and analyzing CrowdStrike Falcon detections |
| [Discover](/falcon-mcp/modules/discover/) | `Assets:read` | Accessing and managing CrowdStrike Falcon Discover applications, managed assets, and unmanaged assets |
| [Exclusions](/falcon-mcp/modules/exclusions/) | `IOA Exclusions:read`, `Machine Learning Exclusions:read`, `Sensor Visibility Exclusions:read`, `IOA Exclusions:write`, `Machine Learning Exclusions:write`, `Sensor Visibility Exclusions:write` | This module provides a unified set of tools for managing CrowdStrike exclusions across four types — IOA, Machine Learning, Sensor Visibility, and Certificate-Based — behind a single `exclusion_type` discriminator |
| [Firewall Management](/falcon-mcp/modules/firewall/) | `Firewall Management:read`, `Firewall Management:write` | Searching and managing firewall rules and rule groups |
| [Fusion SOAR](/falcon-mcp/modules/fusion/) | `Workflows:read`, `Workflows:write` | Searching Fusion SOAR workflow definitions and executions, reading what an execution produced, and running an on-demand workflow |
| [Host Groups](/falcon-mcp/modules/host-groups/) | `Host Groups:read`, `Host Groups:write` | Searching, creating, updating, and deleting CrowdStrike Falcon host groups, as well as managing group membership |
| [Hosts](/falcon-mcp/modules/hosts/) | `Hosts:read`, `Hosts:write` | Accessing and managing CrowdStrike Falcon hosts/devices |
| [Identity Protection](/falcon-mcp/modules/idp/) | `Identity Protection Assessment:read`, `Identity Protection Detections:read`, `Identity Protection Entities:read`, `Identity Protection Timeline:read`, `Identity Protection GraphQL:write` | Accessing and managing CrowdStrike Falcon Identity Protection capabilities |
| [Intel](/falcon-mcp/modules/intel/) | `Actors (Falcon Intelligence):read`, `Indicators (Falcon Intelligence):read`, `Reports (Falcon Intelligence):read` | Accessing and analyzing CrowdStrike Falcon intelligence data |
| [IOC](/falcon-mcp/modules/ioc/) | `IOC Management:read`, `IOC Management:write` | Searching, creating, and deleting custom IOCs using Falcon IOC Service Collection endpoints |
| [NGSIEM](/falcon-mcp/modules/ngsiem/) | `NGSIEM:read`, `NGSIEM:write` | Running search queries against CrowdStrike's Next-Gen SIEM via the asynchronous job-based search API |
| [Policies](/falcon-mcp/modules/policies/) | `Content Update Policies:read`, `Device Control Policies:read`, `Firewall Management:read`, `Prevention Policies:read`, `Response Policies:read`, `Sensor Update Policies:read`, `Content Update Policies:write`, `Device Control Policies:write`, `Firewall Management:write`, `Prevention Policies:write`, `Response Policies:write`, `Sensor Update Policies:write` | This module provides a unified set of tools for managing CrowdStrike host-based policies across all six policy types — prevention, sensor_update, firewall, device_control, response, and content_update — behind a single `policy_type` discriminator |
| [Quarantine](/falcon-mcp/modules/quarantine/) | `Quarantined Files:read`, `Quarantined Files:write` | Investigating quarantined files and applying quarantine actions during triage and remediation workflows |
| [Recon](/falcon-mcp/modules/recon/) | `Monitoring rules (Falcon Intelligence Recon):read` | Searching Falcon Intelligence Recon notifications, monitoring rules, and exposed-data records |
| [Real Time Response](/falcon-mcp/modules/rtr/) | `Real time response:read`, `real-time-response-audit:read`, `Real time response:write` | Initiating and inspecting RTR sessions and for executing read-only RTR commands during host investigations |
| [Scheduled Reports](/falcon-mcp/modules/scheduled-reports/) | `Scheduled Reports:read` | Accessing and managing CrowdStrike Falcon scheduled reports and scheduled searches |
| [Sensor Usage](/falcon-mcp/modules/sensor-usage/) | `Sensor Usage:read` | Accessing CrowdStrike Falcon sensor usage data |
| [Serverless](/falcon-mcp/modules/serverless/) | `Falcon Container Image:read` | Accessing and managing CrowdStrike Falcon Serverless Vulnerabilities |
| [Shield](/falcon-mcp/modules/shield/) | `SaaS Security:read`, `SaaS Security:write` | Shield module for CrowdStrike Falcon. |
| [Spotlight](/falcon-mcp/modules/spotlight/) | `Vulnerabilities:read` | Accessing and managing CrowdStrike Falcon Spotlight vulnerabilities |
| [Zero Trust Assessment](/falcon-mcp/modules/zero-trust-assessment/) | `Zero Trust Assessment:read` | Retrieving Zero Trust Assessment posture scores and sensor and OS hardening signals for hosts |

## CrowdStrike-hosted MCP differences

> [!NOTE]
> This section compares this self-hosted server against CrowdStrike's hosted Falcon MCP. Skip it unless you also use the hosted MCP, or are moving between the two.

The two servers differ in how a client reaches a tool. The hosted Falcon MCP works through discovery: a client calls `search_tools` to find a Falcon tool by name or keyword, then `execute_tool` to run it with arguments. The self-hosted falcon-mcp server registers each `falcon_*` tool up front instead, so a client calls one by name with no discovery round-trip.

If you self-host and want the same discovery pattern, enable [dynamic mode](/falcon-mcp/usage/dynamic-mode/): it swaps the full tool surface for `falcon_search_tools`, `falcon_execute_tool`, and an always-on `falcon_list_enabled_tools` inventory. Mind the `falcon_` prefix — those three are the self-hosted falcon-mcp server's tools, not the hosted MCP's.

Module and tool coverage also differs:

- [Fusion SOAR](/falcon-mcp/modules/fusion/), [Zero Trust Assessment](/falcon-mcp/modules/zero-trust-assessment/), and [Real Time Response](/falcon-mcp/modules/rtr/) are available only on this self-hosted server; the hosted MCP has no equivalent modules.
- [Cloud Security](/falcon-mcp/modules/cloud/): `falcon_search_cloud_insights`, `falcon_list_cloud_insight_definitions`, and `falcon_get_cloud_asset_insights` are not available on the hosted MCP.
- [Discover](/falcon-mcp/modules/discover/): `falcon_search_managed_assets` is not available on the hosted MCP.
- [Policies](/falcon-mcp/modules/policies/): the hosted MCP does not use the unified `policy_type`-discriminated tools. It instead exposes six policy-type-specific variants of each tool (for example `falcon_search_policies_firewall`, `falcon_create_policy_prevention`).
