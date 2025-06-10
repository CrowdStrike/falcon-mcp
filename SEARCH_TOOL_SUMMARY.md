# 🎉 New Advanced Host Search Tool Added!

## What Was Added

A comprehensive new MCP tool called `search_hosts_advanced` that provides powerful host searching capabilities using Falcon Query Language (FQL).

## 🔍 Key Features

### **30+ Searchable Properties**
- **Identity**: `device_id`, `hostname`, `computer_name`, `serial_number`, `mac_address`
- **System**: `platform_name`, `os_version`, `system_manufacturer`, `system_product_name`, `bios_version`
- **Network**: `local_ip`, `external_ip`, `machine_domain`, `ou`, `site_name`
- **Agent**: `agent_version`, `config_id_build`, `release_group`, `product_type_desc`
- **Status**: `status`, `first_seen`, `last_seen`, `modified_timestamp`, `reduced_functionality_mode`
- **Specialized**: `linux_sensor_mode`, `deployment_type`, `tags`

### **Full Falcon Query Language (FQL) Support**
- **Operators**: `!`, `>`, `>=`, `<`, `<=`, `~`, `!~`, `*`
- **Data Types**: Strings, dates, booleans, numbers, wildcards
- **Complex Logic**: AND (`+`), OR (`,`), grouping with `()`

### **Flexible Output Options**
- **Summary tables** for quick overviews
- **Full host details** for comprehensive analysis
- **Custom field selection** for specific data needs
- **Smart analysis** with platform distribution and activity insights

### **High Performance**
- Support for up to **5,000 results** per query
- **Optimized filtering** to reduce unnecessary data transfer
- **Configurable sorting** for relevant result ordering

## 🚀 Example Use Cases

### **Security Operations**
```python
# Find contained hosts needing attention
search_hosts_advanced("status:'contained'", sort="modified_timestamp.desc")

# Find hosts with old agent versions (security risk)
search_hosts_advanced("agent_version:<'7.0.0'")

# Find hosts that haven't checked in (potential compromise)
search_hosts_advanced("last_seen:<'2024-01-18T00:00:00Z'+status:'normal'")
```

### **Infrastructure Management**
```python
# Get Windows server inventory
search_hosts_advanced("platform_name:'Windows'+hostname:'srv*'")

# Find VMware VMs for license compliance
search_hosts_advanced("system_manufacturer:'VMware, Inc.'")

# Find untagged hosts (compliance issue)
search_hosts_advanced("tags:!*")
```

### **Network Analysis**
```python
# Find hosts in specific IP range
search_hosts_advanced("local_ip.raw:*'192.168.1.*'")

# Find hosts in production domain
search_hosts_advanced("machine_domain:'prod.company.com'")

# Find hosts with suspicious external IPs
search_hosts_advanced("external_ip.raw:*'10.*'")
```

### **Operational Health**
```python
# Find offline hosts (not seen in 24 hours)
search_hosts_advanced("last_seen:<'2024-01-20T00:00:00Z'")

# Find hosts in reduced functionality mode
search_hosts_advanced("reduced_functionality_mode:'yes'")

# Complex health check
search_hosts_advanced("status:'normal'+last_seen:>'2024-01-15T00:00:00Z'+agent_version:>='7.0.0'")
```

## 📊 Output Examples

### Summary Table View (Default)
```
# Hostname                Platform   Status          Last Seen            Host ID
1 web-server-01           Windows    normal          2024-01-20 14:30    a1b2c3d4...
2 db-primary-prod         Linux      normal          2024-01-20 14:28    e5f6g7h8...
3 backup-server-02        Windows    contained       2024-01-19 22:15    i9j0k1l2...
```

### Analysis Section
```
## Platform Distribution
• Windows: 45 hosts
• Linux: 23 hosts
• Mac: 2 hosts

## Status Distribution  
• normal: 65 hosts
• contained: 3 hosts
• containment_pending: 2 hosts

## Activity Analysis
• Active (last 7 days): 68 hosts
• Potentially stale (>30 days): 2 hosts
```

## 🛠️ Technical Implementation

### **New Files & Methods**
1. **MCP Tool**: `search_hosts_advanced()` in `src/api/server.py`
2. **Business Logic**: `search_hosts_advanced()` in `src/core/host_manager.py`
3. **API Client**: `search_hosts_combined()` in `src/core/falcon_client.py`
4. **Formatting**: `_format_host_search_results()` and `_format_single_host_summary()`

### **Documentation**
1. **ADVANCED_SEARCH_GUIDE.md** - Comprehensive 300+ line guide with:
   - Complete FQL reference
   - 50+ practical examples
   - Performance optimization tips
   - Troubleshooting guide
   - Best practices

2. **Updated README.md** - Added overview and quick examples

3. **Extensive Docstring** - 200+ lines of inline documentation with examples

## 🎯 Why This Tool is Powerful

### **Beyond Simple Searches**
- Traditional tools only search by hostname or ID
- This tool searches by **ANY combination** of 30+ properties
- Supports complex business logic with AND/OR/grouping

### **Real-World Problem Solving**
- **Security**: Find compromised or vulnerable hosts
- **Compliance**: Identify policy violations or missing configurations  
- **Operations**: Manage large inventories efficiently
- **Troubleshooting**: Quickly locate problematic systems

### **User-Friendly Yet Powerful**
- Extensive documentation prevents user confusion
- Clear error messages and suggestions
- Progressive complexity (simple to advanced examples)
- Smart defaults for ease of use

## 🔒 Security & Best Practices

### **Follows CrowdStrike Standards**
- ✅ **KISS-FIRST**: Simple, clear implementation
- ✅ **YAGNI**: Only implements explicitly needed functionality
- ✅ **SECURITY**: Uses existing secure FalconPy SDK
- ✅ **FRAMEWORK**: Built on FastMCP primitives
- ✅ **STYLE**: Clean, typed Python code
- ✅ **DOCS**: Comprehensive Google-style docstrings

### **Error Handling**
- Validates all parameters
- Provides helpful error messages
- Graceful handling of API failures
- Structured logging for debugging

## 📈 Impact

This tool transforms the MCP server from a basic host lookup utility into a comprehensive **host management and security analysis platform**. Users can now:

1. **Perform complex security investigations** with multi-criteria searches
2. **Manage large host inventories** efficiently with smart filtering
3. **Ensure compliance** by finding policy violations or misconfigurations
4. **Troubleshoot issues** by quickly locating problematic systems
5. **Generate reports** with platform distribution and activity analysis

The extensive documentation ensures users can leverage the full power of the tool without burning down the world! 🌍🔥 