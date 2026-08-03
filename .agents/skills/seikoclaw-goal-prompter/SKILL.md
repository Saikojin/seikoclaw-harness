---
name: seikoclaw-goal-prompter
description: Hardens executor prompts and drafting goal instructions using the 5-part contract (Objective, Read First, Constraints, Validate, Stop Condition, Documentation). Use when preparing long-running tasks, framing `/goal` prompts, or hardening task boundaries.
disable-model-invocation: false
---

# SeikoClaw Goal Prompter & Contract Enforcer

## Goal
To package tasks for autonomous execution with strict scope boundaries, explicit stop conditions, and a 5-part verification contract, preventing hallucination, scope creep, and dangerous improvisation.

## When to Use
Use when:
1. Preparing long-running autonomous execution tasks.
2. Formulating a `/goal` prompt.
3. Task involves >30 minutes of mechanical implementation with a verifiable stop condition.

## The 5-Part Contract Structure

Every hardened goal prompt must adhere to the 5-part contract format:

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

1. **Fitness Evaluation**: Verify task is suitable (has verifiable test/done condition, repo is agent-ready).
2. **Boundary Definition**: Identify allowed file/module scope vs forbidden modifications (database schemas, public signatures).
3. **Validation Selection**: Pick exact, deterministic test command (e.g., `pytest tests/unit/`, `npm test`).
4. **Draft Contract**: Output the structured prompt block.

## Boundaries
- Do not execute the task yourself when running this skill; only compile and output the hardened contract.
