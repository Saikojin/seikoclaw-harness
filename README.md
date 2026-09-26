# SeikoClaw: Agentic Coding Harness

**SeikoClaw** is a modular framework for building AI-native development environments. It provides a standardized way to integrate AI agents (like Claude, Gemini, or ChatGPT) into your local development workflow using persistent memory, structured skills, and goal-oriented workflows.

## Why SeikoClaw?
Most AI agents operate in a vacuum. SeikoClaw gives them:
- **Long-term Memory**: Persistent storage for project context, architectural decisions, and learned skills.
- **Structured Capabilities**: Modular "Skills" that define exactly what the agent can and should do.
- **Predictable Workflows**: Pre-defined loops for planning (Architecting), executing, and verifying code.

---

## Repository Structure

```text
.
├── .agents/
│   ├── skills/             # Modular capability definitions
│   └── workflows/          # Procedural guides (Architect, Executor, etc.)
├── .master_wiki/           # The "Source of Truth" for project knowledge
├── openbrain/              # The Context Persistence Engine
├── scripts/                # Utility scripts (setup, status)
├── templates/              # Standardized document templates
├── seikoclaw.py            # Management CLI (Kanban, Looping, Reflection)
└── .seikoclaw.yaml         # Global configuration
```

---

## Core Capabilities

### 1. Autonomous Looping
SeikoClaw can run in an autonomous "Thinking" loop to complete complex goals. It monitors an iteration budget and context window size.
```bash
python seikoclaw.py loop --goal "Implement the user authentication logic" --turns 5
```

### 2. Kanban Task Management
Manage project progress using a database-backed Kanban system that persists across AI sessions.
```bash
# List all tasks
python seikoclaw.py kanban

# Update a task status
python seikoclaw.py kanban --task "AUTH-001" --status "Done"
```

### 3. Skill Evolution
The agent automatically synthesizes new skills or evolves existing ones based on successful task trajectories.
```bash
python seikoclaw.py reflect --task task.md
```

### 4. Game Forge (Autonomous Game Creation)
SeikoClaw includes **Game Forge** (`/game-forge`), an autonomous framework that coordinates the full lifecycle of game development from pitch to playable build with human-in-the-loop checkpoints:
- **Design & GDD**: `/game-design-critic`, `/genre-competitor-analysis`, `/gdd-generator`
- **Micro-Slice & Prototyping**: `/scope-surgeon`, `/game-prototype-builder`, `/game-systems-modeler`
- **Assets & Workbenches**: `/playtest-feedback-loop`, `/mood-board-curator`, `/asset-generator`, `/game-developer`
- **Autonomous Build & QA**: `/seikoclaw-architect`, `/seikoclaw-executor`, `/tdd`, `/seikojin-qa`

### 5. Cross-Project Memory & Conversation Synchronization
OpenBrain automatically indexes developer interactions, tool executions, and mistake records across all project workspaces into tiered SQLite metadata and ChromaDB vector embeddings.
```bash
# Preview unindexed conversation turns (dry run)
python seikoclaw.py sync-history --dry-run --limit 5

# Synchronize all new conversation turns across projects
python seikoclaw.py sync-history

# Filter synchronization for a specific project
python seikoclaw.py sync-history --project SeikoClaw-Harness

# View sync watermarks and statistics
python seikoclaw.py sync-history --stats

# Semantic query across past memories
python seikoclaw.py memory --query "authentication decisions"
```

---

## Automatic Startup & Background Synchronization

To ensure your AI assistants always start with up-to-date memories from past sessions and across different projects, you can configure automatic synchronization on startup. Below are setup methods for **Antigravity** and **non-Antigravity** development environments.

### 🌐 Method 1: Google Antigravity (AGY) Lifecycle Hooks

Antigravity natively executes lifecycle hooks configured in JSON:

#### A. Global Setup (All Projects on Machine)
Create or edit `~/.gemini/config/hooks.json` (`C:\Users\<username>\.gemini\config\hooks.json` on Windows):
```json
{
  "openbrain-history-sync": {
    "enabled": true,
    "PreInvocation": [
      {
        "type": "command",
        "command": "python d:/DevWorkspace/SeikoClaw-Harness/.agents/hooks/sync-history.py",
        "timeout": 20
      }
    ]
  }
}
```

#### B. Workspace-Specific Setup
Add `.agents/hooks.json` to your project repository:
```json
{
  "openbrain-history-sync": {
    "enabled": true,
    "PreInvocation": [
      {
        "type": "command",
        "command": "python .agents/hooks/sync-history.py",
        "timeout": 20
      }
    ]
  }
}
```

---

### 🤖 Method 2: Claude Code (Anthropic CLI)

If you use **Claude Code**, configure automatic memory synchronization in your project's `CLAUDE.md`:

#### A. `CLAUDE.md` Project Guidelines
Add the following instruction to the top of your `CLAUDE.md`:
```markdown
# Session Startup Routine
On session initialization or when starting a new major task:
1. Run `python seikoclaw.py sync-history --limit 5` to ingest recent cross-project memories.
2. Query OpenBrain for relevant context: `python seikoclaw.py memory --query "<current-topic>"`.
```

#### B. Shell Wrapper / Alias
Add an alias to your shell profile (`~/.bashrc`, `~/.zshrc`, or PowerShell `$PROFILE`):
```bash
# Claude Code with automatic OpenBrain memory synchronization
alias claude-sync="python /path/to/seikoclaw-harness/seikoclaw.py sync-history && claude"
```

