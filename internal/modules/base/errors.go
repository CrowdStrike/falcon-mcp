package base

import (
	"errors"
	"fmt"
	"reflect"
	"strings"

	"github.com/crowdstrike/gofalcon/falcon"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
)

// Error is the normalized error shape returned to tools. It marshals to the
// same JSON envelope the Python server produced: {"error", "required_scopes",
// "resolution"}. StatusCode is internal only (json:"-").
type Error struct {
	Message        string   `json:"error"`
	StatusCode     int      `json:"-"`
	RequiredScopes []string `json:"required_scopes,omitempty"`
	Resolution     string   `json:"resolution,omitempty"`
}

// Error implements the error interface.
func (e *Error) Error() string { return e.Message }

// APIError converts a gofalcon transport error plus a gofalcon *OK response
// into a single *Error, or nil on success. scopes are the API scopes the
// operation requires; on a 403 they are attached so the caller learns exactly
// which permissions to grant. resp may be any gofalcon *OK value; its
// Payload.Errors are extracted reflectively so one funnel serves every
// operation without per-operation helpers.
func APIError(transportErr error, resp any, scopes ...Scope) *Error {
	if transportErr != nil {
		code := statusOf(transportErr)
		e := &Error{Message: falcon.ErrorExplain(transportErr), StatusCode: code}
		if code == 403 {
			if required := scopeStrings(scopes); len(required) > 0 {
				e.RequiredScopes = required
				e.Resolution = resolutionHint(required)
			}
		}
		return e
	}
	if err := falcon.AssertNoError(payloadErrors(resp)); err != nil {
		return &Error{Message: err.Error()}
	}
	return nil
}

// statusOf extracts the HTTP status from any gofalcon error generically, via
// the go-openapi runtime.ClientResponseStatus interface, so no per-operation
// type switch is needed. It returns 0 when the status is not recoverable.
func statusOf(err error) int {
	var st runtime.ClientResponseStatus
	if errors.As(err, &st) {
		for _, c := range []int{400, 401, 403, 404, 409, 429, 500, 503} {
			if st.IsCode(c) {
				return c
			}
		}
		switch {
		case st.IsClientError():
			return 400
		case st.IsServerError():
			return 500
		}
	}
	return 0
}

// scopeStrings flattens the console permission strings for the given scopes.
func scopeStrings(scopes []Scope) []string {
	var out []string
	for _, s := range scopes {
		out = append(out, s.Strings()...)
	}
	return out
}

// resolutionHint renders the 403 resolution message listing the required API
// scopes, so the caller learns exactly which permissions to grant.
func resolutionHint(required []string) string {
	return fmt.Sprintf(
		"This operation requires the following API scopes: %s. "+
			"Please ensure your API client has been granted these scopes in the "+
			"CrowdStrike Falcon console.", strings.Join(required, ", "))
}

// payloadErrors reflectively reads resp.Payload.Errors ([]*models.MsaAPIError)
// from any gofalcon *OK response. Every generated *OK type has a Payload
// pointer whose target carries an Errors field, but the types are distinct per
// operation with no shared interface, so reflection lets one funnel serve all
// operations. It returns nil safely when the field or payload is absent.
func payloadErrors(resp any) []*models.MsaAPIError {
	if resp == nil {
		return nil
	}
	v := reflect.ValueOf(resp)
	for v.Kind() == reflect.Pointer {
		if v.IsNil() {
			return nil
		}
		v = v.Elem()
	}
	if v.Kind() != reflect.Struct {
		return nil
	}
	payload := v.FieldByName("Payload")
	if !payload.IsValid() {
		return nil
	}
	for payload.Kind() == reflect.Pointer {
		if payload.IsNil() {
			return nil
		}
		payload = payload.Elem()
	}
	if payload.Kind() != reflect.Struct {
		return nil
	}
	errsField := payload.FieldByName("Errors")
	if !errsField.IsValid() {
		return nil
	}
	errs, ok := errsField.Interface().([]*models.MsaAPIError)
	if !ok {
		return nil
	}
	return errs
}
