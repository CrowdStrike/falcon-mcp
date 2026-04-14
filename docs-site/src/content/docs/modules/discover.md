---
title: Discover
description: Accessing and managing CrowdStrike Falcon Discover applications and unmanaged assets
sidebar:
  order: 10
---

Accessing and managing CrowdStrike Falcon Discover applications and unmanaged assets

## API Scopes

- `Assets:read`

## Tools

### `falcon_search_applications`

**Required scopes:** `Assets:read`

Search for applications in your CrowdStrike environment.

**Example prompts:**

- "Find all Chrome installations across my environment"

### `falcon_search_unmanaged_assets`

**Required scopes:** `Assets:read`

Search for unmanaged assets (hosts) in your CrowdStrike environment.

These are systems that do not have the Falcon sensor installed but have been
discovered by systems that do have a Falcon sensor installed.

The tool automatically filters for unmanaged assets only by adding entity_type:'unmanaged' to all queries.
You do not need to (and cannot) specify entity_type in your filter - it is always set to 'unmanaged'.

**Example prompts:**

- "Show me unmanaged Windows devices on the network"

## Resources

- **`falcon://discover/applications/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_applications` tool.
- **`falcon://discover/hosts/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_unmanaged_assets` tool.
