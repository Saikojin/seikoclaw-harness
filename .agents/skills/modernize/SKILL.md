---
name: modernize
description: Performs structural migrations and pattern updates. Use when moving a codebase to a new library, framework, or modern design pattern.
---

# Modernize Skill

## Goal
To systematically update a legacy pattern or dependency across the entire codebase without breaking functionality.

## Quick Start
1. **Targeting**: Identify the legacy pattern (e.g., old API call, untyped test).
2. **Templating**: Create a "Bridge" or "Template" for the modern version.
3. **Execution**: Apply the migration in small, testable vertical slices.
4. **Verification**: Run tests after every slice to ensure zero regression.

## Workflows

### The Migration Loop
- Start with a single "Pilot" file to prove the new pattern works.
- Document the migration rules in a temporary `MIGRATION_GUIDE.md`.
- Use `multi_replace_file_content` to apply the pattern to similar files.
- Finalize by deleting the legacy utility or boilerplate.

## Checklists
- [ ] New pattern is fully verified in a pilot file.
- [ ] Migration is performed in small batches (< 5 files per batch).
- [ ] All tests pass before moving to the next batch.

## Anti-Patterns
- **The Global Search-and-Replace**: Mass-changing code without verifying individual file contexts.
- **Half-Baked Migrations**: Leaving two different ways of doing the same thing in the codebase for a long time.
- **Ignoring Edge Cases**: Forgetting that some files might use the legacy pattern in "creative" ways that the new pattern doesn't support.
