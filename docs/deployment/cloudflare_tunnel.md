# Cloudflare Tunnel Deployment (Streamable HTTP)

This guide describes how to expose `falcon-mcp` over a Cloudflare Tunnel using a
custom domain and a tunnel token. It uses the `docker-compose.cloudflare.yml`
file in the repo.

## Prerequisites

- Docker + Docker Compose
- A Cloudflare Tunnel token for your custom domain
- A `.env` file with valid Falcon API credentials

## Environment Variables

Create or update `.env` in the repo root:

```bash
FALCON_CLIENT_ID=your-client-id
FALCON_CLIENT_SECRET=your-client-secret
FALCON_BASE_URL=https://api.crowdstrike.com

# Optional NGSIEM default repo
FALCON_NGSIEM_REPOSITORY=base_sensor

# Required for Cloudflare hostname validation
FALCON_MCP_ALLOWED_HOSTS=your.domain.example
FALCON_MCP_ALLOWED_ORIGINS=https://your.domain.example

# Cloudflare Tunnel token (custom domain)
CLOUDFLARED_TUNNEL_TOKEN=your_tunnel_token
```

## Start the Services

From the repo root:

```bash
docker compose -f docker-compose.cloudflare.yml up -d --build
```

This will:

- Build a local image from `Dockerfile`
- Run `falcon-mcp` on `0.0.0.0:8000` (streamable-http)
- Start `cloudflared` with your tunnel token

## Verify

Check logs:

```bash
docker compose -f docker-compose.cloudflare.yml logs --tail=200 falcon-mcp
docker compose -f docker-compose.cloudflare.yml logs --tail=200 cloudflared
```

You should see `falcon-mcp` running on `0.0.0.0:8000` and `cloudflared` reporting
the tunnel connection.

## MCP Endpoint

Use the Cloudflare domain with the `/mcp` path:

```
https://your.domain.example/mcp
```

## Notes

- Host header validation is enabled by default. Ensure
  `FALCON_MCP_ALLOWED_HOSTS` and `FALCON_MCP_ALLOWED_ORIGINS` match your
  Cloudflare domain exactly.
- If you update `.env`, rebuild/restart the containers to apply changes.
