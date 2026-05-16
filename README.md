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
