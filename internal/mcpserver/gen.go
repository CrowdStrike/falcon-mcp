// Package mcpserver assembles the falcon-mcp MCP server. This file carries the
// generate directive for the module factory aggregator; the generated output
// lives in factories_gen.go.
package mcpserver

//go:generate go run github.com/crowdstrike/falcon-mcp/tools/genmodules -out factories_gen.go
