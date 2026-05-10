---
name: modernize
description: Performs structural migrations and pattern updates. Use when moving a codebase to a new library, framework, or modern design pattern.
---

# Modernize Skill

## Goal
To systematically update a legacy pattern or dependency across the entire codebase without breaking functionality.

## Workflow
1. **Pilot**: Apply the new pattern to a single file to prove it works.
2. **Template**: Document the migration rules.
3. **Batch**: Apply the migration in small, testable batches (< 5 files).
4. **Verify**: Run tests after every batch to ensure zero regression.

## Checklists
- [ ] New pattern is verified in a pilot file.
- [ ] All tests pass before moving to the next batch.
