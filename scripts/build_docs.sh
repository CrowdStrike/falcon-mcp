#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Step 1: Generate module documentation ==="
cd "$PROJECT_ROOT"
uv run python scripts/generate_module_docs.py

echo "=== Step 2: Copy changelog ==="
{
  echo '<!-- meta:title Changelog -->'
  echo '<!-- meta:description Release history for the Falcon MCP Server. -->'
  echo '<!-- meta:link-base /falcon-mcp/ -->'
  echo ''
  cat CHANGELOG.md
} > docs/changelog.md

echo "=== Step 3: Lint markdown ==="
npx markdownlint-cli2@0.18.0 --fix 'docs/**/*.md' '#docs/changelog.md'

echo "=== Done ==="
