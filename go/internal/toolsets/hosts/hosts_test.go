package hosts

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon"
	"github.com/crowdstrike/gofalcon/falcon/client"
	"golang.org/x/oauth2"
)

// rewriteTransport routes every request to the test server, regardless of the
// https host gofalcon targets, so both the lazy OAuth token fetch and the API
// calls land on one httptest.Server.
type rewriteTransport struct {
	base *url.URL
}

func (rt rewriteTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	req.URL.Scheme = rt.base.Scheme
	req.URL.Host = rt.base.Host
	return http.DefaultTransport.RoundTrip(req)
}

// capturedRequest records what the handlers sent, for assertions.
type capturedRequest struct {
	method string
	path   string
	query  url.Values
	body   string
}

// newTestClient builds a gofalcon client wired to an httptest.Server whose mux
// stubs the oauth2 token endpoint plus the two hosts endpoints. queryIDs are
// returned by the query step; details is the raw JSON the details step returns.
// Captured requests are appended to *captured.
func newTestClient(t *testing.T, queryIDs []string, detailsJSON string, captured *[]capturedRequest) *client.CrowdStrikeAPISpecification {
	t.Helper()

	mux := http.NewServeMux()
	mux.HandleFunc("/oauth2/token", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"access_token":"tok","token_type":"bearer","expires_in":1799}`))
	})
	mux.HandleFunc("/devices/queries/devices/v1", func(w http.ResponseWriter, r *http.Request) {
		*captured = append(*captured, capturedRequest{method: r.Method, path: r.URL.Path, query: r.URL.Query()})
		ids, _ := json.Marshal(queryIDs)
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"resources":` + string(ids) + `,"errors":[]}`))
	})
	mux.HandleFunc("/devices/entities/devices/v2", func(w http.ResponseWriter, r *http.Request) {
		body, _ := io.ReadAll(r.Body)
		*captured = append(*captured, capturedRequest{method: r.Method, path: r.URL.Path, body: string(body)})
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(detailsJSON))
	})

	srv := httptest.NewServer(mux)
	t.Cleanup(srv.Close)

	base, _ := url.Parse(srv.URL)
	ctx := context.WithValue(context.Background(), oauth2.HTTPClient, &http.Client{Transport: rewriteTransport{base: base}})

	api := &falcon.ApiConfig{
		ClientId:     "id",
		ClientSecret: "secret",
		Context:      ctx,
		HostOverride: base.Host,
	}
	c, err := falcon.NewClient(api)
	if err != nil {
		t.Fatalf("build test client: %v", err)
	}
	return c
}

func detailsResponse(deviceIDs ...string) string {
	resources := make([]map[string]any, len(deviceIDs))
	for i, id := range deviceIDs {
		resources[i] = map[string]any{"device_id": id, "hostname": "host-" + id}
	}
	b, _ := json.Marshal(map[string]any{"resources": resources, "errors": []any{}})
	return string(b)
}

func asList(t *testing.T, out any) []map[string]any {
	t.Helper()
	b, _ := json.Marshal(out)
	var list []map[string]any
	if err := json.Unmarshal(b, &list); err != nil {
		t.Fatalf("output is not a JSON list: %v (%s)", err, b)
	}
	return list
}

func TestSearchHosts_Success(t *testing.T) {
	var captured []capturedRequest
	c := newTestClient(t, []string{"a", "b"}, detailsResponse("a", "b"), &captured)
	h := &handlers{c: c}

	out, err := h.searchHosts(context.Background(), searchHostsInput{Filter: "platform_name:'Windows'", Sort: "hostname.asc"})
	if err != nil {
		t.Fatalf("searchHosts: %v", err)
	}
	list := asList(t, out)
	if len(list) != 2 || list[0]["device_id"] != "a" {
		t.Fatalf("unexpected result: %v", list)
	}

	// The query step must carry the filter, the default limit (10), and sort.
	q := captured[0].query
	if q.Get("filter") != "platform_name:'Windows'" {
		t.Fatalf("filter not sent: %q", q.Get("filter"))
	}
	if q.Get("limit") != "10" {
		t.Fatalf("default limit not applied: %q", q.Get("limit"))
	}
	if q.Get("sort") != "hostname.asc" {
		t.Fatalf("sort not sent: %q", q.Get("sort"))
	}
}

