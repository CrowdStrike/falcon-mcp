package exclusions

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"testing"

	cbe "github.com/crowdstrike/gofalcon/falcon/client/certificate_based_exclusions"
	ioae "github.com/crowdstrike/gofalcon/falcon/client/ioa_exclusions"
	mle "github.com/crowdstrike/gofalcon/falcon/client/ml_exclusions"
	sve "github.com/crowdstrike/gofalcon/falcon/client/sensor_visibility_exclusions"
	"github.com/crowdstrike/gofalcon/falcon/models"
	"github.com/go-openapi/runtime"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// --- mocks (only the methods each test exercises are populated) ---

type mockIOA struct {
	searchResp *ioae.SsIoaExclusionsSearchV2OK
	searchErr  error
	getResp    *ioae.SsIoaExclusionsGetV2OK
	getGot     *ioae.SsIoaExclusionsGetV2Params
	createResp *ioae.SsIoaExclusionsCreateV2OK
	createGot  *ioae.SsIoaExclusionsCreateV2Params
	deleteResp *ioae.SsIoaExclusionsDeleteV2OK
	deleteGot  *ioae.SsIoaExclusionsDeleteV2Params
}

func (m *mockIOA) SsIoaExclusionsSearchV2(*ioae.SsIoaExclusionsSearchV2Params, ...ioae.ClientOption) (*ioae.SsIoaExclusionsSearchV2OK, error) {
	return m.searchResp, m.searchErr
}
func (m *mockIOA) SsIoaExclusionsGetV2(p *ioae.SsIoaExclusionsGetV2Params, _ ...ioae.ClientOption) (*ioae.SsIoaExclusionsGetV2OK, error) {
	m.getGot = p
	return m.getResp, nil
}
func (m *mockIOA) SsIoaExclusionsCreateV2(p *ioae.SsIoaExclusionsCreateV2Params, _ ...ioae.ClientOption) (*ioae.SsIoaExclusionsCreateV2OK, error) {
	m.createGot = p
	return m.createResp, nil
}
func (m *mockIOA) SsIoaExclusionsUpdateV2(*ioae.SsIoaExclusionsUpdateV2Params, ...ioae.ClientOption) (*ioae.SsIoaExclusionsUpdateV2OK, error) {
	return &ioae.SsIoaExclusionsUpdateV2OK{Payload: &models.DomainSsIoaExclusionsRespV2{}}, nil
}
func (m *mockIOA) SsIoaExclusionsDeleteV2(p *ioae.SsIoaExclusionsDeleteV2Params, _ ...ioae.ClientOption) (*ioae.SsIoaExclusionsDeleteV2OK, error) {
	m.deleteGot = p
	return m.deleteResp, nil
}

type mockCert struct {
	queryResp *cbe.CbExclusionsQueryV1OK
	getResp   *cbe.CbExclusionsGetV1OK
	getGot    *cbe.CbExclusionsGetV1Params
	certResp  *cbe.CertificatesGetV1OK
	certGot   *cbe.CertificatesGetV1Params
}

func (m *mockCert) CbExclusionsQueryV1(*cbe.CbExclusionsQueryV1Params, ...cbe.ClientOption) (*cbe.CbExclusionsQueryV1OK, error) {
	return m.queryResp, nil
}
func (m *mockCert) CbExclusionsGetV1(p *cbe.CbExclusionsGetV1Params, _ ...cbe.ClientOption) (*cbe.CbExclusionsGetV1OK, error) {
	m.getGot = p
	return m.getResp, nil
}
func (m *mockCert) CbExclusionsCreateV1(*cbe.CbExclusionsCreateV1Params, ...cbe.ClientOption) (*cbe.CbExclusionsCreateV1Created, error) {
	return &cbe.CbExclusionsCreateV1Created{Payload: &models.APICertBasedExclusionRespV1{}}, nil
}
func (m *mockCert) CbExclusionsUpdateV1(*cbe.CbExclusionsUpdateV1Params, ...cbe.ClientOption) (*cbe.CbExclusionsUpdateV1OK, error) {
	return &cbe.CbExclusionsUpdateV1OK{Payload: &models.APICertBasedExclusionRespV1{}}, nil
}
func (m *mockCert) CbExclusionsDeleteV1(*cbe.CbExclusionsDeleteV1Params, ...cbe.ClientOption) (*cbe.CbExclusionsDeleteV1OK, error) {
	return &cbe.CbExclusionsDeleteV1OK{Payload: &models.APICertBasedExclusionRespV1{}}, nil
}
func (m *mockCert) CertificatesGetV1(p *cbe.CertificatesGetV1Params, _ ...cbe.ClientOption) (*cbe.CertificatesGetV1OK, error) {
	m.certGot = p
	return m.certResp, nil
}

