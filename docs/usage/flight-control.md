---
title: Flight Control (MSSP)
description: Using the Falcon MCP Server in multi-tenant Flight Control environments.
---

The Falcon MCP Server supports CrowdStrike Flight Control for MSSP (Managed Security Service Provider) environments. Use parent CID API credentials with the `--member-cid` flag or `FALCON_MEMBER_CID` environment variable to target a specific child CID.

## Configuration

**Environment variable:**

```bash
export FALCON_MEMBER_CID="abc123-child-cid-xyz"
falcon-mcp
```

**Command-line flag:**

```bash
falcon-mcp --member-cid "abc123-child-cid-xyz"
```

**In `.env` file:**

```bash
# Parent CID credentials (required)
FALCON_CLIENT_ID=parent-client-id
FALCON_CLIENT_SECRET=parent-client-secret

# Child CID to target (optional)
FALCON_MEMBER_CID=abc123-child-cid-xyz
```

## Requirements

- Parent CID API credentials (`FALCON_CLIENT_ID` and `FALCON_CLIENT_SECRET` from the parent tenant)
- Flight Control enabled on the parent tenant
- Valid child CID identifier
- Parent API client must have appropriate scopes for operations on the child CID

## Behavior

- **Session-level**: All tools in the server instance target the specified child CID
- **Cannot switch mid-session**: The `member_cid` is set during authentication and persists for the server's lifetime
- **Multiple child CIDs**: To query multiple child CIDs, run separate server instances on different ports

## Multi-Tenant Workflow

To work with multiple child CIDs simultaneously, run separate server instances:

```bash
# Parent CID (default)
falcon-mcp --transport streamable-http --port 8000
```

```bash
# Child CID 1
falcon-mcp --member-cid "child-cid-1" --transport streamable-http --port 8001
```

```bash
# Child CID 2
falcon-mcp --member-cid "child-cid-2" --transport streamable-http --port 8002
```

Each instance maintains its own authentication context and can be accessed independently by your MCP client.
