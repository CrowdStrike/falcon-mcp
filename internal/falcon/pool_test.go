package falcon

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"
)

func testPool(t *testing.T, maxSize int, ttl time.Duration) (*Pool, *fakeClock) {
	t.Helper()
	clk := &fakeClock{t: time.Unix(1_700_000_000, 0)}
	p := NewPool(PoolOptions{MaxSize: maxSize, TTL: ttl, Salt: []byte("test-salt")})
	p.now = clk.now
	return p, clk
}

type fakeClock struct {
	mu sync.Mutex
	t  time.Time
}

func (c *fakeClock) now() time.Time {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.t
}
func (c *fakeClock) advance(d time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.t = c.t.Add(d)
}

func creds(id string) Credentials {
	return Credentials{ClientID: id, ClientSecret: "secret-" + id, BaseURL: "https://api.us-2.crowdstrike.com"}
}

func TestPoolKeyIsSecretFree(t *testing.T) {
	p, _ := testPool(t, 10, time.Minute)
	k := p.key(creds("tenant-a"))
	if k == "" {
		t.Fatal("empty key")
	}
	// The key must not contain the raw secret.
	if containsSub(k, "secret-tenant-a") || containsSub(k, "tenant-a") {
		t.Errorf("key leaks credential material: %s", k)
	}
	// Same creds → same key; different creds → different key.
	if p.key(creds("tenant-a")) != k {
		t.Error("key not stable for same credentials")
	}
	if p.key(creds("tenant-b")) == k {
		t.Error("distinct credentials collided")
	}
}

func TestPoolReuseAndIsolation(t *testing.T) {
	p, _ := testPool(t, 10, time.Minute)
	ctx := context.Background()

	a1, err := p.Get(ctx, creds("a"))
	if err != nil {
		t.Fatalf("Get a: %v", err)
	}
	a2, err := p.Get(ctx, creds("a"))
	if err != nil {
		t.Fatalf("Get a again: %v", err)
	}
	if a1 != a2 {
		t.Error("same credentials should return the cached client instance")
	}
	b1, err := p.Get(ctx, creds("b"))
	if err != nil {
		t.Fatalf("Get b: %v", err)
	}
	if a1 == b1 {
		t.Error("different tenants must get isolated clients")
	}
	if p.Len() != 2 {
		t.Errorf("pool size = %d, want 2", p.Len())
	}
}

func TestPoolTTLExpiry(t *testing.T) {
	p, clk := testPool(t, 10, time.Minute)
	ctx := context.Background()

	first, _ := p.Get(ctx, creds("a"))
	clk.advance(2 * time.Minute) // exceed TTL
	second, _ := p.Get(ctx, creds("a"))
	if first == second {
		t.Error("expired entry should have been rebuilt")
	}
}

func TestPoolLRUEviction(t *testing.T) {
	p, _ := testPool(t, 2, time.Hour)
	ctx := context.Background()

	p.Get(ctx, creds("a"))
	p.Get(ctx, creds("b"))
	p.Get(ctx, creds("a")) // touch a → b is now LRU
	p.Get(ctx, creds("c")) // evicts b
	if p.Len() != 2 {
		t.Errorf("pool size = %d, want 2 (maxSize)", p.Len())
	}
	// b should have been evicted; fetching it rebuilds a new client.
	if _, ok := p.entries[p.key(creds("b"))]; ok {
		t.Error("expected b to be evicted as LRU")
	}
	if _, ok := p.entries[p.key(creds("a"))]; !ok {
		t.Error("a should still be cached (recently used)")
	}
}

// TestPoolConcurrent exercises many goroutines fetching a mix of tenants,
// asserting no races and a bounded cache (run with -race).
func TestPoolConcurrent(t *testing.T) {
	p, _ := testPool(t, 8, time.Hour)
	ctx := context.Background()

	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			// 16 distinct tenants across 100 goroutines.
			if _, err := p.Get(ctx, creds(fmt.Sprintf("tenant-%d", i%16))); err != nil {
				t.Errorf("concurrent Get: %v", err)
			}
		}(i)
	}
	wg.Wait()
	if p.Len() > 8 {
		t.Errorf("pool exceeded maxSize: %d", p.Len())
	}
}

func containsSub(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return true
		}
	}
	return false
}
