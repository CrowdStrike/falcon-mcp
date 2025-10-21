"""
NG-SIEM reference documentation and resources.
"""

import glob
import os
from textwrap import dedent
from typing import Dict, List, Optional

# Enhanced function documentation based on actual implementation
NGSIEM_TOOL_REFERENCE = dedent(r"""
# NG-SIEM Tools Reference for Claude Code

*Comprehensive guide to the Falcon MCP NG-SIEM tools and their actual capabilities*

## Available Tools Overview

The NG-SIEM module provides the following tools for interacting with CrowdStrike's Next-Generation SIEM:

### Core Query Tools

**`falcon_execute_ngsiem_query`**
- **Purpose**: Execute LogScale/CQL queries against CrowdStrike NG-SIEM
- **Parameters**:
  - `query` (required): LogScale/CQL query string
  - `time_range` (default: "15m"): Time range for query (e.g., "1h", "24h", "7d", or absolute times)
  - `repository` (default: "search-all"): Repository to search ("search-all")
  - `output_format` (default: "json"): Output format ("json" or "csv")
  - `download` (default: false): Automatically save results to falcon_exports directory
  - `sample_events` (default: 3): Number of sample events to include when data is auto-exported

**`falcon_execute_ngsiem_query_background`**
- **Purpose**: Execute queries in background with real-time progress logging
- **Parameters**:
  - `query` (required): LogScale/CQL query string
  - `time_range` (default: "15m"): Time range for query
  - `repository` (default: "search-all"): Repository to search
- **Returns**: Job ID and progress monitoring information

### Job Management Tools

**`falcon_check_query_job`**
- **Purpose**: Check status of background query jobs
- **Parameters**:
  - `job_id` (required): Job ID from background query execution

**`falcon_list_query_jobs`**
- **Purpose**: List all active background query jobs

**`falcon_cleanup_query_job`**
- **Purpose**: Clean up completed query jobs
- **Parameters**:
  - `job_id` (required): Job ID to clean up

### Query Helper Tools

**`falcon_ngsiem_query_templates`**
- **Purpose**: Get pre-built query templates for common security use cases
- **Parameters**:
  - `template_name` (optional): Specific template name or None to list all
  - `custom_filters` (optional): Custom filter parameters to apply

**`falcon_build_cql_query`**
- **Purpose**: Interactive CQL query builder with guided parameters
- **Parameters**:
  - `event_type` (optional): Event type to filter on (e.g., "ProcessRollup2")
  - `platform` (optional): Platform filter ("Win", "Mac", "Lin")
  - `filters` (optional): Field filters as key-value pairs
  - `regex_filters` (optional): Regex filters for pattern matching
  - `wildcard_filters` (optional): Wildcard filters for flexible matching
  - `group_by` (optional): Fields to group results by
  - `sort_by` (optional): Field to sort by
  - `sort_order` (default: "desc"): Sort order
  - `limit` (default: 1000): Number of results to limit to
  - `select_fields` (optional): Specific fields to select in output

**`falcon_validate_cql_syntax`**
- **Purpose**: Validate CQL syntax and convert Splunk patterns to proper CQL
- **Parameters**:
  - `query` (required): CQL query to validate

### Analysis and Search Tools

**`falcon_analyze_ngsiem_results`**
- **Purpose**: Analyze query results with statistical analysis and pivot tables
- **Parameters**:
  - `results_data` (required): Query results from execute_ngsiem_query
  - `analysis_type` (default: "summary"): Type of analysis ("summary", "pivot", "statistical")
  - `pivot_fields` (optional): Fields to pivot on for pivot analysis

**`falcon_search_ngsiem_fields`**
- **Purpose**: Search available LogScale fields by name or description
- **Parameters**:
  - `search_term` (required): Search term to find relevant fields
  - `field_type` (optional): Filter by field type if known

## Response Handling and Size Management

### Automatic Response Handling

The NG-SIEM tools include sophisticated response handling capabilities:

#### Size Thresholds
- **Auto-CSV Threshold**: 100+ events automatically trigger CSV export consideration
- **Large Dataset Threshold**: 500+ events force CSV export
- **Character Thresholds**:
  - Warning at 50,000 characters (~12,500 tokens)
  - Critical at 200,000 characters (~50,000 tokens)

#### Download Mode
When `download=true` is specified:
- Results are automatically saved to `falcon_exports/` directory
- Only sample events (default: 3) are returned to Claude
- Full dataset is preserved in the saved file
- Bypasses all size checks

### Response Handling Flow

1. **Query Execution**: Query is submitted to CrowdStrike NG-SIEM
2. **Polling**: System polls for results (up to 3 minutes timeout with 7.5s intervals)
3. **Size Analysis**: Response size is evaluated against thresholds
4. **Auto-Export Decision**:
   - If `download=true`: Save to falcon_exports, return sample
   - If large dataset detected: Trigger auto-export with user notification
   - If normal size: Return full data
5. **Format Processing**: Apply requested output format (JSON/CSV)

## Background Job Management

### Progress Monitoring

Background jobs provide real-time progress logging:
- Progress files: `/tmp/falcon_query_{job_id}.log`
- Monitor command: `tail -f /tmp/falcon_query_{job_id}.log`
- Status updates every 15 seconds for long-running queries

### Job Lifecycle

1. **Starting**: Job initiated, progress logging begins
2. **Running**: Query executing, progress updates logged
3. **Completed**: Results available, can be retrieved
4. **Failed**: Error occurred, details in job status
5. **Cleaned**: Job removed from memory, progress file deleted

## Error Handling and Timeouts

### Query Timeouts
- Initial submission: Standard HTTP timeout
- Polling timeout: 3 minutes (24 attempts × 7.5 seconds)
- Progress updates at 30s, 90s intervals for long-running queries

### Error Categories
1. **Authentication Errors**: Invalid credentials or permissions
2. **Syntax Errors**: Invalid CQL query syntax
3. **Timeout Errors**: Query execution exceeded time limits
4. **Network Errors**: Connectivity issues
5. **Permission Errors**: Insufficient access to NG-SIEM

### Error Responses
All tools return structured error responses with:
- Error message and category
- Troubleshooting suggestions
- Query context information
- Authentication status where applicable

## Performance Optimization

### Query Optimization Guidelines

1. **Always start with event type**: `#event_simpleName=ProcessRollup2`
2. **Use specific time ranges**: Avoid overly broad time ranges
3. **Apply filters early**: Add specific filters before aggregation
4. **Limit results appropriately**: Use `head()` function
5. **Use indexed fields**: Prefer metadata fields (# and @ prefixed)

### Repository Selection

- **search-all**: All available ngsiem data repositories (default)

Choose the most specific repository for better performance.

## Integration with Claude Code Resources

### Available Resources

- `falcon://ngsiem/field-mappings`: Complete field reference
- `falcon://ngsiem/query-patterns`: CQL syntax and patterns
- `falcon://ngsiem/use-cases`: Security use cases with examples
- `falcon://ngsiem/functions-reference`: LogScale function documentation

### Usage Recommendations

1. **Start with field mappings**: Understand available fields
2. **Use query patterns**: Follow CQL syntax guidelines
3. **Reference use cases**: See practical security examples
4. **Validate syntax**: Use validation tool before execution
5. **Monitor performance**: Use background execution for complex queries

## Best Practices

### Query Development Workflow

1. **Plan the query**: Identify event types and time ranges
2. **Start simple**: Begin with basic event filtering
3. **Add complexity gradually**: Incrementally add filters and functions
4. **Validate syntax**: Use `falcon_validate_cql_syntax`
5. **Test with small time ranges**: Verify logic before expanding
6. **Use background execution**: For production queries
7. **Export large results**: Use download mode for analysis

### Security Analysis Workflow

1. **Use templates**: Start with relevant security templates
2. **Customize filters**: Apply environment-specific filters
3. **Analyze results**: Use analysis tools for insights
4. **Export for investigation**: Save results for detailed analysis
5. **Document findings**: Keep track of successful queries

### Error Resolution

1. **Check authentication**: Verify API credentials
2. **Validate syntax**: Use syntax validation tool
3. **Simplify query**: Remove complex functions if failing
4. **Check permissions**: Ensure NG-SIEM access rights
5. **Review logs**: Check background job progress logs
6. **Reduce scope**: Try smaller time ranges or event counts

""").strip()

