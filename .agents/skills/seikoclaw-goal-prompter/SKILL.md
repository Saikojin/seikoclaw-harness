---
name: seikoclaw-goal-prompter
description: Hardens executor prompts with strict scope boundaries, out-of-scope definitions, and explicit stop conditions.
---

# Seikoclaw Goal Prompter

## Goal
To package tasks for the Executor with clear boundaries, preventing hallucination, scope creep, and dangerous improvisation.

## Workflow
1. **Input Analysis**: Take a raw task description from the Architect's `task.md`.
2. **Boundary Definition**: Identify exactly which files or modules are permitted to change.
3. **Out-of-Scope Rule**: Explicitly list what the executor should NOT do (e.g., "Do not change the database schema").
4. **Verification Gate**: Define the exact command or visual check the executor must run to prove completion.
5. **Prompt Generation**: Output the hardened objective prompt.

## Required Inputs
- A task description
- The current workspace context

## Output Format
A hardened prompt block containing:
- **Objective**: ...
- **Allowed Scope**: ...
- **Out of Scope**: ...
- **Verification Gate**: ...

## Boundaries
- Do not execute the prompt yourself. Only generate it.
