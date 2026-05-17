---
title: Sensor Usage
description: Accessing CrowdStrike Falcon sensor usage data
sidebar:
  order: 10
---

Accessing CrowdStrike Falcon sensor usage data

## API Scopes

- `Sensor Usage:read`

## Tools

### `falcon_search_sensor_usage`

**Required scopes:** `Sensor Usage:read`

Search for weekly sensor usage data in your CrowdStrike environment.

Use this to retrieve sensor billing and usage metrics by date or period. Consult
falcon://sensor-usage/weekly/fql-guide before constructing filter expressions.
Returns weekly usage records.

**Example prompts:**

- "Show me sensor usage data for the week of 2024-06-11"

## Resources

- **`falcon://sensor-usage/weekly/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_sensor_usage` tool.
