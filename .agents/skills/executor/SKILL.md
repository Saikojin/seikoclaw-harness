---
name: executor
description: Implements technical tasks and automatically verifies them. Use when you have a well-defined task or a checklist item from a task.md file.
---

# Executor Skill

## Goal
To implement code changes accurately and verify them using tests, ensuring the project state remains healthy.

## Workflow
1. **Focus**: Pick the first uncompleted task from `task.md`.
2. **Implementation**: Edit the target files to achieve the task objective.
3. **Verification**: Run the specified test command (e.g., `pytest`, `npm test`, `python script.py`).
4. **Correction**: If tests fail, analyze the error and fix the code immediately.
5. **Update**: Mark the task as completed in `task.md`.

## Checklists
- [ ] Code follows existing project patterns.
- [ ] No unnecessary changes are made.
- [ ] Tests pass before moving to the next task.

## Handoff
Once all tasks in `task.md` are complete, notify the user.
