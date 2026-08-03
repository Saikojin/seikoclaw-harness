Status: open
Labels: wayfinder:map

# Game Design Skills for Non-Coding Designers

## Destination

A complete agent skill/persona lineup that lets a **single non-coding person with game ideas** go from vague concept → structured design → testable prototype → iterate on feedback — without ever touching code, a terminal, or a game engine editor directly.

## Notes

- **Domain**: Game development (Godot 4, UE5, web prototypes)
- **User profile**: Has strong creative vision, cannot code, needs agents to be the hands
- **Skills every session should consult**: `seikoclaw-harness`, `interviewer`, `grilling`, `prototype`, `executor`
- **Standing preferences**: Each new skill should be a standalone `.agents/skills/<name>/SKILL.md` in SeikoClaw-Harness. Follow the existing skill format (YAML frontmatter + markdown body). Skills should be HITL-biased — the non-coder is always in the loop for creative decisions. Technical execution is AFK.
- **Existing infrastructure**: godot-mcp (Godot bridge), ArtistAgent (vision stage), Openbrain (memory), graphify (knowledge graphs)

## Decisions so far

- [01 · Game Design Critic](file:///d:/DevWorkspace/SeikoClaw-Harness/.scratch/game-design-skills/issues/01-game-design-critic.md) — Created dedicated `game-design-critic` skill focused on universal game feel pillars (10s/30s/5m loops, core fantasy, psychology) with dual inline doc updates & summary artifact outputs.
- [02 · GDD Generator](file:///d:/DevWorkspace/SeikoClaw-Harness/.scratch/game-design-skills/issues/02-gdd-generator.md) — Created dedicated `gdd-generator` skill synthesizing vision plans, critic reviews, and ingested notes into living `docs/design/GDD.md` specifications.
- [03 · Scope Surgeon](file:///d:/DevWorkspace/SeikoClaw-Harness/.scratch/game-design-skills/issues/03-scope-surgeon.md) — Created dedicated `scope-surgeon` skill to ruthlessly cut design scope to 30–90s micro-slices testing 1–2 verbs in `VERTICAL_SLICE_SPEC.md` format.
- [04 · Game Prototype Builder](file:///d:/DevWorkspace/SeikoClaw-Harness/.scratch/game-design-skills/issues/04-game-prototype-builder.md) — Created dedicated `game-prototype-builder` skill generating zero-dependency single-file HTML5 Canvas games with Web Audio synth sounds, live tuning sliders, and debug HUDs.
- [05 · Game Systems Modeler](file:///d:/DevWorkspace/SeikoClaw-Harness/.scratch/game-design-skills/issues/05-game-systems-modeler.md) — Created dedicated `game-systems-modeler` skill generating interactive Chart.js dashboards (`balance_simulator.html`) and persisting canonical game math into `docs/design/balance.json`.
- [06 · Playtest Feedback Loop](file:///d:/DevWorkspace/SeikoClaw-Harness/.scratch/game-design-skills/issues/06-playtest-feedback-loop.md) — Created dedicated `playtest-feedback-loop` skill using a Qualitative-to-Quantitative Heuristic Dictionary ("floaty" -> gravity diffs) + `PLAYTEST_RUNBOOK.md` iteration logging.
- [07 · Genre & Competitor Analysis](file:///d:/DevWorkspace/SeikoClaw-Harness/.scratch/game-design-skills/issues/07-genre-competitor-analysis.md) — Created dedicated AFK `genre-competitor-analysis` skill executing 5-point competitive matrix research and saving to `docs/design/COMPETITIVE_LANDSCAPE.md`.
- [08 · Mood Board Curator](file:///d:/DevWorkspace/SeikoClaw-Harness/.scratch/game-design-skills/issues/08-mood-board-curator.md) — Created dedicated `mood-board-curator` skill producing `mood_board.html` galleries and extracting `style_markers.json` to feed ArtistAgent's RAG pipeline while enforcing project style isolation.









## Not yet specified

- **Godot Build Runner**: How to automatically export Godot builds the designer can launch (connects to godot-mcp, but no skill wraps it for a non-coder)
- **UE5 Integration**: Whether/how to support Unreal Engine prototyping for ALIOZ, or whether browser prototypes suffice for design validation
- **Cross-Project Lore Consistency**: How the Adberrain universe lore stays consistent across AdberrainARPG, Tactical-Adberrain, and future entries
- **ArtistAgent ↔ Game Prototype Pipeline**: How generated art assets flow into prototypes and back
- **Automated Playtesting Bots**: Simulating 1000 combat rounds to find degenerate strategies (advanced, post-P1)
- **Non-Coder Architect Override**: How to make the Architect produce design-task checklists instead of code-task checklists when the user is a non-coder

## Out of scope

- Shipping a commercial game (this map is about the design-to-prototype-to-iterate loop, not production/launch)
- Engine selection decisions (already committed to Godot 4 and UE5 per project)
- Code architecture skills (codebase-design, TDD, sweep-loop — these serve the executor, not the designer)
