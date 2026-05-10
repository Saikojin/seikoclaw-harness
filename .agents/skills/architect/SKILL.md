---
name: architect
description: Decomposes high-level goals into granular, verifiable tasks. Use when starting a new feature or when a task is too complex for a single edit.
---

# Architect Skill

## Goal
To decompose a high-level goal into independent, verifiable sub-tasks, establishing the plan of attack for the Executor workflows.

## Workflow
1. **Discovery**: Use `list_dir`, `grep_search`, and `view_file` to understand the project state.
2. **Consult Knowledge**: Check Knowledge Items (KIs) in `.master_wiki` or the Openbrain memory.
3. **Decomposition**: Break the goal into discrete execution blocks (1-2 edits + 1 verification run).
4. **Plan Generation**: Write the task list to `task.md`.

## Checklists
- [ ] Requirements are fully understood.
- [ ] No single task touches more than 5 files.
- [ ] Every task has a corresponding test or verification command.

## Handoff
Once the task blueprint is set, transition to the `executor` skill for implementation.
