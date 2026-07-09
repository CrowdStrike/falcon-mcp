package hosts

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"net/url"
	"sync"
	"testing"

	"github.com/crowdstrike/gofalcon/falcon"
	"github.com/crowdstrike/gofalcon/falcon/client"
	"golang.org/x/oauth2"
)

var errUnexpectedResult = errors.New("unexpected result from concurrent searchHosts")

// newConcurrentTestClient builds a gofalcon client whose stub endpoints are
// safe for concurrent use (the handlers write only response bodies, no shared
// mutable state), so the test isolates races to the client itself.
func newConcurrentTestClient(t *testing.T, queryIDs, detailsJSON string) *client.CrowdStrikeAPISpecification {
	t.Helper()
	mux := http.NewServeMux()
	mux.HandleFunc("/oauth2/token", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"access_token":"tok","token_type":"bearer","expires_in":1799}`))
	})
	mux.HandleFunc("/devices/queries/devices/v1", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"resources":` + queryIDs + `,"errors":[]}`))
	})
	mux.HandleFunc("/devices/entities/devices/v2", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(detailsJSON))
	})

	srv := httptest.NewServer(mux)
	t.Cleanup(srv.Close)

	base, _ := url.Parse(srv.URL)
	ctx := context.WithValue(context.Background(), oauth2.HTTPClient, &http.Client{Transport: rewriteTransport{base: base}})
	c, err := falcon.NewClient(&falcon.ApiConfig{
		ClientId:     "id",
		ClientSecret: "secret",
		Context:      ctx,
		HostOverride: base.Host,
	})
	if err != nil {
		t.Fatalf("build concurrent test client: %v", err)
	}
	return c
}

// TestConcurrency_SharedClientUnderRace proves the gofalcon client is safe to
// share across concurrent tool calls (R6). The streamable-http transport serves
// requests in parallel, and every handler holds only an immutable client
// reference, so a single shared client must tolerate concurrent use. Run under
// `go test -race` to detect data races on the shared client and its transport.
func TestConcurrency_SharedClientUnderRace(t *testing.T) {
	c := newConcurrentTestClient(t, `["a","b"]`, detailsResponse("a", "b"))
	h := &handlers{c: c}

	const goroutines = 32
	var wg sync.WaitGroup
	wg.Add(goroutines)
	errs := make(chan error, goroutines)
	for range goroutines {
		go func() {
			defer wg.Done()
			out, err := h.searchHosts(context.Background(), searchHostsInput{Filter: "x", Sort: "hostname.asc"})
			if err != nil {
				errs <- err
				return
			}
			list := asList(t, out)
			if len(list) != 2 || list[0]["device_id"] != "a" {
				errs <- errUnexpectedResult
			}
		}()
	}
	wg.Wait()
	close(errs)
	for err := range errs {
		t.Fatalf("concurrent searchHosts failed: %v", err)
	}
}
