// Package parity provides the structural comparison engine for the falcon-mcp
// Go rewrite's parity harness. It canonicalizes JSON so key order is ignored
// (decision D4) while array order is preserved, since two-step search tools
// must return entities in the requested sort order (decision D5). Individual
// module tests supply the fixtures; this package supplies the diff.
package parity

import (
	"bytes"
	"encoding/json"
	"fmt"
)

// Canonicalize returns a stable serialization of raw JSON: object keys are
// sorted (Go's json.Marshal sorts map keys), while array element order is
// preserved. Two inputs that differ only in object key order canonicalize to
// identical bytes; two inputs whose arrays differ in order do not.
func Canonicalize(raw []byte) ([]byte, error) {
	var v any
	if err := json.Unmarshal(raw, &v); err != nil {
		return nil, fmt.Errorf("parity: canonicalize: %w", err)
	}
	// Marshaling a decoded value sorts map keys deterministically and keeps
	// slice order, giving the exact canonical form the parity bar requires.
	out, err := json.Marshal(v)
	if err != nil {
		return nil, fmt.Errorf("parity: canonicalize: %w", err)
	}
	return out, nil
}

// Diff compares two JSON documents structurally, ignoring object key order but
// respecting array order. It returns an empty string when they are equivalent,
// or a human-readable description of the first difference otherwise.
func Diff(want, got []byte) (string, error) {
	cw, err := Canonicalize(want)
	if err != nil {
		return "", fmt.Errorf("parity: want side: %w", err)
	}
	cg, err := Canonicalize(got)
	if err != nil {
		return "", fmt.Errorf("parity: got side: %w", err)
	}
	if bytes.Equal(cw, cg) {
		return "", nil
	}
	return fmt.Sprintf("structural mismatch:\n  want: %s\n  got:  %s", cw, cg), nil
}

// DiffSemantic compares two JSON documents like [Diff] but additionally treats a
// null-valued object key as absent (tier-1 payload parity). gofalcon's typed
// models emit null for unset optional fields (no omitempty on pointer/slice
// fields), whereas FalconPy dicts omit the key; both mean "no value". An empty
// list is a real value and is preserved, so it stays distinct from null and the
// envelope-shape bar ([] vs omitted, tier 2) is unaffected.
func DiffSemantic(want, got []byte) (string, error) {
	var wv, gv any
	if err := json.Unmarshal(want, &wv); err != nil {
		return "", fmt.Errorf("parity: want side: %w", err)
	}
	if err := json.Unmarshal(got, &gv); err != nil {
		return "", fmt.Errorf("parity: got side: %w", err)
	}
	cw, err := json.Marshal(stripNulls(wv))
	if err != nil {
		return "", fmt.Errorf("parity: want side: %w", err)
	}
	cg, err := json.Marshal(stripNulls(gv))
	if err != nil {
		return "", fmt.Errorf("parity: got side: %w", err)
	}
	if bytes.Equal(cw, cg) {
		return "", nil
	}
	return fmt.Sprintf("semantic mismatch:\n  want: %s\n  got:  %s", cw, cg), nil
}

// stripNulls recursively removes object keys whose value is JSON null. Arrays
// (including empty ones) and their element order are preserved.
func stripNulls(v any) any {
	switch t := v.(type) {
	case map[string]any:
		out := make(map[string]any, len(t))
		for k, val := range t {
			if val == nil {
				continue
			}
			out[k] = stripNulls(val)
		}
		return out
	case []any:
		for i := range t {
			t[i] = stripNulls(t[i])
		}
		return t
	default:
		return v
	}
}

// OrderOf extracts the sequence of idField values from a top-level JSON array of
// objects, so a test can assert the fixed sort-correct ordering (D5)
// independently of the rest of the payload.
func OrderOf(raw []byte, idField string) ([]string, error) {
	var rows []map[string]any
	if err := json.Unmarshal(raw, &rows); err != nil {
		return nil, fmt.Errorf("parity: order-of: %w", err)
	}
	out := make([]string, 0, len(rows))
	for _, row := range rows {
		if v, ok := row[idField].(string); ok {
			out = append(out, v)
		}
	}
	return out, nil
}
