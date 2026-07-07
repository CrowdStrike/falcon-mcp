package falcon

// This file ports the response-shaping helpers from the Python BaseModule
// (_format_empty_response and _format_fql_error_response) plus the FQL-error
// detection used by search tools. All shapes stay as plain maps so tool
// results serialize as unstructured JSON (structured_output=False parity).

// EmptyResponse is the shape returned by a successful search that matched zero
// resources. It deliberately omits FQL documentation — the filter was accepted
// by the API, so the query was valid.
type EmptyResponse struct {
	Results    []any   `json:"results"`
	Total      int     `json:"total"`
	FilterUsed *string `json:"filter_used"`
}

// FormatEmptyResponse builds an EmptyResponse for the given filter.
func FormatEmptyResponse(filterUsed *string) EmptyResponse {
	return EmptyResponse{
		Results:    []any{},
		Total:      0,
		FilterUsed: filterUsed,
	}
}

// FQLErrorResponse is returned when the API rejects a request with an error
// that indicates the FQL filter syntax is wrong (typically HTTP 400). It
// inlines the module's FQL guide so the model can self-correct.
type FQLErrorResponse struct {
	Results    any     `json:"results"`
	FilterUsed *string `json:"filter_used"`
	FQLGuide   string  `json:"fql_guide"`
	Hint       string  `json:"hint"`
}

// FormatFQLError builds an FQLErrorResponse embedding the given FQL guide.
// errResult is the normalized error (an ErrorResponse or list thereof).
func FormatFQLError(errResult any, filterUsed *string, fqlGuide string) FQLErrorResponse {
	return FQLErrorResponse{
		Results:    errResult,
		FilterUsed: filterUsed,
		FQLGuide:   fqlGuide,
		Hint:       "Filter error occurred. Review the FQL guide above to correct your query syntax.",
	}
}

// IsFQLError reports whether an error status code suggests a filter-syntax
// problem for which the FQL guide should be surfaced. Only 400 qualifies —
// 403/404/429/5xx are not filter problems.
func IsFQLError(statusCode int) bool {
	return statusCode == 400
}
