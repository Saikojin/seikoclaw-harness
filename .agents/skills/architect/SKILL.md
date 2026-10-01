---
name: architect
description: Decomposes high-level goals into granular, verifiable tasks. Use when starting a new feature, when a task feels too complex to implement in one go, or when you need a clear roadmap for execution.
author: Saikojin (SeikoClaw)
---

# Architect Skill & Hybrid DAG Planner

## Goal
To decompose a high-level goal into independent, verifiable sub-tasks, establishing the DAG of attack for the Executor, Seikojin-QA, and Visual Critic workflows.

## Quick Start
1. **Intent Restatement Gate**:
   - Restate the user's core intent, key boundaries, and expected outcome in 1–2 sentences before generating tasks or diving into deep planning.
2. **Health Check**: Run `python seikoclaw.py health` and `python seikoclaw.py doctor` to ensure the environment and dependencies are ready.
3. **Discovery & Mistake Check**: Query OpenBrain memories (`python seikoclaw.py memory --query "[topic] mistakes"`) and read relevant Knowledge Items (KIs) to avoid past pitfalls.
4. **Decomposition & DAG Construction**:
   - Break the goal into discrete execution blocks (1–2 edits + 1 verification run).
   - **Strict Task-Level Test Rule**: Every single `- [ ]` task checkbox MUST specify an exact automated verification command (e.g. `Verify: pytest tests/test_feature.py`) or a visual capture contract. Do not substitute task-level tests with a single plan-level validation note.
   - Create tasks via CLI or `task.md`:
     ```bash
     python seikoclaw.py task --title "Design Data Model" --priority 0
     python seikoclaw.py task --title "Implement Auth Logic" --priority 1 --gate-type qa
     python seikoclaw.py task --title "Hero Combat VFX & Shading" --priority 2 --gate-type critic
     python seikoclaw.py dep --from-id <model-id> --to-id <auth-id> --edge-type blocks
     ```
5. **Gate Contracts & QA/Critic Risk Mapping**:
   - **`gate:qa` / `[GATE: QA]`**: Summon **`seikojin-qa` (QA Strategist)** to identify critical user flows (Rabbit Paths) and attach QA gatekeeping to high-risk nodes.
   - **`gate:critic` / `[GATE: VISUAL_CRITIC]`**: Attach to visual, shader, UI, or game asset tasks. Requires automated screenshot capture, Side-by-Side (SxS) comparison against `refs-locked/`, and 0-punch verification against `art/BAR.md`.
6. **Sync Plan**: Write/sync tasks to `task.md` (`python seikoclaw.py sync-tasks`).

## Checklists
- [ ] Core user intent and non-negotiable boundaries restated and confirmed.
- [ ] High-level requirements are fully understood.
- [ ] Known mistakes & gotchas checked in Openbrain (`python seikoclaw.py memory --query "[topic] mistakes"`).
- [ ] Tasks created in DAG with content-derived hash IDs and dependencies.
- [ ] Critical/high-risk tasks have `gate:qa` or `gate:critic` attached.
- [ ] Visual/game tasks include explicit `refs-locked/` targets and done-when visual contracts.
- [ ] No single task touches more than 5 files.
- [ ] Every single task has a corresponding automated test/verification command inline or visual critic gate.
- [ ] Two-way sync verified in `task.md`.

## Handoff
Once the task DAG is established, transition to the `executor` / `implement` skill. The executor claims unblocked work directly from the ready frontier (`python seikoclaw.py ready --claim`).
