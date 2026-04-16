# Docs Site Guide

## Overview

The Falcon MCP documentation site is built with [Starlight](https://starlight.astro.build/) (an [Astro](https://astro.build/) documentation framework) and deployed to GitHub Pages at [crowdstrike.github.io/falcon-mcp](https://crowdstrike.github.io/falcon-mcp/).

All source files live in the `docs-site/` directory within the main repository.

## Directory Structure

```text
docs-site/
  src/
    content/docs/
      getting-started/         # Hand-authored: installation, credentials, config, quickstart
      usage/                   # Hand-authored: CLI, transports, editor integration, flight control
      modules/                 # AUTO-GENERATED: one page per Python module + overview
      deployment/              # Hand-authored: Docker, Amazon Bedrock, Google Cloud
      development/             # Hand-authored: contributing, module dev, resource dev, testing, docs site
      examples/                # Hand-authored: basic usage, MCP config
      changelog.md             # AUTO-GENERATED: copied from root CHANGELOG.md during build
      index.mdx                # Hand-authored: landing page
    assets/                    # Images (logos, etc.)
    components/                # Custom Astro components (Hero override)
    styles/                    # Custom CSS
  astro.config.mjs             # Starlight config, sidebar definitions
  package.json / pnpm-lock.yaml
```

**Auto-generated files** are overwritten on every build. Do not edit them by hand — your changes will be lost.

## Auto-Generated Content

The script `scripts/generate_module_docs.py` introspects the Python source in `falcon_mcp/modules/` and produces:

### Module Pages (`modules/*.md`)

One page per module, each containing:

- Title and description (derived from the module file's docstring)
- API scopes (derived from operation names found in source code)
- Tools with docstrings, per-tool scopes, annotations (read-only / mutating / destructive), and example prompts
- Resources with URIs and descriptions

### Module Overview Page (`modules/overview.md`)

A summary table listing all modules with their API scopes and descriptions.

### Changelog (`changelog.md`)

The root `CHANGELOG.md` is copied with Starlight frontmatter prepended. This happens in the build script (`scripts/build_docs.sh`) and in the CI workflow.

### How Titles and Descriptions Are Derived

The generator reads each module file's docstring:

- **Title**: Extracted from the first line by stripping the `module for Falcon MCP Server.` suffix
- **Description**: Extracted from the second paragraph's first sentence, stripping the common `This module provides tools for ...` prefix

To override either, add an entry to `MODULE_METADATA` in `scripts/generate_module_docs.py`.

## Adding a New Module to Docs

**Nothing is needed.** The generator uses `pkgutil.iter_modules()` to discover all Python modules in `falcon_mcp/modules/` automatically. Any new module file is picked up on the next build.

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

## Adding or Editing Static Pages

Static pages live under `docs-site/src/content/docs/`. Each `.md` or `.mdx` file needs Starlight frontmatter:

```yaml
---
title: Page Title
description: A short description of the page.
---
```

After creating a new page, add it to the sidebar in `docs-site/astro.config.mjs`:

```js
{
  label: 'Section Name',
  items: [
    { label: 'New Page', slug: 'section/new-page' },
  ],
},
```

The `modules/` section uses `autogenerate: { directory: 'modules' }` — pages there don't need manual sidebar entries.

## Local Development

Generate module docs and start the dev server:

```bash
# Generate module documentation from Python source
uv run python scripts/generate_module_docs.py

# Install docs dependencies and start dev server
cd docs-site
pnpm install
pnpm run dev
```

The dev server runs at `http://localhost:4321/falcon-mcp/` with hot reload.

To run a full production build locally:

```bash
# From the project root
bash scripts/build_docs.sh
```

## CI Deployment

The docs site is deployed automatically by `.github/workflows/docs-deploy.yml`.

**Triggers:**

- Push to `main` when relevant files change (`falcon_mcp/`, `scripts/generate_module_docs.py`, `docs-site/`, `CHANGELOG.md`, or the workflow itself)
- Manual dispatch via `workflow_dispatch`

**Build steps:**

1. Install Python dependencies with `uv sync --all-extras`
2. Generate module docs with `uv run python scripts/generate_module_docs.py`
3. Copy `CHANGELOG.md` with frontmatter into the docs site
4. Install Node.js dependencies with `pnpm install --frozen-lockfile`
5. Build the site with `pnpm run build`
6. Upload the `docs-site/dist/` artifact and deploy to GitHub Pages
