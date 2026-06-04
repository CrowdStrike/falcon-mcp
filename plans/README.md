# Plans (local, gitignored)

This directory holds **local implementation plans, design scratch, and prompt
sequences** — the working notes produced while building a feature.

Everything in this directory is gitignored **except this README**. Drop your
planning markdown here instead of in `docs/`:

- `docs/` is the published documentation tree. It is consumed by an external
  site and markdown-linted by CI (`docs/**/*.md`), so stray planning files there
  will fail the lint and confuse the published docs.
- `plans/` keeps that scratch work next to the repo without committing it.

## Usage

```text
plans/
  README.md              # tracked — this file
  my-feature-plan.md     # ignored
  exclusions_module.md   # ignored
```

Nothing here ships. If a plan contains guidance worth keeping for future
contributors, fold it into `CLAUDE.md`, `docs/development/`, or a code comment
before the branch merges.
