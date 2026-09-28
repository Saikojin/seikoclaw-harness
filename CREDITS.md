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

### 3. Saikojin / SeikoClaw ([@Saikojin](https://github.com/Saikojin))
The autonomous infrastructure sidecar, QA test automation suites, multi-agent coordination, and Game Forge pipeline:
- **OpenBrain Sidecar**: SQLite + ChromaDB memory engines, Task Graph DAG with deterministic gating, Health Patrol watchdog, AES-GCM secrets vault, conversation history sync.
- **Autonomous Infrastructure**: `seikoclaw-harness`, `seikojin-qa` (RBT & QA engineer cabinet), `seikoclaw-red-team`, `seikoclaw-operating-map`, `seikoclaw-shipper`, `seikoclaw-skill-extractor`, `seikoclaw-test-memory`, `seikoclaw-frontend-taste`, `seikoclaw-goal-prompter`, `seikoclaw-ingestor`, `seikoclaw-browser-qa-workflow`, `agent-guardrails`, `agent-self-scheduling`, `distribute-skills`, `architect`, `coverage-loop`, `sweep-loop`, `status`, `learnings`, `modernize`, `interviewer`, `youtube-transcript`.
- **Game Forge Suite**: `game-forge`, `game-design-critic`, `scope-surgeon`, `gdd-generator`, `game-systems-modeler`, `game-prototype-builder`, `mood-board-curator`, `asset-generator`, `game-developer`, `genre-competitor-analysis`, `playtest-feedback-loop`.

---

## 📜 License & Usage
All adapted skills maintain compliance with their respective open licenses. Derivative improvements, security guardrails, candidate skill staging, and sidecar tooling are provided under the MIT License.
