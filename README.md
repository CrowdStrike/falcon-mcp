# CrowdStrike Falcon MCP Server

Official CrowdStrike Falcon MCP (Model Context Protocol) server that provides AI assistants with powerful cybersecurity capabilities through the Falcon platform.

## Features

- **Host Information Management**: Get comprehensive technical details about hosts monitored by CrowdStrike Falcon
- **Security Event Analysis**: Retrieve and analyze recent security detection events 
- **Intelligent Host Lookup**: Support for both Host ID (AID) and hostname-based queries
- **Rich Formatted Output**: Human-readable reports with detailed technical information
- **Built with FastMCP**: Modern, high-performance MCP server framework
- **Structured Logging**: JSON-based logging for observability and debugging
- **Secure Authentication**: Uses CrowdStrike FalconPy SDK with OAuth2
- 🔍 **Advanced Host Search** - Powerful host search using Falcon Query Language (FQL) with 30+ searchable properties
- 🛡️ **Vulnerability-Based Host Search** - Find hosts by vulnerability criteria using CrowdStrike Spotlight integration
- 🖥️ **Host Details** - Comprehensive technical information about hosts including system specs, network config, and policies
- 🚨 **Security Events** - Recent detection events and threat intelligence for hosts
- 📊 **Inventory Management** - Platform distribution, status analysis, and compliance reporting
- 🎯 **Threat Hunting** - Complex filtering for security investigations and operational analysis
- ⚡ **CVE Intelligence** - Search for hosts affected by specific CVEs or vulnerability characteristics
- 🔥 **Risk Prioritization** - Combine vulnerability severity, exploit status, and host criticality for risk-based analysis

## Installation

```bash
# Install the package
pip install -e .

# Install with test dependencies
pip install -e ".[test]"
```

## Configuration

Set the following environment variables for CrowdStrike Falcon API access:

```bash
export FALCON_CLIENT_ID="your-falcon-api-client-id"
export FALCON_CLIENT_SECRET="your-falcon-api-client-secret"
export FALCON_BASE_URL="https://api.crowdstrike.com"  # Optional, auto-detects by default
```

### Getting CrowdStrike Falcon API Credentials

1. Log into your CrowdStrike Falcon console
2. Navigate to **Support and resources** > **API Clients & Keys**
3. Click **Add new API client**
4. Provide a descriptive name (e.g., "MCP Server Integration")
5. Select the following API scopes:
   - **Hosts: Read**
   - **Detections: Read**
   - **Spotlight Vulnerabilities: Read**
6. Copy the **Client ID** and **Client Secret**

## Usage

### Running the server

```bash
# Using the installed script
falcon-mcp

# Or directly with Python
python -m src.api.server
```

### Example Queries

Once the server is running, AI assistants can use these natural language queries:

#### Host Information & Search
1. **"Provide the technical details on the host with the ID 123456789012345678901234567890ab"**
2. **"Show me information about the host named myhost-123"**  
3. **"Find all Windows hosts in the production environment"**
4. **"Show me hosts that haven't been seen in the last 30 days"**

#### Security Events
5. **"Get the last 10 security events from the host with ID 123456789012345678901234567890ab"**
6. **"What are the recent detection events for myhost-123?"**

#### Vulnerability-Based Searches
7. **"Find all hosts affected by CVE-2024-1234"**
8. **"Show me hosts with open critical vulnerabilities"**
9. **"Find Windows systems with actively exploited vulnerabilities"**
10. **"Identify internet-exposed hosts with high-severity vulnerabilities"**
11. **"Search for hosts with CISA Known Exploited Vulnerabilities"**

## MCP Tools

The server provides four main tools:

### 🛡️ `search_hosts_by_vulnerabilities` - **POWERFUL**

**Find hosts based on vulnerability exposure** - Search for hosts affected by specific CVEs, severity levels, or exploit characteristics using CrowdStrike Spotlight.

**Key Features:**
- **CVE-specific searches** for targeted incident response
- **Severity-based filtering** (CRITICAL, HIGH, MEDIUM, LOW)
- **Exploit status analysis** including actively exploited vulnerabilities
- **CISA KEV integration** for compliance and risk assessment
- **Platform-specific vulnerability searches** 
- **Risk prioritization** combining vulnerability and host data
- **Smart analytics** with vulnerability distribution and CVE analysis

**Quick Examples:**
```python
# Find hosts with a specific CVE
search_hosts_by_vulnerabilities("cve.id:['CVE-2024-1234']")

# Find hosts with open critical vulnerabilities
search_hosts_by_vulnerabilities("status:'open'+cve.severity:'CRITICAL'")

# Find Windows hosts with actively exploited vulnerabilities
search_hosts_by_vulnerabilities("host_info.platform_name:'Windows'+cve.exploit_status:'90'")

# Find internet-exposed hosts with CISA KEV vulnerabilities
search_hosts_by_vulnerabilities("host_info.internet_exposure:'Yes'+cve.is_cisa_kev:true")

# Emergency response: Critical + Exploited + Production systems
search_hosts_by_vulnerabilities("cve.severity:'CRITICAL'+cve.exploit_status:['60','90']+host_info.tags:['production']+status:'open'")
```

