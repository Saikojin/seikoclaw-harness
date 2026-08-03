---
name: agent-guardrails
description: Denylist of catastrophic shell commands enforced across AI agents via cross-platform Bash and PowerShell guard hooks. Trigger when adding or tuning blocked command patterns, wiring hooks into agents, or evaluating command security.
disable-model-invocation: false
---

# Agent Guardrails & Command Denylist

## Goal
To enforce a PreToolUse/Pre-Execution safety net that intercepts and blocks catastrophic shell commands (system wipes, disk format, force pushes, remote execution pipes) before execution.

## Files & Components

- `dangerous-patterns.txt`: Shared denylist containing cross-platform POSIX-ERE and PowerShell regex patterns.
- `deny-dangerous.sh`: Bash guard script accepting JSON or raw command on stdin.
- `deny-dangerous.ps1`: PowerShell guard script for Windows environments.
- `test-guard.sh` / `test-guard.ps1`: Automated test harnesses to verify block/allow criteria.

## Usage & Maintenance

1. **Add/Tune Pattern**: Edit `dangerous-patterns.txt`. Add matching test cases to both `test-guard.sh` and `test-guard.ps1`.
2. **Run Test Harness**:
   - Bash: `./.agents/hooks/test-guard.sh`
   - PowerShell: `powershell -ExecutionPolicy Bypass -File ./.agents/hooks/test-guard.ps1`
3. **Design Rule**: Block ONLY catastrophic/irreversible actions (disk format, system directory wipes, force push, exfiltration pipes). Keep recoverable actions allowed so agent capability is not paralyzed.
