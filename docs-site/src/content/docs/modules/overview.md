---
title: Module Overview
description: Overview of all available Falcon MCP modules with API scopes.
sidebar:
  order: 0
---

The Falcon MCP Server provides the following modules. Each module requires specific CrowdStrike API scopes.

| Module | API Scopes | Description |
|--------|-------------------|-------------|
| [Case Management](/falcon-mcp/modules/cases/) | `Case Templates:read`, `Cases:read`, `Cases:write` | Managing CrowdStrike cases, including searching, creating, updating, and managing evidence and tags |
| [Cloud Security](/falcon-mcp/modules/cloud/) | `Cloud Security API Assets:read`, `Cloud Security API Detections:read`, `Cloud Security Policies:read`, `Falcon Container Image:read`, `Cloud Security Policies:write` | Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets |
| [Correlation Rules](/falcon-mcp/modules/correlationrules/) | `Correlation Rules:read`, `Correlation Rules:write` | Correlation Rules module for CrowdStrike Falcon. |
| [Custom IOA](/falcon-mcp/modules/custom-ioa/) | `Custom IOA Rules:read`, `Custom IOA Rules:write` | Searching, creating, updating, and deleting Custom IOA (Indicators of Attack) behavioral rules and rule groups using Falcon Custom IOA Service Collection endpoints |
| [Data Protection](/falcon-mcp/modules/data-protection/) | `Data Protection:read` | Provides read-only access to Data Protection configuration data — classifications, policies, and content patterns — so an LLM can reason about why a Data Protection detection fired |
| [Detections](/falcon-mcp/modules/detections/) | `Alerts:read` | Accessing and analyzing CrowdStrike Falcon detections |
| [Discover](/falcon-mcp/modules/discover/) | `Assets:read` | Accessing and managing CrowdStrike Falcon Discover applications and unmanaged assets |
| [Firewall Management](/falcon-mcp/modules/firewall/) | `Firewall Management:read`, `Firewall Management:write` | Searching and managing firewall rules and rule groups |
| [Hosts](/falcon-mcp/modules/hosts/) | `Hosts:read` | Accessing and managing CrowdStrike Falcon hosts/devices |
| [Identity Protection](/falcon-mcp/modules/idp/) | `Identity Protection Assessment:read`, `Identity Protection Detections:read`, `Identity Protection Entities:read`, `Identity Protection Timeline:read`, `Identity Protection GraphQL:write` | Accessing and managing CrowdStrike Falcon Identity Protection capabilities |
| [Intel](/falcon-mcp/modules/intel/) | `Actors (Falcon Intelligence):read`, `Indicators (Falcon Intelligence):read`, `Reports (Falcon Intelligence):read` | Accessing and analyzing CrowdStrike Falcon intelligence data |
| [IOC](/falcon-mcp/modules/ioc/) | `IOC Management:read`, `IOC Management:write` | Searching, creating, and deleting custom IOCs using Falcon IOC Service Collection endpoints |
| [NGSIEM](/falcon-mcp/modules/ngsiem/) | `NGSIEM:read`, `NGSIEM:write` | Running search queries against CrowdStrike's Next-Gen SIEM via the asynchronous job-based search API |
| [Quarantine](/falcon-mcp/modules/quarantine/) | `Quarantined Files:read`, `Quarantined Files:write` | Investigating quarantined files and applying quarantine actions during triage and remediation workflows |
| [Real Time Response](/falcon-mcp/modules/rtr/) | `Real time response:read`, `real-time-response-audit:read`, `Real time response:write` | Initiating and inspecting RTR sessions and executing read-only RTR commands during host investigations |
| [Real Time Response Admin](/falcon-mcp/modules/rtr-admin/) | `Real time response (admin):write` | Inspect RTR Admin assets, classify command risk, preview payloads, and execute approved single-host admin workflows. |
| [Scheduled Reports](/falcon-mcp/modules/scheduled-reports/) | `Scheduled Reports:read` | Accessing and managing CrowdStrike Falcon scheduled reports and scheduled searches |
| [Sensor Usage](/falcon-mcp/modules/sensor-usage/) | `Sensor Usage:read` | Accessing CrowdStrike Falcon sensor usage data |
| [Serverless](/falcon-mcp/modules/serverless/) | `Falcon Container Image:read` | Accessing and managing CrowdStrike Falcon Serverless Vulnerabilities |
| [Shield](/falcon-mcp/modules/shield/) | `SaaS Security:read`, `SaaS Security:write` | Shield module for CrowdStrike Falcon. |
| [Spotlight](/falcon-mcp/modules/spotlight/) | `Vulnerabilities:read` | Accessing and managing CrowdStrike Falcon Spotlight vulnerabilities |