# LogScale field mappings content
NGSIEM_FIELD_MAPPINGS = dedent(r"""
# CrowdStrike Multi-Source Field Mappings Reference

## Universal Fields (Present in ALL Events)

### Core Identifiers
- `@id` - Unique event identifier
- `@timestamp` - Event timestamp (Unix epoch milliseconds)
- `@ingesttimestamp` - Log ingestion timestamp
- `@timezone` - Timezone (typically "Z" for UTC)
- `#type` - Event source type (`falcon-raw-data`, `paloalto-ngfw`,
`aws-cloudtrail`, `microsoft-windows`)

### System Metadata
- `@sourcetype` - Data source type identifier
- `@source` - Source system (`PlatformEvents`)
- `#repo` - Repository/dataset name (`base_sensor`, `cloudtrail`, etc.)
- `#repo.cid` - Repository customer ID
- `#Vendor` - Vendor of the logs (`crowdstrike`, `paloalto`, `aws`,
`microsoft`)
- `#ecs.version` - Elastic Common Schema version
- `#observer.type` - Observer type (`firewall`, `os`, etc.)
- `@dataConnectionID` - Data connection identifier

## CrowdStrike Falcon Endpoint Fields (#type=falcon-raw-data)

### Event Classification
- `#event_simpleName` - CrowdStrike event type (`ProcessRollup2`,
`NetworkConnectIP4`, `UserLogon`, etc.)
- `name` - Event version name (`ProcessRollup2V19`)
- `EventOrigin` - Event origin indicator (`1`)
- `event_platform` - Platform identifier (`Win`, `Mac`, `Lin`)

### Process Context Fields (ProcessRollup2)
- `FileName` - Executable name (`cmd.exe`, `powershell.exe`, `conhost.exe`)
- `ImageFileName` - Full process path (
`\\Device\\HarddiskVolume1\\Windows\\System32\\cmd.exe`)
- `CommandLine` - Complete command with arguments
- `ProcessStartTime` - Process start time (
Unix epoch seconds: `1760405600.738`)
- `ProcessEndTime` - Process end time (empty if running)
- `RawProcessId` - Numeric process ID (`4420`)
- `TargetProcessId` - Target process ID (`1140735588418`)
- `SourceProcessId` - Source process ID (`1140733370104`)
- `ParentProcessId` - Parent process ID (`1140733370104`)
- `ParentBaseFileName` - Parent process name (
`LogScale Collector.exe`, `explorer.exe`)
- `FilePath` - Process file directory path (
`\\Device\\HarddiskVolume1\\Windows\\System32\\`)

### User and Session Context
- `UserName` - Account name (`SYSTEM`, `EC2AMAZ-UUJS0A3$`, `Administrator`)
- `user.name` - Normalized username field
- `UserSid` - Windows Security Identifier (`S-1-5-18` for SYSTEM,
`S-1-5-21-*` for domain users)
- `AuthenticationId` - Authentication session ID (`999`)
- `ParentAuthenticationId` - Parent authentication ID (`999`)
- `SessionId` - Windows session ID (`0` for system, `1+` for user sessions)
- `TokenType` - Token type identifier (`1`)
- `IntegrityLevel` - Process integrity level (`16384` = System,
`12288` = High, `8192` = Medium)

### Host Information
- `ComputerName` - Host/computer name (`EC2AMAZ-UUJS0A3`)
- `aid` - Agent ID (unique sensor identifier:
`96794994509c48a2802982f571eddaed`)
- `aip` - Agent external IP address (`13.48.5.244`)
- `LocalAddressIP4` - Local IPv4 address (`172.31.28.72`)
- `LocalIP` - Local IP address (`172.31.28.72`)
- `cid` - Customer/tenant ID (`d97d6a2d72dc403d86c585d2c7dfe111`)

### Security Analysis Fields
- `Tactic` - MITRE ATT&CK tactic (`Execution`, `Persistence`,
`Defense Evasion`)
- `Technique` - MITRE ATT&CK technique (`User Execution`,
`Command and Scripting Interpreter`)
- `Tags` - Behavioral analysis tags (comma-separated: `27, 29, 41,
151, 874, 924, 1225`)
- `Entitlements` - Process entitlements (`15`)

### File Hashes and Signatures
- `SHA256HashData` - SHA256 hash (
`970baab9202d8fe98bd9d58a9c90cef212cef39ee591f98178afd35961bbb6e2`)
- `SHA1HashData` - SHA1 hash (`0000000000000000000000000000000000000000` for placeholder)
- `MD5HashData` - MD5 hash (`146d07aaedb5fb53a69d2766710f10d0`)
- `AuthenticodeHashData` - Authenticode signature hash (
`1b90b44d6544d870c94757a749ee2c0aeb557a10`)
- `SignInfoFlags` - Signature information flags (`8683538`)

### System Configuration
- `ConfigBuild` - CrowdStrike agent build version (`1007.3.0019909.15`)
- `ConfigStateHash` - Configuration state hash (`237609349`)
- `EffectiveTransmissionClass` - Transmission class (`3`)
- `ImageSubsystem` - Windows subsystem type (`2` = GUI, `3` = Console)
- `SourceThreadId` - Source thread identifier (`51848531855026`)

### System Metadata
- `#event.module` - Event module (`ngfw`)
- `Parser.version` - Parser version (`3.4.2`)
- `event.created` - Event creation indicator

### Raw Data
- `@rawstring` - Complete raw syslog message with all firewall details

### Network and Location
- `Vendor.sourceIPAddress` - Source IP address (`18.214.175.1`)
- `source.address` / `source.ip` - Normalized source IP
- `Vendor.userAgent` - User agent (`aws-sdk-go-v2/1.36.3...`)

### AWS Context
- `cloud.account.id` - AWS account ID (`042445652404`)
- `cloud.region` - AWS region (`us-east-1`)
- `cloud.provider` - Cloud provider (`aws`)
- `Vendor.awsRegion` - AWS region field
- `Vendor.recipientAccountId` - Recipient account ID

### TLS Information
- `tls.version` - Normalized TLS version (`1.3`)
- `tls.version_protocol` - TLS protocol (`tls`)
- `tls.cipher` - TLS cipher suite

### Event Status
- `#event.outcome` - Event outcome (`success`, `failure`)
- `#event.kind` - Event kind (`event`)
- `event.type[0]` - Event type array (`info`)
- `event.category[0]` - Event category array (`configuration`)

### Metadata
- `Vendor.eventVersion` - CloudTrail event version (`1.10`)
- `Vendor.eventTime` - Event timestamp (`2025-10-15T00:27:43Z`)
- `Vendor.CustomerId` - Customer ID
- `Vendor.__meta.version` - Metadata version (`1.0`)
- `Vendor.__meta.res_id` - Resource ID (`amazon.aws.cloudtrail.semantic.Log`)
- `#event.dataset` - Event dataset (`cloudtrail.log`)
- `#event.module` - Event module (`cloudtrail`)

## Microsoft Windows Fields (#type=microsoft-windows)

### Event Classification
- `windows.ProviderName` - Provider name
- `windows.EventID` - Windows event ID (`33205`, `4624`, `1001`)
- `event.id` - Normalized event ID
- `windows.Channel` - Event log channel (`Application`, `Security`, `System`)
- `@collect.channel` - Collection channel

### Event Metadata
- `windows.Level` - Event level (`0`=Info, `1`=Critical, `2`=Error, `3`=Warning, `4`=Info, `5`=Verbose)
- `log.level` - Normalized log level
- `windows.Version` - Event version (`0`)
- `windows.Task` - Task category (`5`)
- `windows.Opcode` - Operation code (`0`)
- `windows.Keywords` - Event keywords (`0xa0000000000000`)
- `windows.Qualifiers` - Event qualifiers (`16384`)

### Host Information
- `host.name` - Host name (`ec2amaz-0ad0eai`)
- `windows.Computer` - Computer name (`EC2AMAZ-0AD0EAI`)
- `@collect.host` - Collection host
- `host.os.type` - Operating system type (`windows`)
- `local` - Local IP address (`172.31.15.75`)

### Process Information
- `windows.ProcessID` - Process ID (`0`)
- `process.pid` - Normalized process ID
- `windows.ThreadID` - Thread ID (`0`)

### Timing Information
- `windows.TimeCreated` - Event creation time (`2025-10-15T00:28:20.6363013Z`)
- `windows.EventRecordId` - Event record ID (`617836`)

### Collection Context
- `@collect.source_type` - Collection source type (`wineventlog`)
- `@collect.source_name` - Collection source name (`windows_events`)
- `@collect.timezone` - Collection timezone (`UTC`)
- `@collect.timestamp` - Collection timestamp
- `@collect.id` - Collection identifier
- `Parser.version` - Parser version (`5.0.1`)

### Event Data
- `windows.EventData[0]` - Event data payload (detailed structured data)
- `windows.XML` - Complete XML event structure
- `event.reason` - Event reason/message
- `@rawstring` - Raw event string

### System Context
- `#event.kind` - Event kind (`event`)
- `#event.dataset` - Event dataset (`windows.application`)
- `#event.module` - Event module (`windows`)

## Field Categories for CQL Queries

### Universal Time-Based Filtering
```cql
@timestamp >= 1760400000000
@timestamp > (now() - 3600000)  // Last hour
```

### Event Source Selection
```cql
#type=falcon-raw-data           // CrowdStrike endpoint data
#type=paloalto-ngfw            // Palo Alto firewall data
#type=aws-cloudtrail           // AWS audit logs
#type=microsoft-windows        // Windows event logs
```

### CrowdStrike Process Analysis
```cql
#type=falcon-raw-data #event_simpleName=ProcessRollup2
FileName=cmd.exe
CommandLine=*powershell*
ParentBaseFileName=explorer.exe
IntegrityLevel>=16384           // High privilege processes
UserName!=SYSTEM               // Non-system processes
```

### Palo Alto Network Security
```cql
#type=paloalto-ngfw
#event.dataset=ngfw.globalprotect      // GlobalProtect VPN connections events
#event.dataset=ngfw.hipmatch    // Host Information Profile (HIP) events
#event.dataset=ngfw.threat     // Security threat detection events
#event.dataset=ngfw.traffic        // Network traffic flow events
#event.dataset=ngfw.userid        // User identification mapping events
```

### AWS Cloud Security
```cql
#type=aws-cloudtrail
Vendor.eventName=*SignIn*       // Authentication events
Vendor.userIdentity.type=AssumedRole    // Role assumption events
event.provider=ec2.amazonaws.com        // EC2 API calls
#event.outcome!=success         // Failed operations
cloud.region=us-east-1          // Regional filtering
```

### Windows System Monitoring
```cql
#type=microsoft-windows
event.provider=MSSQLSERVER      // SQL Server events
windows.Channel=Application     // Application log events
windows.Channel=Security        // Security log events
windows.Level>2                 // Warning and error events
host.name=*SERVER*              // Server host filtering
```

## Multi-Source Correlation Patterns

### Cross-Platform User Activity
```cql
// Correlate CrowdStrike process events with AWS API calls
defineTable(query={#type=falcon-raw-data #event_simpleName=ProcessRollup2
                    | groupBy([UserName, ComputerName], limit=max)
                    | cs_user := lower(UserName)},
                        name="admin_processes",
                            include=[cs_user, ComputerName])

| #type=aws-cloudtrail Vendor.userIdentity.type=AssumedRole
| aws_user := lower(user.name)
| match(table="admin_processes", field=aws_user, column=cs_user)
```

### System Event Correlation
```cql
// Correlate Windows events with CrowdStrike process activity
defineTable(query={#type=microsoft-windows
                  | lower(host.name, as=host.name)
                  | groupBy([host.name], limit=max)},
                      name="m$_events",
                          include=[host.name])

| #type=falcon-raw-data #event_simpleName=ProcessRollup2 | lower("ComputerName", as=ComputerName)
| match(table="m$_events", field=ComputerName, column=host.name)
```

## Data Quality and Parsing Notes

### Hash Fields
- **Placeholder Hashes**: Some events contain placeholder values (`0000000000000000000000000000000000000000`)
- **Authentic Hashes**: Real file hashes provide valuable IOC data
- **Hash Verification**: Compare across SHA256, SHA1, MD5 for validation

### Empty/Null Fields
- **ProcessEndTime**: Often empty for running processes
- **ParentAuthenticationId**: May be null for system processes
- **Vendor.addendum**: Frequently contains `Unknown` values

### Field Consistency
- **Universal Fields**: `@timestamp`, `#type`, `@id` consistently present across all sources
- **Vendor-Specific**: Each vendor maintains unique field structures and naming conventions
- **Normalization**: ECS fields provide standardized equivalents where available

### Nested Structures
- **AWS CloudTrail**: Heavy use of dot notation (`Vendor.userIdentity.sessionContext.sessionIssuer.arn`)
- **Windows Events**: Complex XML structures in `windows.XML` field
- **Palo Alto**: Syslog format with positional parameters in `@rawstring`
- **CrowdStrike**: Structured JSON with consistent field naming

### Timestamp Formats
- **Universal**: `@timestamp` in Unix epoch milliseconds (1760405601329)
- **CrowdStrike**: `ProcessStartTime` in Unix epoch seconds with decimals (1760405600.738)
- **AWS**: `Vendor.eventTime` in ISO format (2025-10-15T00:27:43Z)
- **Windows**: `windows.TimeCreated` in ISO format (2025-10-15T00:28:20.6363013Z)

### Multi-Source Event Analysis

#### Event Source Distribution
```cql
// Analyze event distribution across all sources
* | groupBy(["#type"]) | sort(_count, order=desc, limit=20)
```

#### Cross-Source Time Analysis
```cql
// Compare event volumes across sources over time
* | bucket(span="1h", field=#type, limit=100)
```

### CrowdStrike Process Monitoring (falcon-raw-data)
```cql
#type=falcon-raw-data #event_simpleName=ProcessRollup2
```

### AWS CloudTrail Analysis (aws-cloudtrail)

#### API Call Analysis
```cql
#type=aws-cloudtrail
| select([Vendor.eventName, Vendor.sourceIPAddress, cloud.account.id,
cloud.region])
```

#### Failed AWS Authentication Events
```cql
#type=aws-cloudtrail Vendor.eventName=*SignIn* #event.outcome!=success
| select([Vendor.eventName, Vendor.sourceIPAddress, Vendor.userIdentity.type])
```

#### EC2 Activity Monitoring
```cql
#type=aws-cloudtrail event.provider=ec2.amazonaws.com
| groupBy([Vendor.eventName], limit=20) | sort()
```

#### AssumedRole Activity (Privilege Escalation Monitoring)
```cql
#type=aws-cloudtrail Vendor.userIdentity.type=AssumedRole
| select([@timestamp, Vendor.eventName, Vendor.userIdentity.arn,
Vendor.sourceIPAddress])
```

### Microsoft Windows Analysis (microsoft-windows)

#### SQL Server Audit Events
```cql
#type=microsoft-windows event.provider=MSSQLSERVER
| select([@timestamp, host.name, windows.EventID, event.reason])
```

#### Application Event Analysis
```cql
#type=microsoft-windows windows.Channel=Application
```

### Session Analysis and User Behavior
```cql
// Group user activities into sessions with 30-minute timeout
#event_simpleName=ProcessRollup2
| groupBy(UserName, function=session(maxpause="30m", collect([ImageFileName])))
| _count > 10  // Filter for active sessions
```

### Network Connection Analysis
```cql
// Analyze external connections with geographic context
#event_simpleName=NetworkConnectIP4
RemoteAddressIP4!=/^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)/
| ipLocation(RemoteAddressIP4)
| groupBy([RemoteAddressIP4, country])
| sort(_count, order=desc)
```

### Time-Based Anomaly Detection
```cql
// Detect unusual process creation rates per host
#event_simpleName=ProcessRollup2
| bucket(span=1h)
| groupBy([_bucket, ComputerName])
| count(as=processes_per_hour)
| neighbor(field=processes_per_hour, as=prev_hour_count, by=ComputerName)
| eval(change_pct = (processes_per_hour -
prev_hour_count) / prev_hour_count * 100)
| test(change_pct > 100)  // 100% increase from previous hour
```

## Data Quality Notes

- **Hash Fields**: Some events contain placeholder hashes (
`0000000000000000000000000000000000000000`)
- **Empty Fields**: `ProcessEndTime` often empty for running processes
- **Field Consistency**: Core CrowdStrike fields consistently present
- **Nested Fields**: FEM events use dot notation for nested structures

## Complete Field Reference

*Based on extraction from 17 CrowdStrike SIEM result files*

### All Available #<fields> (Query/Filter Fields)
- `#error` - Error handling field
- `#event_simpleName` - CrowdStrike Event type identifier
- `#repo` - Repository identifier
- `#repo.cid` - Repository customer ID
- `#repo != risks` - Repository exclusion filter (not equal to risks)
- `#type` - Data type field
- `#type=falcon-raw-data` - Falcon raw data type filter
- `#Vendor` - Vendor identifier (CrowdStrike)

### All Available @<fields> (System/Metadata Fields)
- `@dataConnectionID` - Data connection identifier
- `@error` - General error field
- `@error_msg` - Error message field
- `@error_msg[0]` - First error message in array
- `@event_parsed` - Event parsing status
- `@id` - Unique event identifier
- `@ingesttimestamp` - Data ingestion timestamp
- `@rawstring` - Raw event data string
- `@source` - Event source (e.g., PlatformEvents)
- `@sourcetype` - Source type (e.g., xdr/xdr-base-parsers:falcon-raw-data)
- `@timestamp` - Event timestamp
- `@timestamp.nanos` - Timestamp nanoseconds
- `@timezone` - Timezone identifier

## Field Naming Conventions

- **@-prefixed**: System/processing fields (`@timestamp`, `@id`)
- **#-prefixed**: Metadata fields (`#event_simpleName`, `#type`)
- **Dot notation**: Nested structures (
`FEMRemediationMutation.FEMRemediationInstance.Title`)
- **CamelCase**: Most field names use CamelCase (`ComputerName`,
`ProcessStartTime`)

""").strip()

