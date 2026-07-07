package falcon

import (
	"container/list"
	"context"
	"crypto/hmac"
	crand "crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"sync"
	"time"
)

// Pool is a bounded, TTL-expiring cache of FalconClients keyed by a salted hash
// of their credentials. It backs multi-tenant mode: each incoming request's
// credentials map to a cached client (built once, reused across requests) with
// per-tenant OAuth token isolation. Eviction is LRU with idle-TTL expiry so a
// burst of distinct tenants cannot grow memory without bound.
//
// Pool is safe for concurrent use.
type Pool struct {
	mu        sync.Mutex
	entries   map[string]*list.Element // hash → element in lru
	lru       *list.List               // front = most recently used
	maxSize   int
	ttl       time.Duration
	salt      []byte
	debug     bool
	uaComment string
	now       func() time.Time // injectable clock for tests
}

type poolEntry struct {
	key      string
	client   *FalconClient
	lastUsed time.Time
}

// PoolOptions configures a Pool.
type PoolOptions struct {
	// MaxSize is the maximum number of cached clients (default 256).
	MaxSize int
	// TTL is the idle expiry for a cached client (default 30m).
	TTL time.Duration
	// Salt is mixed into credential hashes so cache keys never equal raw
	// secrets. A random salt is generated if empty.
	Salt []byte
	// Debug and UserAgentComment are passed to each built client.
	Debug            bool
	UserAgentComment string
}

// NewPool creates a credential-keyed client pool.
func NewPool(opts PoolOptions) *Pool {
	if opts.MaxSize <= 0 {
		opts.MaxSize = 256
	}
	if opts.TTL <= 0 {
		opts.TTL = 30 * time.Minute
	}
	salt := opts.Salt
	if len(salt) == 0 {
		// A process-lifetime random salt. Not persisted — cache keys need only
		// be stable within one process.
		salt = randomSalt()
	}
	return &Pool{
		entries:   map[string]*list.Element{},
		lru:       list.New(),
		maxSize:   opts.MaxSize,
		ttl:       opts.TTL,
		salt:      salt,
		debug:     opts.Debug,
		uaComment: opts.UserAgentComment,
		now:       time.Now,
	}
}

// key derives a stable, secret-free cache key from credentials using HMAC-SHA256
// with the pool salt. The client secret is included so distinct secrets for the
// same client ID never collide.
func (p *Pool) key(creds Credentials) string {
	mac := hmac.New(sha256.New, p.salt)
	// Length-prefix each field to avoid ambiguity between concatenations.
	for _, f := range []string{creds.ClientID, creds.ClientSecret, creds.MemberCID, creds.BaseURL} {
		_, _ = mac.Write([]byte{byte(len(f) >> 8), byte(len(f))})
		_, _ = mac.Write([]byte(f))
	}
	return hex.EncodeToString(mac.Sum(nil))
}

// Get returns a FalconClient for the given credentials, building and caching one
// on a miss. Expired entries are rebuilt. The returned client is safe for
// concurrent use.
func (p *Pool) Get(ctx context.Context, creds Credentials) (*FalconClient, error) {
	k := p.key(creds)

	p.mu.Lock()
	if el, ok := p.entries[k]; ok {
		ent := el.Value.(*poolEntry)
		if p.now().Sub(ent.lastUsed) < p.ttl {
			ent.lastUsed = p.now()
			p.lru.MoveToFront(el)
			p.mu.Unlock()
			return ent.client, nil
		}
		// Expired: drop and rebuild below.
		p.lru.Remove(el)
		delete(p.entries, k)
	}
	p.mu.Unlock()

	// Build outside the lock (NewClient may do cloud autodiscovery I/O).
	client, err := NewClient(ctx, creds, p.debug, p.uaComment)
	if err != nil {
		return nil, err
	}

	p.mu.Lock()
	defer p.mu.Unlock()
	// Another goroutine may have inserted concurrently; prefer the existing one.
	if el, ok := p.entries[k]; ok {
		ent := el.Value.(*poolEntry)
		ent.lastUsed = p.now()
		p.lru.MoveToFront(el)
		return ent.client, nil
	}
	ent := &poolEntry{key: k, client: client, lastUsed: p.now()}
	el := p.lru.PushFront(ent)
	p.entries[k] = el
	p.evictLocked()
	return client, nil
}

// evictLocked removes least-recently-used entries beyond maxSize. Caller holds mu.
func (p *Pool) evictLocked() {
	for p.lru.Len() > p.maxSize {
		back := p.lru.Back()
		if back == nil {
			return
		}
		ent := back.Value.(*poolEntry)
		p.lru.Remove(back)
		delete(p.entries, ent.key)
	}
}

// Len returns the current number of cached clients.
func (p *Pool) Len() int {
	p.mu.Lock()
	defer p.mu.Unlock()
	return p.lru.Len()
}

// randomSalt returns 32 random bytes for HMAC keying.
func randomSalt() []byte {
	b := make([]byte, 32)
	if _, err := crand.Read(b); err != nil {
		// crypto/rand failure is catastrophic; fall back to a fixed salt so the
		// process still starts (keys stay secret-free either way).
		return []byte("falcon-mcp-static-pool-salt-fallback")
	}
	return b
}