---

### 💻 Method 3: Cursor / Windsurf / VS Code

If you use Cursor, Windsurf, or VS Code, trigger memory sync automatically whenever you open a project folder:

#### A. `.vscode/tasks.json` (Auto-Run on Folder Open)
Create `.vscode/tasks.json` in your repository:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "OpenBrain Memory Sync",
      "type": "shell",
      "command": "python seikoclaw.py sync-history --limit 10",
      "runOptions": {
        "runOn": "folderOpen"
      },
      "presentation": {
        "reveal": "silent",
        "panel": "shared"
      }
    }
  ]
}
```

#### B. Cursor Rules (`.cursorrules`)
Add this directive to your `.cursorrules`:
```markdown
Before executing complex multi-file edits, query OpenBrain memory:
Run `python seikoclaw.py memory --query "<current feature or error>"`
To sync latest context: `python seikoclaw.py sync-history`
```

---

### 🦙 Method 4: Aider & Other CLI Agents

For **Aider**, **Ollama CLI**, or other terminal agents, create a lightweight launcher script:

#### Bash / Zsh (`~/bin/run-agent.sh`):
```bash
#!/usr/bin/env bash
# 1. Sync memory from recent transcripts
python /path/to/seikoclaw.py sync-history --limit 5
# 2. Launch Aider
aider "$@"
```

#### PowerShell (`profile.ps1`):
```powershell
function Invoke-AiderWithMemory {
    python d:\DevWorkspace\SeikoClaw-Harness\seikoclaw.py sync-history --limit 5
    aider $args
}
Set-Alias aider-sync Invoke-AiderWithMemory
```

---

### ⏰ Method 5: OS Background Heartbeat (Scheduled Task / Cron)

If you prefer background synchronization on a timer or at OS login without agent-specific configuration:

#### Windows (Task Scheduler via PowerShell):
```powershell
$Action = New-ScheduledTaskAction -Execute "python.exe" `
    -Argument "d:\DevWorkspace\SeikoClaw-Harness\seikoclaw.py sync-history" `
    -WorkingDirectory "d:\DevWorkspace\SeikoClaw-Harness"

$Trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "OpenBrain-History-Sync" -Action $Action -Trigger $Trigger
```

#### Linux / macOS (Crontab):
```bash
# Run OpenBrain history sync every 30 minutes
*/30 * * * * cd /path/to/seikoclaw-harness && python seikoclaw.py sync-history >/dev/null 2>&1
```

---

### 🪝 Method 6: Git Hook (Branch Switch / Post-Checkout)

Keep memory synchronized whenever you switch branches or pull changes:

Create `.git/hooks/post-checkout`:
```bash
#!/usr/bin/env bash
python seikoclaw.py sync-history --limit 5 >/dev/null 2>&1 &
```
Make executable: `chmod +x .git/hooks/post-checkout`.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- `sqlite3`
- (Optional) `chromadb` for vector-based search.

### 2. Installation
Clone this repository into your workspace or as a submodule:
```bash
git clone https://github.com/your-repo/seikoclaw-harness.git .agents
```

### 3. Bootstrapping a Project
Run the setup script to initialize the SeikoClaw directories in your current folder:
```bash
python .agents/scripts/setup_harness.py
```

### 4. Talking to your Agent
Tell your AI assistant:
> "I have the SeikoClaw harness installed. Please check `.agents/workflows/architect.md` for our planning loop and use the local skills in `.agents/skills` to complete my tasks."

---

## Using with Other LLMs (Claude, ChatGPT, Grok, etc.)

SeikoClaw is designed to be platform-agnostic. While it works seamlessly with advanced agents, you can manually "activate" these benefits in any LLM conversation by using the following prompting strategies.

### 1. The Bootstrap Prompt
If you are starting a fresh conversation with Claude or ChatGPT, paste this as your first message to ground the model in the SeikoClaw environment:

> "I am working in a SeikoClaw-enabled workspace. You have access to a `.agents/` directory containing modular **Skills** and **Workflows**. Before we begin, please:
> 1. List the contents of `.agents/skills` to understand your available capabilities.
> 2. Read `.agents/workflows/architect.md` to understand our standard planning process.
> 3. Always check `.master_wiki/` for project-specific standards before suggesting code changes.
> 
> Acknowledge when you are ready to proceed with the Architect phase of our task."

### 2. Activating a Specific Skill
When you want the LLM to focus on a specific type of work (e.g., refactoring), point it directly to the skill:
> "Use the `executor` skill in `.agents/skills/executor/SKILL.md` to implement the next task in our `task.md` file."

### 3. Maintaining State (Openbrain)
If your LLM has tool-use capabilities (like Claude's computer use or ChatGPT's data analyst), you can tell it to use the `openbrain/engine.py` script to save/load memories:
> "Run `python openbrain/engine.py` to record our architectural decision regarding the database migration so we don't forget it in future sessions."

---

## The "Skill" Specification
Each skill is a folder containing a `SKILL.md` file. It uses YAML frontmatter to describe its purpose to the AI agent:
```markdown
---
name: architect
description: Decomposes high-level goals into granular, verifiable tasks.
---
# Architect Skill
...
```

---

## License
MIT

