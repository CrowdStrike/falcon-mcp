package base

// Scope is an API scope an operation requires, declared by the module that
// calls the operation. Read and Write map to the CrowdStrike console
// permission suffixes ":read" and ":write".
type Scope struct {
	// Name is the console permission name (e.g. "Hosts", "host-group").
	Name string
	// Read grants the ":read" permission for Name.
	Read bool
	// Write grants the ":write" permission for Name.
	Write bool
}

// Strings renders the console permission strings for the scope (e.g.
// {"Hosts:read", "Hosts:write"}). It returns nil when neither Read nor Write
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
