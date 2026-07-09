package parity

import "testing"

func TestCanonicalize_SortsObjectKeysRecursively(t *testing.T) {
	a := []byte(`{"b":1,"a":{"d":4,"c":3},"e":[{"z":26,"y":25}]}`)
	b := []byte(`{"a":{"c":3,"d":4},"b":1,"e":[{"y":25,"z":26}]}`)

	ca, err := Canonicalize(a)
	if err != nil {
		t.Fatalf("canonicalize a: %v", err)
	}
	cb, err := Canonicalize(b)
	if err != nil {
		t.Fatalf("canonicalize b: %v", err)
	}
	if string(ca) != string(cb) {
		t.Fatalf("canonical forms differ:\n a=%s\n b=%s", ca, cb)
	}
}

func TestCanonicalize_PreservesArrayOrder(t *testing.T) {
	// Array order is semantically meaningful (sort-correctness), so it must be
	// preserved, unlike object key order.
	a := []byte(`[3,1,2]`)
	b := []byte(`[1,2,3]`)
	ca, _ := Canonicalize(a)
	cb, _ := Canonicalize(b)
	if string(ca) == string(cb) {
		t.Fatal("Canonicalize must NOT reorder arrays")
	}
}

func TestDiff_EqualIgnoringKeyOrder(t *testing.T) {
	a := []byte(`{"device_id":"abc","hostname":"h1","tags":["x","y"]}`)
	b := []byte(`{"hostname":"h1","device_id":"abc","tags":["x","y"]}`)
	d, err := Diff(a, b)
	if err != nil {
		t.Fatalf("diff: %v", err)
	}
	if d != "" {
		t.Fatalf("expected no diff, got:\n%s", d)
	}
}

func TestDiff_ReportsStructuralDifference(t *testing.T) {
	a := []byte(`{"device_id":"abc","hostname":"h1"}`)
	b := []byte(`{"device_id":"xyz","hostname":"h1"}`)
	d, err := Diff(a, b)
	if err != nil {
		t.Fatalf("diff: %v", err)
	}
	if d == "" {
		t.Fatal("expected a diff for differing values, got none")
	}
}

func TestDiff_ArrayOrderMatters(t *testing.T) {
	// Two-step ordering: [c,a,b] vs [a,b,c] must be reported as different.
	a := []byte(`[{"device_id":"c"},{"device_id":"a"},{"device_id":"b"}]`)
	b := []byte(`[{"device_id":"a"},{"device_id":"b"},{"device_id":"c"}]`)
	d, err := Diff(a, b)
	if err != nil {
		t.Fatalf("diff: %v", err)
	}
	if d == "" {
		t.Fatal("array order difference should be reported")
	}
}

func TestOrderOf_ExtractsIDSequence(t *testing.T) {
	raw := []byte(`[{"device_id":"c","x":1},{"device_id":"a"},{"device_id":"b"}]`)
	got, err := OrderOf(raw, "device_id")
	if err != nil {
		t.Fatalf("OrderOf: %v", err)
	}
	want := []string{"c", "a", "b"}
	if len(got) != len(want) {
		t.Fatalf("len = %d, want %d (%v)", len(got), len(want), got)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("order = %v, want %v", got, want)
		}
	}
}

// TestDiffSemantic_TreatsNullAsAbsent covers the gofalcon vs FalconPy divergence:
// gofalcon's typed models emit null for unset optional fields while Python omits
// the key entirely. Both mean "no value" (tier-1 payload parity), so a semantic
// diff must ignore null-valued keys.
func TestDiffSemantic_TreatsNullAsAbsent(t *testing.T) {
	python := []byte(`[{"device_id":"a","hostname":"host-a"}]`)
	golang := []byte(`[{"device_id":"a","hostname":"host-a","tags":null,"groups":null}]`)
	d, err := DiffSemantic(python, golang)
	if err != nil {
		t.Fatalf("DiffSemantic: %v", err)
	}
	if d != "" {
		t.Fatalf("null-valued keys should be treated as absent, got diff:\n%s", d)
	}
}

// TestDiffSemantic_EmptyListIsNotNull guards the envelope-shape bar (tier 2):
// an empty list [] is a real value distinct from null and must NOT be elided.
func TestDiffSemantic_EmptyListIsNotNull(t *testing.T) {
	a := []byte(`{"errors":[]}`)
	b := []byte(`{"errors":null}`)
	d, err := DiffSemantic(a, b)
	if err != nil {
		t.Fatalf("DiffSemantic: %v", err)
	}
	if d == "" {
		t.Fatal("[] and null must be reported as different (envelope shape matters)")
	}
}

// TestDiffSemantic_StillReportsRealValueDifference ensures stripping nulls does
// not mask genuine value mismatches.
func TestDiffSemantic_StillReportsRealValueDifference(t *testing.T) {
	a := []byte(`{"device_id":"abc"}`)
	b := []byte(`{"device_id":"xyz","tags":null}`)
	d, err := DiffSemantic(a, b)
	if err != nil {
		t.Fatalf("DiffSemantic: %v", err)
	}
	if d == "" {
		t.Fatal("differing device_id must still be reported")
	}
}
