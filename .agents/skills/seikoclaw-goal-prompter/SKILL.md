---
name: seikoclaw-goal-prompter
description: Hardens executor prompts using the 7-field contract format.
author: Saikojin (SeikoClaw)
---

# SeikoClaw Goal Prompter & Contract Enforcer

## Goal
To package tasks for autonomous execution with strict scope boundaries, explicit stop conditions, and a 7-field verification contract, preventing hallucination, scope creep, and dangerous improvisation.

## When to Use
Use when:
1. Preparing long-running autonomous execution tasks.
2. Formulating a `/goal` prompt.
3. Task involves >30 minutes of mechanical implementation with a verifiable stop condition.

## The 7-Field Hardened Contract Structure

Every hardened goal prompt must adhere to the 7-field contract format:

```markdown
**Objective:** <one-sentence concrete objective>
**Read First:** <files/PLAN.md/issue context>
**Constraints:** <what must NOT change, allowed scope, forbidden libs/conventions>
**Validate:** `<exact shell command>` to run after each change
**Document:** Write concise, targeted documentation for all changes (.md updates)
**Checkpoints:** Work in small checkpoints and log progress briefly
**Stop when:** <verifiable condition (e.g. tests pass)>, OR when further changes require human/product input
```

## Workflow

1. **Fitness Evaluation & Intent Restatement**: Verify the task is suitable (has verifiable test/done condition) and restate the user's core intent and non-negotiable boundaries.
2. **Boundary Definition**: Identify allowed file/module scope vs forbidden modifications (database schemas, public signatures).
3. **Validation Selection**: Pick exact, deterministic test command (e.g., `pytest tests/unit/`, `npm test`).
4. **Draft Contract**: Output the structured 7-field prompt block.

## Boundaries
- Do not execute the task yourself when running this skill; only compile and output the hardened contract.
