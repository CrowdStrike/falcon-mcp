package falcon

import (
	"reflect"
	"testing"
)

func TestReorderByIDs_RestoresQueryOrder(t *testing.T) {
	ordered := []string{"c", "a", "b"}
	// Details returned in a different (arbitrary) order.
	entities := []string{"a", "b", "c"}
	got := ReorderByIDs(ordered, entities, func(s string) string { return s })
	want := []string{"c", "a", "b"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("ReorderByIDs = %v, want %v", got, want)
	}
}

func TestReorderByIDs_AppendsUnreferenced(t *testing.T) {
	ordered := []string{"a"}
	entities := []string{"a", "x", "y"} // x,y not referenced by ordered
	got := ReorderByIDs(ordered, entities, func(s string) string { return s })
	want := []string{"a", "x", "y"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("ReorderByIDs = %v, want %v (unreferenced appended in order)", got, want)
	}
}

func TestReorderByIDs_SkipsMissingIDs(t *testing.T) {
	ordered := []string{"a", "missing", "b"}
	entities := []string{"b", "a"}
	got := ReorderByIDs(ordered, entities, func(s string) string { return s })
	want := []string{"a", "b"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("ReorderByIDs = %v, want %v (missing id skipped)", got, want)
	}
}

func TestReorderByIDs_Idempotent(t *testing.T) {
	ordered := []string{"c", "a", "b"}
	entities := []string{"a", "b", "c"}
	once := ReorderByIDs(ordered, entities, func(s string) string { return s })
	twice := ReorderByIDs(ordered, once, func(s string) string { return s })
	if !reflect.DeepEqual(once, twice) {
		t.Fatalf("ReorderByIDs not idempotent: once=%v twice=%v", once, twice)
	}
}

func TestReorderByIDs_NoDuplicateEntitiesForRepeatedID(t *testing.T) {
	// A repeated ID in ordered must not place the same entity twice.
	ordered := []string{"a", "a", "b"}
	entities := []string{"a", "b"}
	got := ReorderByIDs(ordered, entities, func(s string) string { return s })
	want := []string{"a", "b"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("ReorderByIDs = %v, want %v (no dup for repeated id)", got, want)
	}
}
