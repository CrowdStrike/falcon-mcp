package idp

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon"
	"github.com/crowdstrike/gofalcon/falcon/client"
	"golang.org/x/oauth2"
)

// rewriteTransport routes every request to the test server so the lazy OAuth
// token fetch and the GraphQL call land on one httptest.Server.
type rewriteTransport struct{ base *url.URL }

func (rt rewriteTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	req.URL.Scheme = rt.base.Scheme
	req.URL.Host = rt.base.Host
	return http.DefaultTransport.RoundTrip(req)
}

// graphqlStub serves scripted GraphQL responses. Each call to the endpoint pops
// the next body from responses and records the sent query.
type graphqlStub struct {
	responses []string
	queries   []string
	idx       int
}

func newIDPTestClient(t *testing.T, stub *graphqlStub) *client.CrowdStrikeAPISpecification {
	t.Helper()

	mux := http.NewServeMux()
	mux.HandleFunc("/oauth2/token", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"access_token":"tok","token_type":"bearer","expires_in":1799}`))
	})
	mux.HandleFunc("/identity-protection/combined/graphql/v1", func(w http.ResponseWriter, r *http.Request) {
		raw, _ := io.ReadAll(r.Body)
		var sent map[string]any
		_ = json.Unmarshal(raw, &sent)
		if q, ok := sent["query"].(string); ok {
			stub.queries = append(stub.queries, q)
		}
		body := `{"data":{}}`
		if stub.idx < len(stub.responses) {
			body = stub.responses[stub.idx]
		}
		stub.idx++
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(body))
	})

	srv := httptest.NewServer(mux)
	t.Cleanup(srv.Close)

	base, _ := url.Parse(srv.URL)
	ctx := context.WithValue(context.Background(), oauth2.HTTPClient, &http.Client{Transport: rewriteTransport{base: base}})
	c, err := falcon.NewClient(&falcon.ApiConfig{
		ClientId: "id", ClientSecret: "secret", Context: ctx, HostOverride: base.Host,
	})
	if err != nil {
		t.Fatalf("build test client: %v", err)
	}
	return c
}
