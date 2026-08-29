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
- [ ] Known mistakes & gotchas checked in Openbrain (`python seikoclaw.py memory --query "[topic] mistakes"`).
- [ ] Mandatory task list is generated and saved to `task.md` with `- [ ]` checkboxes.
- [ ] No single task touches more than 5 files.
- [ ] Every task has a corresponding automated test/verification command.
- [ ] Post-completion hook (`python auto_capture.py`) wired for automated reflection.

## Anti-Patterns
- **The "Big Bang" Task**: Creating a single task for a complex feature without sub-steps.
- **Proceeding Without `task.md`**: Beginning execution without an explicit, verifiable task checklist.
- **Vague Verification**: Using "Check if it works" instead of a specific command like `pytest`.
- **Ignoring Past Mistakes**: Repeating pitfalls already documented in Openbrain or `.master_wiki/`.

## Handoff
Once the task blueprint is set in `task.md`, notify the user or transition to `executor` for implementation. When all items are marked `[x]`, `auto_capture.py` automatically triggers the reflection and skill gating loop.
