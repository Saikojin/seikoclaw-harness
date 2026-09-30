---
name: architect
description: Decomposes high-level goals into granular, verifiable tasks.
author: Saikojin (SeikoClaw)
---

# Architect Skill & Hybrid DAG Planner

## Goal
To decompose a high-level goal into independent, verifiable sub-tasks, establishing the DAG of attack for the Executor and Seikojin-QA workflows.

## Quick Start
1. **Health Check**: Run `python seikoclaw.py health` and `python seikoclaw.py doctor` to ensure the environment and dependencies are ready.
2. **Discovery & Mistake Check**: Query OpenBrain memories (`python seikoclaw.py memory --query "[topic] mistakes"`) and read relevant Knowledge Items (KIs) to avoid past pitfalls.
3. **Decomposition & DAG Construction**:
   - Break the goal into discrete execution blocks (1-2 edits + 1 verification run).
   - **Strict Task-Level Test Rule**: Every single `- [ ]` task checkbox MUST specify an exact automated verification command (e.g. `Verify: pytest tests/test_feature.py`). Do not substitute task-level tests with a single plan-level validation note.
   - Create tasks via CLI or `task.md`:
     ```bash
     python seikoclaw.py task --title "Design Data Model" --priority 0
     python seikoclaw.py task --title "Implement Auth Logic" --priority 1 --gate-type qa
     python seikoclaw.py dep --from-id <model-id> --to-id <auth-id> --edge-type blocks
     ```
4. **QA Risk Map Collaboration**:
   - Summon the **`seikojin-qa` (QA Strategist)** to identify critical user flows (Rabbit Paths) and attach `gate:qa` to high-risk nodes.
5. **Sync Plan**: Write/sync tasks to `task.md` (`python seikoclaw.py sync-tasks`).

## Checklists
- [ ] High-level requirements are fully understood.
- [ ] Known mistakes & gotchas checked in Openbrain (`python seikoclaw.py memory --query "[topic] mistakes"`).
- [ ] Tasks created in DAG with content-derived hash IDs and dependencies.
- [ ] Critical/high-risk tasks have `gate:qa` attached for Seikojin QA certification.
- [ ] No single task touches more than 5 files.
- [ ] **Every single task has a corresponding automated test/verification command inline.**
- [ ] Two-way sync verified in `task.md`.

## Handoff
Once the task DAG is established, transition to the `executor` skill. The executor claims unblocked work directly from the ready frontier (`python seikoclaw.py ready --claim`).
