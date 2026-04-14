---
title: Cloud Security
description: Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets
sidebar:
  order: 10
---

Accessing and analyzing CrowdStrike Falcon cloud resources like Kubernetes & Containers Inventory, Images Vulnerabilities, Cloud Assets

## API Scopes

- `Cloud Security API Assets:read`
- `Falcon Container Image:read`

## Tools

### `falcon_count_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Count kubernetes containers in your CrowdStrike Kubernetes & Containers Inventory

**Example prompts:**

- "How many containers are running in Azure?"

### `falcon_search_cspm_assets`

**Required scopes:** `Cloud Security API Assets:read`

Search for cloud assets in your CrowdStrike CSPM Asset Inventory.

This tool queries cloud resources (EC2 instances, VPCs, subnets, load balancers, etc.)
managed by CrowdStrike CSPM. Supports comprehensive FQL filtering including:
- Cloud provider and resource type filtering
- Tag-based filtering (AWS/Azure/GCP tags)
- Security posture (publicly exposed, severity, IOM/IOA counts)
- Compliance status and benchmarks
- Temporal filtering (creation time, last updated)

**Example prompts:**

- "Find all AWS EC2 instances in my cloud inventory"

### `falcon_search_images_vulnerabilities`

**Required scopes:** `Falcon Container Image:read`

Search for images vulnerabilities in your CrowdStrike Image Assessments

**Example prompts:**

- "Find image vulnerabilities with CVSS score above 7"

### `falcon_search_kubernetes_containers`

**Required scopes:** `Falcon Container Image:read`

Search for kubernetes containers in your CrowdStrike Kubernetes & Containers Inventory

**Example prompts:**

- "Find all containers running in AWS clusters"
- "Show me containers in the prod cluster"

## Resources

- **`falcon://cloud/kubernetes-containers/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_kubernetes_containers` and `falcon_count_kubernetes_containers` tools.
- **`falcon://cloud/images-vulnerabilities/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_images_vulnerabilities` tool.
- **`falcon://cloud/cspm-assets/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_cspm_assets` tool.