# LogScale query patterns content
NGSIEM_QUERY_PATTERNS = dedent(r"""
# CQL Query Patterns & Syntax Reference

*LogScale/CQL syntax reference for CrowdStrike NG-SIEM queries with optimization guidelines*

## Core CQL Architecture

CQL uses a **pipeline architecture** where "each expression passes its result to the next expression in the sequence." This enables complex data analysis by chaining processing commands together, similar to Unix pipes.

### Comments
- Single-line: `// Comment text`
- Multi-line: `/* Comment block */`

## Event Type Selection

### Basic Event Filtering
```cql
# Select specific event type (most efficient)
#event_simpleName=ProcessRollup2

# Multiple event types
(#event_simpleName=ProcessRollup2 OR #event_simpleName=UserLogon)

# All events (use sparingly - performance impact)
*
```

### Detection Event Types (Based on Production Analysis)

**Primary Detection Events (Past Year Analysis):**
- `Event_XdrDetectionSummaryEvent` -
Most active detection type (369 events/year)
- `Event_DetectionSummaryEvent` - General detections (25 events/year)
- `Event_EppDetectionSummaryEvent` - Endpoint detections (25 events/year)
- `Event_IncidentSummaryEvent` - Security incidents (2 events/year)
- `DetectionExcluded` - Excluded detections (42 events/year)

**Recommended Detection Queries:**
```cql
# All XDR detections (most reliable for finding detections)
#event_simpleName=Event_XdrDetectionSummaryEvent | head(20)

# All detection types combined
#event_simpleName=Event_XdrDetectionSummaryEvent OR #event_simpleName=Event_DetectionSummaryEvent OR #event_simpleName=Event_EppDetectionSummaryEvent

# Security incidents
#event_simpleName=Event_IncidentSummaryEvent

# Detection exclusions analysis
#event_simpleName=DetectionExcluded

# Detection activity trend analysis
#event_simpleName=Event_XdrDetectionSummaryEvent OR #event_simpleName=Event_DetectionSummaryEvent OR #event_simpleName=Event_EppDetectionSummaryEvent
| bucket(span=1d)
| groupBy([_bucket, #event_simpleName])
| sort([_bucket, _count], order=[asc, desc])
```

**Audit and Activity Events (High Volume):**
```cql
# User activity audit (769K events/year - highest volume)
#event_simpleName=Event_UserActivityAuditEvent | head(10)

# API activity audit (53K events/year)
#event_simpleName=Event_APIActivityAuditEvent | head(10)

# Authentication activity audit (10K events/year)
#event_simpleName=Event_AuthActivityAuditEvent | head(10)
```

## Field Filtering Patterns

### Exact Matches
```cql
UserName=admin                    # String exact match
CommandLine="/c echo test"        # Quoted strings (spaces/special chars)
SessionId=0                       # Numeric exact match
```

### Wildcard Patterns
```cql
FileName=*powershell*            # Contains pattern
ComputerName=EC2AMAZ*            # Starts with
FileName=*.exe                   # Ends with
```

### Boolean Logic
```cql
# AND (default - space-separated)
FileName=cmd.exe UserName=admin

# OR conditions
(FileName=cmd.exe OR FileName=powershell.exe)

# NOT conditions
FileName!=cmd.exe
NOT UserName=admin

# Complex combinations
(FileName=*powershell* OR FileName=*cmd*) UserName!=SYSTEM
```

### Comparison Operators
```cql
@timestamp > 1759500000000       # Greater than
IntegrityLevel < 16384           # Less than
@timestamp >= 1759500000000      # Greater than or equal
SessionId <= 5                   # Less than or equal
UserName != "SYSTEM"             # Not equal
```

### Field Existence
```cql
CommandLine != null              # Field exists and is not null
CommandLine != ""                # Field exists and is not empty
CommandLine == null              # Field does not exist
```

## Data Selection and Output

### Field Selection and Projection
```cql
# Select specific fields
#event_simpleName=ProcessRollup2
| select([@timestamp, ComputerName, UserName, FileName, CommandLine])

# Select with field renaming
#event_simpleName=ProcessRollup2
| cmd := CommandLine
| select([@timestamp, ComputerName, UserName, FileName, cmd])
```

### Sorting and Limiting
```cql
# Sort by timestamp (newest first)
#event_simpleName=ProcessRollup2
| sort(@timestamp, order=desc)
| head(100)

# Sort by multiple fields
#event_simpleName=ProcessRollup2
| sort([ComputerName, @timestamp], order=[asc, desc])

# Sort and limit results
#event_simpleName=ProcessRollup2
| sort([ComputerName], limit=1000)

# Sort and limit by max results
#event_simpleName=ProcessRollup2
| sort([ComputerName], limit=max)
```

### Aggregation Patterns
```cql
# Count events by computer
#event_simpleName=ProcessRollup2
| groupBy([ComputerName])

# Multiple grouping with statistics
*
| groupBy([ComputerName, UserName], function=[count(), avg(Entitlements)])

# Top analysis
*
| top(ComputerName)
```

## Advanced Pattern Matching

### Regular Expressions
```cql
# Regex pattern matching (case-insensitive)
CommandLine=/.*-enc.*/i

# Case-sensitive regex
CommandLine=/powershell\\.exe/

# Multiple regex patterns
(CommandLine=/-enc/ OR CommandLine=/bypass/)
```

### IN Operator and Lists
```cql
# Multiple exact values case insensitive
in(FileName, values=[cmd.exe, powershell.exe, wmic.exe], ignoreCase=true)

# Multiple exact values case sensitive
in(FileName, values=[cmd.exe, powershell.exe, wmic.exe])

# Numeric values
in(ProcessSxsFlags, values=[1, 2, 10, 64])
```

## Time-Based Analysis

### Timestamp Filtering
```cql

# Unix epoch seconds (ProcessStartTime)
#event_simpleName=ProcessRollup2 ProcessStartTime > 1759505129.000

# Custom Time Range Interval
setTimeInterval(start=7d, end=1d)
| groupBy(["#type", "#Vendor"])

```

### Time Bucketing
```cql
# Time-based bucketing (hourly)
#event_simpleName=ProcessRollup2
| bucket(span=1h, field=ComputerName)

# Time chart visualization
#event_simpleName=ProcessRollup2
| timeChart(span=1h, function=count(), series=UserName)
```

## Security Analysis Patterns

### Detection Event Analysis
```cql
# Find all detection events in last 24 hours
#event_simpleName=Event_XdrDetectionSummaryEvent | head(50)

# Detection frequency analysis
#event_simpleName=Event_XdrDetectionSummaryEvent OR #event_simpleName=Event_DetectionSummaryEvent OR #event_simpleName=Event_EppDetectionSummaryEvent
| bucket(span=1h)
| groupBy([_bucket, #event_simpleName])
| sort([_bucket, _count], order=[asc, desc])

# Detection exclusion analysis (investigate why detections were excluded)
#event_simpleName=DetectionExcluded
| groupBy([ExclusionReason, DetectionType])
| sort(_count, order=desc)
```

### Suspicious Process Detection
```cql
# Encoded PowerShell commands
#event_simpleName=ProcessRollup2 FileName=*powershell*
| (CommandLine=*-enc* OR CommandLine=*-e* OR CommandLine=*EncodedCommand*)

```

### Command Line Analysis
```cql
# Base64 encoded content
#event_simpleName=ProcessRollup2
CommandLine=/[A-Za-z0-9+\\/]{20,}={0,2}/

# Network-related commands

```

## Performance Optimization

### Statement Ordering (Critical)
```cql
# GOOD: Event type first (indexed), specific filters early
#event_simpleName=ProcessRollup2 FileName=cmd.exe UserName=admin

# BAD: Wildcards first, no metadata (# or @) field first
*powershell* UserName=admin
```

### Index-Friendly Patterns
```cql
# Start with metadata field (always indexed)
#event_simpleName=*

# Use specific fields early in query
#event_simpleName=ProcessRollup2 FileName=cmd.exe

# Pre-filter before aggregation
#event_simpleName=ProcessRollup2 UserName != "SYSTEM"
| groupBy([ComputerName, UserName])
```

## Query Building Workflow

1. **Start with metadata fields**: `#event_simpleName=*`
2. **Add specific filters**: `UserName=admin FileName=cmd.exe`
3. **Apply time constraints**: Use tool's time range parameters
4. **Add aggregation**: `| groupBy([FieldName])` if needed
5. **Sort results**: `| sort(@timestamp, order=desc)`
6. **Limit output**: `| head(100)`

## Common Syntax Errors

### Avoid These Mistakes
```cql
# WRONG: Missing quotes for multi-word values
CommandLine=echo test

# CORRECT: Quoted multi-word values
CommandLine="echo test"

# WRONG: Incorrect field names (case sensitive)
filename=cmd.exe

# CORRECT: Exact field names
FileName=cmd.exe

# WRONG: Missing metadata field (# or @) fields (slow performance)
UserName=admin

# CORRECT: Always specify metadata field (# or @ fields)
#event_simpleName=ProcessRollup2 UserName=admin
```

""").strip()

