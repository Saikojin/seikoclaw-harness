---
name: grill_with_docs
description: Reconciles code with documentation. Use when exploring a codebase by comparing it against its own docs or best practices to find hidden technical debt or architectural drift.
---

# Grill With Docs Skill

## Goal
To identify gaps, drift, and contradictions between the intended design (Docs) and the actual implementation (Code).

## Workflow
1. **Read Docs**: Review READMEs, ADRs, and Knowledge Items (KIs) in `.master_wiki/`.
2. **Scan Code**: Trace the logic described in the docs within the codebase.
3. **Compare**: List every contradiction found.
4. **Grill**: Formulate questions for the user to clarify why the code drifted.

## Checklists
- [ ] Documentation is up-to-date with current code logic.
- [ ] Drift is documented as a task for refactoring.
