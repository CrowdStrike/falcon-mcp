<!-- meta:title API Credentials -->
<!-- meta:description Create and configure CrowdStrike API credentials for the Falcon MCP Server. -->
<!-- meta:section getting-started -->
<!-- meta:link-base /falcon-mcp/ -->

Before using the Falcon MCP Server, you need to create API credentials in your CrowdStrike console.

## Creating API Credentials

1. **Log into your CrowdStrike console**
2. **Navigate to Support > API Clients and Keys**
3. **Click "Add new API client"**
4. **Configure your API client**:
   - **Client Name**: Choose a descriptive name (e.g., "Falcon MCP Server")
   - **Description**: Optional description for your records
   - **API Scopes**: Select the scopes based on which modules you plan to use

> [!CAUTION]
> Ensure your API client has the necessary scopes for the modules you plan to use. You can always update scopes later in the CrowdStrike console.

## API Scopes by Module

Each module requires specific CrowdStrike API scopes. See the [Module Overview](/falcon-mcp/modules/overview/) for a complete list of modules and their required scopes.

## API Region URLs

Select the correct base URL for your CrowdStrike region:

| Region | URL |
|--------|-----|
| US-1 (Default) | `https://api.crowdstrike.com` |
| US-2 | `https://api.us-2.crowdstrike.com` |
| EU-1 | `https://api.eu-1.crowdstrike.com` |
| US-GOV | `https://api.laggar.gcw.crowdstrike.com` |