# Use case examples content
NGSIEM_USE_CASES = dedent(r"""
# NG-SIEM Use Case Examples: Natural Language to CQL

*Practical examples of converting security analysis requests into effective LogScale queries*

## Detection Analysis

### "Show me recent security detections"
```cql
#event_simpleName=Event_XdrDetectionSummaryEvent
| select([@timestamp, DetectionId, ThreatName, Severity, HostName, UserName])
| sort(@timestamp, order=desc)
| head(50)
```

### "Find high severity detections from the past week"
```cql
#event_simpleName=Event_XdrDetectionSummaryEvent OR #event_simpleName=Event_DetectionSummaryEvent OR #event_simpleName=Event_EppDetectionSummaryEvent
| Severity>=7 OR SeverityName=*High*
| select([@timestamp, DetectionId, ThreatName, Severity, HostName, UserName])
| sort(Severity, order=desc)
| head(100)
```

### "Show me detection trends over time"
```cql
#event_simpleName=Event_XdrDetectionSummaryEvent OR #event_simpleName=Event_DetectionSummaryEvent OR #event_simpleName=Event_EppDetectionSummaryEvent
| bucket(span=1d)
| groupBy([_bucket, #event_simpleName, SeverityName])
| sort([_bucket, _count], order=[asc, desc])
```

### "Find excluded detections and why they were excluded"
```cql
#event_simpleName=DetectionExcluded
| select([@timestamp, DetectionId, ExclusionReason, DetectionType, HostName])
| groupBy([ExclusionReason, DetectionType])
| sort(_count, order=desc)
| head(20)
```

## Process Monitoring

### "Show me suspicious PowerShell activity"
```cql
#event_simpleName=ProcessRollup2 FileName=*powershell*
(CommandLine=*-enc* OR CommandLine=*-e* OR CommandLine=*EncodedCommand* OR CommandLine=*bypass* OR CommandLine=*hidden*)
| select([@timestamp, ComputerName, UserName, FileName, CommandLine])
| head(100)
```

### "Find processes running with high privileges"
```cql
#event_simpleName=ProcessRollup2 IntegrityLevel>=16384
| groupBy([UserName, FileName])
| sort(_count, order=desc)
| head(50)
```

### "Show me all processes spawned by Office applications"
```cql
#event_simpleName=ProcessRollup2
ParentBaseFileName in (winword.exe, excel.exe, outlook.exe, powerpnt.exe)
| select([@timestamp, ComputerName, UserName, ParentBaseFileName,
FileName, CommandLine])
| head(200)
```

## Network Analysis

### "Show outbound connections to suspicious ports"
```cql
#event_simpleName=NetworkConnectIP4
(RemotePort=443 OR RemotePort=80 OR RemotePort=8080 OR RemotePort=4444)
RemoteAddressIP4!=/^10\./ RemoteAddressIP4!=/^192\.168\./ RemoteAddressIP4!=/^172\.(1[6-9]|2[0-9]|3[01])\./
| head(100)
```

### "Find all DNS queries to suspicious domains"
```cql
#event_simpleName=DnsRequest
(DomainName=*malware* OR DomainName=*phishing* OR DomainName=*suspicious* OR DomainName=*temp*)
| groupBy([DomainName, ComputerName])
| sort(_count, order=desc)
| head(50)
```

## User Behavior Analysis

### "Show failed login attempts"
```cql
#event_simpleName=UserLogon LogonType_decimal!=10 Status!=0
| groupBy([UserName, ComputerName])
| sort(_count, order=desc)
| head(50)
```

### "Find administrative logons outside business hours"
```cql
#event_simpleName=UserLogon LogonType_decimal=10
UserName=*admin* OR UserName=*root* OR UserName=*Administrator*
| eval(hour = time:hour(@timestamp))
| hour < 8 or hour > 18

```

### "Show users accessing sensitive files"
```cql
#event_simpleName=FileOpenInfo
(TargetFileName=*password* OR TargetFileName=*secret* OR TargetFileName=*credential* OR TargetFileName=*.key)
| groupBy([UserName, TargetFileName], limit=max)
```

## Threat Hunting

### "Detect Living Off the Land Binaries (LOLBAS) usage"
```cql
#event_simpleName=ProcessRollup2
FileName in (certutil.exe, bitsadmin.exe, regsvr32.exe, rundll32.exe,
mshta.exe, wmic.exe)
| regex("(?<suspicious_args>-decode|-encodehex|-urlcache|-split|javascript:|vbscript:|scrobj.dll)", field=CommandLine, strict=false)
| test(suspicious_args != null)
| select([@timestamp, ComputerName, UserName, FileName, CommandLine,
suspicious_args])
| head(200)
```

### "Hunt for potential command and control beaconing"
```cql
#event_simpleName=NetworkConnectIP4
RemoteAddressIP4!=/^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)/
| bucket(span=5m)
| groupBy([_bucket, ComputerName, RemoteAddressIP4])
| count(as=connections_per_5min)
| connections_per_5min > 3 AND connections_per_5min < 20  // Regular but not too frequent
| sort([ComputerName, _bucket])
```

### "Detect process hollowing indicators"
```cql
#event_simpleName=ProcessRollup2
| eval(is_system_process = if(FileName in (svchost.exe, rundll32.exe,
dllhost.exe), "yes", "no"))
| test(is_system_process == "yes")
| regex("(?<unusual_path>(?!.*system32)(?!.*syswow64).*)",
field=ImageFileName, strict=false)
| test(unusual_path != null)
| select([@timestamp, ComputerName, UserName, FileName,
ImageFileName, CommandLine])
```

### "Hunt for persistence mechanisms via scheduled tasks"
```cql
#event_simpleName=ProcessRollup2
FileName=schtasks.exe OR CommandLine=*schtasks*
| regex("(?<task_action>/create|/change|/run)", field=CommandLine,
strict=false)
| test(task_action != null)
| regex("(?<task_name>/tn\\s+[\"']?([^\"'\\s]+)[\"']?)",
field=CommandLine, strict=false)
| select([@timestamp, ComputerName, UserName, CommandLine,
task_action, task_name])
```

### "Detect potential data exfiltration via compression tools"
```cql
#event_simpleName=ProcessRollup2
(FileName=*rar.exe OR FileName=*7z.exe OR FileName=*zip.exe OR CommandLine=*compress* OR CommandLine=*archive*)
| regex("(?<archive_target>\\s+-[a-z]*\\s+[\"']?([^\"'\\s]+\\.(rar|7z|zip))[\"']?)", field=CommandLine, strict=false)
| test(archive_target != null)
| groupBy([ComputerName, UserName, archive_target])
| sort(_count, order=desc)
```

### "Hunt for lateral movement via WMI"
```cql
#event_simpleName=ProcessRollup2
(FileName=wmic.exe OR FileName=wmiprvse.exe)
| regex("(?<wmi_command>process\\s+call\\s+create|/node:|ComputerName=)", field=CommandLine, strict=false)
| test(wmi_command != null)
| regex("(?<target_host>/node:\"?([^\"\\s]+)\"?|ComputerName=\"?([^\"\\s]+)\"?)", field=CommandLine, strict=false)
| select([@timestamp, ComputerName, UserName, CommandLine, target_host])
```


## File System Analysis

### "Show new executable files written to suspicious locations"
```cql
#event_simpleName=NewExecutableWritten
(TargetFileName=*temp* OR TargetFileName=*appdata* OR TargetFileName=*public*)

```

### "Find files with suspicious names"
```cql
#event_simpleName=FileOpenInfo
TargetFileName=*svchost* TargetFileName!=*system32*
OR TargetFileName=*lsass* TargetFileName!=*system32*
OR TargetFileName=*winlogon* TargetFileName!=*system32*

```

## Compliance and Monitoring

### "Show all administrative actions in the last hour"
```cql
#event_simpleName=ProcessRollup2 @timestamp > (now() - 3600000)
(UserName=*admin* OR IntegrityLevel>=16384)
| select([@timestamp, ComputerName, UserName, FileName, CommandLine])
| sort(@timestamp, order=desc)
| head(200)
```

### "Find unauthorized software installations"
```cql
#event_simpleName=ProcessRollup2
(FileName=*install* OR FileName=*setup* OR CommandLine=*msiexec*)
UserName!=SYSTEM
| select([@timestamp, ComputerName, UserName, FileName, CommandLine])
| head(100)
```

## Performance-Optimized Queries

### "Top processes by execution frequency (efficient grouping)"
```cql
#event_simpleName=ProcessRollup2
| groupBy([FileName], limit=20)
| sort(_count, order=desc)
```

### "Host activity summary (pre-filtered for performance)"
```cql
#event_simpleName=ProcessRollup2 UserName!=SYSTEM
| groupBy([ComputerName], function=[count(), collect([, FileName]) ])
```

## Advanced Correlation

### "Correlate process creation with network activity"
```cql
// Step 1: Create lookup table of network connections
defineTable(query={#event_simpleName=NetworkConnectIP4
                   RemoteAddressIP4!=/^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)/},
                       name="external_connections",
                           include=[ContextProcessId, RemoteAddressIP4, RemotePort,
                               @timestamp])

// Step 2: Join with process events
| #event_simpleName=ProcessRollup2
| match(table="external_connections", field=ProcessId, column=ContextProcessId)
| test(RemoteAddressIP4 != null)  // Only processes with external connections
| select([@timestamp, ComputerName, UserName, ImageFileName,
CommandLine, RemoteAddressIP4, RemotePort])
```

### "Find processes that accessed files and made network connections"
```cql
// Multi-stage correlation using defineTable
defineTable(query={#event_simpleName=FileOpenInfo TargetFileName=*.exe},
           name="file_access",
               include=[ContextProcessId, ComputerName, TargetFileName])

defineTable(query={#event_simpleName=NetworkConnectIP4
                   RemoteAddressIP4!=/^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)/},
                       name="network_activity",
                           include=[ContextProcessId, ComputerName, RemoteAddressIP4])

| #event_simpleName=ProcessRollup2
| match(table="file_access", field=[ProcessId, ComputerName],
column=[ContextProcessId, ComputerName])
| match(table="network_activity", field=[ProcessId, ComputerName],
column=[ContextProcessId, ComputerName])
| test(TargetFileName != null AND RemoteAddressIP4 != null)
| select([@timestamp, ComputerName, UserName, ImageFileName,
TargetFileName, RemoteAddressIP4])
```

### "Detect privilege escalation followed by lateral movement"
```cql
// Step 1: Find privilege escalation events
defineTable(query={#event_simpleName=ProcessRollup2
                   IntegrityLevel>=16384
                   UserName!=SYSTEM},
                       name="privilege_escalation",
                           include=[ComputerName, UserName, @timestamp, ProcessId])

// Step 2: Look for network activity from escalated processes
| #event_simpleName=NetworkConnectIP4
| match(table="privilege_escalation", field=[ComputerName,
ContextProcessId], column=[ComputerName, ProcessId])
| test(@timestamp > _timestamp)  // Network activity after privilege escalation
| eval(time_diff = @timestamp - _timestamp)
| test(time_diff < 3600000)  // Within 1 hour
| select([@timestamp, ComputerName, UserName, RemoteAddressIP4,
RemotePort, time_diff])
```

## Query Customization Tips

Each query can be customized by:
- **Adjusting time ranges**: Use tool's time range parameters (1h,
24h, 7d, etc.)
- **Adding specific host filters**:
`ComputerName=SERVER01` or `ComputerName=*DC*`
- **Including additional event types**:
Add OR conditions for multiple event types
- **Modifying field filters**: Adapt patterns for your environment's naming conventions
- **Adding exclusions**: Use `NOT` or `!=` to filter out known-good activity
- **Changing output limits**: Adjust `head()` values based on your analysis needs

## Best Practices for Security Queries

1. **Always start with event type**: Improves performance significantly
2. **Use time constraints**: Apply reasonable time ranges to prevent large result sets
3. **Filter early**: Add specific filters before aggregation functions
4. **Include context fields**: Always select relevant fields for investigation
5. **Limit results**: Use `head()` to prevent overwhelming output
6. **Test incrementally**: Start with basic filters and add complexity gradually

""").strip()

