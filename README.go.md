# falcon-mcp (Go)

A Go rewrite of the CrowdStrike Falcon MCP server, using the official
[Go MCP SDK](https://github.com/modelcontextprotocol/go-sdk) and
[GoFalcon](https://github.com/crowdstrike/gofalcon). It exposes the Falcon
platform to MCP clients with full feature parity with the Python server:
**24 domain modules, 115 tools, 36 FQL-guide resources**, three transports
(stdio / sse / streamable-http), dynamic mode, module selection, MSSP, proxy,
and a custom User-Agent — plus a first-class **hosted concurrent mode**
(single- and multi-tenant).

## Why Go

A single static binary (~5 MB stripped, no interpreter), goroutine-per-request
concurrency, compile-time-checked API calls, and a smaller attack surface —
better suited to hosted/SaaS deployment.

## Build & run

```sh
go build -o falcon-mcp ./cmd/falcon-mcp

# stdio (default)
FALCON_CLIENT_ID=... FALCON_CLIENT_SECRET=... ./falcon-mcp

# streamable-http, single-tenant
./falcon-mcp --transport streamable-http --host 0.0.0.0 --port 8000

# dynamic mode (3 meta-tools instead of all module tools)
./falcon-mcp --dynamic

# multi-tenant (per-request credentials from headers; HTTP only, TLS required)
./falcon-mcp --transport streamable-http --multi-tenant
```

### Configuration

Flags mirror the Python server; every flag has an environment-variable fallback
(precedence: flag > env > default).

| Flag | Env | Default |
|------|-----|---------|
| `--transport` | `FALCON_MCP_TRANSPORT` | `stdio` |
| `--modules` | `FALCON_MCP_MODULES` | all |
| `--host` / `--port` | `FALCON_MCP_HOST` / `FALCON_MCP_PORT` | `127.0.0.1` / `8000` |
| `--debug` | `FALCON_MCP_DEBUG` | false |
| `--base-url` | `FALCON_BASE_URL` | autodiscover |
| `--member-cid` | `FALCON_MEMBER_CID` | – |
| `--proxy` | `FALCON_PROXY_URL` | – |
| `--api-key` | `FALCON_MCP_API_KEY` | – |
| `--stateless-http` | `FALCON_MCP_STATELESS_HTTP` | false |
| `--dynamic` | `FALCON_MCP_DYNAMIC` | false |
| `--multi-tenant` | `FALCON_MCP_MULTI_TENANT` | false |
| `--user-agent-comment` | `FALCON_MCP_USER_AGENT_COMMENT` | – |

Credentials come from `FALCON_CLIENT_ID` / `FALCON_CLIENT_SECRET` (single-tenant)
or, in multi-tenant mode, per-request `X-Falcon-Client-Id` /
`X-Falcon-Client-Secret` / `X-Falcon-Member-Cid` / `X-Falcon-Base-Url` headers.

### Hosted mode

- **Single-tenant** (default): one shared, thread-safe client; `getServer`
  returns the same server for every request. `--stateless-http` enables
  horizontal scaling behind a load balancer.
- **Multi-tenant** (`--multi-tenant`): per-request credentials resolve to a
  pooled client (LRU + idle-TTL, keyed by a salted HMAC of the credentials so
  cache keys never equal secrets). Credential-bearing requests require TLS
  (direct or `X-Forwarded-Proto: https`); secrets are never logged.
- Health probes: `/healthz` (liveness) and `/readyz` (Falcon token
  reachability). Graceful shutdown on SIGINT/SIGTERM.

## Architecture

Layout mirrors
[kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server):

- `cmd/falcon-mcp` — entry point; loads config, blank-imports toolsets, dispatches transport.
- `internal/falcon` — `FalconClient` over the gofalcon client, credential factory, error normalization + API-scope hints, response formatters, multi-tenant client pool.
- `internal/fql` — 36 FQL guides embedded via `//go:embed`, served as resources.
- `pkg/api` + `pkg/toolsets` — explicit toolset registry (no reflection).
- `pkg/toolsets/<name>` — one package per domain module; each declares a narrow interface over only the gofalcon ops it uses and self-registers via `init()`.
- `pkg/server` — builds the `mcp.Server`, registers enabled toolsets, and implements dynamic mode.
- `pkg/http` — `net/http` server, middleware, health probes, multi-tenant `getServer`.

## Distribution

- **Go binaries:** GoReleaser (`.goreleaser.yaml`) builds darwin/linux/windows × amd64/arm64.
- **npm:** `npm/falcon-mcp` — Node launcher spawning the per-platform binary via optionalDependencies.
- **PyPI:** `python/` — setuptools console-script that downloads and execs the matching release binary.
- **Docker:** `Dockerfile.go` — multi-stage `golang:1.23` → `distroless/static-debian12:nonroot`.

## Development

```sh
go test ./...                       # unit + protocol tests
go test -race ./...                 # race-checked (pool concurrency)
go run scripts/gen_docs.go docs/modules-go   # regenerate module docs
```

Each toolset has unit tests using hand-written mocks of its narrow gofalcon
interface, covering two-step chaining, empty results, FQL-error-with-guide (400),
and 403 scope injection. `pkg/server` asserts full inventory parity (115 tools /
36 resources) over an in-process MCP session.
