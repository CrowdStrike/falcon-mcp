package falcon

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

// rewriteTransport routes every request to the test server, regardless of the
// https host gofalcon targets, so both the lazy OAuth token fetch and the API
// call land on one httptest.Server.
type rewriteTransport struct{ base *url.URL }

func (rt rewriteTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	req.URL.Scheme = rt.base.Scheme
	req.URL.Host = rt.base.Host
	return http.DefaultTransport.RoundTrip(req)
}

// newGraphQLTestClient wires a gofalcon client to an httptest.Server that stubs
// the oauth2 token endpoint and the identity-protection GraphQL endpoint. The
// handler returns respStatus/respBody and records the raw request body sent.
func newGraphQLTestClient(t *testing.T, respStatus int, respBody string, gotBody *string) *client.CrowdStrikeAPISpecification {
	t.Helper()

	mux := http.NewServeMux()
	mux.HandleFunc("/oauth2/token", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"access_token":"tok","token_type":"bearer","expires_in":1799}`))
	})
	mux.HandleFunc("/identity-protection/combined/graphql/v1", func(w http.ResponseWriter, r *http.Request) {
		b, _ := io.ReadAll(r.Body)
		if gotBody != nil {
			*gotBody = string(b)
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(respStatus)
		_, _ = w.Write([]byte(respBody))
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

func TestGraphQL_SuccessReturnsParsedBody(t *testing.T) {
	var gotBody string
	respBody := `{"data":{"entities":{"nodes":[{"entityId":"e1","primaryDisplayName":"Admin"}]}}}`
	c := newGraphQLTestClient(t, http.StatusOK, respBody, &gotBody)

	query := `query { entities(entityIds: ["e1"]) { nodes { entityId } } }`
	out, apiErr := GraphQL(context.Background(), c, query)
	if apiErr != nil {
		t.Fatalf("GraphQL returned error: %v", apiErr)
	}

	// The typed OK type discards the body; this proves the raw reader captured it.
	data, ok := out["data"].(map[string]any)
	if !ok {
		t.Fatalf("missing data in response: %#v", out)
	}
	nodes := data["entities"].(map[string]any)["nodes"].([]any)
	if len(nodes) != 1 || nodes[0].(map[string]any)["entityId"] != "e1" {
		t.Fatalf("unexpected nodes: %#v", nodes)
	}

	// The query must be sent as the "query" field of the JSON body.
	var sent map[string]any
	if err := json.Unmarshal([]byte(gotBody), &sent); err != nil {
		t.Fatalf("request body not JSON: %v (%s)", err, gotBody)
	}
	if sent["query"] != query {
		t.Fatalf("query not sent verbatim: %q", sent["query"])
	}
}

func TestGraphQL_ForbiddenAttachesScopes(t *testing.T) {
	c := newGraphQLTestClient(t, http.StatusForbidden, `{"errors":[{"message":"access denied"}]}`, nil)

	_, apiErr := GraphQL(context.Background(), c, "query {}", Scope{Name: "Identity Protection Entities", Read: true})
	if apiErr == nil {
		t.Fatal("expected error on 403")
	}
	if apiErr.StatusCode != 403 {
		t.Fatalf("StatusCode = %d, want 403", apiErr.StatusCode)
	}
	if len(apiErr.RequiredScopes) == 0 {
		t.Fatalf("403 should attach required scopes, got none")
	}
}
