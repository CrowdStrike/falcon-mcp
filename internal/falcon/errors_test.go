package falcon

import (
	"errors"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon/client/hosts"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
)

func TestStatusCodeFromTypedStatus(t *testing.T) {
	// A gofalcon typed status struct exposes Code() int.
	err := hosts.NewQueryDevicesByFilterForbidden()
	if got := StatusCode(err); got != 403 {
		t.Errorf("StatusCode(Forbidden) = %d, want 403", got)
	}
}

func TestStatusCodeFromAPIError(t *testing.T) {
	// The generic default-case error is *runtime.APIError with a Code field.
	err := runtime.NewAPIError("op", "bad filter", 400)
	if got := StatusCode(err); got != 400 {
		t.Errorf("StatusCode(APIError 400) = %d, want 400", got)
	}
}

func TestStatusCodeFromPlainError(t *testing.T) {
	if got := StatusCode(errors.New("network down")); got != 0 {
		t.Errorf("StatusCode(plain) = %d, want 0", got)
	}
}

func TestNormalizeError403InjectsScopes(t *testing.T) {
	err := hosts.NewQueryDevicesByFilterForbidden()
	resp := NormalizeError("QueryDevicesByFilter", "Failed to search hosts", err)

	if resp.StatusCode != 403 {
		t.Errorf("StatusCode = %d, want 403", resp.StatusCode)
	}
	if len(resp.RequiredScopes) != 1 || resp.RequiredScopes[0] != "Hosts:read" {
		t.Errorf("RequiredScopes = %v, want [Hosts:read]", resp.RequiredScopes)
	}
	if resp.Resolution == "" {
		t.Error("expected a resolution hint for 403")
	}
}

func TestNormalizeError400NoScopes(t *testing.T) {
	err := runtime.NewAPIError("QueryDevicesByFilter", "invalid FQL", 400)
	resp := NormalizeError("QueryDevicesByFilter", "Failed to search hosts", err)

	if resp.StatusCode != 400 {
		t.Errorf("StatusCode = %d, want 400", resp.StatusCode)
	}
	if len(resp.RequiredScopes) != 0 {
		t.Errorf("RequiredScopes = %v, want none for 400", resp.RequiredScopes)
	}
	if !IsFQLError(resp.StatusCode) {
		t.Error("IsFQLError should be true for 400")
	}
}

func TestRequiredScopesKnownAndUnknown(t *testing.T) {
	if got := RequiredScopes("QueryDevicesByFilter"); len(got) != 1 || got[0] != "Hosts:read" {
		t.Errorf("RequiredScopes(QueryDevicesByFilter) = %v", got)
	}
	if got := RequiredScopes("NoSuchOperation"); got != nil {
		t.Errorf("RequiredScopes(unknown) = %v, want nil", got)
	}
}

func TestFormatEmptyResponse(t *testing.T) {
	f := "platform_name:'Windows'"
	resp := FormatEmptyResponse(&f)
	if resp.Total != 0 || len(resp.Results) != 0 {
		t.Errorf("empty response not empty: %+v", resp)
	}
	if resp.FilterUsed == nil || *resp.FilterUsed != f {
		t.Errorf("FilterUsed = %v, want %q", resp.FilterUsed, f)
	}
}

// compile-time guard: the models package is used to keep imports honest as the
// error surface grows.
var _ = models.MsaReplyMetaOnly{}