📖 **[See VULNERABILITY_SEARCH_GUIDE.md for complete documentation with examples](./VULNERABILITY_SEARCH_GUIDE.md)**

### 🔍 `search_hosts_advanced` - **ENHANCED**

**The most comprehensive host search tool** - Search hosts using any combination of 30+ properties with advanced Falcon Query Language (FQL) filtering.

**Key Features:**
- **30+ searchable properties** including system specs, network info, timestamps, agent details
- **Full FQL support** with all operators (`!`, `>`, `>=`, `<`, `<=`, `~`, `!~`, `*`)
- **Complex filtering** with AND (`+`), OR (`,`), and grouping `()`
- **Flexible output** - summary tables or full host details
- **Smart analysis** - platform distribution, status breakdown, activity analysis

**Quick Examples:**
```python
# Find all Windows hosts
search_hosts_advanced("platform_name:'Windows'")

# Find hosts not seen in 30 days  
search_hosts_advanced("last_seen:<'2024-01-01T00:00:00Z'")

# Find contained or pending containment hosts
search_hosts_advanced("(status:'contained'),(status:'containment_pending')")

# Complex: Production Windows servers, healthy, recent activity
search_hosts_advanced("platform_name:'Windows'+hostname:'prod-*'+status:'normal'+last_seen:>'2024-01-15T00:00:00Z'")
```

📖 **[See ADVANCED_SEARCH_GUIDE.md for complete documentation with 50+ examples](./ADVANCED_SEARCH_GUIDE.md)**

### `get_host_details(host_identifier: str)`

Retrieves comprehensive technical information about a CrowdStrike Falcon-monitored host.

**Parameters:**
- `host_identifier`: Host ID (AID) or hostname

**Returns:** Formatted report including:
- Basic host information (hostname, status, agent version)
- System specifications (OS, platform, architecture)
- Network configuration (IPs, MAC address)
- Domain and group memberships
- Applied security policies
- Important timestamps

### `get_host_events(host_identifier: str, limit: int = 10)`

Retrieves recent security detection events for a specific host.

**Parameters:**
- `host_identifier`: Host ID (AID) or hostname  
- `limit`: Maximum number of events to return (1-50, default: 10)

**Returns:** Formatted report including:
- Detection event details
- Severity and status information
- MITRE ATT&CK tactics and techniques
- Command line and file information
- Event timestamps and assignments

## Integration Workflows

The tools work seamlessly together for comprehensive security analysis:

```python
# 1. Find vulnerable hosts
vulnerable_hosts = search_hosts_by_vulnerabilities("cve.severity:'CRITICAL'+status:'open'")

# 2. Get detailed information for priority hosts
get_host_details("host_id_from_results")

# 3. Check for recent security events
get_host_events("host_id_from_results", limit=20)

# 4. Use advanced search for additional context
search_hosts_advanced("device_id:'host_id_from_results'", include_details=True)
```

## Use Cases

### Security Operations
- **Incident Response**: Quickly identify all hosts affected by specific CVEs
- **Threat Hunting**: Complex filtering for security investigations
- **Risk Assessment**: Prioritize remediation based on vulnerability severity and exploitability
- **Compliance**: Track CISA KEV vulnerabilities and critical asset exposure

### Vulnerability Management
- **Patch Planning**: Identify systems needing specific patches
- **Asset Inventory**: Map vulnerabilities to business-critical systems
- **Trend Analysis**: Track vulnerability exposure over time
- **Risk Scoring**: Combine vulnerability severity with host criticality

### Infrastructure Management  
- **Inventory Management**: Platform distribution and status analysis
- **Health Monitoring**: Find offline, contained, or problematic hosts
- **Compliance Reporting**: Identify policy violations or misconfigurations
- **Operational Analysis**: System lifecycle and deployment tracking

## Architecture

The server follows a clean, modular architecture:

```
src/
├── api/           # FastMCP server implementation
│   └── server.py  # MCP tools and server configuration
├── core/          # Business logic
│   ├── falcon_client.py   # CrowdStrike API client wrapper
│   ├── host_manager.py    # Host operations and formatting
│   └── services.py          # Service initialization
└── __init__.py
```

## Security

- Uses OAuth2 authentication with CrowdStrike Falcon APIs
- Credentials managed via environment variables
- Read-only API permissions required
- Structured logging without sensitive data exposure
- Scope-aware operations respecting customer boundaries

## Contributing

This project follows the CrowdStrike development standards:

1. **KISS Principle**: Keep solutions simple and focused
2. **Security First**: All code passes security scans
3. **Clean Code**: Passes ruff, black, and mypy checks
4. **Documentation**: Google-style docstrings for all public functions
5. **Testing**: Maintain ≥80% test coverage

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
