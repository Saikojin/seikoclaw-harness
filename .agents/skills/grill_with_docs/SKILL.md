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
4. **Patch & Verify Loop**: 
   - Iteratively patch the documentation (if the code is correct) or the code (if the documentation is correct).
   - Re-verify the patched section against the other to ensure alignment.
   - Continue looping until the drift is completely reduced to zero.
5. **Grill (Fallback)**: Only formulate questions for the user if the correct source of truth cannot be inferred automatically or if the patch involves a destructive architectural decision.

## Checklists
- [ ] Documentation is up-to-date with current code logic.
- [ ] Drift is documented as a task for refactoring.
