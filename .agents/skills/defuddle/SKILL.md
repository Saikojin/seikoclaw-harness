---
name: defuddle
description: Extract clean, readable Markdown from web pages using Defuddle CLI, stripping navigation, ads, headers, and clutter to minimize token usage. Use when fetching, reading, or scraping web URLs, or converting HTML pages into clean markdown.
author: Steph Ango (kepano)
---

# Defuddle

Use Defuddle CLI to extract clean readable content from web pages. Prefer over WebFetch for standard web pages — it removes navigation, ads, and clutter, reducing token usage and protecting the context window.

If not installed: `npm install -g defuddle` (or run via `npx defuddle`).

## Usage

Always use `--md` for markdown output:

```bash
defuddle parse <url> --md
```

Save to file:

```bash
defuddle parse <url> --md -o content.md
```

Extract specific metadata:

```bash
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

## Output formats

| Flag | Format |
|------|--------|
| `--md` | Markdown (default choice) |
| `--json` | JSON with both HTML and markdown |
| (none) | HTML |
| `-p <name>` | Specific metadata property |

## SeikoClaw Integration Patterns

- **Guard Context Window (Principle 22)**: When researching an external URL or documentation page, avoid dumping raw HTML into context. Run `defuddle parse <url> --md` to extract high-density semantic text.
- **Pipeline to Knap**: Defuddle pairs directly with `knap` to ingest web articles directly into structured Obsidian vault notes:
  ```bash
  defuddle parse https://example.com/article --md --json | knap render template.md --data - -o note.md
  ```
