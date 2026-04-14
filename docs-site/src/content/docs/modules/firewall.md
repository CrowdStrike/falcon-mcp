---
title: Firewall Management
description: Searching and managing firewall rules and rule groups
sidebar:
  order: 10
---

Searching and managing firewall rules and rule groups

## API Scopes

- `Firewall Management:read`
- `Firewall Management:write`

## Tools

### `falcon_create_firewall_rule_group`

:::note
This tool modifies data.
:::

**Required scopes:** `Firewall Management:write`

Create a firewall rule group.

**Example prompts:**

- "Create a Windows firewall rule group named 'Prod Outbound'"

### `falcon_delete_firewall_rule_groups`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `Firewall Management:write`

Delete firewall rule groups by ID.

**Example prompts:**

- "Delete firewall rule group abc123"

### `falcon_search_firewall_policy_rules`

**Required scopes:** `Firewall Management:read`

Search firewall rules in a specific policy container and return full rule details.

**Example prompts:**

- "Show me all rules in firewall policy abc123"

### `falcon_search_firewall_rule_groups`

**Required scopes:** `Firewall Management:read`

Search firewall rule groups and return full rule group details.

**Example prompts:**

- "Find all enabled firewall rule groups for Windows"

### `falcon_search_firewall_rules`

**Required scopes:** `Firewall Management:read`

Search firewall rules and return full rule details.

**Example prompts:**

- "Show me all enabled Windows firewall rules"
- "Find firewall rules matching 'outbound'"

## Resources

- **`falcon://firewall/rules/fql-guide`**: Contains the guide for the `filter` param of firewall search tools.
