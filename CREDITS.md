# Credits & Upstream Attribution

SeikoClaw Harness is built upon and inspired by pioneering work from the AI agent and developer tooling community. We gratefully acknowledge the creators and maintainers of upstream skills, patterns, and architectures.

---

## 🎖️ Upstream Creators & Maintainers

### 1. Matt Pocock ([@mattpocockuk](https://github.com/mattpocock))
Many core developer workflows, spec pipelines, and prompt ergonomics in SeikoClaw were adapted from Matt Pocock's foundational agent skill work:
- **Spec & Planning**: `before-building`, `to-spec` (incorporating `to-prd`), `to-tickets` (incorporating `to-issues`), `wayfinder`, `wizard`, `research`
- **Execution & Feedback**: `implement` (incorporating `implement-spec`), `tdd`, `prototype`, `diagnosing-bugs`, `resolving-merge-conflicts`, `triage`, `pr`
- **Agent Authoring**: `agent-authoring` (incorporating `writing-for-agents`, `writing-great-skills`, `writing-beats`, `writing-fragments`, `writing-shape`)

### 2. David Andrej ([@davidandrej](https://github.com/davidandrej))
Key architectural decision-making, domain design, and multi-perspective review workflows were adapted from David Andrej's agent blueprints:
- **Architecture & Modeling**: `codebase-design` (domain modeling, design-it-twice, context mapping), `adr` (Architecture Decision Records)
- **Deep Alignment**: `grill-me` (stress-testing against domain models, ContextContent, and design-it-twice principles)
- **Review & Handoff**: `code-review` (parallel Spec & Standards reviewer agents), `handoff`

### 3. Lauren Tan ([@poteto](https://github.com/poteto)) & Cursor Team
High-rigor engineering playbooks, anti-slop code hygiene, and verification disciplines from Cursor's official `pstack` plugin:
- **Engineering Principles**: 24 First-Principle Engineering Directives (`laziness-protocol`, `fix-root-causes`, `boundary-discipline`, `prove-it-works`, `foundational-thinking`, `attack-the-premise`, etc.).
- **Anti-Slop & Quality**: `no-comments` (Comment Sicko), `unslop`, `deslop`, `blast-radius`, `benchmark-checklist`, `explain-the-number`.
- **Multi-Agent & Review**: `interrogate` (multi-model adversarial red team), `arena` (competitive multi-candidate synthesis), `swarm` (fan-out parallel workers).
- **Workflows & Decision Trails**: `show-me-your-work` (TSV decision trails), `how`, `why`, `teach`, `create-verification-skill`, `maintain-verification-skill`, `figure-it-out`.

### 4. Michael Denyer ([@michael-denyer](https://github.com/michael-denyer))
Cross-harness translation layer, multi-environment hooks, and open standard packaging from `pstack-claude`:
- **Cross-Harness Translation**: SessionStart routing hooks (`session-start.sh` / `session-start.ps1`), cross-platform skill symlinking, and multi-model effort matrix conventions.

### 5. Addy Osmani ([@addyosmani](https://github.com/addyosmani))
Production-grade software engineering lifecycles, evaluation suites, and performance standards from `addyosmani/agent-skills`:
- **Evaluation Discipline**: Tier 2 deterministic skill routing evaluation, description vocabulary collision detection (`scripts/eval_skill_routing.py`), and automated trigger verification (`evals/routing/`).
- **Engineering References**: Universal Definition of Done (`references/definition-of-done.md`), Core Web Vitals targets (`references/performance-checklist.md`), WCAG 2.1 AA standards (`references/accessibility-checklist.md`), and testing patterns (`references/testing-patterns.md`).
- **Google SWE Culture**: Hyrum's Law, Beyoncé Rule, test pyramid (80/15/5), DAMP over DRY, and trunk-based deployment principles embedded into review and testing workflows.

### 6. Saikojin / SeikoClaw ([@Saikojin](https://github.com/Saikojin))
The autonomous infrastructure sidecar, QA test automation suites, multi-agent coordination, and Game Forge pipeline:
- **OpenBrain Sidecar**: SQLite + ChromaDB memory engines, Task Graph DAG with deterministic gating and declarative playbooks, Health Patrol watchdog, AES-GCM secrets vault, conversation history sync, persistent decision trails.
- **Autonomous Infrastructure**: `seikoclaw-harness`, `seikojin-qa` (RBT, adversarial gating & QA engineer cabinet), `seikoclaw-red-team`, `seikoclaw-operating-map`, `seikoclaw-shipper`, `seikoclaw-skill-extractor`, `seikoclaw-test-memory`, `seikoclaw-frontend-taste`, `seikoclaw-goal-prompter`, `seikoclaw-ingestor`, `seikoclaw-browser-qa-workflow`, `agent-guardrails`, `agent-self-scheduling`, `distribute-skills`, `architect`, `coverage-loop`, `sweep-loop`, `status`, `learnings`, `modernize`, `interviewer`, `youtube-transcript`.
- **Game Forge Suite**: `game-forge`, `game-router`, `game-design-critic`, `scope-surgeon`, `gdd-generator`, `game-systems-modeler`, `game-prototype-builder`, `mood-board-curator`, `asset-generator`, `game-developer`, `genre-competitor-analysis`, `playtest-feedback-loop`.

