---
name: seikoclaw-red-team
description: Audits an implementation plan for load-bearing assumptions, missing evidence, and risks before handoff.
---

# Seikoclaw Red Team (Assumption Checker)

## Goal
To scrutinize the Architect's generated `implementation_plan.md` for hidden risks and unsupported assumptions, ensuring stability before the Executor writes code.

## Workflow
1. **Plan Ingestion**: Read the `implementation_plan.md`.
2. **Assumption Extraction**: List all assumptions made (e.g., "assuming the API returns JSON", "assuming the library is thread-safe").
3. **Risk Scoring**: Grade each assumption. If a load-bearing assumption lacks evidence, flag it.
4. **Intervention**: Require the Architect to add verification steps to the plan or ask the user for clarification before proceeding.

## Required Inputs
- The generated `implementation_plan.md`.

## Output Format
A Red Team review appended to the plan or provided as a standalone review artifact, detailing:
- Identified assumptions.
- Missing evidence.
- Required changes to the plan.

## Boundaries
- Do not disagree with the user's core vision, only audit the technical assumptions of the implementation.
