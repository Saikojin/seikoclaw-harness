---
description: "Architect Workflow: Breaks down broad project directives into granular task checklists."
---

# Architect Workflow

## Goal
To decompose a high-level goal into independent, verifiable sub-tasks, establishing the plan of attack for the Executor workflows.

## Prerequisites
- A clear high-level user request (e.g., "Add Karate tests for Tablebuddy").

## Steps

0. **Context Recall**
   Before planning, query Openbrain to identify similar past tasks, implementation patterns, or relevant engineering skills.
   - Action: `python seikoclaw.py memory --query "[concise task description]"`

1. **Project & Source Discovery**
   Perform deep discovery of the active codebase. Use `view_file`, `list_dir`, `grep_search`, and review the recalled memories to understand the existing project structure and capabilities.

2. **Decompose the Goal**
   Break the project directive down into discrete execution blocks. A good block should take no more than 1-2 code edits and a single verification run.

3. **Token Budget Assessment**
   Estimate the "output weight" of the plan. 
   - Rule: If the planned response (report + task list + code previews) is likely to exceed ~32,000 tokens, pause and ask the user to proceed with the first half.
   - Action: `python d:\DevWorkspace\SeikoClaw\token_estimator.py "[draft content snippet]"`

4. **Generate `task.md`**
   If we are working in Planning Mode, write the blocks to `<appDataDir>\brain\<conversation-id>/task.md`.
   Use the standard format:
   ```markdown
   - `[ ]` Objective 1
     - `[ ]` Task A (Target specific file)
     - `[ ]` Test A (Target specific test command)
   ```

5. **Yield or Pass to Executor**
   Once the task blueprint is set, alert the user the Architect phase is done, or immediately transition to the `executor.md` workflow for the first uncompleted task. 
   *Note: If the transition itself will push the response over the token limit, stop after generating task.md.*
