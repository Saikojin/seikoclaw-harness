---
name: executor
description: Implements technical tasks and automatically verifies them. Use when you have a well-defined task or a checklist item from a task.md file. Use when you need to write code, run tests, and fix errors autonomously.
---

# Executor Skill

## Goal
To rapidly implement a technical task and automatically verify it without distracting the user with intermediate failures.

## Quick Start
1. **Recall**: Search Openbrain for similar past tasks: `python seikoclaw.py memory search "task description"`.
2. **Implement**: Write code adjustments using `replace_file_content`. Consult `skills/third-party/incremental-implementation/SKILL.md`.
3. **Verify**: Run the associated test command. Self-correct up to 3 times on failure.
4. **Capture**: Run `python seikoclaw.py wiki-sync` on success.

## Workflows

### Implementation & Test Loop
- Use `skills/third-party/test-driven-development/SKILL.md` for verification requirements.
- Always write or update a test harness for the change.
- **Auto-Correction**: If a test fails, read the log, fix, and retry (Max 3 attempts).

## Checklists
- [ ] Task is singular and well-defined.
- [ ] Openbrain was queried for success patterns.
- [ ] Test command is specified (e.g., `pytest`, `npm test`).
- [ ] **Mobile**: Appium is running with `--relaxed-security` (if ADB shell needed).
- [ ] Session state is captured to the Master Wiki on completion.

## Anti-Patterns
- **The Infinite Loop**: Retrying a fix more than 3 times without alerting the user.
- **Silent Failures**: Moving to the next task if the verification command failed.
- **Context Amnesia**: Forgetting to update `task.md` or the Master Wiki after a success.

## Verification Command Examples
- **Python**: `pytest test_file.py`
- **Node**: `npm test -- -t "component_name"`
- **Android**: `mvn test -Dtest=ClassName#MethodName`
- **Generic**: `python run_tests.py`
