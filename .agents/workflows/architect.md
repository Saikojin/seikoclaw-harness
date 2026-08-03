---
description: "Architect Workflow: Breaks down broad project directives into granular task checklists."
---

# Architect Workflow

## Goal
To decompose a high-level goal into independent, verifiable sub-tasks, establishing the plan of attack for the Executor workflows.

## Prerequisites
- A clear high-level user request (e.g., "Add Karate tests for Tablebuddy").

## Steps

0. **Context Recall & Instant Gut-Check**
   Before planning, check if this is a new feature or build request.
   - If proposing a new build/feature, trigger `/before-building` to surface 1–3 consequential choices first.
   - Query Openbrain to identify similar past tasks, implementation patterns, or relevant engineering skills:
     `python seikoclaw.py memory --query "[concise task description]"`

1. **Project & Source Discovery**
   Perform deep discovery of the active codebase. Use `view_file`, `list_dir`, `grep_search`, and review the recalled memories to understand the existing project structure and capabilities.

2. **Decompose the Goal**
   Break the project directive down into discrete execution blocks using the 5-part goal contract from `seikoclaw-goal-prompter` (Objective, Read First, Constraints, Validate, Document, Stop Condition). A good block should take no more than 1-2 code edits and a single verification run.

3. **Token Budget Assessment**
   Estimate the "output weight" of the plan. 
   - Rule: If the planned response (report + task list + code previews) is likely to exceed ~32,000 tokens, pause and ask the user to proceed with the first half.
   - Action: `python d:\DevWorkspace\SeikoClaw\token_estimator.py "[draft content snippet]"`

4. **Generate and Serve Visual Plan**
   - If we are working in Planning Mode, write the blocks to `<appDataDir>\brain\<conversation-id>/task.md`.
   - Run the visual plan subcommand: `python seikoclaw.py plan --task task.md`
   - This parses `task.md` and generates a structured visual plan in `.agents/plans/plan/plan.mdx`, then starts the local bridge server using `npx @agent-native/core`.
   - Review the served bridge URL to verify syntax and wireframe layouts.

5. **Yield or Pass to Executor**
   Once the visual plan is served and approved by the user, transition to the `executor.md` workflow for the first uncompleted task. 
   *Note: If the transition itself will push the response over the token limit, stop after generating task.md and serving the plan.*
