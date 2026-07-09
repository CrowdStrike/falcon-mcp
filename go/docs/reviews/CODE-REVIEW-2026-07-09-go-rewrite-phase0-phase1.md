# Code Review — Go Rewrite Phase 0 + Phase 1

**Date:** 2026-07-09
**Scope:** go/ subdirectory (all files listed in dispatch)
**Branch:** gocmm-rewrite
**Note:** Reviewing without git-range context. Findings are pattern-based. Severity ratings are provisional except where concrete evidence is cited.

All 58 tests pass under `-race`, `gofmt` and `go vet` are clean per the dispatch. This review targets what those tools cannot catch.

---

## Finding 1 — IMPORTANT: `IdempotentHint` annotation silently drops the pointer semantics (addtool.go)

**Confidence: 92**

`mcp.ToolAnnotations.IdempotentHint` is `bool` (not `*bool`) in the SDK:

```
// go-sdk@v1.6.1 mcp/protocol.go
IdempotentHint bool `json:"idempotentHint,omitempty"`
```

`toolsets.Annotations.Idempotent` is `*bool`, so "unset" is `nil`. `toSDKAnnotations` copies it with a dereference:

```go
if a.Idempotent != nil {
    ann.IdempotentHint = *a.Idempotent
}
```

This is correct for the nil-guard. However, `DestructiveHint` and `OpenWorldHint` in the same struct **are** `*bool` in the SDK, and `toSDKAnnotations` assigns those as pointer fields. The inconsistency is not a crash, but when `Idempotent` is `nil` the SDK field stays `false`, which means the hint is implicitly emitted as `idempotentHint: false` in JSON (omitempty applies only to the zero value, which happens to be false for bool — so this one is fine). The bigger risk: when 23 more modules are added and someone writes `Annotations{Idempotent: &trueVal}`, the value flows correctly *today*, but if the SDK ever aligns `IdempotentHint` to `*bool` a silent compile break won't happen. Document this asymmetry in a comment inside `toSDKAnnotations` so maintainers don't accidentally flip it.

---

## Finding 2 — IMPORTANT: `Tool.InputSchema` is the pre-resolve schema; `resolved` is captured in the closure (api.go)

**Confidence: 88**

`NewTool` stores `schema` (the raw `*jsonschema.Schema`) in `Tool.InputSchema` and captures `resolved` (a `*Resolved`) inside the handler closure for validation:

```go
resolved, err := schema.Resolve(nil)
// ...
return Tool{
    InputSchema: schema,        // raw, pre-resolution
    handler: func(...) {
        resolved.Validate(...)  // resolved copy
    },
}
```

The MCP SDK also passes `InputSchema` to its own validation layer (`srv.AddTool` in go-sdk@v1.6.1 uses `jsonschema-go` internally when `InputSchema` is set as a `*jsonschema.Schema`). That means input is validated **twice**: once by the SDK using the raw schema, and once by the handler closure using `resolved`. These two validate against the same source schema, so results should agree, but any `$ref` or `$defs` that `Resolve` normalises may diverge. This is worth confirming with a test that uses a `$ref` in a schema. More importantly: when `ApplyConstraints` mutates schema properties (e.g. `lim.Minimum = &minLimit`) those mutations are visible in the `*jsonschema.Schema` pointer handed to the SDK **and** are the same mutations that `resolved` was built from, because `Resolve` is called after `ApplyConstraints`. The current flow is safe. Add a short comment clarifying that `InputSchema` goes to the SDK transport layer (for schema advertisement) while `resolved` is used for call-time validation, so future maintainers don't "simplify" by removing the closure capture.

---

## Finding 3 — IMPORTANT: Missing package comment on `internal/falcon` (Effective Go, rule 1)

**Confidence: 97**

None of the files under `internal/falcon/` carry a `// Package falcon …` comment, and there is no `doc.go`. Every other in-scope package has a package comment (`toolsets`, `mcpx`, `config`, `cli`, `hosts`, `version`). The `falcon` package is the most-imported internal package; it is the foundation that all 23 modules will depend on. A missing package comment is a go-doc blind spot.

```
$ grep -r "^// Package falcon" go/internal/falcon/
(no output)
```

With 10 source files, a `doc.go` is the right fix:

```go
// Package falcon wraps the gofalcon SDK with credential verification,
// proxy injection, error normalisation, and parameter utilities shared
// by all Falcon domain modules.
package falcon
```

---

## Finding 4 — IMPORTANT: `config.Validate` error string starts with a capital letter (errors.go companion rule, CLAUDE.md EC-1)

**Confidence: 90**

```go
// config/config.go:46
return fmt.Errorf("Falcon API credentials are required: ...")
```

Effective Go and the project CLAUDE.md require error strings to be lower-case and unpunctuated. The string begins with `"Falcon API credentials…"`. Because this error is returned from `cfg.Validate()` and printed via `fmt.Fprintln(os.Stderr, "falcon-mcp:", err)` in `main.go`, the final user-visible output would be:

