---
description: "Executor & Verifier Workflow: Implements a single task, tests it, and auto-corrects on failure up to N times."
---

# Executor Workflow

## Goal
To rapidly implement a technical task and automatically verify it without distracting the user with intermediate failures. 

## Prerequisites
- A singular, well-defined task (from the Architect workflow or `task.md`).
- SeikoClaw CLI (`seikoclaw.py`) and Openbrain initialized.

## Steps

0. **Recall Context & Pre-flight**
   - Query Openbrain for similar past tasks: `python seikoclaw.py memory --query "[task description]"`
   - **Token Pre-flight**: If the task involves modifying files > 1000 lines, use `token_estimator.py` to check current size.
   - **Chunking Rule**: Prefer `multi_replace_file_content` for specific lines over full-file rewrites to keep output < 24,000 tokens per implementation step.

1. **Implementation**
   - Write the required code adjustments using `replace_file_content` or `multi_replace_file_content`.
   - Write the automated test harness for the change if one doesn't exist.

2. **Automated Verification Loop**
   // turbo-all
   Run the test command associated with the code.
   - Example Python `run_command`: `pytest test_file.py`
   - Example Node `run_command`: `npm test -- -t "component_name"`

3. **Correction & Retry (The Micro-Loop)**
   If the command fails:
   - Read the error log from the command output.
   - Formulate a fix, apply it.
   - Rerun the verification.
   - **Self-correct up to a maximum of 3 times**. 
   - **Context Check**: Use `python seikoclaw.py loop` logic to ensure we aren't exceeding the token budget during retries.

4. **Conclusion & Capture**
   - If passes: 
     - Update `task.md` to `[x]`, commit changes.
     - **Update Kanban**: `python seikoclaw.py kanban --task [ID] --status "Done"`
     - **Auto-Capture & Visual Recap**: Run `python auto_capture.py` to save session state/new skills to Openbrain and automatically generate a visual recap (`python seikoclaw.py recap`).
     - Display the local bridge URL for the visual recap to the user for final review.
     - Notify the user of victory.
   - If fails 3 times: 
     - **Update Kanban**: `python seikoclaw.py kanban --task [ID] --status "Blocked"`
     - Stop and generate an "Error Report" outlining the final failure trace, alerting the user for manual review.
