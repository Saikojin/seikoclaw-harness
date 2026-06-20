---
name: executor
description: Implements technical tasks and automatically verifies them. Use when you have a well-defined task or a checklist item from a task.md file.
---

# Executor Skill

## Goal
To implement code changes accurately and verify them using tests, ensuring the project state remains healthy.

## Workflow
1. **Focus**: Pick the first uncompleted task from `task.md`.
2. **Implementation**: Edit the target files to achieve the task objective.
3. **Automated Verification & Reviewer Subagent Loop**: 
   - Run the automated test command (e.g., `pytest`, `npm test`, `python script.py`).
   - If the automated tests pass, invoke the **Reviewer Subagent (QA Lead persona)** to perform independent verification before closing the task.
   
   **QA Lead Testing Rubric:**
   The Reviewer Subagent must actively evaluate the implementation against this comprehensive rubric (adapt to the specific task domain, using login/auth as a thorough model):
   *   **Functional Testing:** Valid/invalid inputs, empty fields, state management, workflow completion.
   *   **Security Testing:** Injection attacks, brute force protection, data at rest/transit (HTTPS/hashing), dynamic sessions (token rotation).
   *   **UI/UX Testing:** Logical mechanics (tab ordering), usability features, helpful error states, responsive layouts, native browser integrations (autofill).
   *   **Edge Cases:** Extreme input limits, atypical character encoding (Unicode), concurrency conflicts, network degradation (offline/reconnect), state paradoxes (back button).
   *   **API Level:** Strict semantic response codes, token lifecycles, infrastructure defenses (rate limiting), performance baselines.
   *   **Accessibility:** Screen reader compatibility, complete keyboard navigation, contrast ratios, comprehensive ARIA labels.

4. **Correction & Quality Streak Limit**: 
   If the automated test fails OR the Reviewer Subagent identifies gaps:
   - Formulate a fix based on the error log or subagent feedback, apply it, and restart the loop.
   - **Quality Streak Limit:** The Executor must pass the entire suite of tests (both automated and subagent review) consecutively without regression.
   - Self-correct up to a maximum of 3 times *per failure type*, but the overall task is only marked `[x]` when the Quality Streak clears and the Reviewer Subagent approves.

5. **Update**: Mark the task as completed in `task.md` with the required evidence.

## Checklists
- [ ] Code follows existing project patterns.
- [ ] No unnecessary changes are made.
- [ ] Tests pass before moving to the next task.

## Handoff
Once all tasks in `task.md` are complete, notify the user.