// stub ml/sv (unused in most tests, present to satisfy the apis struct)
type stubML struct{}

func (stubML) QueryMLExclusionsV1(*mle.QueryMLExclusionsV1Params, ...mle.ClientOption) (*mle.QueryMLExclusionsV1OK, error) {
	return &mle.QueryMLExclusionsV1OK{Payload: &models.MsaspecQueryResponse{}}, nil
}
func (stubML) GetMLExclusionsV1(*mle.GetMLExclusionsV1Params, ...mle.ClientOption) (*mle.GetMLExclusionsV1OK, error) {
	return &mle.GetMLExclusionsV1OK{Payload: &models.ExclusionsRespV1{}}, nil
}
func (stubML) ExclusionsCreateV2(*mle.ExclusionsCreateV2Params, ...mle.ClientOption) (*mle.ExclusionsCreateV2OK, error) {
	return &mle.ExclusionsCreateV2OK{}, nil
}
func (stubML) ExclusionsUpdateV2(*mle.ExclusionsUpdateV2Params, ...mle.ClientOption) (*mle.ExclusionsUpdateV2OK, error) {
	return &mle.ExclusionsUpdateV2OK{}, nil
}
func (stubML) ExclusionsDeleteV2(*mle.ExclusionsDeleteV2Params, ...mle.ClientOption) (*mle.ExclusionsDeleteV2OK, error) {
	return &mle.ExclusionsDeleteV2OK{}, nil
}

type stubSV struct{}

func (stubSV) QuerySensorVisibilityExclusionsV1(*sve.QuerySensorVisibilityExclusionsV1Params, ...sve.ClientOption) (*sve.QuerySensorVisibilityExclusionsV1OK, error) {
	return &sve.QuerySensorVisibilityExclusionsV1OK{Payload: &models.MsaQueryResponse{}}, nil
}
func (stubSV) GetSensorVisibilityExclusionsV1(*sve.GetSensorVisibilityExclusionsV1Params, ...sve.ClientOption) (*sve.GetSensorVisibilityExclusionsV1OK, error) {
	return &sve.GetSensorVisibilityExclusionsV1OK{Payload: &models.SvExclusionsRespV1{}}, nil
}
func (stubSV) CreateSVExclusionsV1(*sve.CreateSVExclusionsV1Params, ...sve.ClientOption) (*sve.CreateSVExclusionsV1Created, error) {
	return &sve.CreateSVExclusionsV1Created{Payload: &models.ExclusionsRespV1{}}, nil
}
func (stubSV) UpdateSensorVisibilityExclusionsV1(*sve.UpdateSensorVisibilityExclusionsV1Params, ...sve.ClientOption) (*sve.UpdateSensorVisibilityExclusionsV1OK, error) {
	return &sve.UpdateSensorVisibilityExclusionsV1OK{Payload: &models.SvExclusionsRespV1{}}, nil
}
func (stubSV) DeleteSensorVisibilityExclusionsV1(*sve.DeleteSensorVisibilityExclusionsV1Params, ...sve.ClientOption) (*sve.DeleteSensorVisibilityExclusionsV1OK, error) {
	return &sve.DeleteSensorVisibilityExclusionsV1OK{Payload: &models.MsaQueryResponse{}}, nil
}

func callTool(t *testing.T, register func(*mcp.Server, apis), a apis, name string, args map[string]any) string {
	t.Helper()
	srv := mcp.NewServer(&mcp.Implementation{Name: "t", Version: "0"}, nil)
	register(srv, a)
	ct, st := mcp.NewInMemoryTransports()
	ctx := context.Background()
	if _, err := srv.Connect(ctx, st, nil); err != nil {
		t.Fatalf("server connect: %v", err)
	}
	cs, err := mcp.NewClient(&mcp.Implementation{Name: "c", Version: "0"}, nil).Connect(ctx, ct, nil)
	if err != nil {
		t.Fatalf("client connect: %v", err)
	}
	defer cs.Close()
	res, err := cs.CallTool(ctx, &mcp.CallToolParams{Name: name, Arguments: args})
	if err != nil {
		t.Fatalf("CallTool: %v", err)
	}
	return res.Content[0].(*mcp.TextContent).Text
}

