# SeikoClaw: Agentic Coding Harness

**SeikoClaw** is a modular framework for building AI-native development environments. It pairs a curated, high-signal library of developer and game-dev agent skills with **OpenBrain**, a lightweight Python sidecar that provides persistent memory, task dependency graphs with deterministic gating, declarative execution playbooks, execution security guardrails, and cross-project history synchronization.

---

## Live Showcase & A/B Case Study (`RawExerMart` vs. `ClawExerMart`)

Compare how an AI agent codes from the exact same prompt **without** vs. **with** the SeikoClaw Harness:

- **Interactive GitHub Pages Showcase & Split-Screen Sandbox**: [`https://saikojin.github.io/seikoclaw-harness/`](https://saikojin.github.io/seikoclaw-harness/) ([open directly in Executive Story view](https://saikojin.github.io/seikoclaw-harness/?view=executive))
- **Executive Story (3-Minute C-Suite One-Pager)**: [`docs/EXECUTIVE_STORY.md`](docs/EXECUTIVE_STORY.md)
- **Play Live `ClawExerMart` (With SeikoClaw Harness)**: [`https://saikojin.github.io/seikoclaw-harness/demos/clawexermart/index.html`](https://saikojin.github.io/seikoclaw-harness/demos/clawexermart/index.html) ([launch in `break-ui` worst-case stress mode](https://saikojin.github.io/seikoclaw-harness/demos/clawexermart/index.html?data=worst))
- **Play Live `RawExerMart` (Control Group Without Harness)**: [`https://saikojin.github.io/seikoclaw-harness/demos/rawexermart/index.html`](https://saikojin.github.io/seikoclaw-harness/demos/rawexermart/index.html)
- **Full Forensic Report & 12-Dimension Chart**: [`docs/EXERMART_CASE_STUDY.md`](docs/EXERMART_CASE_STUDY.md)
- **Source Repositories**: [`Saikojin/ClawExerMart`](https://github.com/Saikojin/ClawExerMart) vs. [`Saikojin/RawExerMart`](https://github.com/Saikojin/RawExerMart)

---

## 🎯 Highlights

- **24 First-Principle Engineering Directives**: Enforces zero-slop code hygiene, minimal diffs, boundary discipline, root-cause debugging, and empirical verification (`.agents/rules/principles.md`).
- **Tier 2 Skill Routing & Collision Evals**: Automated frontmatter linting, pairwise vocabulary collision detection, and canonical utterance routing benchmark (`evals/routing/`, `python seikoclaw.py eval-skills`).
- **Production Reference Checklists**: Industry-grade standards for Core Web Vitals (`performance-checklist`), WCAG 2.1 AA (`accessibility-checklist`), Definition of Done, and testing patterns (`references/`).
- **Declarative Execution Playbooks**: Standard operating procedures (`bug-fix`, `feature`, `hillclimb`, `refactoring`, `visual-parity`, `shipping`) that auto-expand into sequential DAG wisps with blocking verification gates.
- **Adversarial QA Gating**: Multi-model red-team review (`/interrogate`) paired with **Seikojin QA** Risk-Based Testing (100% stable pass mandate, zero visual punches).
- **Persistent Decision Trails & Vector Memory**: Ingests and vector-indexes structured TSV decision trails (`/show-me-your-work`) into SQLite and ChromaDB alongside conversation turns.
- **Cross-Harness Export & Namespace-Isolated Ingestion**: Export canonical skills to Claude, Codex, Pi, or Antigravity, or ingest external skill packs with namespace protection (`python seikoclaw.py import-skills`).
- **P0 Safety Guarantees**: Non-destructive defaults. Skill evolution stages candidates to `.agents/skills/.candidates/` instead of overwriting production files.
- **Pre-Execution Guardrails**: Cross-platform POSIX and PowerShell pre-exec safety hooks that intercept catastrophic shell commands (`rm -rf /`, `curl | bash`, forced git pushes) before execution.
- **Game Forge**: An autonomous end-to-end game creation pipeline from Socratic design critiques and GDDs to zero-install HTML5 Canvas playable prototypes.
- **Poly Haven CC0 Asset Pipeline**: Automated search, metadata inspection, and downloading of CC0 textures, HDRIs, and models with strict 2K resolution default gating and multi-engine adapters for Godot, Unity, Unreal, and Blender (`scripts/polyhaven.py`, `polyhaven-assets`).
- **Gameplay Atlas Offline Intelligence**: High-performance local SQLite FTS5 database and CLI query lever (`scripts/gameplay_atlas.py`, `gameplay-atlas`) indexing 280 structured game mechanics across 28 systems, complete with 4-stage core loops, player dilemmas, tunable parameters, shipped game cases, and Stage B micro-slice prototyping recipes.

---

## 📂 Repository Structure

```text
.
├── .agents/
│   ├── hooks/             # Security pre-exec guards & session-start routing
│   ├── rules/             # 24 First Principles & Graphify rules
│   ├── skills/            # Modular capability definitions (80+ canonical skills)
│   │   └── .candidates/   # Staged evolutionary skill candidates
│   └── workflows/         # Procedural guides (Architect, Shipper, etc.)
├── data/                  # Offline datasets & SQLite indexes (Gameplay Atlas DB & raw cache)
├── docs/                  # GitHub Pages Interactive Showcase & Architecture Docs
│   ├── index.html         # Interactive A/B Showcase (Executive Story + Engineering Audit)
│   ├── EXECUTIVE_STORY.md # 3-minute C-suite narrative one-pager
│   ├── demos/             # Embedded static builds of ClawExerMart & RawExerMart
│   └── assets/exermart/   # Non-headless visual verification captures (R1..R7)
├── evals/                 # Benchmark routing evaluation datasets
│   └── routing/           # Canonical utterance test suites
├── openbrain/             # Context Persistence & Sidecar Engine
│   ├── schema.sql         # Unified SQLite database schema
│   ├── memory_engine.py   # Tiered memory store, vector search & decision trails
│   ├── playbooks.py       # Declarative engineering playbooks
│   ├── task_graph.py      # Dependency DAG, playbook expansion & frontier
│   ├── gates.py           # QA, adversarial interrogation & human sign-off gates
│   ├── history_sync.py    # Per-conversation transcript synchronization
│   ├── vault.py           # Encrypted secrets store (AES-GCM)
│   └── watchdog.py        # Loop health patrol & circuit breaker
├── references/            # Production standards (CWV, a11y, DoD, Testing patterns)
├── scripts/               # Eval runners, setup & cross-harness skill exporter utilities
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

### 4. Cross-Harness Skill Export & Ingestion
Export and symlink skills for Claude Code, Codex, Pi, or Antigravity, or ingest external skill packs with namespace protection:
```bash
# Export skills to standard shared agents location
python seikoclaw.py export-skills --harness agents

# Symlink skills to Claude Code
python seikoclaw.py export-skills --harness claude --symlink

# Ingest external skill pack into SeikoClaw with namespace protection
python seikoclaw.py import-skills --source ../agent-skills --namespace addy
```

### 5. Deterministic Skill Routing & Collision Evaluation
Validate frontmatter, check vocabulary collisions, and run benchmark routing tests:
```bash
# Run deterministic Tier 2 skill catalog evaluation
python seikoclaw.py eval-skills
```

### 6. Memory & Decision Trail Querying
Search across past developer actions, transcripts, and architectural decision trails:
```bash
python seikoclaw.py memory --query "why was sqlite chosen over postgres"
```

### 7. Gameplay Atlas Mechanics Lookup & Prototyping Recipes
Query the offline SQLite FTS5 database of 280 game mechanics across 28 systems:
```bash
# Full-text search with optional system or tag filtering
python scripts/gameplay_atlas.py search "stamina" --system combat

# Inspect complete mechanic card (rules, loop, dilemmas, parameters, shipped cases)
python scripts/gameplay_atlas.py get combat-stamina-budget

# Extract Stage B micro-slice rapid prototyping recipe (firstStep, pitfall, test criteria)
python scripts/gameplay_atlas.py prototype-recipe automation-belt-routing

# Explore cross-system mechanic combinations & shipped game references
python scripts/gameplay_atlas.py combine combat farming
python scripts/gameplay_atlas.py cases "Factorio"
```

---

## 🎖️ Attribution & Upstream Credits

SeikoClaw builds upon foundational work from:
- **Matt Pocock**: Core developer skills, spec pipelines (`before-building`, `to-spec`, `to-tickets`, `implement`, `tdd`, `prototype`, `diagnosing-bugs`, `agent-authoring`).
- **David Andrej**: Architecture modeling, ADR decision trees, multi-perspective reviews (`codebase-design`, `adr`, `code-review`, `grill-me`, `handoff`).
- **Lauren Tan (`@poteto`)**: Cursor `pstack` plugin, 24 First Principles, 23 Playbooks, anti-slop hygiene (`unslop`, `deslop`, `no-comments`), `/interrogate`, `/arena`, `/blast-radius`, `/show-me-your-work`.
- **Michael Denyer**: `pstack-claude` multi-harness translation, SessionStart hooks, and open standard packaging.
- **Addy Osmani**: Production-grade engineering lifecycles, Tier 2 skill routing evals, Google SWE culture, Core Web Vitals (`performance-checklist`), and WCAG accessibility standards.
- **Poly Haven ([polyhaven.com](https://polyhaven.com/))**: Greg Zaal, Rob Tuytel, and the Poly Haven community for the 100% free CC0 PBR textures, HDRIs, and 3D models integrated into our game development tooling and visual parity pipelines.
- **Abhishek Barali & Contributors ([`awesome-gamedev-agent-skills`](https://github.com/gamedev-skills/awesome-gamedev-agent-skills))**: The 77-skill gamedev catalog across 12 game engines, disciplines, genres, and publishing workflows integrated under the `gamedev-*` namespace and dispatched via `game-router`.
- **Gameplay Atlas ([`gameplayatlas.loopyhop.com`](https://gameplayatlas.loopyhop.com/)) by Loopyhop**: The curated field guide of 280 game mechanics across 28 systems, loops, player dilemmas, parameters, shipped game cases, and prototyping recipes powering `gameplay-atlas` and Game Forge.
- **Saikojin (SeikoClaw)**: OpenBrain sidecar, QA test automation (`seikojin-qa`), execution security guardrails, and the **Game Forge** creation suite.

See [`CREDITS.md`](CREDITS.md) for full details.

---

## 📜 License
MIT License.