```
falcon-mcp: Falcon API credentials are required: ...
```

The double-capital (`falcon-mcp: Falcon`) is cosmetically acceptable but the canonical fix is lower-case:

```go
return fmt.Errorf("falcon: API credentials are required: set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET")
```

---

## Finding 5 — IMPORTANT: `filterReadOnly` uses a slice-reuse trick that could surprise future maintainers (registry.go)

**Confidence: 82**

```go
func filterReadOnly(tools []Tool) []Tool {
    kept := tools[:0:0]
    for _, t := range tools {
        if t.Annotations.ReadOnly {
            kept = append(kept, t)
        }
    }
    return kept
}
```

`tools[:0:0]` yields a nil-length, nil-capacity slice with the same **underlying array** pointer as `tools` when `tools` is non-nil. `append` will allocate a fresh backing array before writing because capacity is 0, so the original slice is not clobbered. The idiom is safe here because the capacity limit of 0 forces immediate reallocation. However, `tools[:0]` (without the third index) would share backing memory and could silently alias, which is the common misremembering of this pattern. With 23 modules replicating filtering logic, the safer and equally readable form is:

```go
kept := make([]Tool, 0, len(tools))
```

which is unambiguously safe and reads clearly. The current code is correct, but the [:0:0] trick is a maintenance hazard at scale.

---

## Finding 6 — NORMAL: Double JSON decode per call in `NewTool` handler closure (api.go)

**Confidence: 85**

The handler closure unconditionally decodes `raw` twice for each tool call: first into the typed `In` value, then into a `map[string]any` for schema validation:

```go
var in In
if len(raw) > 0 {
    json.Unmarshal(raw, &in)
}
var generic any = map[string]any{}
if len(raw) > 0 {
    json.Unmarshal(raw, &generic)
}
resolved.Validate(generic)
return h(ctx, in)
```

For a stdio MCP server this is negligible. When streamable-http is enabled (planned), this runs on every tool call across concurrent requests. The fix — unmarshal once into `any`, then marshal back into `In` via an intermediate `json.RawMessage` or use `mapstructure` — adds complexity that likely isn't justified at PoC stage. Flag this as a TODO comment rather than a change now, since the dispatch explicitly notes the transport isn't implemented yet. The note is especially important because the double-decode path also means a type-mismatched field (e.g. `"limit": "notanumber"`) is caught at the first unmarshal (typed) but the second unmarshal into `any` succeeds, so the validation order matters: a type error surfaces before schema validation, which is the desired behaviour. Confirm this is intentional by adding a comment.

---

## Finding 7 — NORMAL: `Constrainer` probes both pointer and value receiver unnecessarily (api.go)

**Confidence: 83**

```go
var zero In
if c, ok := any(&zero).(Constrainer); ok {
    c.ApplyConstraints(schema)
} else if c, ok := any(zero).(Constrainer); ok {
    c.ApplyConstraints(schema)
}
```

