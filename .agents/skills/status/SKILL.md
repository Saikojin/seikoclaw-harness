---
name: status
description: Displays the current context health and token budget. Use when you are concerned about hitting token limits.
---

# Status Skill

## Goal
To provide a visual dashboard of the current session's context usage.

## Workflow
1. **Check Status**: Run `python scripts/status.py`.
2. **Action**: If Session Weight is > 80%, recommend a summarization task.

## Checklists
- [ ] Session Weight is healthy (< 80% or 100k tokens).
