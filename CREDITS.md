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
- **Game Forge Suite**: `game-forge`, `game-design-critic`, `scope-surgeon`, `gdd-generator`, `game-systems-modeler`, `game-prototype-builder`, `mood-board-curator`, `asset-generator`, `game-developer`, `genre-competitor-analysis`, `playtest-feedback-loop`.

---

## 📜 License & Usage
All adapted skills maintain compliance with their respective open licenses (MIT / Apache 2.0). Derivative improvements, security guardrails, candidate skill staging, and sidecar tooling are provided under the MIT License.
