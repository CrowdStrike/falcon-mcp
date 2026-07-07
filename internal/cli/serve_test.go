package cli

import (
	"context"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestServeHTTPGracefulShutdown(t *testing.T) {
	h := http.NewServeMux()
	ctx, cancel := context.WithCancel(context.Background())
	errc := make(chan error, 1)
	go func() { errc <- serveHTTP(ctx, "127.0.0.1:0", h) }() // :0 = OS-assigned free port, no collisions

	time.Sleep(50 * time.Millisecond)
	cancel()

	select {
	case err := <-errc:
		if err != nil {
			t.Fatalf("serveHTTP returned error on graceful shutdown: %v", err)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("serveHTTP did not return after ctx cancel")
	}
}

func TestServeHTTPInvalidAddr(t *testing.T) {
	h := http.NewServeMux()
	// An unparseable address fails to bind and surfaces through the error channel
	// before ctx is cancelled.
	if err := serveHTTP(t.Context(), "bad:addr:99", h); err == nil {
		t.Fatal("expected error for invalid listen address")
	}
}

func TestWithAPIKey(t *testing.T) {
	t.Parallel()
	const key = "s3cret"

	// next records whether the wrapped handler was reached and returns 200.
	newNext := func(reached *bool) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
			*reached = true
			w.WriteHeader(http.StatusOK)
		})
	}

	tests := []struct {
		name       string
		key        string // key passed to withAPIKey
		header     string // x-api-key sent by the client
		setHeader  bool
		wantStatus int
		wantNext   bool // whether next should be reached
	}{
		{name: "no auth configured passes through", key: "", setHeader: false, wantStatus: http.StatusOK, wantNext: true},
		{name: "missing header rejected", key: key, setHeader: false, wantStatus: http.StatusUnauthorized, wantNext: false},
		{name: "wrong key rejected", key: key, header: "nope", setHeader: true, wantStatus: http.StatusUnauthorized, wantNext: false},
		{name: "empty header rejected", key: key, header: "", setHeader: true, wantStatus: http.StatusUnauthorized, wantNext: false},
		{name: "correct key passes through", key: key, header: key, setHeader: true, wantStatus: http.StatusOK, wantNext: true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			var reached bool
			h := withAPIKey(tt.key, newNext(&reached))

			req := httptest.NewRequest(http.MethodGet, "/", nil)
			if tt.setHeader {
				req.Header.Set("x-api-key", tt.header)
			}
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)

			if rec.Code != tt.wantStatus {
				t.Errorf("status = %d, want %d", rec.Code, tt.wantStatus)
			}
			if reached != tt.wantNext {
				t.Errorf("next reached = %v, want %v", reached, tt.wantNext)
			}
			if tt.wantStatus == http.StatusUnauthorized {
				if ct := rec.Header().Get("Content-Type"); ct != "application/json" {
					t.Errorf("Content-Type = %q, want application/json", ct)
				}
				body, _ := io.ReadAll(rec.Body)
				if got := string(body); got != `{"error":"Unauthorized"}` {
					t.Errorf("body = %q, want unauthorized JSON", got)
				}
			}
		})
	}
}
