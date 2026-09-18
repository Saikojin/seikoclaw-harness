---
name: executor
description: Implements technical tasks and automatically verifies them. Use when you have a well-defined task or a checklist item from a task.md file. Use when you need to write code, run tests, and fix errors autonomously.
---

# Executor Skill & Ready Frontier Worker

## Goal
To claim and rapidly implement ready tasks from the SeikoClaw DAG frontier, verify them autonomously, and hand off to `seikojin-qa` when gated.

## Quick Start
1. **Claim Work**: Claim the next available task from the ready frontier:
   ```bash
   python seikoclaw.py ready --claim --json
   ```
2. **Recall**: Search Openbrain for similar past solutions or pitfalls:
   ```bash
   python seikoclaw.py memory --query "<task keywords>"
   ```
3. **Implement**: Write surgical code edits using test-driven development.
4. **Local Verify**: Run the associated test suite.
5. **QA Handoff / Completion**:
   - If the task has `[GATE: QA]`, update status to `in_qa` and summon `seikojin-qa` (QA Engineer) for Clean Slate certification.
   - If no gate, close task:
     ```bash
     python seikoclaw.py task --task <task-id> --status closed
     ```

## Checklists
- [ ] Claimed work from `python seikoclaw.py ready --claim`.
- [ ] Openbrain was queried for success patterns and mistakes.
- [ ] Automated tests pass locally before handoff.
- [ ] If protected by `[GATE: QA]`, handed off to `seikojin-qa` for 100% pass certification.
- [ ] Task graph synchronized (`python seikoclaw.py sync-tasks`).
- [ ] Post-completion reflection hook triggered upon milestone completion.

## Anti-Patterns
- **Working on Blocked Tasks**: Attempting to implement tasks that are not yet on the ready frontier.
- **Bypassing QA Gates**: Closing a `gate:qa` task without Seikojin QA Engineer certification.
- **The Infinite Loop**: Retrying a fix more than 3 times without alerting the watchdog or user.