# LogScale functions reference content


def get_logscale_functions_content() -> str:
    """Get the complete LogScale functions content."""
    return ""


# This will be the complete content from the logscale-functions.md file

NGSIEM_FUNCTIONS = r"""# LogScale Functions Reference for Claude

*Comprehensive CQL function reference optimized for Claude Code usage with CrowdStrike SIEM*

## Function Categories Overview

LogScale functions are organized into functional categories based on their purpose:

- **Aggregate Functions**: Statistical operations (`count()`,
`avg()`, `sum()`, `groupBy()`)
- **Array Functions**: Array manipulation and processing
- **Data Manipulation**: Field creation, modification,
and formatting (`eval()`, `format()`)
- **Filtering Functions**: Event filtering and pattern matching (
`test()`, `regex()`)
- **Parsing Functions**: Data extraction (`parseJson()`, `regex()`,
`kvParse()`)
- **String Functions**: Text manipulation and processing
- **Time/Date Functions**: Timestamp handling and time-based operations
- **Mathematical Functions**: Calculations and transformations
- **Network Functions**: IP, DNS, and network-related operations
- **Security Functions**: Hash generation, IOC lookups, security analysis

## Core Function Reference

### Essential Aggregate Functions

**count([field], [as=string], [distinct=boolean])**
```cql
// Count all events
count()

// Count with custom field name
count(as=total_events)

// Count distinct values (estimated accuracy <2%)
count(user_id, distinct=true)

// Usage in groupBy
#event_simpleName=ProcessRollup2
| groupBy([ComputerName], function=count())
```

**groupBy(field, [function], [limit])**
```cql
// Basic grouping by field
#event_simpleName=ProcessRollup2
| groupBy([ComputerName])

// Multiple aggregations with nested groupBy
#event_simpleName=ProcessRollup2
| groupBy([UserName], function=[count(as=total_processes),
                                groupBy(ImageFileName,
                                    function=count(as=process_count))])

// Find unique values only (memory efficient)
#event_simpleName=ProcessRollup2
| groupBy([UserName], function=[])

// Session analysis with collect
#event_simpleName=ProcessRollup2
| groupBy(UserName, function=session(maxpause=30m, collect([ImageFileName])))
```
**bucket([span], [buckets], [field], [function])**
```cql
// Time-based bucketing (hourly) for CrowdStrike events
#event_simpleName=ProcessRollup2
| bucket(span=1h, field=@timestamp)
| groupBy([_bucket, ComputerName])
| count(as=processes_per_hour)

// Create 24 buckets over query timerange for trend analysis
#event_simpleName=NetworkConnectIP4
| bucket(buckets=24, function=[count(), groupBy(RemoteAddressIP4)])
```

### Essential Data Processing Functions

**regex(regex, [field], [flags], [strict])**
```cql
// Extract data with named groups from command lines
#event_simpleName=ProcessRollup2
| regex("(?<encoded_cmd>-enc[a-zA-Z]*\\s+(?<b64>[A-Za-z0-9+/=]+))",
field=CommandLine, strict=false)

// Case-insensitive matching for LOLBAS detection
#event_simpleName=ProcessRollup2
| regex("(?<lolbas_technique>javascript:|vbscript:|scrobj.dll|javascript|vbscript)", field=CommandLine, flags="i", strict=false)

// Multiple extractions from network data
#event_simpleName=NetworkConnectIP4
| regex("(?<ip_class>^(10|172|192)\\.)", field=RemoteAddressIP4, strict=false)
```

**eval(field_name = expression)**
```cql
// Create calculated fields for security analysis
#event_simpleName=ProcessRollup2
| eval(is_admin = if(UserName=*admin*, "yes", "no"),
    is_suspicious = if(CommandLine=*-enc*, "true", "false"),
           risk_score = case(
               IntegrityLevel >= 16384, 10,
                   CommandLine=*bypass*, 8,
                       CommandLine=*hidden*, 7,
                           3))

// Time-based analysis fields
#event_simpleName=ProcessRollup2
| eval(hour = time:hour(@timestamp),
    is_business_hours = if(hour >= 9 AND hour <= 17, "yes", "no"),
           day_of_week = time:dayOfWeekName(@timestamp))
```

**test(expression)**
```cql
// Complex filtering conditions for threat hunting
#event_simpleName=ProcessRollup2
| test(length(CommandLine) > 100 AND UserName != "SYSTEM" AND IntegrityLevel >= 16384)

// Time-based filtering with mathematical operations
#event_simpleName=ProcessRollup2
| eval(process_age = now() - ProcessStartTime)
| test(process_age < 300000)  // Processes started in last 5 minutes
```

**defineTable() - Advanced Correlation Examples**
```cql
// Example 1: IOC enrichment table
defineTable(query={CommandLine=*malware*|*trojan*|*backdoor*
                   | regex("(?<ioc_ip>\\d+\\.\\d+\\.\\d+\\.\\d+)",
                       field=CommandLine)
                   | test(ioc_ip != null)
                   | eval(threat_level = "high", ioc_type = "ip")},
                       name="threat_indicators",
                           include=[ioc_ip, threat_level, ioc_type])

| #event_simpleName=NetworkConnectIP4
| match(table="threat_indicators", field=RemoteAddressIP4, column=ioc_ip)
| test(threat_level != null)
| select([@timestamp, ComputerName, RemoteAddressIP4, threat_level])

// Example 2: Baseline deviation detection
defineTable(query={#event_simpleName=ProcessRollup2 @timestamp > (now() - 30d)
                   | groupBy([ComputerName, ImageFileName])
                   | count()
                   | eval(baseline_count = _count, is_normal = "yes")},
                       name="process_baseline",
                           include=[ComputerName, ImageFileName, baseline_count])

| #event_simpleName=ProcessRollup2 @timestamp > (now() - 1h)
| groupBy([ComputerName, ImageFileName])
| count()
| match(table="process_baseline", field=[ComputerName,
ImageFileName], column=[ComputerName, ImageFileName])
| eval(deviation = if(baseline_count == null, "NEW_PROCESS",
                     if(_count > baseline_count * 3,
                         "HIGH_FREQUENCY", "NORMAL")))
| test(deviation != "NORMAL")
```

### Essential Time Functions

**timeChart([span], [function], [series])**
```cql
// Basic time chart for process creation monitoring
#event_simpleName=ProcessRollup2
| timeChart(span=1h, function=count())

// Multiple series analysis by user
#event_simpleName=ProcessRollup2
| timeChart(span=1h, function=count(), series=UserName)

// Advanced time chart with filtering
#event_simpleName=ProcessRollup2 IntegrityLevel>=16384
| timeChart(span=30m, function=count(), series=ComputerName)
```

**slidingTimeWindow([function], [span])**
```cql
// Detect beaconing behavior with sliding windows
#event_simpleName=NetworkConnectIP4
| groupBy([ComputerName, RemoteAddressIP4],
          function=slidingTimeWindow([count()], span=5m))
| _count > 5  // More than 5 connections in any 5-minute window
```

### Array and Collection Functions

**collect([field])**
```cql
// Collect processes per user session
#event_simpleName=ProcessRollup2
| groupBy(UserName, function=session(maxpause=15m, collect([ImageFileName])))

// Collect unique command line arguments
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:dedup(cmd_args)
| groupBy(ImageFileName, function=collect([cmd_args]))
```

**array:contains() and array:filter()**
```cql
// Find processes with suspicious arguments
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:contains(cmd_args, value="-enc")
| test(array_contains_result == true)

// Filter command arguments to show only flags
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:filter(cmd_args, test=/^-/))
```

### Essential Data Processing Functions

**regex(regex, [field], [flags], [strict])**
```cql
// Extract data with named groups
#Vendor=*
| regex("(?<domain>\\w+\\.com)", field=@rawstring)

// Case-insensitive matching with regex function
#Vendor=paloalto
| regex("(?<type>url|traffic|threat)", field=@rawstring, flags="i")

// Case-insensitive matching shorthand
#Vendor=paloalto
| @rawstring = /url|traffic|threat/i

```

**parseJson([field], [prefix], [exclude])**
```cql
// Parse JSON field
#type=*aws*
| parseJson()

// Parse with prefix and exclusions
#event_simpleName=ProcessRollup2
| parseJson(field=event_data, prefix="evt_", exclude=["debug", "trace"])
```

**eval(field_name = expression)**
```cql
// Create calculated fields
#event_simpleName=ProcessRollup2
| eval(is_admin = if(UserName=*admin*, "yes", "no"))

// Multiple field creation
#event_simpleName=ProcessRollup2
| eval(hour = strftime("%H", @timestamp),
    is_suspicious = if(CommandLine=*-enc*, "true", "false"))
```

**test(expression)**
```cql
// Complex filtering conditions
#event_simpleName=ProcessRollup2
| test(length(CommandLine) > 100 and UserName != "SYSTEM")

// Time-based filtering
#event_simpleName=ProcessRollup2
| test(@timestamp > (now() - 86400000))
```

**defineTable()**
```cql
// Example 1: Join network listeners with processes
defineTable(query={#event_simpleName=NetworkListenIP4 LocalPort<1024 LocalPort!=0},
           name="network_listeners",
               include=[ContextProcessId, LocalAddressIP4, LocalPort])
| #event_simpleName=ProcessRollup2
| match(table="network_listeners", field=TargetProcessId,
column=ContextProcessId)
| select([ImageFileName, CommandLine, LocalAddressIP4, LocalPort])

// Example 2: Join privileged logons with process executions
defineTable(query={#event_simpleName=UserLogon LogonType_decimal=10},
           name="privileged_logons",
               include=[UserName, ComputerName, LogonTime])
| #event_simpleName=ProcessRollup2
| match(table="privileged_logons", field=UserName, column=UserName)
| test(@timestamp > LogonTime)  // Only processes after privileged logon
| select([@timestamp, UserName, ComputerName, ImageFileName, CommandLine])

// Example 3: Join suspicious network connections with processes
defineTable(query={#event_simpleName=NetworkConnectIP4
                   RemoteAddressIP4!=/^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)/},
                       name="external_connections",
                           include=[ContextProcessId, RemoteAddressIP4, RemotePort])
| #event_simpleName=ProcessRollup2
| match(table="external_connections", field=ProcessId, column=ContextProcessId)
| select([@timestamp, ComputerName, UserName, ImageFileName,
          RemoteAddressIP4, RemotePort, CommandLine])

// Example 4: Complex multi-field matching
defineTable(query={#event_simpleName=FileOpenInfo TargetFileName=*.exe},
           name="exe_access",
               include=[ContextProcessId, ComputerName, TargetFileName])
| #event_simpleName=ProcessRollup2
| match(table="exe_access", field=[ProcessId, ComputerName],
column=[ContextProcessId, ComputerName])
| select([timestamp, UserName, ComputerName, ImageFileName, TargetFileName])
```

### Essential Time Functions

**timeChart([span], [function], [series])**
```cql
// Basic time chart
#event_simpleName=ProcessRollup2
| timeChart(span=1h, function=count())

// Multiple series analysis
#event_simpleName=ProcessRollup2
| timeChart(span=1h, function=count(), series=UserName)
```

**formatTime(field, format, [timezone])**
```cql
// Format timestamps
#event_simpleName=ProcessRollup2
| formatTime(@timestamp, format="%Y-%m-%d %H:%M:%S", as=readable_time)
```

## Complete Function Categories

### Aggregate Functions
- `accumulate()` - Applies an aggregation function cumulatively to a sequence of events
```cql
// Track cumulative login count per user over time
#event_simpleName=UserLogon
| sort(@timestamp)
| accumulate(count(), field=cumulative_logins, by=UserName)
```

- `avg()` - Calculates the average for a field of a set of events
```cql
// Average process execution time
#event_simpleName=ProcessRollup2
| eval(exec_time = ProcessEndTime - ProcessStartTime)
| groupBy([ImageFileName])
| avg(exec_time, as=avg_execution_time)
```

- `bucket()` - Extends the groupBy() function for grouping by time
```cql
// Process creation rate over time (hourly buckets)
#event_simpleName=ProcessRollup2
| bucket(span=1h)
| groupBy([_bucket, ComputerName])
| count(as=processes_per_hour)
```

- `callFunction()` - Calls the named function on a field over a group of events
```cql
// Apply custom function to process command lines
#event_simpleName=ProcessRollup2
| callFunction(myCustomParser, field=CommandLine)
```

- `collect()` - Collects multiple values into an array
```cql
// Collect all processes run by each user
#event_simpleName=ProcessRollup2
| groupBy([UserName])
| collect(ImageFileName, as=user_processes)
```

- `correlate()` - Correlates events based on time proximity
```cql
// Correlate network connections with process starts
#event_simpleName=NetworkConnectIP4
| correlate(field=ComputerName,
           query={#event_simpleName=ProcessRollup2},
               timeWindow=5m)
```

- `count()` - Counts events or distinct values
```cql
// Count unique processes per host
#event_simpleName=ProcessRollup2
| groupBy([ComputerName])
| count(ImageFileName, distinct=true, as=unique_processes)
```

- `counterAsRate()` - Converts counter values to rates
```cql
// Convert process count to rate per minute
#event_simpleName=ProcessRollup2
| bucket(span=1m)
| groupBy([_bucket, ComputerName])
| count()
| counterAsRate(field=_count, as=processes_per_minute)
```

- `fieldstats()` - Calculates statistics for fields
```cql
// Statistics on command line lengths
#event_simpleName=ProcessRollup2
| eval(cmd_length = length(CommandLine))
| fieldstats(cmd_length)
```

- `groupBy()` - Groups results by field values
```cql
// Group processes by user and computer
#event_simpleName=ProcessRollup2
| groupBy([UserName, ComputerName], function=[count(), collect(ImageFileName)])
```

- `head()` - Returns the first N events
```cql
// Get first 100 process events
#event_simpleName=ProcessRollup2
| sort(@timestamp)
| head(100)
```

- `linReg()` - Performs linear regression analysis
```cql
// Linear regression on process creation rate over time
#event_simpleName=ProcessRollup2
| bucket(span=1h)
| groupBy([_bucket])
| count()
| linReg(x=_bucket, y=_count)
```

- `max()` - Finds the maximum value
```cql
// Find maximum process ID per host
#event_simpleName=ProcessRollup2
| groupBy([ComputerName])
| max(ProcessId, as=max_pid)
```

- `min()` - Finds the minimum value
```cql
// Find earliest process start time per user
#event_simpleName=ProcessRollup2
| groupBy([UserName])
| min(ProcessStartTime, as=first_process_time)
```

- `neighbor()` - Accesses neighboring events
```cql
// Compare current process with previous process on same host
#event_simpleName=ProcessRollup2
| sort(@timestamp)
| neighbor(field=ImageFileName, as=prev_process, by=ComputerName)
| test(ImageFileName != prev_process)
```

- `partition()` - Partitions events into groups
```cql
// Partition processes into administrative vs normal
#event_simpleName=ProcessRollup2
| partition(field=partition_type,
           by=if(UserName=*admin*, "admin", "normal"))
```

- `percentage()` - Calculates percentages
```cql
// Percentage of processes by type
#event_simpleName=ProcessRollup2
| groupBy([ImageFileName])
| count()
| percentage()
```

- `percentile()` - Calculates percentiles
```cql
// 95th percentile of command line length
#event_simpleName=ProcessRollup2
| eval(cmd_length = length(CommandLine))
| percentile(cmd_length, percentiles=[50, 95])
```

- `range()` - Calculates the range of values
```cql
// Range of process execution times
#event_simpleName=ProcessRollup2
| eval(exec_time = ProcessEndTime - ProcessStartTime)
| groupBy([ComputerName])
| range(exec_time)
```

- `rdns()` - Performs reverse DNS lookups
```cql
// Reverse DNS lookup for network connections
#event_simpleName=NetworkConnectIP4
| rdns(field=RemoteAddressIP4, as=remote_hostname)
```

- `sankey()` - Creates Sankey diagrams
```cql
// Process execution flow diagram
#event_simpleName=ProcessRollup2
| sankey(source=ParentCommandLine, target=CommandLine)
```

- `selectFromMax()` - Selects events with maximum values
```cql
// Select process with highest PID per host
#event_simpleName=ProcessRollup2
| selectFromMax(ProcessId, by=ComputerName)
```

- `selectFromMin()` - Selects events with minimum values
```cql
// Select first process per user session
#event_simpleName=ProcessRollup2
| selectFromMin(ProcessStartTime, by=[UserName, ComputerName])
```

- `selectLast()` - Selects the last event from each group
```cql
// Select last process execution per host
#event_simpleName=ProcessRollup2
| groupBy([ComputerName])
| selectLast()
```

- `series()` - Creates time series data
```cql
// Create time series of process creation rate
#event_simpleName=ProcessRollup2
| series(x=@timestamp, y=ProcessId, groupBy=ComputerName)
```

- `session()` - Groups events into sessions
```cql
// Group user activities into sessions (30min timeout)
#event_simpleName=ProcessRollup2
| session(maxPause=30m, by=UserName)
```

- `slidingTimeWindow()` - Creates sliding time windows
```cql
// Sliding 5-minute window for process activity
#event_simpleName=ProcessRollup2
| slidingTimeWindow(window=5m)
| groupBy([_window, ComputerName])
| count()
```

- `slidingWindow()` - Creates sliding windows
```cql
// Sliding window of 10 events per host
#event_simpleName=ProcessRollup2
| sort(@timestamp)
| slidingWindow(size=10, by=ComputerName)
```

- `sort()` - Sorts events
```cql
// Sort by ComputerName, UserName, CommandLine
#event_simpleName=ProcessRollup2
| select([ComputerName, UserName, CommandLine])
| sort([ComputerName, UserName, CommandLine], order=[desc, asc, desc])
```

- `stats()` - Calculates statistics
```cql
// Comprehensive statistics on process IDs
#event_simpleName=ProcessRollup2
| stats(avg(ProcessId), stdDev(ProcessId), by=ComputerName)
```

- `stdDev()` - Calculates standard deviation
```cql
// Standard deviation of command line lengths by user
#event_simpleName=ProcessRollup2
| eval(cmd_length = length(CommandLine))
| groupBy([UserName])
| stdDev(cmd_length)
```

- `sum()` - Sums values
```cql
// Total bytes transferred per host
#event_simpleName=NetworkConnectIP4
| groupBy([ComputerName])
| sum(BytesTransferred)
```

- `table()` - Creates tabular output
```cql
// Create formatted table of process summary
#event_simpleName=ProcessRollup2
| groupBy([ComputerName, UserName])
| count()
| table(ComputerName, UserName, _count, title="Process Summary")
```

- `tail()` - Returns the last N events
```cql
// Get last 50 network connections
#event_simpleName=NetworkConnectIP4
| sort(@timestamp)
| tail(50)
```

- `timeChart()` - Creates time-based charts
```cql
// Time chart of process creation by user
#event_simpleName=ProcessRollup2
| timeChart(span=1h, function=count(), series=UserName)
```

- `top()` - Returns top values
```cql
// Top 10 most common processes
#event_simpleName=ProcessRollup2
| top(ImageFileName, limit=10)
```

- `transpose()` - Transposes data
```cql
// Transpose user activity matrix
#event_simpleName=ProcessRollup2
| groupBy([UserName, ImageFileName])
| count()
| transpose()
```

- `window()` - Creates windowed views
```cql
// 1-hour windows for anomaly detection
#event_simpleName=ProcessRollup2
| window(span=1h)
| groupBy([_window, ComputerName])
| count()
```

- `worldMap()` - Creates geographical visualizations
```cql
// World map of network connections
#event_simpleName=NetworkConnectIP4
| ipLocation(RemoteAddressIP4)
| worldMap(lat=lat, lon=lon)
```

### Array Functions
- `array:append()` - Appends values to an array
```cql
// Build array of process names per user
#event_simpleName=ProcessRollup2
| groupBy([UserName])
| array:append(processes, ImageFileName)
```

- `array:contains()` - Checks if array contains a value
```cql
// Check if user has run suspicious processes
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:contains(cmd_args, "powershell.exe")
```

- `array:dedup()` - Removes duplicate elements from an array
```cql
// Remove duplicate command line arguments
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:dedup(cmd_args)
```

- `array:drop()` - Drops all fields of an array
```cql
// Clean up temporary array fields
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=temp_args)
| eval(arg_count = array:length(temp_args))
| array:drop(temp_args)
```

- `array:eval()` - Evaluates functions on array values
```cql
// Apply uppercase to all command arguments
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:eval(cmd_args, function=upper(%s))
```

- `array:exists()` - Filters events based on array element conditions
```cql
// Find processes with encoded arguments
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:exists(cmd_args, test(/^[A-Za-z0-9+\/=]{20,}$/))
```

- `array:filter()` - Filters array elements
```cql
// Filter command arguments to only show flags
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:filter(cmd_args, test(/^-/))
```

- `array:intersection()` - Performs array intersection operations
```cql
// Find common processes between two users
#event_simpleName=ProcessRollup2 UserName=alice
| collect(ImageFileName, as=alice_processes)
| array:intersection(alice_processes,
    {#event_simpleName=ProcessRollup2 UserName=bob | collect(ImageFileName)})
```

- `array:length()` - Counts elements in an array
```cql
// Count command line arguments
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| eval(arg_count = array:length(cmd_args))
| test(arg_count > 10)
```

- `array:reduceAll()` - Reduces all array elements to a single value
```cql
// Concatenate all process names into single string
#event_simpleName=ProcessRollup2
| groupBy([ComputerName])
| collect(ImageFileName, as=processes)
| array:reduceAll(processes, function=concat(%s, separator=","))
```

- `array:regex()` - Applies regex to array elements
```cql
// Find encoded parameters in command arguments
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:regex(cmd_args, /^[A-Za-z0-9+\/=]{20,}$/)
```

- `array:rename()` - Renames array fields
```cql
// Rename process array fields
#event_simpleName=ProcessRollup2
| collect(ImageFileName, as=temp_processes)
| array:rename(temp_processes, as=user_processes)
```

- `array:sort()` - Sorts array elements
```cql
// Sort command arguments alphabetically
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| array:sort(cmd_args, order=asc)
```

- `array:union()` - Performs array union operations
```cql
// Combine process lists from multiple users
#event_simpleName=ProcessRollup2 UserName=alice
| collect(ImageFileName, as=alice_processes)
| array:union(alice_processes,
    {#event_simpleName=ProcessRollup2 UserName=bob | collect(ImageFileName)})
```

- `concatArray()` - Concatenates arrays
```cql
// Combine multiple command line arrays
#event_simpleName=ProcessRollup2
| split(CommandLine, delimiter=" ", as=cmd_args)
| split(ParentCommandLine, delimiter=" ", as=parent_args)
| concatArray([cmd_args, parent_args], as=all_args)
```

- `objectArray:eval()` - Evaluates functions on object arrays
```cql
// Process structured event data arrays
#event_simpleName=ProcessRollup2
| parseJson(field=event_metadata)
| objectArray:eval(metadata_array, function=upper(process_name))
```

- `objectArray:exists()` - Tests existence in object arrays
```cql
// Check if process metadata contains specific attributes
#event_simpleName=ProcessRollup2
| parseJson(field=process_metadata)
| objectArray:exists(metadata, test(privilege_level="admin"))
```

### Data Manipulation Functions
- `bitfield:extractFlags()` - Extracts flags from bitfields
- `bitfield:extractFlagsAsArray()` - Extracts bitfield flags as arrays
- `bitfield:extractFlagsAsString()` - Extracts bitfield flags as strings
- `coalesce()` - Returns the first non-null value
- `concat()` - Concatenates strings
- `copyEvent()` - Creates copies of events
- `default()` - Provides default values for missing fields
- `defineTable()` - Creates lookup tables from query results
- `drop()` - Drops fields from events
- `dropEvent()` - Drops entire events
- `eval()` - Creates calculated fields
- `format()` - Formats strings with variables
- `getField()` - Gets field values dynamically
- `rename()` - Renames fields
- `replace()` - Replaces text in fields
- `select()` - Selects specific fields
- `setField()` - Sets field values dynamically
- `unit:convert()` - Converts between units

### Parsing Functions
- `kvParse()` - Parses key-value pairs
- `parseCEF()` - Parses Common Event Format data
- `parseCsv()` - Parses CSV data
- `parseFixedWidth()` - Parses fixed-width data
- `parseHexString()` - Parses hexadecimal strings
- `parseInt()` - Parses integers
- `parseJson()` - Parses JSON data
- `parseLEEF()` - Parses Log Event Extended Format data
- `parseTimestamp()` - Parses timestamps
- `parseUri()` - Parses URIs
- `parseUrl()` - Parses URLs
- `parseXml()` - Parses XML data
- `regex()` - Extracts data using regular expressions

### String Functions
- `base64Decode()` - Decodes Base64 strings
- `base64Encode()` - Encodes strings to Base64
- `length()` - Returns string length
- `lower()` - Converts to lowercase
- `lowercase()` - Converts to lowercase (alias)
- `split()` - Splits strings into arrays
- `splitString()` - Splits strings
- `stripAnsiCodes()` - Removes ANSI codes from strings
- `text:contains()` - Tests if text contains substring
- `text:endsWith()` - Tests if text ends with substring
- `text:length()` - Returns text length
- `text:positionOf()` - Finds position of substring
- `text:startsWith()` - Tests if text starts with substring
- `text:substring()` - Extracts substring
- `upper()` - Converts to uppercase
- `urlDecode()` - Decodes URL-encoded strings
- `urlEncode()` - Encodes strings for URLs

### Network Functions
- `asn()` - Gets Autonomous System Number for IP addresses
- `cidr()` - Tests if IP is in CIDR range
- `communityId()` - Generates Community ID hashes for network flows
- `geography:distance()` - Calculates geographical distances
- `geohash()` - Generates geohash for coordinates
- `ipLocation()` - Gets geographical location for IP addresses
- `reverseDns()` - Performs reverse DNS lookups
- `subnet()` - Tests if IP is in subnet

### Security Functions
- `crypto:md5()` - Generates MD5 hashes
- `crypto:sha1()` - Generates SHA1 hashes
- `crypto:sha256()` - Generates SHA256 hashes
- `hash()` - Generates non-cryptographic hashes
- `hashMatch()` - Matches against hash values
- `hashRewrite()` - Rewrites hash values
- `ioc:lookup()` - Performs threat intelligence lookups
- `shannonEntropy()` - Calculates Shannon entropy
- `tokenHash()` - Generates token hashes

### Mathematical Functions
- `math:abs()` - Absolute value
- `math:arccos()` - Arc cosine
- `math:arcsin()` - Arc sine
- `math:arctan()` - Arc tangent
- `math:arctan2()` - Arc tangent of two variables
- `math:ceil()` - Ceiling function
- `math:cos()` - Cosine
- `math:cosh()` - Hyperbolic cosine
- `math:deg2rad()` - Converts degrees to radians
- `math:exp()` - Exponential function
- `math:expm1()` - Exponential minus 1
- `math:floor()` - Floor function
- `math:log()` - Natural logarithm
- `math:log10()` - Base-10 logarithm
- `math:log1p()` - Natural logarithm of 1 plus argument
- `math:log2()` - Base-2 logarithm
- `math:mod()` - Modulo operation
- `math:pow()` - Power function
- `math:rad2deg()` - Converts radians to degrees
- `math:sin()` - Sine
- `math:sinh()` - Hyperbolic sine
- `math:sqrt()` - Square root
- `math:tan()` - Tangent
- `math:tanh()` - Hyperbolic tangent
- `round()` - Rounds to nearest integer

### Time/Date Functions
- `duration()` - Calculates time durations
- `end()` - Gets end time of time window
- `findTimestamp()` - Finds timestamps in text
- `formatDuration()` - Formats duration values
- `formatTime()` - Formats timestamps
- `now()` - Gets current timestamp
- `parseTimestamp()` - Parses timestamp strings
- `setTimeInterval()` - Sets time intervals
- `start()` - Gets start time of time window
- `time:dayOfMonth()` - Extracts day of month
- `time:dayOfWeek()` - Extracts day of week (numeric)
- `time:dayOfWeekName()` - Extracts day of week (name)
- `time:dayOfYear()` - Extracts day of year
- `time:hour()` - Extracts hour
- `time:millisecond()` - Extracts milliseconds
- `time:minute()` - Extracts minutes
- `time:month()` - Extracts month (numeric)
- `time:monthName()` - Extracts month (name)
- `time:second()` - Extracts seconds
- `time:weekOfYear()` - Extracts week of year
- `time:year()` - Extracts year

### Filter Functions
- `if()` - Conditional expressions
- `in()` - Tests if value is in list
- `match()` - Pattern matching
- `sample()` - Statistical sampling
- `test()` - Complex filtering conditions
- `wildcard()` - Wildcard pattern matching

### Event Manipulation Functions
- `createEvents()` - Creates new events
- `eventFieldCount()` - Counts fields in events
- `eventInternals()` - Access event internal information
- `eventSize()` - Gets event size information
- `fieldset()` - Creates field sets

### Join Functions
- `join()` - Joins with external data
- `selfJoin()` - Joins events with themselves
- `selfJoinFilter()` - Filters self-joined events

### Utility Functions
- `beta:param()` - Beta parameter functions
- `beta:repeating()` - Beta repeating functions
- `json:prettyPrint()` - Pretty-prints JSON
- `readFile()` - Reads files
- `writeJson()` - Writes JSON output
- `xml:prettyPrint()` - Pretty-prints XML

## CrowdStrike-Specific Usage Patterns

### Advanced defineTable() Usage - Creating Lookup Tables for Joins

**Example 1: User Privilege Escalation Detection**
```cql
// Step 1: Create baseline of normal user activities
defineTable(query={#event_simpleName=ProcessRollup2 @timestamp < (now() - 7d)
                   | groupBy([UserName, ImageFileName])
                   | count()
                   | eval(baseline_activity = _count)},
                       name="user_baseline",
                           include=[UserName, ImageFileName, baseline_activity])

// Step 2: Detect privilege escalation using match
| #event_simpleName=ProcessRollup2 @timestamp > (now() - 1d)
| match(table="user_baseline", field=[UserName, ImageFileName],
column=[UserName, ImageFileName])
| test(baseline_activity == null)  // New process for this user
| test(ImageFileName=/admin|elevated|privilege/i)
| select([@timestamp, UserName, ComputerName, ImageFileName, CommandLine])
```

**Example 2: Network Connection Enrichment**
```cql
// Step 1: Create IP reputation table from threat intel
defineTable(query={CommandLine=/malware|trojan/i
                   | regex("(?<malicious_ip>\\d+\\.\\d+\\.\\d+\\.\\d+)", field=CommandLine)
                   | test(malicious_ip != null)
                   | groupBy([malicious_ip])
                   | eval(threat_level = "high",
                       threat_type = "known_malware")},
                           name="malicious_ips",
                               include=[malicious_ip, threat_level, threat_type])

// Step 2: Enrich network connections with threat data
| #event_simpleName=NetworkConnectIP4
| match(table="malicious_ips", field=RemoteAddressIP4, column=malicious_ip)
| test(threat_level != null)  // Only connections to known bad IPs
| select([timestamp, ComputerName, UserName, RemoteAddressIP4,
threat_level, threat_type])
```

**Example 3: Asset Inventory and Anomaly Detection**
```cql
// Step 1: Build asset inventory with normal software
defineTable(query={#event_simpleName=ProcessRollup2 @timestamp > (now() - 30d)
                   | groupBy([ComputerName, ImageFileName])
                   | count()
                   | eval(frequency = _count,
                          last_seen = now(),
                              asset_type = if(ImageFileName=/admin|system|service/i,
                                         "system", "user_app"))},
                                             name="asset_inventory",
                                                 include=[ComputerName, ImageFileName, frequency, asset_type])

// Step 2: Detect new/unusual software executions
| #event_simpleName=ProcessRollup2 @timestamp > (now() - 1h)
| match(table="asset_inventory", field=[ComputerName, ImageFileName],
column=[ComputerName, ImageFileName])
| eval(is_new_software = if(frequency == null, "YES", "NO"),
    risk_score = case(
         frequency == null, 10,           // Completely new
         frequency < 5, 7,                // Rarely used
         asset_type == "system", 2,       // System process
         3))                              // Normal user app
| test(risk_score >= 7)
| select([@timestamp, ComputerName, UserName, ImageFileName,
is_new_software, risk_score, CommandLine])
```

**Example 4: Multi-Stage Attack Chain Detection**
```cql
// Step 1: Identify initial compromise indicators
defineTable(query={#event_simpleName=ProcessRollup2
                   (CommandLine=/powershell.*-enc/i) OR
                   (CommandLine=/wget|curl/i) OR
                   (ImageFileName=/temp|appdata/i)
                   | eval(compromise_stage = "initial", compromise_score = 5)
                   | groupBy([ComputerName, UserName])
                   | min(@timestamp, as=first_compromise)},
                       name="compromised_hosts",
                           include=[ComputerName, UserName, first_compromise,
                               compromise_score])

// Step 2: Track lateral movement from compromised hosts
| #event_simpleName=NetworkConnectIP4
| match(table="compromised_hosts", field=[ComputerName, UserName],
column=[ComputerName, UserName])
| test(first_compromise != null)  // Only from compromised hosts
| test(@timestamp > first_compromise)  // After initial compromise
| test(RemoteAddressIP4=/192\.168\.|10\.|172\./)  // Internal networks
| eval(lateral_movement_score = compromise_score + 5)
| select([@timestamp, ComputerName, UserName, RemoteAddressIP4,
RemotePort, lateral_movement_score])
```

**Example 5: Join Multiple Lookup Tables**
```cql
// Create privileged users table
defineTable(query={#event_simpleName=UserLogon LogonType_decimal=10
                   | groupBy([UserName])
                   | eval(privilege_level = "admin")},
                       name="privileged_users",
                           include=[UserName, privilege_level])

// Create critical hosts table
defineTable(query={#event_simpleName=ProcessRollup2 ImageFileName=/system|service/i
                   | groupBy([ComputerName])
                   | eval(criticality_level = "high")},
                       name="critical_hosts",
                           include=[ComputerName, criticality_level])

// Create approved software table
defineTable(query={#event_simpleName=ProcessRollup2 @timestamp > (now() - 7d)
                   | groupBy([ImageFileName])
                   | count()
                   | test(_count > 100)
                   | eval(approval_status = "approved")},
                       name="approved_software",
                           include=[ImageFileName, approval_status])

// Main query with multiple table matches
| #event_simpleName=ProcessRollup2
| match(table="privileged_users", field=UserName, column=UserName)
| match(table="critical_hosts", field=ComputerName, column=ComputerName)
| match(table="approved_software", field=ImageFileName, column=ImageFileName)
| eval(risk_score = case(
    privilege_level == "admin" AND criticality_level == "high", 10,
        approval_status == null, 8,
            privilege_level == "admin", 6,
                criticality_level == "high", 5,
                    2))
| test(risk_score >= 6)
| select([timestamp, UserName, ComputerName, ImageFileName,
privilege_level, criticality_level, risk_score])
```

### Process Analysis with Advanced Functions
```cql
// Comprehensive process analysis with multiple functions
#event_simpleName=ProcessRollup2
| regex("(?<encoded_cmd>-enc[a-zA-Z]*\\s+(?<b64>[A-Za-z0-9+/=]+))",
        field=CommandLine, strict=false)
| eval(cmd_entropy = shannonEntropy(CommandLine),
    cmd_length = length(CommandLine),
           has_encoded = if(encoded_cmd != null, "YES", "NO"))
| test(cmd_entropy > 4.5 OR cmd_length > 500 OR has_encoded == "YES")
| ipLocation(LocalIP)  // Add geo data if available
| select([@timestamp, ComputerName, UserName, ImageFileName,
          CommandLine, cmd_entropy, has_encoded, country])
```

### Network Analysis with Geography and Correlation
```cql
// Advanced network analysis combining multiple functions
#event_simpleName=NetworkConnectIP4
| ipLocation(RemoteAddressIP4)
| eval(distance = geography:distance(
         LocalLat, LocalLon, RemoteAddressLat, RemoteAddressLon),
             connection_hash = crypto:sha256(concat(LocalAddressIP4,
                 RemoteAddressIP4)),
                     is_external = if(RemoteAddressIP4!=/^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)/,
                         "YES", "NO"))
| test(is_external == "YES" AND distance > 5000)
 // Long-distance external connections
| correlate(field=ComputerName,
           query={#event_simpleName=ProcessRollup2
                  CommandLine=*download*|*wget*|*curl*},
                      timeWindow=5m,
                          as=suspicious_process)
| test(suspicious_process != null)
 // Only connections with suspicious processes
| select([timestamp, ComputerName, RemoteAddressIP4, RemoteCountry,
          distance, suspicious_process])
```

### Time-Based Anomaly Detection with Statistical Analysis
```cql
// Multi-layered anomaly detection
#event_simpleName=ProcessRollup2
| bucket(span=1h)
| groupBy([_bucket, ComputerName])
| count(as=processes_per_hour)
// Calculate rolling statistics
| neighbor(field=processes_per_hour, as=prev_hour_count, by=ComputerName)
| stats(avg(processes_per_hour), stdDev(processes_per_hour), by=ComputerName)
| eval(z_score = (processes_per_hour -
avg_processes_per_hour) / stdDev_processes_per_hour,
    change_from_prev = if(prev_hour_count != null,
                            (processes_per_hour -
                            prev_hour_count) / prev_hour_count * 100,
                                0))
| test(z_score > 2 OR math:abs(change_from_prev) > 50)
 // Statistical anomalies
| select([_bucket, ComputerName, processes_per_hour, z_score,
change_from_prev])
```

## Performance Optimization Tips

1. **Use specific metadata fields (# or @) first**: `#<field_name>>=*`
2. **Apply filters before aggregation**: Filter early in the pipeline
3. **Limit results appropriately**: Use `head()` or `tail()` functions
4. **Choose efficient functions**:
`groupBy()` before `sort()` for better performance
5. **Use time ranges**: Apply time constraints through tool parameters
6. **Use defineTable() for efficient joinss**:
More efficient than multiple joins
7. **Cache complex calculations**: Use `eval()` to store intermediate results

"""