func TestSearchHosts_RestoresSortOrder(t *testing.T) {
	var captured []capturedRequest
	// Query returns c,a,b (sorted); details endpoint returns them scrambled.
	c := newTestClient(t, []string{"c", "a", "b"}, detailsResponse("a", "b", "c"), &captured)
	h := &handlers{c: c}

	out, err := h.searchHosts(context.Background(), searchHostsInput{Filter: "x"})
	if err != nil {
		t.Fatalf("searchHosts: %v", err)
	}
	list := asList(t, out)
	gotOrder := []string{
		list[0]["device_id"].(string),
		list[1]["device_id"].(string),
		list[2]["device_id"].(string),
	}
	want := []string{"c", "a", "b"}
	for i := range want {
		if gotOrder[i] != want[i] {
			t.Fatalf("sort not restored: got %v, want %v", gotOrder, want)
		}
	}
}

func TestSearchHosts_EmptyResultsBareList(t *testing.T) {
	var captured []capturedRequest
	c := newTestClient(t, []string{}, detailsResponse(), &captured)
	h := &handlers{c: c}

	out, err := h.searchHosts(context.Background(), searchHostsInput{Filter: "nomatch"})
	if err != nil {
		t.Fatalf("searchHosts: %v", err)
	}
	list := asList(t, out)
	if len(list) != 0 {
		t.Fatalf("empty search should return bare [], got %v", list)
	}
	// Details endpoint must NOT be called when there are no IDs.
	for _, r := range captured {
		if strings.Contains(r.path, "entities/devices") {
			t.Fatal("details endpoint should not be called when query returns no IDs")
		}
	}
}

func TestGetHostDetails_EmptyIDsShortCircuits(t *testing.T) {
	var captured []capturedRequest
	c := newTestClient(t, nil, detailsResponse(), &captured)
	h := &handlers{c: c}

	out, err := h.getHostDetails(context.Background(), getHostDetailsInput{IDs: nil})
	if err != nil {
		t.Fatalf("getHostDetails: %v", err)
	}
	if len(asList(t, out)) != 0 {
		t.Fatalf("empty ids should return [], got %v", out)
	}
	if len(captured) != 0 {
		t.Fatalf("no API call expected for empty ids, got %d", len(captured))
	}
}

func TestGetHostDetails_Success(t *testing.T) {
	var captured []capturedRequest
	c := newTestClient(t, nil, detailsResponse("x", "y"), &captured)
	h := &handlers{c: c}

	out, err := h.getHostDetails(context.Background(), getHostDetailsInput{IDs: []string{"x", "y"}})
	if err != nil {
		t.Fatalf("getHostDetails: %v", err)
	}
	list := asList(t, out)
	if len(list) != 2 || list[0]["device_id"] != "x" {
		t.Fatalf("unexpected details: %v", list)
	}
	if captured[0].method != http.MethodPost {
		t.Fatalf("details must be POST, got %s", captured[0].method)
	}
	if !strings.Contains(captured[0].body, `"x"`) {
		t.Fatalf("request body missing ids: %s", captured[0].body)
	}
}

func TestNew_RegistersToolsAndResource(t *testing.T) {
	ts := New(nil)
	if ts.Name != "hosts" {
		t.Fatalf("toolset name = %q", ts.Name)
	}
	if len(ts.Tools) != 2 {
		t.Fatalf("want 2 tools, got %d", len(ts.Tools))
	}
	names := map[string]bool{}
	for _, tool := range ts.Tools {
		names[tool.Name] = true
	}
	if !names["falcon_search_hosts"] || !names["falcon_get_host_details"] {
		t.Fatalf("missing expected tool names: %v", names)
	}
	if len(ts.Resources) != 1 || ts.Resources[0].URI != "falcon://hosts/search/fql-guide" {
		t.Fatalf("FQL resource missing or wrong URI: %+v", ts.Resources)
	}
	if !strings.Contains(ts.Resources[0].Text, "FQL") {
		t.Fatal("FQL guide text not embedded")
	}
}

func TestSearchHostsInput_Constraints(t *testing.T) {
	ts := New(nil)
	for _, tool := range ts.Tools {
		if tool.Name != "falcon_search_hosts" {
			continue
		}
		lim := tool.InputSchema.Properties["limit"]
		if lim == nil || lim.Minimum == nil || *lim.Minimum != 1 || lim.Maximum == nil || *lim.Maximum != 5000 {
			t.Fatalf("limit constraints not applied: %+v", lim)
		}
		if string(lim.Default) != "10" {
			t.Fatalf("limit default = %s, want 10", lim.Default)
		}
	}
}
