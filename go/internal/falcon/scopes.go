package falcon

// Scope is an API scope an operation requires, declared by the module that
// calls the operation. It is passed to APIError so a 403 response can be
// enriched with the exact console permissions the caller must grant.
type Scope struct {
	Name  string // e.g. "Hosts".
	Read  bool
	Write bool
}

// Strings renders the console permission strings for the scope, e.g.
// {"Hosts:read", "Hosts:write"}. It returns nil when neither Read nor Write
// is set.
func (s Scope) Strings() []string {
	var out []string
	if s.Read {
		out = append(out, s.Name+":read")
	}
	if s.Write {
		out = append(out, s.Name+":write")
	}
	return out
}
