# Issue tracker: Local Markdown

Issues and PRDs for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The PRD is `.scratch/<feature-slug>/PRD.md`
- Implementation issues are `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

- **Map**: `.scratch/<effort-slug>/MAP.md` — the wayfinder map issue, labelled `wayfinder:map`
- **Child tickets**: `.scratch/<effort-slug>/issues/<NN>-<slug>.md` — child issues of the map
- **Blocking**: Expressed as a `Blocked by:` line in the ticket frontmatter, referencing ticket filenames
- **Frontier query**: All `.scratch/<effort-slug>/issues/*.md` where `Status: open` and no `Blocked by:` entries reference open tickets
- **Claiming**: Set `Assigned:` in the ticket frontmatter
- **Closing**: Change `Status: open` to `Status: closed`
