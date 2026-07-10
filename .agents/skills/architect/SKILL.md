---
name: architect
description: Decomposes high-level goals into granular, verifiable tasks. Use when starting a new feature, when a task feels too complex to implement in one go, or when you need a clear roadmap for execution.
---

# Architect Skill

## Goal
To decompose a high-level goal into independent, verifiable sub-tasks, establishing the plan of attack for the Executor workflows.

## Quick Start
1. **Health Check**: Run `python seikoclaw.py doctor` to ensure the environment and dependencies are ready.
2. **Discovery**: Use `list_dir`, `grep_search`, and read relevant Knowledge Items (KIs) to understand the project state.
3. **Decomposition**: Break the goal into discrete execution blocks (1-2 edits + 1 verification run).
4. **Plan**: Write tasks to `task.md` using the standard `[ ]` checkbox format.

## Workflows

### Task Decomposition
When breaking down a task, ensure every item has:
- A specific **Objective** (what is being changed).
- A specific **Test/Verification** (how to prove it works).
- Consult `skills/third-party/planning-and-task-breakdown/SKILL.md` for sizing rules.

## Checklists
- [ ] High-level requirements are fully understood.
- [ ] Task list is written to `task.md`.
- [ ] No single task touches more than 5 files.
- [ ] Every task has a corresponding test command.

## Anti-Patterns
- **The "Big Bang" Task**: Creating a single task for a complex feature without sub-steps.
- **Vague Verification**: Using "Check if it works" instead of a specific command like `pytest`.
- **Ignoring KIs**: Implementing a pattern that contradicts an existing Knowledge Item.

## Handoff
Once the task blueprint is set, notify the user or transition to `executor` for the first uncompleted task.
