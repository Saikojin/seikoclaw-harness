---
name: status
description: Displays the current context health and token budget. Use when you are concerned about hitting token limits, or want to check the 'weight' of the current session before a large task.
---

# Status Skill

## Goal
To provide a visual dashboard of the current session's context usage and daily budget health.

## Quick Start
1. **Check Status**: Run `python seikoclaw.py usage` or the dedicated status script.

## Workflows

### Context Monitoring
- Run `python status.py` whenever a task feels "heavy" or involves large files.
- If the **Session Weight** is > 80%, recommend a **Summarization Task** to clear the context.

## Checklists
- [ ] Daily Budget is below the limit.
- [ ] Session Weight is healthy (< 80k tokens).

## Anti-Patterns
- **Flying Blind**: Continuing a complex implementation loop without checking context health.
- **Context Bloat**: Allowing the session weight to hit 100% without summarizing, leading to partial responses.
