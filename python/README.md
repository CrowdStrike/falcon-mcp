# falcon-mcp (Python)

Installs and runs the CrowdStrike Falcon MCP server binary.

    uvx falcon-mcp --help
    pip install falcon-mcp && falcon-mcp --help

On first run the matching platform binary is downloaded from GitHub releases,
verified against the release `checksums.txt`, and cached under
`~/.falcon-mcp/bin/<version>/`.
