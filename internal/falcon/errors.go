package falcon

import (
	"errors"
	"fmt"
	"strings"

	gofalcon "github.com/crowdstrike/gofalcon/falcon"
	"github.com/go-openapi/runtime"
)

// errorCodeDescriptions maps HTTP status codes to the human-readable guidance
// ported verbatim from the Python ERROR_CODE_DESCRIPTIONS map.
var errorCodeDescriptions = map[int]string{
	400: "Invalid request. Check your filter syntax — FQL uses + for AND, , for OR, and values must be quoted.",
	401: "Authentication failed. The API credentials are invalid or expired.",
	403: "Permission denied. The API credentials don't have the required access.",
	404: "Resource not found. The requested resource does not exist.",
	429: "Rate limit exceeded. Too many requests in a short period.",
	500: "Server error. An unexpected error occurred on the server.",
	503: "Service unavailable. The service is temporarily unavailable.",
}

// coder is implemented by every gofalcon typed response status struct
// (both the ...OK success types and the ...Forbidden/...TooManyRequests error
// types), exposing the HTTP status code.
type coder interface {
	Code() int
}

// StatusCode extracts the HTTP status code from a gofalcon error, or 0 if the
// error does not carry one (e.g. a network/transport error).
//
// Typed per-operation status structs (…Forbidden, …TooManyRequests, …) expose
// the code via a Code() int method, while the generic default-case error is a
// *runtime.APIError that carries the code in a struct field — both are handled.
func StatusCode(err error) int {
	var c coder
	if errors.As(err, &c) {
		return c.Code()
	}
	var apiErr *runtime.APIError
	if errors.As(err, &apiErr) {
		return apiErr.Code
	}
	return 0
}

// ErrorResponse is the normalized error shape returned to MCP clients. It
// mirrors the Python _format_error_response output: an "error" message plus,
// for 403s, the required scopes and a resolution hint.
type ErrorResponse struct {
	Error          string   `json:"error"`
	StatusCode     int      `json:"status_code,omitempty"`
	RequiredScopes []string `json:"required_scopes,omitempty"`
	Resolution     string   `json:"resolution,omitempty"`
}

// NormalizeError converts a gofalcon error into a structured ErrorResponse,
// enriching it with a status-code description, the underlying API message
// (via ErrorExplain), and — for 403 responses — the API scopes the operation
// requires. operation is the gofalcon op name used to look up required scopes.
func NormalizeError(operation string, errorMessage string, err error) ErrorResponse {
	code := StatusCode(err)

	statusMessage, ok := errorCodeDescriptions[code]
	if !ok {
		if code != 0 {
			statusMessage = fmt.Sprintf("Request failed with status code %d", code)
		} else {
			statusMessage = "Request failed"
		}
	}

	// Append the API's own explanation (payload body) when available.
	if explained := gofalcon.ErrorExplain(err); explained != "" {
		statusMessage += " API said: " + explained
	}

	resp := ErrorResponse{
		StatusCode: code,
	}

	if code == 403 {
		if scopes := RequiredScopes(operation); len(scopes) > 0 {
			resp.RequiredScopes = scopes
			statusMessage += " Required scopes: " + strings.Join(scopes, ", ")
			resp.Resolution = fmt.Sprintf(
				"This operation requires the following API scopes: %s. Please ensure your "+
					"API client has been granted these scopes in the CrowdStrike Falcon console.",
				strings.Join(scopes, ", "),
			)
		}
	}

	resp.Error = fmt.Sprintf("%s: %s", errorMessage, statusMessage)
	return resp
}
