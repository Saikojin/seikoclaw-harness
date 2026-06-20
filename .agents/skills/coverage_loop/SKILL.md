---
name: coverage_loop
description: Iteratively write tests and run coverage tools until a specific target threshold is met.
---

# Coverage Loop Skill

## Goal
To aggressively increase test coverage until a predefined threshold (e.g., 90% or 100%) is met without manual intervention.

## Workflow
1. **Target Identification**: Read `task.md` or query the user for the target module/project and the target coverage threshold.
2. **Coverage Generation Loop**:
   - Run the coverage tool (e.g., `pytest --cov`, `jest --coverage`).
   - Parse the coverage report to identify uncovered lines or branches.
   - Write a new unit test targeting the largest untested gap.
   - Rerun the coverage tool.
3. **Streak & Threshold Check**: Continue looping until the target threshold is met. Ensure no existing tests were broken in the process (streak limit).
4. **Completion**: Update the Evidence Contract in `task.md` with the final coverage report.