def get_all_ngsiem_content() -> Dict[str, str]:
    """Get all NG-SIEM reference content."""
    return {
        "tool_reference": NGSIEM_TOOL_REFERENCE,
        "field_mappings": NGSIEM_FIELD_MAPPINGS,
        "query_patterns": NGSIEM_QUERY_PATTERNS,
        "use_cases": NGSIEM_USE_CASES,
        "functions": NGSIEM_FUNCTIONS,
    }


# Path to scraped LogScale documentation (relative to this file)

SCRAPED_DOCS_PATH = os.path.join(os.path.dirname(__file__), "ngsiem")


def get_scraped_docs_list() -> List[Dict[str, str]]:
    """Get list of available scraped LogScale documentation files."""
    if not os.path.exists(SCRAPED_DOCS_PATH):
        return []

    docs = []
    md_files = glob.glob(os.path.join(SCRAPED_DOCS_PATH, "*.md"))

    for file_path in sorted(md_files):
        filename = os.path.basename(file_path)
        # Create clean resource name from filename
        resource_name = filename.replace(".md", "").replace("___", " - ").replace("_", " ")
        docs.append({"filename": filename, "resource_name": resource_name, "path": file_path})

    return docs


def read_scraped_doc(filename: str) -> str:
    """Read content from a specific scraped documentation file."""
    file_path = os.path.join(SCRAPED_DOCS_PATH, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Documentation file not found: {filename}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        raise Exception(f"Error reading documentation file {filename}: {str(e)}")


def search_scraped_docs(search_term: str, max_results: int = 10) -> List[Dict[str, str]]:
    """Search for documentation files matching a search term."""
    docs = get_scraped_docs_list()
    matches = []

    search_term_lower = search_term.lower()

    for doc in docs:
        # Search in filename and resource name
        if (
            search_term_lower in doc["filename"].lower()
            or search_term_lower in doc["resource_name"].lower()
        ):
            matches.append(doc)

        if len(matches) >= max_results:
            break

    return matches


def get_function_docs(function_name: str) -> Optional[Dict[str, str]]:
    """Get documentation for a specific LogScale function."""
    search_results = search_scraped_docs(f"{function_name}()", max_results=5)

    # Look for exact function documentation
    for result in search_results:
        if function_name.lower() in result["filename"].lower():
            try:
                content = read_scraped_doc(result["filename"])
                return {
                    "function_name": function_name,
                    "filename": result["filename"],
                    "content": content,
                }
            except Exception:
                continue

    return None


def get_query_examples(topic: str) -> List[Dict[str, str]]:
    """Get query examples for a specific topic."""
    search_results = search_scraped_docs(topic, max_results=10)

    examples = []
    for result in search_results:
        if "examples" in result["filename"].lower():
            try:
                content = read_scraped_doc(result["filename"])
                examples.append(
                    {
                        "topic": topic,
                        "filename": result["filename"],
                        "title": result["resource_name"],
                        "content": content,
                    }
                )
            except Exception:
                continue

    return examples