func ioaSearchOK(ids ...string) *ioae.SsIoaExclusionsSearchV2OK {
	return &ioae.SsIoaExclusionsSearchV2OK{Payload: &models.MsaspecQueryResponse{Resources: ids}}
}

func TestSearchIOATwoStep(t *testing.T) {
	id := "ioa-1"
	m := &mockIOA{
		searchResp: ioaSearchOK("ioa-1"),
		getResp:    &ioae.SsIoaExclusionsGetV2OK{Payload: &models.DomainSsIoaExclusionsRespV2{Resources: []*models.DomainSsIoaExclusionsV2{{ID: &id}}}},
	}
	a := apis{ioa: m, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	text := callTool(t, registerSearch, a, "falcon_search_exclusions", map[string]any{"exclusion_type": "ioa", "filter": "name:'x'"})
	if !strings.Contains(text, "ioa-1") {
		t.Fatalf("expected details, got %s", text)
	}
	if m.getGot == nil || len(m.getGot.Ids) != 1 || m.getGot.Ids[0] != "ioa-1" {
		t.Errorf("get not called with queried ID: %+v", m.getGot)
	}
}

func TestSearchCertificateTwoStep(t *testing.T) {
	cid := "cert-1"
	m := &mockCert{
		queryResp: &cbe.CbExclusionsQueryV1OK{Payload: &models.MsaspecQueryResponse{Resources: []string{"cert-1"}}},
		getResp:   &cbe.CbExclusionsGetV1OK{Payload: &models.APICertBasedExclusionRespV1{Resources: []*models.APICertBasedExclusionV1{{ID: &cid}}}},
	}
	a := apis{ioa: &mockIOA{}, ml: stubML{}, sv: stubSV{}, cert: m}
	text := callTool(t, registerSearch, a, "falcon_search_exclusions", map[string]any{"exclusion_type": "certificate"})
	if !strings.Contains(text, "cert-1") {
		t.Fatalf("expected cert details, got %s", text)
	}
	if m.getGot == nil || len(m.getGot.Ids) != 1 {
		t.Errorf("cert get not called with IDs: %+v", m.getGot)
	}
}

func TestSearchInvalidType(t *testing.T) {
	a := apis{ioa: &mockIOA{}, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	text := callTool(t, registerSearch, a, "falcon_search_exclusions", map[string]any{"exclusion_type": "bogus"})
	if !strings.Contains(text, "Invalid exclusion_type") {
		t.Errorf("expected invalid type error, got %s", text)
	}
}

func TestSearchEmpty(t *testing.T) {
	m := &mockIOA{searchResp: ioaSearchOK()}
	a := apis{ioa: m, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	text := callTool(t, registerSearch, a, "falcon_search_exclusions", map[string]any{"exclusion_type": "ioa"})
	if !strings.Contains(text, `"total": 0`) {
		t.Errorf("expected empty response, got %s", text)
	}
	if m.getGot != nil {
		t.Error("details fetched despite no IDs")
	}
}

func TestSearchFQLError(t *testing.T) {
	m := &mockIOA{searchErr: runtime.NewAPIError("ss_ioa_exclusions_search_v2", "bad", 400)}
	a := apis{ioa: m, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	text := callTool(t, registerSearch, a, "falcon_search_exclusions", map[string]any{"exclusion_type": "ioa", "filter": "x=="})
	if !strings.Contains(text, "fql_guide") {
		t.Errorf("expected fql_guide, got %s", text)
	}
}

func TestSearch403Scopes(t *testing.T) {
	m := &mockIOA{searchErr: ioae.NewSsIoaExclusionsSearchV2Forbidden()}
	a := apis{ioa: m, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	text := callTool(t, registerSearch, a, "falcon_search_exclusions", map[string]any{"exclusion_type": "ioa"})
	if strings.Contains(text, "fql_guide") {
		t.Errorf("403 should not include fql_guide: %s", text)
	}
	if !strings.Contains(text, "status_code") {
		t.Errorf("expected normalized error, got %s", text)
	}
}

func TestCreateIOA(t *testing.T) {
	m := &mockIOA{createResp: &ioae.SsIoaExclusionsCreateV2OK{Payload: &models.DomainSsIoaExclusionsRespV2{}}}
	a := apis{ioa: m, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	_ = callTool(t, registerCreate, a, "falcon_create_exclusion", map[string]any{
		"exclusion_type": "ioa", "name": "myexcl", "pattern_id": "p1", "host_groups": []any{"g1"},
	})
	if m.createGot == nil || m.createGot.Body == nil || len(m.createGot.Body.Exclusions) != 1 {
		t.Fatalf("create body not populated: %+v", m.createGot)
	}
	ex := m.createGot.Body.Exclusions[0]
	if ex.Name == nil || *ex.Name != "myexcl" || len(ex.HostGroups) != 1 {
		t.Errorf("create fields wrong: %+v", ex)
	}
}

func TestDeleteIOA(t *testing.T) {
	m := &mockIOA{deleteResp: &ioae.SsIoaExclusionsDeleteV2OK{Payload: &models.DomainSsIoaExclusionsRespV2{}}}
	a := apis{ioa: m, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	_ = callTool(t, registerDelete, a, "falcon_delete_exclusions", map[string]any{"exclusion_type": "ioa", "ids": []any{"i1", "i2"}})
	if m.deleteGot == nil || len(m.deleteGot.Ids) != 2 {
		t.Errorf("delete ids not passed: %+v", m.deleteGot)
	}
}

func TestDeleteEmptyIDs(t *testing.T) {
	a := apis{ioa: &mockIOA{}, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	text := callTool(t, registerDelete, a, "falcon_delete_exclusions", map[string]any{"exclusion_type": "ioa", "ids": []any{}})
	if !strings.Contains(text, "ids is required") {
		t.Errorf("expected ids-required error, got %s", text)
	}
}

func TestMLDeleteAck(t *testing.T) {
	// ML v2 delete OK discards the body; a success returns an ack object.
	a := apis{ioa: &mockIOA{}, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	text := callTool(t, registerDelete, a, "falcon_delete_exclusions", map[string]any{"exclusion_type": "ml", "ids": []any{"m1"}})
	var got map[string]any
	if err := json.Unmarshal([]byte(text), &got); err != nil {
		t.Fatalf("not object: %v", err)
	}
	if got["status"] != "ok" {
		t.Errorf("expected ok ack, got %s", text)
	}
}

func TestGetCertificateDetails(t *testing.T) {
	m := &mockCert{certResp: &cbe.CertificatesGetV1OK{Payload: &models.APIRespCertificatesV1{Resources: []*models.APICertificatesResponseV1{{}}}}}
	a := apis{ioa: &mockIOA{}, ml: stubML{}, sv: stubSV{}, cert: m}
	_ = callTool(t, registerGetCert, a, "falcon_get_certificate_details", map[string]any{"ids": []any{"sha256abc"}})
	if m.certGot == nil || m.certGot.Ids != "sha256abc" {
		t.Errorf("cert get id not passed: %+v", m.certGot)
	}
}

func TestGetCertificateEmpty(t *testing.T) {
	a := apis{ioa: &mockIOA{}, ml: stubML{}, sv: stubSV{}, cert: &mockCert{}}
	text := callTool(t, registerGetCert, a, "falcon_get_certificate_details", map[string]any{"ids": []any{}})
	if strings.TrimSpace(text) != "[]" {
		t.Errorf("expected empty array, got %s", text)
	}
}

func TestClampLimit(t *testing.T) {
	if got := clampLimit("certificate", 0); got != 100 {
		t.Errorf("certificate default = %d, want 100", got)
	}
	if got := clampLimit("certificate", 999); got != 100 {
		t.Errorf("certificate cap = %d, want 100", got)
	}
	if got := clampLimit("ioa", 0); got != 100 {
		t.Errorf("ioa default = %d, want 100", got)
	}
	if got := clampLimit("ioa", 9999); got != 500 {
		t.Errorf("ioa cap = %d, want 500", got)
	}
}

var _ = errors.New
