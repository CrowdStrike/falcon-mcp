---
title: Custom IOA
description: Searching, creating, updating, and deleting Custom IOA (Indicators of Attack) behavioral rules and rule groups using Falcon Custom IOA Service Collection endpoints
sidebar:
  order: 10
---

Searching, creating, updating, and deleting Custom IOA (Indicators of Attack) behavioral rules and rule groups using Falcon Custom IOA Service Collection endpoints

## API Scopes

- `Custom IOA Rules:read`
- `Custom IOA Rules:write`

## Tools

### `falcon_create_ioa_rule`

:::note
This tool modifies data.
:::

**Required scopes:** `Custom IOA Rules:write`

Create a new Custom IOA behavioral detection rule within a rule group.

Before creating a rule:
1. Use `falcon_get_ioa_rule_types` to discover available rule types, their IDs,
   required fields, and valid disposition IDs.
2. Use `falcon_search_ioa_rule_groups` to find the target rule group ID.

The `field_values` parameter defines the behavioral criteria the rule will match
against (e.g., process names, file paths, command line patterns using regex).

**Example prompts:**

- "Add a process creation rule to IOA group abc123 that detects cmd.exe spawned from Word"

### `falcon_create_ioa_rule_group`

:::note
This tool modifies data.
:::

**Required scopes:** `Custom IOA Rules:write`

Create a new Custom IOA rule group.

Rule groups are containers that hold behavioral detection rules for a specific
platform. After creating a group, use `falcon_create_ioa_rule` to add detection
rules to it.

Use `falcon_get_ioa_platforms` to see available platform values.

**Example prompts:**

- "Create a Windows IOA rule group named 'Suspicious PowerShell Activity'"

### `falcon_delete_ioa_rule_groups`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `Custom IOA Rules:write`

Delete Custom IOA rule groups by ID.

This permanently removes the rule groups and all rules within them.
Use `falcon_search_ioa_rule_groups` to find rule group IDs.

**Example prompts:**

- "Delete Custom IOA rule groups abc123 and def456"

### `falcon_delete_ioa_rules`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `Custom IOA Rules:write`

Delete Custom IOA behavioral detection rules from a rule group.

Use `falcon_search_ioa_rule_groups` to find the rule group ID and
the individual rule IDs (instance IDs) to delete.

**Example prompts:**

- "Delete rules from IOA group abc123"

### `falcon_get_ioa_platforms`

**Required scopes:** `Custom IOA Rules:read`

Get all available platforms for Custom IOA rule groups.

Returns details about each available platform (e.g., windows, mac, linux).
Use this to discover valid platform values before creating a rule group.

**Example prompts:**

- "What platforms are available for Custom IOA rule groups?"

### `falcon_get_ioa_rule_types`

**Required scopes:** `Custom IOA Rules:read`

Get all available Custom IOA rule types.

Returns details about each rule type including its name, platform, fields,
and supported disposition IDs. Use this to discover valid rule type IDs and
required field values before creating a behavioral rule.

Rule types define the category of behavioral detection (e.g., Process Creation,
Network Connection, File Creation).

**Example prompts:**

- "What Custom IOA rule types are available?"

### `falcon_search_ioa_rule_groups`

**Required scopes:** `Custom IOA Rules:read`

Search Custom IOA rule groups and return full rule group details including their rules.

Rule groups are containers that hold behavioral detection rules. Each group is
associated with a specific platform (windows, mac, or linux).

**Example prompts:**

- "Find enabled Windows Custom IOA rule groups"

### `falcon_update_ioa_rule`

:::note
This tool modifies data.
:::

**Required scopes:** `Custom IOA Rules:write`

Update an existing Custom IOA behavioral detection rule.

The `rulegroup_version` is required for optimistic locking to prevent
concurrent modification conflicts. Use `falcon_search_ioa_rule_groups` to
retrieve the current version and instance ID.

**Example prompts:**

- "Enable IOA rule instance abc in group xyz"

### `falcon_update_ioa_rule_group`

:::note
This tool modifies data.
:::

**Required scopes:** `Custom IOA Rules:write`

Update an existing Custom IOA rule group.

You can modify the name, description, and enabled state of a rule group.
The `rulegroup_version` is required for optimistic locking to prevent
concurrent modification conflicts.

Use `falcon_search_ioa_rule_groups` to retrieve the current version number.

**Example prompts:**

- "Disable IOA rule group abc123"

## Resources

- **`falcon://custom-ioa/rule-groups/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_ioa_rule_groups` tool.
