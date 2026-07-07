//go:build ignore

// gen_docs generates per-module documentation under docs/modules-go/ from the
// live toolset registry: each module's tools, descriptions, and annotations. Run
// with `go run scripts/gen_docs.go`. CI compares the output against the committed
// docs to guard against undocumented tool changes (the Go analogue of the Python
// docs-check).
package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"github.com/crowdstrike/falcon-mcp-go/internal/falcon"
	"github.com/crowdstrike/falcon-mcp-go/pkg/toolsets"

	_ "github.com/crowdstrike/falcon-mcp-go/pkg/toolsets/all"
)

func main() {
	outDir := "docs/modules-go"
	if len(os.Args) > 1 {
		outDir = os.Args[1]
	}
	if err := run(outDir); err != nil {
		fmt.Fprintln(os.Stderr, "gen_docs:", err)
		os.Exit(1)
	}
}

func run(outDir string) error {
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		return err
	}
	// A dummy client with a host override avoids network I/O during doc gen.
	fc, err := falcon.NewClient(context.Background(), falcon.Credentials{
		ClientID: "doc", ClientSecret: "doc", BaseURL: "https://api.us-2.crowdstrike.com",
	}, false, "")
	if err != nil {
		return err
	}
	ctx := context.Background()

	for _, ts := range toolsets.Toolsets(nil) {
		name := ts.GetName()

		// Register this module's tools into a scratch server and list them via
		// an in-process client to read the generated descriptions + annotations.
		scratch := mcp.NewServer(&mcp.Implementation{Name: "doc-scratch", Version: "0"}, nil)
		for _, st := range ts.GetTools(fc) {
			st.Register(scratch, fc)
		}
		clientT, serverT := mcp.NewInMemoryTransports()
		if _, err := scratch.Connect(ctx, serverT, nil); err != nil {
			return err
		}
		cs, err := mcp.NewClient(&mcp.Implementation{Name: "doc-client", Version: "0"}, nil).Connect(ctx, clientT, nil)
		if err != nil {
			return err
		}
		listed, err := cs.ListTools(ctx, nil)
		if err != nil {
			return err
		}
		tools := listed.Tools
		sort.Slice(tools, func(i, j int) bool { return tools[i].Name < tools[j].Name })

		var b strings.Builder
		fmt.Fprintf(&b, "# %s\n\n%s\n\n", titleCase(name), ts.GetDescription())
		fmt.Fprintf(&b, "## Tools\n\n")
		for _, t := range tools {
			fmt.Fprintf(&b, "### `%s`\n\n", t.Name)
			if t.Annotations != nil {
				kind := "read-only"
				if !t.Annotations.ReadOnlyHint {
					kind = "mutating"
					if t.Annotations.DestructiveHint != nil && *t.Annotations.DestructiveHint {
						kind = "destructive"
					}
				}
				fmt.Fprintf(&b, "**Type:** %s\n\n", kind)
			}
			if t.Description != "" {
				fmt.Fprintf(&b, "%s\n\n", t.Description)
			}
		}

		if res := ts.GetResources(); len(res) > 0 {
			fmt.Fprintf(&b, "## Resources\n\n")
			for _, r := range res {
				fmt.Fprintf(&b, "- `%s` — %s\n", r.Resource.URI, r.Resource.Description)
			}
			b.WriteString("\n")
		}

		_ = cs.Close()
		if err := os.WriteFile(filepath.Join(outDir, name+".md"), []byte(b.String()), 0o644); err != nil {
			return err
		}
	}
	return nil
}

func titleCase(s string) string {
	parts := strings.Split(s, "_")
	for i, p := range parts {
		if p != "" {
			parts[i] = strings.ToUpper(p[:1]) + p[1:]
		}
	}
	return strings.Join(parts, " ")
}
