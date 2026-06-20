---
name: sweep_loop
description: Takes a specific technical learning or architectural pattern and aggressively sweeps the entire codebase to apply it.
---

# Sweep Loop Skill

## Goal
To eliminate technical debt, apply new architectural patterns, or fix widespread anti-patterns by aggressively sweeping and patching the entire codebase.

## Workflow
1. **Pattern Definition**: Define the specific technical learning or pattern to apply (e.g., from `learnings` or user prompt).
2. **Sweep & Patch Loop**:
   - Scan the entire codebase (`grep_search` or similar) for instances of the anti-pattern.
   - For each instance found, apply the required patch.
   - Run the relevant test suite or CI checks to ensure the patch didn't break functionality.
3. **Exhaustion Check**: Repeat the scan. The loop only stops when zero instances of the anti-pattern are detected.
4. **Completion**: Document the files changed and provide a final clean scan result as evidence.
