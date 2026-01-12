# Deploy to Amazon Bedrock AgentCore via AWS Marketplace

The Falcon MCP Server is available on the [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-afoqfhvuepgne) for streamlined deployment to Amazon Bedrock AgentCore. The Marketplace listing provides a pre-built container image hosted in AWS and handles IAM permission configuration automatically.

## Prerequisites

Before deploying, ensure you have your CrowdStrike API credentials and AWS environment configured.

### CrowdStrike API Credentials

Create API credentials in your CrowdStrike console:

1. Log into your CrowdStrike console
2. Navigate to **Support > API Clients and Keys**
3. Click **Add new API client**
4. Configure your API client:
   - **Client Name**: Choose a descriptive name (e.g., "Falcon MCP Server")
   - **Description**: Optional description for your records
   - **API Scopes**: Select scopes based on which modules you plan to use ([see scope requirements](https://github.com/CrowdStrike/falcon-mcp#available-modules-tools--resources))
5. Note down these values (you cannot retrieve them later):
   - `FALCON_CLIENT_ID` - Your API client ID
   - `FALCON_CLIENT_SECRET` - Your API client secret
   - `FALCON_BASE_URL` - Your API base URL (region-specific)

### AWS VPC Requirements

The MCP Server requires internet connectivity to communicate with CrowdStrike's APIs.

- **Internet Gateway or NAT Gateway** - Enables outbound internet connectivity
- **Outbound HTTPS Access** - Allow communication to `api.crowdstrike.com` on port 443
- **Security Groups** - Configure appropriate rules for your network requirements

## Getting Started

To deploy the Falcon MCP Server to Amazon Bedrock AgentCore:

1. Visit the [Falcon MCP Server on AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-afoqfhvuepgne)
2. Follow the subscription and deployment instructions
3. Configure your CrowdStrike API credentials and environment variables as described below

## Usage Instructions

### Environment Variables

Configure these environment variables when deploying your AgentCore agent:

| Variable | Value | Description |
| :--- | :--- | :--- |
| `FALCON_CLIENT_ID` | Your client ID | CrowdStrike API client ID |
| `FALCON_CLIENT_SECRET` | Your client secret | CrowdStrike API client secret |
| `FALCON_BASE_URL` | `https://api.crowdstrike.com` | API base URL (region-specific) |
| `FALCON_MCP_TRANSPORT` | `streamable-http` | Transport protocol |
| `FALCON_MCP_HOST` | `0.0.0.0` | Host binding |
| `FALCON_MCP_PORT` | `8000` | Server port |
| `FALCON_MCP_USER_AGENT_COMMENT` | `AWS/Bedrock/AgentCore` | Request identifier |
| `FALCON_MCP_STATELESS_HTTP` | `true` | **Required** for AgentCore |

> **Important:** `FALCON_MCP_STATELESS_HTTP` must be set to `true` for proper operation in AgentCore's stateless container environment.

### Available Modules

The Falcon MCP Server provides security tools organized into modules. Each module requires specific API scopes.

| Module | Purpose |
| :--- | :--- |
| Cloud Security | Analyze Kubernetes containers and container image vulnerabilities |
| Detections | Find and analyze detections for malicious activity |
| Discover | Search application inventory across your environment |
| Hosts | Manage and query host/device information |
| Identity Protection | Entity investigation and identity protection analysis |
| Incidents | Analyze security incidents and coordinated activities |
| Intel | Research threat actors, IOCs, and intelligence reports |
| Sensor Usage | Access and analyze sensor usage data |
| Serverless | Search vulnerabilities in serverless functions |
| Spotlight | Manage vulnerability data and security assessments |

**Example tool invocation** (search for recent detections):

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "falcon_search_detections",
    "arguments": { "filter": "status:'new'" }
  }
}
```

### Verify Deployment

After deployment, verify connectivity by invoking the `falcon_check_connectivity` tool:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": { "name": "falcon_check_connectivity" }
}
```

### Additional Resources

For full details, visit the [Falcon MCP GitHub repository](https://github.com/CrowdStrike/falcon-mcp).
