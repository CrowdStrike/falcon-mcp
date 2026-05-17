<!-- meta:title Content Tag Guide -->
<!-- meta:description Reference for HTML comment tags used in documentation files. -->
<!-- meta:section development -->
<!-- meta:link-base /falcon-mcp/ -->

# CrowdStrike Developer Center — Content Tag Guide

This guide documents all HTML comment tags used in GitHub Wiki content that feeds the CrowdStrike Developer Center documentation site. These tags are invisible when rendered on GitHub but are consumed by conversion scripts to produce MDX output with Starlight components and site-specific enhancements.

---

## Page Metadata Tags

These tags appear at the top of every page and provide information used to generate MDX frontmatter and site structure.

### `<!-- meta:title {value} -->`

Defines the page title used in the MDX frontmatter `title:` field.

```markdown
<!-- meta:title Installation -->
```

### `<!-- meta:description {value} -->`

Defines the page description used in the MDX frontmatter `description:` field.

```markdown
<!-- meta:description Install the Falcon MCP Server using uv or pip. -->
```

### `<!-- meta:section {directory} -->`

Declares which site subdirectory this page belongs to. Used by the MD→MDX script to resolve flat wiki links (like `(Credentials)`) to full site paths (like `/falcon-mcp/getting-started/credentials/`).

**Values:** `getting-started`, `modules`, `usage`, `deployment`, `development`, `examples`

```markdown
<!-- meta:section modules -->
```

### `<!-- meta:link-base {prefix} -->`

Defines the URL prefix prepended to internal links during MD→MDX conversion. Most pages use `/falcon-mcp/`. The modules overview page uses `/` because its links are root-relative on the site.

```markdown
<!-- meta:link-base /falcon-mcp/ -->
```

---

## Frontmatter Tags

These tags store site-specific rendering configuration that gets injected into MDX YAML frontmatter.

### `<!-- frontmatter:sidebar order:{n} -->`

Controls the page's position in the Starlight sidebar navigation. Lower numbers appear first.

```markdown
<!-- frontmatter:sidebar order:10 -->
```

### `<!-- frontmatter:index sidebar hidden:true -->`

Used only in `Home.md`. Tells the converter that the generated `index.mdx` file should have `sidebar: hidden: true` (hidden from navigation).

```markdown
<!-- frontmatter:index sidebar hidden:true -->
```

### `<!-- frontmatter:overview sidebar label:"Overview" -->`

Used only in `Home.md`. Tells the converter that the generated `overview.mdx` file should have `sidebar: label: Overview`.

```markdown
<!-- frontmatter:overview sidebar label:"Overview" -->
```

---

## Layout Tags

These tags add visual structure and imagery to the MDX site that doesn't appear on the GitHub Wiki. The content between or near these tags renders normally on the wiki — the tags only affect the documentation site.

### `<!-- layout:split-section image:"{path}" -->` ... `<!-- /layout:split-section -->`

Creates a two-column layout on the site: text on the left, image on the right. The content between the opening and closing tags becomes the left column. The image only appears on the site.

**Remove both tags** if you want to eliminate the column layout and image.

```markdown
<!-- layout:split-section image:"/images/liminal-close-up.png" -->

Your paragraph text here. This renders as plain text on the wiki
and as a left-column with the image beside it on the site.

<!-- /layout:split-section -->
```

### `<!-- layout:accent-image src:"{path}" class:"{css-class}" -->`

Inserts a decorative image on the site only. Self-closing (no content to wrap). Nothing renders on the wiki.

```markdown
<!-- layout:accent-image src:"/images/adversaries/spectral-kitten.png" class:"sdk-accent" -->
```

---

## Component Tags

These tags convert standard markdown structures into interactive JSX components on the site.

### `<!-- component:card-grid -->` ... `<!-- /component:card-grid -->`

Converts a markdown table into a visual card grid with linked cards. The table must have two columns: `Title` (containing a link) and `Description`.

**On the wiki:** Renders as a normal table with clickable links.
**On the site:** Renders as a styled card grid.

```markdown
<!-- component:card-grid -->
| Title | Description |
|-------|-------------|
| [Investigate Threats](Detections) | Search detections by severity. |
| [Analyze Incidents](Incidents) | Retrieve incident details. |
<!-- /component:card-grid -->
```

