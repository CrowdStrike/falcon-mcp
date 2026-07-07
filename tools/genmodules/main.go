// Command genmodules generates the falcon-mcp module factory aggregator. It
// scans the tool-module packages under internal/modules, verifies each exports
// a package-level `Factory` var, and writes a Go source file that collects those
// factories into one slice for the server to build.
//
// It exists so that adding a tool module requires only creating its package and
// exporting a Factory var: no hand-edited import list, no init-time
// registration. The generator is invoked from a //go:generate directive in the
// internal/mcpserver package. Its output is deterministic (modules sorted by
// directory name) and idempotent — re-running with no module changes rewrites
// the same bytes.
package main

import (
	"bytes"
	"flag"
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"log"
	"os"
	"path"
	"path/filepath"
	"sort"
	"strings"
	"text/template"
)

// modulePath is the Go module path of this repository, used to build the
// import paths of the discovered module packages.
const modulePath = "github.com/crowdstrike/falcon-mcp"

// excluded names the non-module packages under internal/modules so the scan
// skips them. These provide the module contract (base, registry) or a distinct
// meta layer (dynamic) rather than a tool module with a Factory.
var excluded = map[string]bool{
	"base":     true,
	"registry": true,
	"dynamic":  true,
}

// module is one discovered tool-module package: its directory name (used for
// deterministic ordering and the import path) and its real package identifier
// (used to reference Factory and to decide whether an import alias is needed).
type module struct {
	Dir     string
	Package string
}

// ImportPath is the full Go import path of the module package.
func (m module) ImportPath() string {
	return path.Join(modulePath, "internal", "modules", m.Dir)
}

// NeedsAlias reports whether the import must be aliased because the package
// identifier differs from the import-path basename (e.g. host_groups contains
// package hostgroups).
func (m module) NeedsAlias() bool {
	return m.Package != path.Base(m.ImportPath())
}

func main() {
	log.SetFlags(0)

	out := flag.String("out", "factories_gen.go", "output file for the generated aggregator")
	dir := flag.String("dir", "../modules", "path to the modules root, relative to the invocation directory")
	pkg := flag.String("pkg", "mcpserver", "package name for the generated file")
	flag.Parse()

	modules, err := discover(*dir)
	if err != nil {
		log.Fatalf("genmodules: %v", err)
	}

	src, err := render(*pkg, modules)
	if err != nil {
		log.Fatalf("genmodules: %v", err)
	}

	// The generated file is committed source, so it must be world-readable.
	if err := os.WriteFile(*out, src, 0o644); err != nil { //nolint:gosec // generated source is not sensitive
		log.Fatalf("genmodules: write %s: %v", *out, err)
	}
}

// discover scans root for tool-module packages, skipping the excluded set. It
// requires each remaining package to export a package-level Factory var and
// fails loudly, naming every offender, if any does not — so a module that omits
// the contract is caught at generate time rather than silently dropped.
func discover(root string) ([]module, error) {
	entries, err := os.ReadDir(root)
	if err != nil {
		return nil, fmt.Errorf("read modules dir %s: %w", root, err)
	}

	var modules []module
	var offenders []string
	for _, e := range entries {
		if !e.IsDir() || excluded[e.Name()] {
			continue
		}

		pkgName, hasFactory, err := inspect(filepath.Join(root, e.Name()))
		if err != nil {
			return nil, err
		}
		if !hasFactory {
			offenders = append(offenders, e.Name())
			continue
		}
		modules = append(modules, module{Dir: e.Name(), Package: pkgName})
	}

	if len(offenders) > 0 {
		sort.Strings(offenders)
		return nil, fmt.Errorf("module packages missing an exported Factory var: %s "+
			"(each module must declare `var Factory registry.Factory`)", strings.Join(offenders, ", "))
	}

	sort.Slice(modules, func(i, j int) bool { return modules[i].Dir < modules[j].Dir })
	return modules, nil
}

// inspect parses the Go source files in dir (ignoring test files) and reports
// its package identifier and whether it declares a package-level `Factory` var.
func inspect(dir string) (pkgName string, hasFactory bool, err error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return "", false, fmt.Errorf("read %s: %w", dir, err)
	}

	fset := token.NewFileSet()
	seen := false
	for _, e := range entries {
		name := e.Name()
		if e.IsDir() || !strings.HasSuffix(name, ".go") || strings.HasSuffix(name, "_test.go") {
			continue
		}

		file, err := parser.ParseFile(fset, filepath.Join(dir, name), nil, 0)
		if err != nil {
			return "", false, fmt.Errorf("parse %s: %w", name, err)
		}
		if seen && file.Name.Name != pkgName {
			return "", false, fmt.Errorf("multiple packages in %s: %s and %s", dir, pkgName, file.Name.Name)
		}
		pkgName = file.Name.Name
		seen = true
		if declaresFactory(file) {
			hasFactory = true
		}
	}

	if !seen {
		return "", false, fmt.Errorf("no Go source files in %s", dir)
	}
	return pkgName, hasFactory, nil
}

// declaresFactory reports whether file has a package-level var named Factory.
func declaresFactory(file *ast.File) bool {
	for _, decl := range file.Decls {
		gen, ok := decl.(*ast.GenDecl)
		if !ok || gen.Tok != token.VAR {
			continue
		}
		for _, spec := range gen.Specs {
			vs, ok := spec.(*ast.ValueSpec)
			if !ok {
				continue
			}
			for _, name := range vs.Names {
				if name.Name == "Factory" {
					return true
				}
			}
		}
	}
	return false
}

// aggregatorTemplate renders the generated file. Imports are aliased only when
// the package identifier differs from the import-path basename; format.Source
// then applies gofmt so the committed file stays clean for the CI diff check.
var aggregatorTemplate = template.Must(template.New("aggregator").Parse(`// Code generated by tools/genmodules; DO NOT EDIT.

package {{ .Package }}

import (
{{- range .Modules }}
	{{ if .NeedsAlias }}{{ .Package }} {{ end }}"{{ .ImportPath }}"
{{- end }}
	"{{ .ModulePath }}/internal/modules/registry"
)

// moduleFactories returns every discovered module's factory, ordered by package
// directory name for deterministic module ordering.
func moduleFactories() []registry.Factory {
	return []registry.Factory{
{{- range .Modules }}
		{{ .Package }}.Factory,
{{- end }}
	}
}
`))

// render executes the template for pkg and modules and gofmt-formats the result.
func render(pkg string, modules []module) ([]byte, error) {
	var buf bytes.Buffer
	data := struct {
		Package    string
		ModulePath string
		Modules    []module
	}{Package: pkg, ModulePath: modulePath, Modules: modules}

	if err := aggregatorTemplate.Execute(&buf, data); err != nil {
		return nil, fmt.Errorf("render template: %w", err)
	}

	src, err := format.Source(buf.Bytes())
	if err != nil {
		return nil, fmt.Errorf("format generated source: %w", err)
	}
	return src, nil
}
