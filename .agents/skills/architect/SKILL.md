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
4. **Plan Generation (Evidence Contracts)**: Write the task list to `task.md` using the **Evidence Contract** pattern.
   Instead of just generating a checklist, define exact "Evidence Requirements" for each task. The Executor must append test outputs, screenshots, or benchmark metrics next to the task to prove completion before marking it done.
   Use the standard format:
   ```markdown
   - `[ ]` Objective 1
     - `[ ]` Task A (Target specific file)
       - Evidence Required: [e.g., successful pytest log snippet, screenshot of UI change]
     - `[ ]` Test A (Target specific test command)
   ```

## Checklists
- [ ] Requirements are fully understood.
- [ ] No single task touches more than 5 files.
- [ ] Every task has a corresponding test or verification command.

## Handoff
Once the task blueprint is set, transition to the `executor` skill for implementation.
