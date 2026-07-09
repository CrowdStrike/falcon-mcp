package falcon

import "strings"

// sanitizeReplacer strips the characters the Python sanitize_input removes:
// backslash, double quote, single quote, newline, carriage return, and tab.
// These could otherwise break out of an interpolated GraphQL string literal.
var sanitizeReplacer = strings.NewReplacer(
	`\`, "",
	`"`, "",
	`'`, "",
	"\n", "",
	"\r", "",
	"\t", "",
)

// SanitizeInput removes characters that could be used to inject into an
// interpolated GraphQL query string and caps the result at 255 characters. It
// ports common/utils.py:sanitize_input, which is mandatory for Identity
// Protection because gofalcon's SwaggerGraphQLQuery carries only a query string
// (no variables), so every value is interpolated into the query text.
func SanitizeInput(s string) string {
	sanitized := sanitizeReplacer.Replace(s)
	if len(sanitized) > 255 {
		return sanitized[:255]
	}
	return sanitized
}
