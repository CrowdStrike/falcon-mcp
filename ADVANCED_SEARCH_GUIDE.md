# 🔍 Advanced Host Search Guide

This guide provides comprehensive documentation for the `search_hosts_advanced` MCP tool, which enables powerful host searching using Falcon Query Language (FQL) with 30+ searchable properties.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Falcon Query Language (FQL) Reference](#falcon-query-language-fql-reference)
4. [Searchable Properties](#searchable-properties)
5. [Practical Examples](#practical-examples)
6. [Advanced Techniques](#advanced-techniques)
7. [Performance Tips](#performance-tips)
8. [Troubleshooting](#troubleshooting)

## Overview

The `search_hosts_advanced` tool provides comprehensive host search functionality that goes far beyond simple hostname or ID lookups. It supports:

- **30+ searchable properties** covering all aspects of host information
- **Falcon Query Language (FQL)** with full operator support
- **Complex filtering** with AND, OR, and grouping operations
- **Flexible output formats** from summary tables to full host details
- **Smart analysis** including platform distribution and activity insights
- **High performance** with results up to 5,000 hosts

## Quick Start

### Basic Usage

```python
# Find all Windows hosts
search_hosts_advanced("platform_name:'Windows'")

# Find hosts not seen recently (30+ days ago)
search_hosts_advanced("last_seen:<'2024-01-01T00:00:00Z'")

# Get all hosts (up to limit) with summary info
search_hosts_advanced("", limit=500)
```

### Tool Parameters

```python
search_hosts_advanced(
    query_filter="",              # FQL filter expression
    limit=100,                    # Max results (1-5000)
    sort="hostname.asc",          # Sort expression
    fields="",                    # Specific fields to return
    include_details=False         # Full details vs summary
)
```

## Falcon Query Language (FQL) Reference

### Basic Syntax

```
property_name:[operator]'value'
```

### Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| (none) | Equals | `hostname:'web-01'` |
| `!` | Not equal | `platform_name:!'Linux'` |
| `>` | Greater than | `last_seen:>'2024-01-15T00:00:00Z'` |
| `>=` | Greater than or equal | `agent_version:>='7.0.0'` |
| `<` | Less than | `first_seen:<'2024-01-01T00:00:00Z'` |
| `<=` | Less than or equal | `last_seen:<='2024-01-10T00:00:00Z'` |
| `~` | Text match (fuzzy) | `hostname:~'server'` |
| `!~` | Does not text match | `hostname:!~'test'` |
| `*` | Wildcard | `hostname:'web*'` |

### Data Types & Syntax

| Type | Syntax | Example |
|------|--------|---------|
| String | `'value'` | `hostname:'web-server'` |
| Exact String | `['value']` | `hostname:['web-server']` |
| Date (UTC) | `'YYYY-MM-DDTHH:MM:SSZ'` | `last_seen:'2024-01-15T12:00:00Z'` |
| Boolean | `true` or `false` | `some_flag:true` |
| Number | `123` | `some_count:>10` |
| Wildcard | `'partial*'` | `hostname:'app*'` |
| IP with wildcards | Use `.raw` property | `local_ip.raw:*'192.168.*'` |

### Combining Conditions

| Operator | Purpose | Example |
|----------|---------|---------|
| `+` | AND | `platform_name:'Windows'+status:'normal'` |
| `,` | OR | `status:'contained',status:'containment_pending'` |
| `()` | Grouping | `(hostname:'web*'),(hostname:'db*'+platform_name:'Linux')` |

## Searchable Properties

### Identity & Basic Info
- `device_id` - Host unique identifier (AID)
- `hostname` - Machine hostname (supports wildcards)
- `computer_name` - Computer display name
- `serial_number` - Hardware serial number
- `mac_address` - Network MAC address

### System Information
- `platform_name` - OS platform (Windows, Mac, Linux)
- `os_version` - Operating system version
- `major_version` - OS major version number
- `minor_version` - OS minor version number
- `system_manufacturer` - Hardware manufacturer (e.g., "Dell Inc.", "VMware, Inc.")
- `system_product_name` - System model/product name
- `bios_manufacturer` - BIOS manufacturer
- `bios_version` - BIOS version
- `cpu_signature` - CPU type/signature

### Network Information
- `local_ip` - Internal IP address
- `local_ip.raw` - Internal IP with wildcard support
- `external_ip` - External/public IP address
- `machine_domain` - Active Directory domain
- `ou` - Organizational Unit
- `site_name` - AD site name

### Agent & Configuration
- `agent_version` - Falcon agent version
- `agent_load_flags` - Agent configuration flags
- `config_id_base` - Configuration base ID
- `config_id_build` - Configuration build ID
- `config_id_platform` - Platform configuration ID
- `platform_id` - Platform identifier
- `product_type_desc` - Product type description
- `release_group` - Sensor deployment group

### Status & Timestamps
- `status` - Host status (normal, containment_pending, contained, lift_containment_pending)
- `first_seen` - First connection timestamp
- `last_seen` - Most recent connection timestamp
- `last_login_timestamp` - User login timestamp
- `modified_timestamp` - Last record update timestamp

### Specialized Properties
- `reduced_functionality_mode` - RFM status (yes, no, blank for unknown)
- `linux_sensor_mode` - Linux mode (Kernel Mode, User Mode)
- `deployment_type` - Linux deployment (Standard, DaemonSet)
- `tags` - Falcon grouping tags

## Practical Examples

### Network-Based Searches

```python
# Find hosts in specific IP subnet
search_hosts_advanced("local_ip.raw:*'192.168.1.*'")

# Find hosts by external IP
search_hosts_advanced("external_ip:'203.0.113.45'")

# Find hosts in specific domain
search_hosts_advanced("machine_domain:'contoso.com'")

# Find hosts with private IPs in external_ip (suspicious)
search_hosts_advanced("external_ip.raw:*'10.*'")
```

### Time-Based Searches

```python
# Find hosts not seen in last 30 days
search_hosts_advanced("last_seen:<'2024-01-01T00:00:00Z'")

# Find recently joined hosts (last 7 days)  
search_hosts_advanced("first_seen:>'2024-01-15T00:00:00Z'")

# Find hosts with recent configuration changes
search_hosts_advanced("modified_timestamp:>'2024-01-15T00:00:00Z'")
```

### Status & Health Searches

```python
# Find contained hosts
search_hosts_advanced("status:'contained'")

# Find all unhealthy hosts (contained or pending)
search_hosts_advanced("(status:'contained'),(status:'containment_pending')")

# Find hosts in reduced functionality mode
search_hosts_advanced("reduced_functionality_mode:'yes'")

# Find offline hosts (not seen in 24 hours)
search_hosts_advanced("last_seen:<'2024-01-20T00:00:00Z'")
```

### System Specification Searches

```python
# Find all Linux hosts
search_hosts_advanced("platform_name:'Linux'")

# Find VMware virtual machines
search_hosts_advanced("system_manufacturer:'VMware, Inc.'")

# Find specific OS version
search_hosts_advanced("os_version:'Windows Server 2019'")

# Find hosts with old agent versions
search_hosts_advanced("agent_version:<'7.0.0'")
```

### Infrastructure & Inventory

```python
# Find all web servers (by hostname pattern)
search_hosts_advanced("hostname:'web*'")

# Find domain controllers
search_hosts_advanced("hostname:'dc-*'+platform_name:'Windows'")

# Find database servers
search_hosts_advanced("hostname:'db-*'")

# Find untagged hosts (compliance check)
search_hosts_advanced("tags:!*")

# Find hosts with specific tags
search_hosts_advanced("tags:'production'")
```

## Advanced Techniques

### Complex Multi-Criteria Searches

```python
# Production Windows servers that are healthy and recently active
search_hosts_advanced("platform_name:'Windows'+hostname:'prod-*'+status:'normal'+last_seen:>'2024-01-15T00:00:00Z'")

# Critical infrastructure (domain controllers OR database servers)
search_hosts_advanced("(hostname:'dc-*'+platform_name:'Windows'),(hostname:'db-*')")

# Hosts needing attention (old, offline, or contained)
search_hosts_advanced("(last_seen:<'2024-01-10T00:00:00Z'),(status:'contained'),(agent_version:<'6.0.0')")

# Development vs production separation
search_hosts_advanced("hostname:!'dev-*'+hostname:!'test-*'+status:'normal'")
```

### Exclusion Patterns

```python
# All Windows hosts except test systems
search_hosts_advanced("platform_name:'Windows'+hostname:!'test-*'")

# Healthy hosts (exclude all problem states)
search_hosts_advanced("status:!'contained'+status:!'containment_pending'+reduced_functionality_mode:!'yes'")

# Physical hosts only (exclude VMs)
search_hosts_advanced("system_manufacturer:!'VMware, Inc.'+system_manufacturer:!'Microsoft Corporation'")
```

### Performance Optimization

```python
# Large inventory scan - just key fields
search_hosts_advanced("", limit=5000, fields="hostname,device_id,platform_name,last_seen,status")

# Quick counts by sorting and limiting
search_hosts_advanced("platform_name:'Windows'", limit=1, sort="hostname.asc")

# Get most recently active hosts first
search_hosts_advanced("status:'normal'", limit=100, sort="last_seen.desc")
```

### Output Customization

```python
# Summary table view (default)
search_hosts_advanced("platform_name:'Linux'", limit=50)

# Full details for analysis (slower)
search_hosts_advanced("status:'contained'", limit=10, include_details=True)

# Custom field selection
search_hosts_advanced("hostname:'web*'", fields="hostname,local_ip,last_seen,agent_version")

# Sorted results
search_hosts_advanced("platform_name:'Windows'", sort="last_seen.desc", limit=25)
```

## Performance Tips

### Optimizing Large Searches

1. **Use specific filters** - Narrow your search criteria to reduce result sets
2. **Limit results appropriately** - Don't request more hosts than you need
3. **Use field selection** - Specify only needed fields for faster responses
4. **Avoid include_details=True** for large result sets - Use for small, focused searches only

### Efficient Filtering

```python
# Good: Specific platform filter
search_hosts_advanced("platform_name:'Windows'+hostname:'prod-*'")

# Better: Add time constraints
search_hosts_advanced("platform_name:'Windows'+hostname:'prod-*'+last_seen:>'2024-01-15T00:00:00Z'")

# Best: Combine with status for health checks
search_hosts_advanced("platform_name:'Windows'+hostname:'prod-*'+status:'normal'+last_seen:>'2024-01-15T00:00:00Z'")
```

### Batch Processing

```python
# Process large inventories in chunks
for offset in range(0, 10000, 1000):
    results = search_hosts_advanced("platform_name:'Linux'", limit=1000, sort="hostname.asc")
    # Process this batch
```

## Troubleshooting

### Common Issues

**No results returned:**
- Check filter syntax - use single quotes around string values
- Verify property names are correct (see full list above)
- Try broader searches to ensure data exists
- Use wildcard searches for partial matches

**Syntax errors:**
- Ensure proper quoting: `hostname:'value'` not `hostname:"value"`
- Check operator placement: `property:!'value'` not `property!:'value'`
- Verify date format: `'YYYY-MM-DDTHH:MM:SSZ'` in UTC
- Balance parentheses in complex expressions

**Performance issues:**
- Reduce result limits for exploratory searches
- Use field selection to minimize data transfer
- Add specific filters to narrow scope
- Avoid include_details=True for large result sets

### Debugging Tips

```python
# Start simple and add complexity
search_hosts_advanced("hostname:'web-01'")  # Test basic connectivity
search_hosts_advanced("hostname:'web*'")    # Test wildcard
search_hosts_advanced("hostname:'web*'+platform_name:'Linux'")  # Test combination

# Use empty filter to see all available data
search_hosts_advanced("", limit=10, include_details=True)

# Test individual properties
search_hosts_advanced("platform_name:'Windows'", limit=5)
search_hosts_advanced("status:'normal'", limit=5)
```

### Date and Time Considerations

- **Always use UTC timezone** in date filters
- **Include seconds** in timestamp format: `2024-01-15T12:30:45Z`
- **Use comparison operators** for date ranges: `last_seen:>'2024-01-15T00:00:00Z'`
- **Test date filters** with known data first

### Advanced Debugging

```python
# Check what fields are available
search_hosts_advanced("hostname:'known-host'", limit=1, include_details=True)

# Verify filter syntax with simple known case
search_hosts_advanced("device_id:'known-device-id'")

# Test complex filters step by step
search_hosts_advanced("platform_name:'Windows'")  # Step 1
search_hosts_advanced("platform_name:'Windows'+status:'normal'")  # Step 2
search_hosts_advanced("platform_name:'Windows'+status:'normal'+hostname:'prod-*'")  # Step 3
```

## Best Practices

1. **Start simple** - Begin with basic filters and add complexity gradually
2. **Use meaningful limits** - Don't request more data than you need
3. **Leverage sorting** - Use appropriate sort orders for your use case
4. **Test incrementally** - Build complex queries step by step
5. **Document filters** - Save working filters for reuse
6. **Monitor performance** - Be mindful of query complexity and result sizes
7. **Combine with other tools** - Use `get_host_details()` for deep dives on specific hosts

This guide provides a comprehensive foundation for using the advanced host search capabilities. For specific use cases or advanced scenarios, refer to the extensive examples in the tool's docstring. 