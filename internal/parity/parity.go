// Package parity documents the expected tool/resource inventory per Falcon
// module, ported from the Python implementation's counts. It is the source of
// truth for the parity test that guards against dropped tools during the Go
// rewrite. Counts were extracted from falcon_mcp/modules/*.py (_add_tool calls)
// and falcon_mcp/resources (36 FQL guides total).
package parity

// ExpectedTools maps each module name to the number of tools it registers in
// the Python implementation (excluding the 3 server-level tools).
var ExpectedTools = map[string]int{
	"cases":             8,
	"cloud":             8,
	"correlation_rules": 4,
	"custom_ioa":        9,
	"data_protection":   3,
	"detections":        3,
	"discover":          2,
	"exclusions":        5,
	"firewall":          5,
	"host_groups":       6,
	"hosts":             2,
	"idp":               1,
	"intel":             4,
	"ioc":               3,
	"ngsiem":            1,
	"policies":          7,
	"quarantine":        4,
	"recon":             3,
	"rtr":               11,
	"scheduled_reports": 4,
	"sensor_usage":      1,
	"serverless":        1,
	"shield":            16,
	"spotlight":         1,
}

// TotalModuleTools is the sum of ExpectedTools (module tools only).
const TotalModuleTools = 112

// ServerLevelTools is the count of tools registered by the server itself
// (falcon_list_enabled_modules, falcon_check_connectivity, falcon_list_modules).
const ServerLevelTools = 3

// TotalTools is the full tool inventory in non-dynamic mode.
const TotalTools = TotalModuleTools + ServerLevelTools // 115

// TotalResources is the number of FQL-guide resources across all modules.
const TotalResources = 36
