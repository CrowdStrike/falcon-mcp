# Phase 2 Findings — idp GraphQL Exotic Spike

**Date:** 2026-07-09
**Branch:** `gocmm-rewrite`
**Scope:** Plan Phase 2 (`plans/go-rewrite-design.md`) — de-risk the densest cluster of R1 (gofalcon op-gap) unknowns on the `idp` Identity Protection GraphQL module before broad fan-out.
**Verdict:** **GO** for broad fan-out. Both feared unknowns are real but each has a clean, localized, idiomatic-Go solution, now proven live against the production API.

---

## What was built

| Unit | File | Purpose |
|------|------|---------|
| `SanitizeInput` | `internal/falcon/sanitize.go` | Ports `common/utils.py:sanitize_input`; strips `\ " ' \n \r \t`, caps at 255. Mandatory for GraphQL string interpolation. |
| `GraphQL` executor | `internal/falcon/graphql.go` | Submits a raw `runtime.ClientOperation` with a body-capturing reader; funnels errors through the existing `APIError` path. |
| `idp` module | `internal/toolsets/idp/` | `idp_investigate_entity`: validation, AND-logic entity resolution, 4 investigation types, response synthesis. |
| Live test | `internal/toolsets/idp/live_integration_test.go` | `//go:build integration`; validates the op name + raw body read against production. |

Unit tests: 15 across the two packages, all pass `-race`. gofmt / `go vet` / golangci-lint v1.64.8 (CI parity) all clean.

---

## R1 unknown #1 — no GraphQL variables field (CONFIRMED, solved)

`models.SwaggerGraphQLQuery` carries **only** `Query *string` — no `variables` map. Verified in gofalcon v0.21.0 source (`falcon/models/swagger_graph_q_l_query.go`). Every dynamic value must be interpolated into the query text, exactly as the Python server does.

**Consequence:** `sanitize_input` is not optional hardening — it is the **only** injection defense, and porting it was mandatory. Done wholesale as `falcon.SanitizeInput`, applied at every interpolation site (`jsonString`, `jsonStringSlice`, and the unquoted-enum timeline categories).

**Parity note (documented, not a defect):** Python caps the sanitized string at 255 **code points**; Go caps at 255 **bytes**. Identical for the ASCII entity names / IPs / domains this tool handles. Flagged for any future multibyte field.

## R1 unknown #2 — typed OK type discards the response body (CONFIRMED, solved)

This is the sharp edge. `APIPreemptProxyPostGraphqlOK` has **no `Payload` field** — only rate-limit/trace headers. Its generated `readResponse` never calls `consumer.Consume` on the body. So gofalcon's typed method **throws the entire GraphQL response away**; the data is unreachable through the normal typed client.

Worse, the generated method (`identity_protection_client.go:163`) type-asserts its result to `*...OK` and **`panic`s** on anything else — so you cannot simply override the operation's `Reader` through the typed method and return a different type.

**Solution (idiomatic, no gofalcon fork):** `*CrowdStrikeAPISpecification` exposes its `Transport` (a `runtime.ClientTransport`). We build the `runtime.ClientOperation` by hand (reusing the generated `...Params` type for `WriteToRequest`, so body marshaling and auth are unchanged) and set our own `runtime.ClientResponseReaderFunc` that:
- on 2xx, reads and JSON-decodes the raw body into `map[string]any`;
- on non-2xx, returns `runtime.NewAPIError(...)`, which implements `runtime.ClientResponseStatus` — so the **existing** `falcon.statusOf`/`APIError` funnel recovers the status code and does 403 scope-enrichment with zero new error code.

This is contained entirely in `internal/falcon/graphql.go` (70 lines). No change to the shared error funnel, no per-operation error plumbing.

---

## Live validation (the decisive result)

`go test -tags=integration ./internal/toolsets/idp/ -run TestLive_InvestigateEntity` against the production API:

```
live GraphQL data captured (316 bytes)
--- PASS (1.48s)
```

This proves, against the real API — not a mock:
1. The gofalcon method `APIPreemptProxyPostGraphql` and path `POST /identity-protection/combined/graphql/v1` are correct (mock tests pass on a wrong op name; this does not).
2. The raw body reader **captures the `data` payload the typed OK type discards** — the core workaround works end-to-end.
3. Auth, the `Identity Protection Entities:read` scope, and the `SwaggerGraphQLQuery{Query}` body shape are all correct.

Op-name divergence, restated for the fan-out table: Python `api_preempt_proxy_post_graphql` → gofalcon `APIPreemptProxyPostGraphql` (note the lowercase `ql`; **not** `GraphQL`). Resolved by swagger path+verb, as the plan prescribes — never by transforming the Python string.

---

## Deltas from the Python module (deliberate)

- **`unwrap_field_default` not ported.** It exists only to unwrap Pydantic `FieldInfo` leakage (issue #384). Go's typed input struct + `NewTool` has no equivalent failure mode; the plumbing simply doesn't exist to leak. YAGNI.
- **`include_*` flags are `*bool`.** Python defaults them to `true`; a plain `bool` zero value would flip that to `false`. Pointer + `boolOpt` (nil → true) preserves the default. This is the plan's documented "zero is meaningfully distinct from absent" carve-out to the `Opt[T]` rule.
- **Cross-investigation insights** (`_generate_investigation_insights` and its helpers) are **not yet ported.** They are pure post-processing over already-fetched results (no API surface), so they add zero spike risk and were out of scope for de-risking. Flagged as a follow-up when idp is finalized in the fan-out; noted here so it is not mistaken for complete parity.
- **GraphQL query whitespace differs** from Python's. GraphQL is whitespace-insensitive; the parity bar is structural (D4), not byte-for-byte.

---

## Impact on the fan-out estimate

The spike **confirms the plan's estimate holds** and narrows the risk band:

- **`sanitize_input` + raw-body `GraphQL` executor are now shared, done once.** idp is the only GraphQL module (1 tool), so this cost does not recur — but the *raw-consumer technique* (build the op by hand, override the Reader) is the **same one the binary/download endpoints need** (`get_mitre_report`, scheduled-report PDF download — plan "Beyond hosts"). This spike de-risks that whole class: the mechanism is now proven, ~70 lines, and reusable.
- **No gofalcon fork or upstream fix required** for the "no typed payload" class. This was the biggest latent threat to the estimate (a fork would blow up R3/R4). Retired.
- **Per-tool op-name resolution by path+verb works** and is quick (minutes per op with the module cache). No surprises in the transform.

Net: the **~6–9 week fan-out for 24 modules / 112 tools is unchanged**, and its single largest tail risk (an operation whose data is simply unreachable via the typed client) is now a solved, tested pattern rather than an open question.

---

## Recommended next step

Proceed to **Phase 3 (cross-cutting parity)** as planned — HTTP transports, middleware, `--modules`/`--read-only` wiring, `.env` via godotenv (the integration test currently self-loads `.env`; fold that into the real config path), dynamic mode, and the generalized parity + compliance harness — then fan out modules in Phase 4 with the raw-consumer pattern in hand for the download/GraphQL specializations.
