// Command genfqlguide normalizes an FQL guide Markdown file in place: it trims
// trailing whitespace from every line and the surrounding blank lines of the
// file, leaving a single trailing newline. It is invoked from //go:generate
// directives so the file that //go:embed embeds carries no incidental
// whitespace. The operation is idempotent — running it on an already-normalized
// file leaves it byte-for-byte unchanged.
package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
)

func main() {
	log.SetFlags(0)

	in := flag.String("in", "", "path to the Markdown guide to normalize in place")
	flag.Parse()

	if *in == "" {
		log.Fatal("genfqlguide: -in is required")
	}

	if err := normalize(*in); err != nil {
		log.Fatalf("genfqlguide: %v", err)
	}
}

func normalize(path string) error {
	raw, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("read %s: %w", path, err)
	}

	// A single trailing newline keeps the file POSIX-clean and editor-friendly.
	guide := normalizeGuide(string(raw)) + "\n"

	if err := os.WriteFile(path, []byte(guide), 0o644); err != nil {
		return fmt.Errorf("write %s: %w", path, err)
	}
	return nil
}

func normalizeGuide(raw string) string {
	lines := strings.Split(raw, "\n")
	for i, line := range lines {
		lines[i] = strings.TrimSpace(line)
	}
	return strings.TrimSpace(strings.Join(lines, "\n"))
}
