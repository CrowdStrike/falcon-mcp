package falcon

import (
	"encoding/json"
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/models"
)

// fakeStatusErr implements runtime.ClientResponseStatus for a chosen HTTP code,
// standing in for a gofalcon per-operation transport error.
type fakeStatusErr struct {
	code int
	msg  string
}

func (e fakeStatusErr) Error() string       { return e.msg }
func (e fakeStatusErr) IsSuccess() bool     { return e.code >= 200 && e.code < 300 }
func (e fakeStatusErr) IsRedirect() bool    { return e.code >= 300 && e.code < 400 }
func (e fakeStatusErr) IsClientError() bool { return e.code >= 400 && e.code < 500 }
func (e fakeStatusErr) IsServerError() bool { return e.code >= 500 }
func (e fakeStatusErr) IsCode(c int) bool   { return e.code == c }

// fakeOKPayload mirrors a gofalcon *OK payload: a struct carrying Errors.
type fakeOKPayload struct {
	Errors    []*models.MsaAPIError
	Resources []string
}

// fakeOK mirrors a gofalcon *OK response: a pointer to a payload.
type fakeOK struct {
	Payload *fakeOKPayload
}

func TestAPIError_SuccessReturnsNil(t *testing.T) {
	resp := &fakeOK{Payload: &fakeOKPayload{Resources: []string{"a", "b"}}}
	if e := APIError(nil, resp, Scope{Name: "Hosts", Read: true}); e != nil {
		t.Fatalf("APIError on clean success = %+v, want nil", e)
	}
}

func TestAPIError_403AttachesScopes(t *testing.T) {
	transportErr := fakeStatusErr{code: 403, msg: "forbidden"}
	e := APIError(transportErr, nil, Scope{Name: "Hosts", Read: true})
	if e == nil {
		t.Fatal("APIError on 403 = nil, want *Error")
	}
	if e.StatusCode != 403 {
		t.Fatalf("StatusCode = %d, want 403", e.StatusCode)
	}
	if len(e.RequiredScopes) != 1 || e.RequiredScopes[0] != "Hosts:read" {
		t.Fatalf("RequiredScopes = %v, want [Hosts:read]", e.RequiredScopes)
	}
	if e.Resolution == "" {
		t.Fatal("Resolution empty on 403, want scope-grant hint")
	}
}

func TestAPIError_Non403NoScopes(t *testing.T) {
	e := APIError(fakeStatusErr{code: 400, msg: "bad request"}, nil, Scope{Name: "Hosts", Read: true})
	if e == nil {
		t.Fatal("APIError on 400 = nil, want *Error")
	}
	if e.StatusCode != 400 {
		t.Fatalf("StatusCode = %d, want 400", e.StatusCode)
	}
	if len(e.RequiredScopes) != 0 || e.Resolution != "" {
		t.Fatalf("400 should not attach scopes/resolution, got %+v", e)
	}
}

func TestAPIError_PayloadErrors(t *testing.T) {
	code := int32(500)
	msg := "internal boom"
	resp := &fakeOK{Payload: &fakeOKPayload{Errors: []*models.MsaAPIError{{Code: &code, Message: &msg}}}}
	e := APIError(nil, resp, Scope{Name: "Hosts", Read: true})
	if e == nil {
		t.Fatal("APIError with payload errors = nil, want *Error")
	}
	if e.Message == "" {
		t.Fatal("Message empty, want payload error text")
	}
}

func TestAPIError_ReflectiveNilGuards(t *testing.T) {
	// nil response, no transport error: nothing to report.
	if e := APIError(nil, nil, Scope{Name: "Hosts", Read: true}); e != nil {
		t.Fatalf("APIError(nil, nil) = %+v, want nil", e)
	}
	// response with nil Payload pointer must not panic and must return nil.
	if e := APIError(nil, &fakeOK{Payload: nil}, Scope{Name: "Hosts", Read: true}); e != nil {
		t.Fatalf("APIError with nil Payload = %+v, want nil", e)
	}
	// a response type with no Payload field at all must not panic.
	type noPayload struct{ X int }
	if e := APIError(nil, &noPayload{X: 1}, Scope{Name: "Hosts", Read: true}); e != nil {
		t.Fatalf("APIError with no Payload field = %+v, want nil", e)
	}
}

func TestError_JSONEnvelope(t *testing.T) {
	e := &Error{Message: "boom", StatusCode: 403, RequiredScopes: []string{"Hosts:read"}, Resolution: "grant it"}
	b, err := json.Marshal(e)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var m map[string]any
	if err := json.Unmarshal(b, &m); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if m["error"] != "boom" {
		t.Fatalf(`json["error"] = %v, want "boom"`, m["error"])
	}
	if _, ok := m["status_code"]; ok {
		t.Fatal("status_code must not be serialized (json:\"-\")")
	}
	if m["required_scopes"] == nil {
		t.Fatal("required_scopes missing from envelope")
	}
	if m["resolution"] != "grant it" {
		t.Fatalf(`json["resolution"] = %v`, m["resolution"])
	}
}

func TestError_OmitsEmptyOptionalFields(t *testing.T) {
	b, _ := json.Marshal(&Error{Message: "boom"})
	var m map[string]any
	_ = json.Unmarshal(b, &m)
	if _, ok := m["required_scopes"]; ok {
		t.Fatal("required_scopes should be omitted when empty")
	}
	if _, ok := m["resolution"]; ok {
		t.Fatal("resolution should be omitted when empty")
	}
}

// statusOf should recover the code via the interface even when wrapped.
func TestStatusOf_Wrapped(t *testing.T) {
	wrapped := errors.Join(errors.New("context"), fakeStatusErr{code: 429, msg: "rate limited"})
	if got := statusOf(wrapped); got != 429 {
		t.Fatalf("statusOf(wrapped 429) = %d, want 429", got)
	}
}