### `<!-- component:tabs -->` ... `<!-- /component:tabs -->`

Converts heading sections into a tabbed interface. Each `####` heading becomes a tab label, and the content below it becomes the tab body.

**On the wiki:** Renders as sequential sections with headings.
**On the site:** Renders as a tabbed component where only one tab is visible at a time.

````markdown
<!-- component:tabs -->
#### pip

```bash
pip install -r requirements.txt
```

#### uv

```bash
uv pip install -r requirements.txt
```
<!-- /component:tabs -->
````

---

## Inline Tags

These tags modify individual elements inline rather than wrapping blocks.

### `<!-- link:external -->`

Placed immediately after a markdown link to indicate it should open in a new tab on the site (converted to `<a target="_blank" rel="noopener noreferrer">`). Only use on links that are inline within paragraph text. Links in lists do not need this tag.

```markdown
the [Model Context Protocol](https://modelcontextprotocol.io)<!-- link:external -->
```

---

## Component Tags (Self-Closing)

These tags generate complete UI components from a single annotation.

### `<!-- component:github-card {url} -->`

Generates a GitHub repository card with the GitHub logo, link, and "View on GitHub" label. Self-closing — no content to wrap. Nothing renders on the wiki.

The URL must be a full GitHub repository URL.

```markdown
<!-- component:github-card https://github.com/CrowdStrike/gofalcon -->
```

**Converts to MDX:**

```html
<div class="sdk-hero-action">
<a href="https://github.com/CrowdStrike/gofalcon" target="_blank" rel="noopener noreferrer" class="github-card">
<svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor"><path d="M12 .3a12 12 0 0 0-3.8 23.38c.6.12.83-.26.83-.57L9 21.07c-3.34.72-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.08-.74.09-.73.09-.73 1.2.09 1.83 1.24 1.83 1.24 1.08 1.83 2.81 1.3 3.5 1 .1-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.14-.3-.54-1.52.1-3.18 0 0 1-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.28-1.55 3.29-1.23 3.29-1.23.64 1.66.24 2.88.12 3.18a4.65 4.65 0 0 1 1.23 3.22c0 4.61-2.8 5.63-5.48 5.92.42.36.81 1.1.81 2.22l-.01 3.29c0 .31.2.69.82.57A12 12 0 0 0 12 .3Z"/></svg>
</a>
<span class="github-card-label">View on GitHub</span>
</div>
```

---

## Code Block Tags

These tags add Starlight-specific attributes to code fences that aren't supported in standard markdown.

### `<!-- code-title: {title} -->`

Adds a visible title/label above the code block on the site. Place on the line immediately before the code fence.

````markdown
<!-- code-title: Import sorting -->
```bash
uv run ruff check . --select I
```
````

### `<!-- code-frame: {value} -->`

Controls the visual frame style of the code block on the site. Values: `code` (adds filename-style header), `none` (removes frame/border).

````markdown
<!-- code-frame: none -->
```bash
FALCON_CLIENT_ID=your-client-id
FALCON_CLIENT_SECRET=your-client-secret
```
````

---

## Quick Reference

| Tag | Scope | Purpose |
|-----|-------|---------|
| `meta:title` | Page | Page title for site |
| `meta:description` | Page | Page description for site |
| `meta:section` | Page | Subdirectory for link resolution |
| `meta:link-base` | Page | URL prefix for internal links |
| `frontmatter:sidebar` | Page | Sidebar position/visibility |
| `frontmatter:index` | Home only | index.mdx sidebar config |
| `frontmatter:overview` | Home only | overview.mdx sidebar config |
| `layout:split-section` | Block | Two-column layout with image |
| `layout:accent-image` | Self-closing | Decorative site-only image |
| `component:card-grid` | Block | Table → visual card grid |
| `component:tabs` | Block | Headings → tabbed interface |
| `component:github-card` | Self-closing | GitHub repository card with logo and link |
| `link:external` | Inline | Open link in new tab |
| `code-title` | Line | Label above code block |
| `code-frame` | Line | Code block frame style |
