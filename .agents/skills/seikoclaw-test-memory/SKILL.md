---
name: seikoclaw-test-memory
description: Records successful testing procedures and DOM selectors into a repo-local runbook to prevent redundant discovery.
---

# Seikoclaw Test Memory

## Goal
To persist complex DOM selectors, test accounts, and page-specific testing quirks locally so future Executor runs do not need to rediscover them.

## Workflow
1. **Fact Extraction**: When a testing run succeeds, extract the precise selectors, setup commands, or fixture data used.
2. **Runbook Location**: Identify or create `.testing_runbook.md` in the workspace root.
3. **Update Entry**: Append or update the entry for the specific page/component being tested.

## Required Inputs
- A successful testing session summary or transcript.
- The path to the component or page tested.

## Output Format
Updated entries in `.testing_runbook.md`.

## Boundaries
- Separate generic QA rules (which belong in global `AGENTS.md`) from specific DOM selectors and test accounts (which belong here).
- Do not store actual passwords. Use environment variable references or local fixture placeholders.
