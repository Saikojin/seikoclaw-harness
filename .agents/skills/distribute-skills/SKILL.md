---
name: distribute-skills
description: Sync and distribute agent skills between the local workspace (.agents/skills) and global/plugin locations. Trigger when asked to publish, sync, or distribute skills across environments.
disable-model-invocation: false
---

# Skill Distribution & Sync Workflow

## Goal
To synchronize skills between local workspace repositories (`.agents/skills/`) and global plugin directories (`.gemini/config/plugins/science/skills/`) or remote repositories.

## Workflow

1. **Source Check**: Identify changed or new `SKILL.md` files in `.agents/skills/`.
2. **Cross-Platform Sync**:
   - **Bash**:
     ```bash
     rsync -av --include='*/' --include='SKILL.md' --include='*.sh' --include='*.ps1' --include='*.txt' --exclude='*' .agents/skills/ ~/.gemini/config/plugins/science/skills/
     ```
   - **PowerShell**:
     ```powershell
     Copy-Item -Path ".agents\skills\*" -Destination "$env:USERPROFILE\.gemini\config\plugins\science\skills\" -Recurse -Force
     ```
3. **Router Audit**: Update `seikoclaw-harness/SKILL.md` to index any new skill.
