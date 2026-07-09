package falcon

// ReorderByIDs restores the query-step order on entities hydrated by a
// get-by-IDs step. Two-step search tools query entity IDs first (honoring the
// requested sort) and then hydrate full details by ID; some details endpoints
// return resources in arbitrary order, discarding the sort. This reorders
// entities to match orderedIDs.
//
// id extracts the ID from an entity. Entities whose ID is not in orderedIDs are
// appended in their original order (never dropped); IDs with no matching entity
// are skipped. The function is idempotent and safe against repeated IDs.
func ReorderByIDs[T any](orderedIDs []string, entities []T, id func(T) string) []T {
	byID := make(map[string]T, len(entities))
	for _, e := range entities {
		byID[id(e)] = e
	}

	result := make([]T, 0, len(entities))
	placed := make(map[string]bool, len(entities))
	for _, wantID := range orderedIDs {
		if placed[wantID] {
			continue
		}
		if e, ok := byID[wantID]; ok {
			result = append(result, e)
			placed[wantID] = true
		}
	}

	// Preserve entities not referenced by orderedIDs rather than dropping them.
	for _, e := range entities {
		if !placed[id(e)] {
			result = append(result, e)
		}
	}
	return result
}