This is a reasonable defensive pattern for the generic context. However, the value-receiver branch (`any(zero)`) is dead code in practice: if `In` implements `Constrainer` with a value receiver, the pointer branch `any(&zero)` also satisfies it (Go's addressability rule for method sets means `*T` has both pointer and value methods). The only case where the second branch fires is when `In` is a non-addressable type that cannot take a pointer — which is impossible inside a generic function because `var zero In` is always addressable. The `else if` branch can be removed. As written across 23 modules this will look intentional; document or simplify.

---

## Finding 8 — NORMAL: `resolveConfig` final `else` branch for `port` is dead code (cli/root.go)

**Confidence: 88**

```go
if f.Changed("port") {
    cfg.Port, _ = f.GetInt("port")
} else if v, ok := os.LookupEnv("FALCON_MCP_PORT"); ok {
    if p, err := strconv.Atoi(v); err == nil {
        cfg.Port = p
    }
} else {
    cfg.Port, _ = f.GetInt("port")  // same as the if-branch
}
```

The final `else` reads `f.GetInt("port")`, which when the flag was not changed returns the default value registered with `f.IntP("port", "p", def.Port, ...)`. But `cfg.Port` is already set to `def.Port` by `cfg := config.Defaults()` at the top of `resolveConfig`. So the final `else` unconditionally reassigns `cfg.Port` the value it already holds. This is harmless but confusing. The `str` and `boolVal` closures above don't have this issue because strings and bools get the same final `f.GetX(name)` call which is correct (the default and the zero value may differ). For `port`, the `else` branch can simply be dropped. This pattern will be replicated for numeric fields in 23 modules.

---

## Finding 9 — NORMAL: No compile-time interface check for `Constrainer` implementors (Effective Go interfaces rule 11)

**Confidence: 80**

`searchHostsInput` and `sampleInput` (in tests) implement `Constrainer` via value receiver. There is no `var _ toolsets.Constrainer = searchHostsInput{}` assertion. If `ApplyConstraints` signature drifts (e.g. the `jsonschema.Schema` type changes upstream), the break is silent until runtime. At PoC scale this is low risk, but given that 23 modules will each add an input type with `ApplyConstraints`, establishing the pattern now prevents 23 silent failures later.

---

## Finding 10 — NIT: `gofalconVersion` constant in client.go will drift silently (client.go)

**Confidence: 80**

```go
const gofalconVersion = "v0.21.0"
```

This string is embedded in the user agent and must be kept in sync with `go.mod`. The comment says "Keep in sync" but there is no automated check. When upgrading gofalcon, this constant will be forgotten. A build-time check (a `TestGoFalconVersionMatchesModFile` in `client_test.go` that reads `go.mod` and asserts) would catch this. Alternatively, the version could be extracted from `runtime/debug.ReadBuildInfo()` but that has its own pitfalls in stripped binaries.

---

## Effective Go 20-Point Self-Check Results

| Check | Status | Notes |
|---|---|---|
| 1. Package comments | FAIL | `internal/falcon` has no package comment across any of its 5 source files |
| 2. No Get prefix | PASS | No getter methods |
| 3. Receiver names | PASS | `h *handlers`, `s Scope`, `t Tool`, `r *Registry` — all short and consistent |
| 4. Doc comments on exported symbols | PASS with minor gaps | `searchHostsInput`, `getHostDetailsInput`, `handlers` are unexported — OK. All exported symbols have docs. |
| 5. Pointer/value receiver consistency | PASS | Each type uses one receiver kind consistently |
| 6. Error strings lower-case, unpunctuated | FAIL | `config.Validate` returns `"Falcon API credentials are required: …"` (capital F) |
| 7. `errors.Is`/`errors.As` | PASS | `errors.As` used in `statusOf` |
| 8. Custom error types implement `Unwrap()` | N/A | `falcon.Error` wraps nothing; it is a leaf error |
| 9. Panics contained in package boundaries | PASS | Panics in `NewTool` and `Register` are build-time init failures; appropriate |
| 10. Single-method interfaces use `-er` naming | PASS | `Constrainer` is correct |
| 11. Compile-time interface checks | WARN | No `var _ Constrainer` assertions for module input types |
| 12. Comma-ok for type assertions | PASS | All type assertions use comma-ok |
| 13. Embedding used correctly | PASS | No embedding misuse |
| 14. Zero value of structs safe | PASS | `Registry` documented as requiring `NewRegistry`; zero value safety elsewhere fine |
| 15. `iota` for enumerated constants | N/A | No enumerated constants |
| 16. Named returns where they improve clarity | PASS | Not overused; used nowhere — appropriate |
| 17. No blank identifier import hacks | PASS | Blank imports are legitimate module self-registration |
| 18. Goroutine closures capture variables safely | PASS | No goroutines in reviewed code |
| 19. Correct channel patterns | N/A | No channels |
| 20. Concurrency/parallelism distinction clear | PASS (with caveat) | See concurrency note below |

### Concurrency Note

The shared `*client.CrowdStrikeAPISpecification` is created once in `run()` and passed to `Registry.Build`, which distributes it into every `handlers` struct. Under streamable-http multiple tool calls will invoke `h.c.Hosts.*` concurrently. gofalcon's generated client uses `go-openapi/runtime` which is documented as goroutine-safe (one HTTP client, no mutable state per call). This is acceptable, but it should be verified against the gofalcon version in use and documented in a comment on the `handlers` struct or `fetchDetails` once streamable-http is implemented.

---

## Summary — Ranked by Severity

1. **Missing `internal/falcon` package comment** (Finding 3) — affects all 23 future modules' documentation; trivially fixed with a `doc.go`.
2. **`IdempotentHint` asymmetry vs SDK type** (Finding 1) — not a bug today, but an undocumented divergence that will be replicated 23 times.
3. **Error string capitalisation in `config.Validate`** (Finding 4) — violates project CLAUDE.md EC-1 and Effective Go; one-line fix.
4. **`Tool.InputSchema` vs `resolved` — clarify the two-schema model** (Finding 2) — correct as implemented but needs a comment to prevent "simplification" bugs in future.
5. **Dead `else` branch in `resolveConfig` port handling** (Finding 8) — harmless noise that will be replicated in numeric fields across 23 modules.
6. **`filterReadOnly` slice trick** (Finding 5) — safe but fragile by visual similarity to the unsafe [:0] variant; replace with `make([]Tool, 0, len(tools))`.
7. **Double JSON decode per call** (Finding 6) — fine for stdio, needs a TODO comment before streamable-http.
8. **Dead value-receiver branch in `Constrainer` probe** (Finding 7) — document or remove.
9. **No compile-time `Constrainer` assertions** (Finding 9) — establish the pattern now before 23 modules omit it.
10. **`gofalconVersion` constant drift** (Finding 10) — add a test or a build-time assertion.
