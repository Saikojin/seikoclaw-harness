---
description: "Architect Workflow: Breaks down broad project directives into granular task checklists."
---

# Architect Workflow

## Goal
To decompose a high-level goal into independent, verifiable sub-tasks, establishing the plan of attack for the Executor workflows.

## Prerequisites
- A clear high-level user request (e.g., "Add Karate tests for Tablebuddy").

## Steps

0. **Context Recall, Mistake Check & Instant Gut-Check**
   Before planning, check if this is a new feature or build request.
   - If proposing a new build/feature, trigger `/before-building` to surface 1–3 consequential choices first.
   - Query Openbrain for past tasks, skills, and **known mistakes/pitfalls**:
     `python seikoclaw.py memory --query "[task description] mistakes pitfalls gotchas"`

1. **Project & Source Discovery**
   Perform deep discovery of the active codebase. Use `view_file`, `list_dir`, `grep_search`, and review the recalled memories to understand the existing project structure and capabilities.

2. **Decompose the Goal**
   Break the project directive down into discrete execution blocks using the 5-part goal contract from `seikoclaw-goal-prompter` (Objective, Read First, Constraints, Validate, Document, Stop Condition). A good block should take no more than 1-2 code edits and a single verification run.

3. **Mandatory Task List (`task.md`) Generation**
   - **Rule**: Every implementation plan MUST output a concrete `task.md` checklist with verifiable checkboxes (`- [ ]`) and test commands before proceeding to execution.
   - Write the checklist to `task.md` (or `<appDataDir>\brain\<conversation-id>/task.md`).
   - This task list acts as the deterministic trigger for the **Automated Post-Task Reflection Hook** (`auto_capture.py` / `seikoclaw reflect`) upon completion.

4. **Token Budget Assessment & Visual Plan**
   - Estimate output weight using `token_estimator.py`.
   - Run visual plan subcommand if needed: `python seikoclaw.py plan --task task.md`
   - This generates `.agents/plans/plan/plan.mdx` and serves the local bridge.

5. **Yield or Pass to Executor**
   Once `task.md` is generated and approved by the user, transition to the `executor.md` workflow for the first uncompleted task.
