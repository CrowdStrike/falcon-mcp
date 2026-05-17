---
title: Documentation Guide
description: Architecture and maintenance guide for the Falcon MCP documentation.
---

## Overview

This repository is the single source of truth for Falcon MCP documentation. The `docs/` directory contains Markdown and MDX content files with [Starlight](https://starlight.astro.build/)-compatible frontmatter. An external Astro/Starlight site clones this repository and consumes `docs/` directly to build the published documentation.

## Directory Structure

```text
docs/
  getting-started/         # Hand-authored: installation, credentials, config, quickstart
  usage/                   # Hand-authored: CLI, transports, editor integration, flight control
  modules/                 # AUTO-GENERATED: one page per Python module + overview
  deployment/              # Hand-authored: Docker, Amazon Bedrock, Google Cloud
  development/             # Hand-authored: contributing, module dev, resource dev, testing, this guide
  examples/                # Hand-authored: basic usage, MCP config
  changelog.md             # AUTO-GENERATED: copied from root CHANGELOG.md
```

Governance files (`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`) live in `.github/`, not in `docs/`.

:::caution
Auto-generated files are overwritten on every build. Do not edit them by hand — your changes will be lost.
:::

## Frontmatter

All content files require Starlight-compatible frontmatter:

```yaml
---
title: Page Title
description: A short description of the page.
sidebar:
  order: 1  # Optional — controls sidebar ordering
---
```

## Auto-Generated Content

### Module Pages

The script `scripts/generate_module_docs.py` introspects the Python source in `falcon_mcp/modules/` and produces one page per module under `docs/modules/`, each containing:

- Title and description (derived from the module file's docstring)
- API scopes (derived from operation names found in source code)
- Tools with docstrings, per-tool scopes, annotations (read-only / mutating / destructive), and example prompts
- Resources with URIs and descriptions

### Module Overview Page

A summary table (`docs/modules/overview.md`) listing all modules with their API scopes and descriptions.

### Changelog

The root `CHANGELOG.md` is copied with Starlight frontmatter prepended. This happens in `scripts/build_docs.sh`.

### How Titles and Descriptions Are Derived

The generator reads each module file's docstring:

- **Title**: Extracted from the first line by stripping the `module for Falcon MCP Server.` suffix
- **Description**: Extracted from the second paragraph's first sentence, stripping the common `This module provides tools for ...` prefix

To override either, add an entry to `MODULE_METADATA` in `scripts/generate_module_docs.py`.

## Adding a New Module to Docs

Nothing is needed. The generator uses `pkgutil.iter_modules()` to discover all Python modules in `falcon_mcp/modules/` automatically. Any new module file is picked up on the next build.

If you need a custom title, slug, or description, add an entry to `MODULE_METADATA` in `scripts/generate_module_docs.py`:

```python
MODULE_METADATA: dict[str, dict[str, Any]] = {
    "mymodule": {
        "title": "My Custom Title",      # optional
        "slug": "my-module",             # optional (defaults to module key)
        "description": "Custom desc.",   # optional (defaults to docstring-derived)
    },
}
```

To add example prompts for a tool, add entries to `TOOL_EXAMPLES`:

```python
TOOL_EXAMPLES: dict[str, list[str]] = {
    "falcon_my_tool": [
        "Example prompt for the tool",
    ],
}
```

## Adding or Editing Content Pages

Content pages live under `docs/`. Each `.md` or `.mdx` file needs Starlight frontmatter (see above). The external site handles sidebar configuration. Use the `sidebar.order` frontmatter field to control page ordering within each section.

The `modules/` directory is auto-generated; pages there don't need manual creation.

## Local Workflow

Generate module docs, copy the changelog, and lint all markdown:

```bash
bash scripts/build_docs.sh
```

This runs:

1. `uv run python scripts/generate_module_docs.py` — regenerates `docs/modules/`
2. Copies `CHANGELOG.md` with frontmatter to `docs/changelog.md`
3. Runs `markdownlint` on all files under `docs/`

You can also run the generation script directly:

```bash
uv run python scripts/generate_module_docs.py
```

## CI Freshness Check

The `.github/workflows/docs-check.yml` workflow ensures module documentation stays in sync with the code. On pull requests that touch `falcon_mcp/`, `scripts/generate_module_docs.py`, or `docs/`, the workflow:

1. Runs `uv run python scripts/generate_module_docs.py`
2. Checks `git diff --exit-code docs/modules/`

If the committed module docs differ from what the script produces, the check fails. This prevents stale documentation from being merged.

After adding or modifying a module, always regenerate and commit the updated docs:

```bash
uv run python scripts/generate_module_docs.py
git add docs/modules/
```
