<!-- meta:title Amazon Bedrock -->
<!-- meta:description Deploy the Falcon MCP Server to Amazon Bedrock AgentCore. -->
<!-- meta:section deployment -->
<!-- meta:link-base /falcon-mcp/ -->

The Falcon MCP Server is available on the [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-afoqfhvuepgne) for streamlined deployment to Amazon Bedrock AgentCore.

## Prerequisites

### CrowdStrike API Credentials

Create API credentials in your CrowdStrike console:

1. Log into your CrowdStrike console
2. Navigate to **Support > API Clients and Keys**
3. Click **Add new API client**
4. Configure scopes based on the modules you plan to use (see [API Credentials](/falcon-mcp/getting-started/credentials/))
5. Note down your `FALCON_CLIENT_ID`, `FALCON_CLIENT_SECRET`, and `FALCON_BASE_URL`

### AWS VPC Requirements

The MCP Server requires internet connectivity to communicate with CrowdStrike's APIs:

- Internet Gateway or NAT Gateway for outbound connectivity
- Outbound HTTPS access to `api.crowdstrike.com` on port 443
- Appropriate security group rules

## Getting Started

1. Visit the [Falcon MCP Server on AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-afoqfhvuepgne)
2. Subscribe and follow the deployment instructions
3. Configure the environment variables below

## Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `FALCON_CLIENT_ID` | Your client ID | CrowdStrike API client ID |
| `FALCON_CLIENT_SECRET` | Your client secret | CrowdStrike API client secret |
| `FALCON_BASE_URL` | `https://api.crowdstrike.com` | API base URL (region-specific) |
| `FALCON_MCP_TRANSPORT` | `streamable-http` | Transport protocol |
| `FALCON_MCP_HOST` | `0.0.0.0` | Host binding |
| `FALCON_MCP_PORT` | `8000` | Server port |
| `FALCON_MCP_USER_AGENT_COMMENT` | `AWS/Bedrock/AgentCore` | Request identifier |
| `FALCON_MCP_STATELESS_HTTP` | `true` | **Required** for AgentCore |
| `FALCON_MCP_API_KEY` | *(optional)* | API key to secure the MCP endpoint |
| `FALCON_MCP_MODULES` | *(optional)* | Comma-separated list of modules to enable. Defaults to all modules when unset |
| `FALCON_MEMBER_CID` | *(optional)* | Child CID for Flight Control (MSSP multi-tenancy). Targets a specific child CID when authenticating with parent credentials |
| `FALCON_MCP_DEBUG` | `false` | Enable debug logging |
| `FALCON_PROXY_URL` | *(optional)* | HTTP/HTTPS proxy URL for outbound Falcon API connections in restricted network environments |
| `FALCON_MCP_READ_ONLY` | *(optional)* | When set to `true`, register only read-only (non-mutating) tools. Excludes any tool that modifies Falcon state |
| `FALCON_MCP_TOOLS` | *(optional)* | Comma-separated allow-list of specific tool names to enable, additive to the modules selected via `FALCON_MCP_MODULES` |
| `FALCON_MCP_EXCLUDE_TOOLS` | *(optional)* | Comma-separated deny-list of tool names to disable. Takes precedence over `FALCON_MCP_TOOLS` and `FALCON_MCP_READ_ONLY` |
| `FALCON_MCP_DYNAMIC` | *(optional)* | Enable dynamic mode, which exposes a small set of meta-tools for on-demand tool discovery instead of registering the full tool surface |

> [!CAUTION]
> `FALCON_MCP_STATELESS_HTTP` must be set to `true` for proper operation in AgentCore's stateless container environment.

<!-- -->

> [!NOTE]
> `FALCON_MCP_HOST=0.0.0.0`: AgentCore runs the container behind its own managed network
> security layer, so the server is not directly exposed to the public internet the way a self-managed
> `0.0.0.0` bind would be. `FALCON_MCP_API_KEY` is optional in this environment and adds defense in depth
> if you want callers to present an `x-api-key` header as well.

## Verify Deployment

After deployment, verify connectivity by invoking the `falcon_check_connectivity` tool:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": { "name": "falcon_check_connectivity" }
}
```

## Example Tool Invocation

Search for recent detections:

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
