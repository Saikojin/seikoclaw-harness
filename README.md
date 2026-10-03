# SeikoClaw: Agentic Coding Harness

**SeikoClaw** is a modular framework for building AI-native development environments. It pairs a curated, high-signal library of developer and game-dev agent skills with **OpenBrain**, a lightweight Python sidecar that provides persistent memory, task dependency graphs with deterministic gating, declarative execution playbooks, execution security guardrails, and cross-project history synchronization.

---

## 🎯 Highlights

- **24 First-Principle Engineering Directives**: Enforces zero-slop code hygiene, minimal diffs, boundary discipline, root-cause debugging, and empirical verification (`.agents/rules/principles.md`).
- **Declarative Execution Playbooks**: Standard operating procedures (`bug-fix`, `feature`, `hillclimb`, `refactoring`, `visual-parity`, `shipping`) that auto-expand into sequential DAG wisps with blocking verification gates.
- **Adversarial QA Gating**: Multi-model red-team review (`/interrogate`) paired with **Seikojin QA** Risk-Based Testing (100% stable pass mandate, zero visual punches).
- **Persistent Decision Trails & Vector Memory**: Ingests and vector-indexes structured TSV decision trails (`/show-me-your-work`) into SQLite and ChromaDB alongside conversation turns.
- **Cross-Harness Exportability**: Distribute and symlink canonical skills to Claude Code, Codex, Pi, Antigravity, or OpenCode with a single command.
- **P0 Safety Guarantees**: Non-destructive defaults. Skill evolution stages candidates to `.agents/skills/.candidates/` instead of overwriting production files.
- **Pre-Execution Guardrails**: Cross-platform POSIX and PowerShell pre-exec safety hooks that intercept catastrophic shell commands (`rm -rf /`, `curl | bash`, forced git pushes) before execution.
- **Game Forge**: An autonomous end-to-end game creation pipeline from Socratic design critiques and GDDs to zero-install HTML5 Canvas playable prototypes.

---

## 📂 Repository Structure

```text
.
├── .agents/
│   ├── hooks/             # Security pre-exec guards & session-start routing
│   ├── rules/             # 24 First Principles & Graphify rules
│   ├── skills/            # Modular capability definitions (70 canonical skills)
│   │   └── .candidates/   # Staged evolutionary skill candidates
│   └── workflows/         # Procedural guides (Architect, Shipper, etc.)
├── openbrain/             # Context Persistence & Sidecar Engine
│   ├── schema.sql         # Unified SQLite database schema
│   ├── memory_engine.py   # Tiered memory store, vector search & decision trails
│   ├── playbooks.py       # Declarative engineering playbooks
│   ├── task_graph.py      # Dependency DAG, playbook expansion & frontier
│   ├── gates.py           # QA, adversarial interrogation & human sign-off gates
│   ├── history_sync.py    # Per-conversation transcript synchronization
│   ├── vault.py           # Encrypted secrets store (AES-GCM)
│   └── watchdog.py        # Loop health patrol & circuit breaker
├── scripts/               # Setup & cross-harness skill exporter utilities
├── templates/             # Task & project vision templates
├── tests/                 # Subsystem verification test suite
├── CREDITS.md             # Upstream authors & attribution
├── seikoclaw.py           # Management CLI & autonomous execution engine
└── .seikoclaw.yaml.example # Optional workspace configuration template
```

---

## 🩺 System Diagnostics (`seikoclaw doctor`)

Verify all sidecar subsystems, databases, and safety guards on your machine with a single command:
```bash
python seikoclaw.py doctor
```

---

## 🚀 Core CLI Commands

### 1. Declarative Task Creation with Playbooks
Create a task and auto-expand it into sequential DAG steps with blocking gates:
```bash
# Create bug-fix task (expands to: repro -> root cause -> fix -> verify -> blast radius -> deslop)
python seikoclaw.py task --title "Fix login session drift" --playbook bug-fix

# Create metric hillclimb optimization task
python seikoclaw.py task --title "Optimize vector query latency" --playbook hillclimb
```

### 2. Task Execution & Sandboxing
Execute commands within an isolated, git-backed sandbox branch. Review the branch directly, or pass `--auto-merge` to merge on success:
```bash
# Execute task in sandbox branch (leaves branch checked out for review)
python seikoclaw.py execute --task "sc-101" --command "pytest tests/" --sandbox

# Auto-merge sandbox branch back to main on verification success
python seikoclaw.py execute --task "sc-101" --command "pytest tests/" --verify "pytest tests/" --sandbox --auto-merge
```

### 3. QA & Adversarial Gate Certification
Certify gates to unlock downstream ready frontier tasks:
```bash
# Certify Seikojin QA gate (100% pass mandate on Rabbit Path)
python seikoclaw.py gate --task "sc-101.5" --certify-qa --worker "Seikojin-QA"

# Certify Adversarial Interrogation gate (multi-model red team)
python seikoclaw.py gate --task "sc-101.6" --certify-adversarial --worker "Adversarial-Reviewer"
```

### 4. Cross-Harness Skill Export
Export and symlink skills for Claude Code, Codex, Pi, or Antigravity:
```bash
# Export skills to standard shared agents location
python seikoclaw.py export-skills --harness agents

# Symlink skills to Claude Code
python seikoclaw.py export-skills --harness claude --symlink
```

### 5. Memory & Decision Trail Querying
Search across past developer actions, transcripts, and architectural decision trails:
```bash
python seikoclaw.py memory --query "why was sqlite chosen over postgres"
```

---

## 🎖️ Attribution & Upstream Credits

SeikoClaw builds upon foundational work from:
- **Matt Pocock**: Core developer skills, spec pipelines (`before-building`, `to-spec`, `to-tickets`, `implement`, `tdd`, `prototype`, `diagnosing-bugs`, `agent-authoring`).
- **David Andrej**: Architecture modeling, ADR decision trees, multi-perspective reviews (`codebase-design`, `adr`, `code-review`, `grill-me`, `handoff`).
- **Lauren Tan (`@poteto`)**: Cursor `pstack` plugin, 24 First Principles, 23 Playbooks, anti-slop hygiene (`unslop`, `deslop`, `no-comments`), `/interrogate`, `/arena`, `/blast-radius`, `/show-me-your-work`.
- **Michael Denyer**: `pstack-claude` multi-harness translation, SessionStart hooks, and open standard packaging.
- **Saikojin (SeikoClaw)**: OpenBrain sidecar, QA test automation (`seikojin-qa`), execution security guardrails, and the **Game Forge** creation suite.

See [`CREDITS.md`](CREDITS.md) for full details.

---

## 📜 License
MIT License.
