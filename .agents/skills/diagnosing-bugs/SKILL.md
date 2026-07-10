---
name: diagnosing-bugs
description: Structured bug diagnosis loop with HITL (human-in-the-loop) script execution and evidence gathering.
disable-model-invocation: false
---

# Diagnosing Bugs

Implement a systematic diagnosis procedure to reproduce and solve issues.

## Workflow

1. **Information gathering.** Collect console logs, error stacks, and system environments.
2. **Write reproduction test.** Try to write a failing test reproducing the issue.
3. **Execute diagnosis script.** Use the local `scripts/hitl-loop.ps1` to test the fix iteratively.
4. **Fix & Verify.** Apply patches and confirm they pass the reproduction test.
