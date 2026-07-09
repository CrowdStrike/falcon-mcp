package falcon

// Opt converts a value into an optional pointer, returning nil for the zero
// value so gofalcon omits the optional param. It ports the Python
// prepare_api_parameters omit-empty rule (drop falsy values).
//
// Caveat: this conflates a real zero (e.g. offset=0) with "unset", matching the
// Python behavior. For a param where zero is meaningfully distinct from absent,
// take a pointer in the input struct instead.
func Opt[T comparable](v T) *T {
	var zero T
	if v == zero {
		return nil
	}
	return &v
}
