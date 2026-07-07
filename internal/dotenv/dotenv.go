// Package dotenv provides a minimal .env file loader, equivalent to the subset
// of python-dotenv's load_dotenv used by falcon-mcp: it reads KEY=VALUE lines
// from a .env file in the current directory and sets them in the environment
// without overriding variables that are already set.
package dotenv

import (
	"bufio"
	"os"
	"strings"
)

// Load reads .env from the current working directory (if present) and sets any
// variables that are not already defined in the environment. Missing files are
// ignored. Parse errors on individual lines are skipped silently, matching
// python-dotenv's lenient behavior.
func Load() {
	loadFile(".env")
}

func loadFile(path string) {
	f, err := os.Open(path)
	if err != nil {
		return
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		line = strings.TrimPrefix(line, "export ")
		key, val, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		key = strings.TrimSpace(key)
		val = strings.TrimSpace(val)
		if key == "" {
			continue
		}
		// Strip surrounding matching quotes.
		val = unquote(val)
		if _, exists := os.LookupEnv(key); !exists {
			_ = os.Setenv(key, val)
		}
	}
}

func unquote(s string) string {
	if len(s) >= 2 {
		if (s[0] == '"' && s[len(s)-1] == '"') || (s[0] == '\'' && s[len(s)-1] == '\'') {
			return s[1 : len(s)-1]
		}
	}
	return s
}