### 7. Poly Haven ([polyhaven.com](https://polyhaven.com/))
Open public library for CC0 3D assets, PBR textures, and environment HDRIs, founded by Greg Zaal and Rob Tuytel:
- **CC0 Asset Infrastructure**: Powers the `polyhaven-assets` skill and `scripts/polyhaven.py` pipeline.
- **PBR Realism & Visual Parity**: Supplies photorealistic environment lighting, ground textures, and 3D props that anchor Game Forge's visual parity critique against locked shipped-game references without paywalls or restrictive licensing.
- **Licensing**: All Poly Haven content is released under the [Creative Commons 0 (CC0)](https://creativecommons.org/publicdomain/zero/1.0/) public domain dedication. Support their work on [Patreon](https://www.patreon.com/polyhaven).

### 8. Abhishek Barali & the `awesome-gamedev-agent-skills` Contributors ([gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills))
The comprehensive, 77-skill catalog for game engines, genres, disciplines, and workflow automation:
- **Engine Coverage**: Portable SKILL.md playbooks for Godot 4.7, Unity 6.3 LTS, Unreal Engine 5.8, Ebitengine, Web engines (Phaser 4, PixiJS 8, Three.js), Bevy, Defold, LÖVE, Pygame, and Roblox Luau.
- **Game Design & Disciplines**: Cross-engine foundations for AI behavior trees, Utility AI, save systems, audio mixing/ducking, procedural generation, camera systems, and physics feel tuning.
- **Genre Templates & Workflows**: Platformer, roguelike, RPG, card game/deckbuilder, survival crafting, tower defense, visual novel, FPS, puzzle, game jam, and store publishing (`itch-publish`, `steam-publish`).
- **Licensing**: Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). All imported skills in SeikoClaw are isolated under the `gamedev-*` namespace and dispatched via `game-router`.

### 9. Gameplay Atlas by Loopyhop ([gameplayatlas.loopyhop.com](https://gameplayatlas.loopyhop.com/))
The definitive field guide to game mechanics created by Loopyhop:
- **Mechanics Catalog**: 280 structured game mechanics across 28 systems (combat, movement, deckbuilding, progression, survival, automation, building, cooking, gathering, matching, narrative, projectiles, command, farming, fishing, inventory, puzzles, relationships, cooperation, defense, ecology, allocation, driving, rhythm, exploration) and 16 tags (`planning`, `risk`, `spatial`, `optimization`, etc.).
- **Rich Design Breakdown**: Every entry provides 4-stage core player loops, player dilemmas and trade-offs, tunable parameters with documented psychological and pacing effects, real shipped game implementation cases with official wiki citations and reference images (e.g. Factorio, Satisfactory, Celeste, Hades, Elden Ring, Dark Souls III, Stardew Valley), cross-system combinations, and concrete micro-slice rapid prototyping recipes (`firstStep`, `pitfall`, `test`).
- **Integration in SeikoClaw**: Offline SQLite FTS5 database (`data/gameplay_atlas.db`), automated sync scraper (`scripts/sync_gameplay_atlas.py`), high-performance CLI query lever (`scripts/gameplay_atlas.py`), agent skill (`gameplay-atlas`), and deep integration into Game Forge (Stage A GDD loops, Stage B micro-slice specs & test criteria, Stage C parameter tuning) and `game-router`.
- **Source & Attribution**: Content and source provenance available at [gameplayatlas.loopyhop.com/about/](https://gameplayatlas.loopyhop.com/about/).

---

## 📜 License & Usage
All adapted skills maintain compliance with their respective open licenses (MIT / Apache 2.0 / CC0). Derivative improvements, security guardrails, candidate skill staging, and sidecar tooling are provided under the MIT License. Poly Haven assets remain under Creative Commons 0 (CC0). Imported `gamedev-*` skills remain under the Apache License 2.0. Gameplay Atlas mechanics taxonomy and reference metadata are attributed to Loopyhop ([gameplayatlas.loopyhop.com](https://gameplayatlas.loopyhop.com/)).
