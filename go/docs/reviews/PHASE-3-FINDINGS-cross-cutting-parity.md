# Phase 3 findings — cross-cutting parity (falcon-mcp Go rewrite)

Branch `gocmm-rewrite`. Companion to `PHASE-2-FINDINGS-idp-graphql-spike.md`.
Covers the six Phase 3 work items (HTTP transports, middleware, dynamic mode,
`.env`/logging, parity+compliance harness, R6 concurrency).

## R6 — concurrency: shared gofalcon client is safe under concurrent tool calls

**Verdict: CONFIRMED SAFE, proven under `-race`.**

The streamable-http transport serves requests concurrently (`http.Server` spawns
a goroutine per request; the go-sdk `StreamableHTTPHandler` reuses the single
shared `*mcp.Server` returned by the getter). Two race-tested proofs:

1. `internal/toolsets/hosts/concurrency_test.go::TestConcurrency_SharedClientUnderRace`
   — 32 goroutines share one `*client.CrowdStrikeAPISpecification` and call the
   real `searchHosts` handler (two-step: query + hydrate) concurrently.
2. `internal/mcpx/transport_test.go::TestRunStreamableHTTP_ConcurrentToolCalls`
   — 16 concurrent MCP clients call a tool through the actual streamable-http
   server end-to-end.

Both pass clean under `go test -race`. This matches the Phase 2 reasoning: the
gofalcon client is a connection pool built on `net/http` (designed for
concurrent use), and each `handlers` struct holds only an immutable client
reference — no per-call mutable state. No mutex was needed anywhere in the
handler or client path.

## Parity harness surfaced two real divergences (as designed)

The harness (`internal/parity`) is a structural JSON differ implementing D4
(key-order canonicalization) and D5 (array order preserved for sort-correctness).
On its first run against the real `hosts` handler it immediately caught two
gofalcon-vs-FalconPy divergences:

### 1. Typed models emit `null` for unset optional fields (tier-1 payload)

`models.DeviceapiDeviceSwagger` has `omitempty` on string fields but NOT on
pointer/slice fields (`cid`, `groups`, `tags`, `policies`, …), so Go emits
`"tags":null` where FalconPy's dict omits the key entirely. Both mean "no value"
— semantically equal per the D4 tier-1 bar.

**Resolution:** `parity.DiffSemantic` treats a null-valued object key as absent
(recursively), so tier-1 payload parity holds. `parity.Diff` remains strict
(null ≠ absent) for envelope-shape assertions (tier 2), where an empty list `[]`
is a real value distinct from null and must never be elided. Module parity tests
use `DiffSemantic` for payloads and `OrderOf` for the fixed sort order.

### 2. Tool names are heterogeneous — no universal `falcon_` prefix

The generalized compliance test initially asserted every tool name starts with
`falcon_`. The `idp` module's tool is `idp_investigate_entity` (no prefix), and a
scan of the Python modules shows many more (`create_case`, `add_ioc`,
`aggregate_rtr_sessions`, …). Tool names must match the Python originals exactly
(agents/configs depend on them), so the prefix is not an invariant.

**Resolution:** compliance asserts the real invariants only — non-empty
name/description, non-nil `InputSchema`, **no** `OutputSchema` (D6: structured
output stays OFF), annotations present — across the full registered set
(`internal/cli/compliance_test.go`). Phase 4 modules are validated automatically
as they register.

## Notes for Phase 4

- The parity pattern is table-driven per module: reuse the module's fake
  transport + handlers, assert `parity.DiffSemantic(pythonShape, goOutput)` for
  payloads and `parity.OrderOf` for two-step ordering. `hosts/parity_test.go` is
  the reference.
- Live Python-vs-Go diffing (DoD tier-2) is the manual `.env`-creds step; the
  committed harness is the structural engine + per-module fixtures.
- `.env` now loads through one loader (`config.LoadDotEnv`, godotenv v1.5.1),
  used by both `cli.Execute` and the idp live integration test.
