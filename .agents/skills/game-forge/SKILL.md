---
name: game-forge
description: Master autonomous framework for end-to-end game creation. Orchestrates design critique, GDD authoring, micro-slice slicing, zero-install HTML5 prototyping, asset generation, developer tooling, Visual Bar parity loops, and autonomous engine builds without requiring manual skill invocations.
author: Saikojin (SeikoClaw - Game Forge)
---

# Game Forge: Master Autonomous Game Creation Framework

The **Game Forge** framework is an end-to-end game creation orchestrator. It unifies modular game design, prototyping, asset generation, developer tooling, visual parity critic loops, and execution skills into an automated, sequential pipeline with strict Human-in-the-Loop (HITL) checkpoints and Stage-Gated Visual Parity validation.

Integrated with **[`game-router`](../game-router/SKILL.md)** and the 78-skill gamedev catalog (`gamedev-*`), Game Forge automatically discovers the project engine, binds genre mechanics, and coordinates specialized tools without manual intervention.

```
[Pitch / Idea] ──► (Stage A: Auto-Route, Brief & Locked Refs) ──► (Stage B: 30s Foundation Prototype)
                                    │                                              │
                                    ▼                                              ▼
                          [HITL Gate 1: GDD Review]                      [Gate B: Playable Loop Check]
                                                                                   │
                                                                                   ▼
[Shipped Game] ◄── (Stage E: Engine Build & Ship) ◄── (Stage D: SxS Visual Bar) ◄── (Stage C: Assets & Workbenches)
                                                             │
                                                             ▼
                                                    [Gate D*: Stuck Diagnoser]
```

---

## 1. Project Manifest & State Tracking

Game Forge maintains a single canonical manifest at `docs/design/game_manifest.json` (or `.scratch/<project>/game_manifest.json`):

```json
{
  "project_name": "GameTitle",
  "current_stage": "STAGE_A_BRIEF_AND_REFS",
  "active_hypothesis": "Parrying telegraphed attacks creates high-risk tension in 30s encounters",
  "core_verbs": ["move", "parry", "strike"],
  "target_engine": "godot",
  "bound_skills": [
    "game-router",
    "gamedev-godot-2d-movement",
    "gamedev-platformer",
    "gamedev-game-feel",
    "gamedev-save-systems"
  ],
  "artifacts": {
    "brief": "docs/design/BRIEF.md",
    "gdd": "docs/design/GDD.md",
    "refs_locked": "refs-locked/SOURCES.md",
    "visual_bar": "art/BAR.md",
    "vertical_slice": "docs/design/VERTICAL_SLICE_SPEC.md",
    "prototype_html": "prototypes/prototype.html",
    "balance_json": "docs/design/balance.json",
    "balance_simulator": "docs/design/balance_simulator.html",
    "tooling_architecture": "docs/design/GAME_TOOLING_ARCHITECTURE.md",
    "rounds_log": "captures/rounds.log",
    "task_list": "task.md"
  },
  "stage_history": []
}
```

---

## 2. The 5-Stage Autonomous Pipeline

### Stage A: Brief, Locked References & Deep Plan (Autonomous $\rightarrow$ HITL Gate 1)
1. **Intake Pitch & One-Call Skill Binding**: 
   - Execute **[`game-router`](../game-router/SKILL.md)** to fingerprint the project engine and bind the corresponding genre template (`gamedev-platformer`, `gamedev-roguelike`, `gamedev-card-game`, etc.) and discipline playbooks (`gamedev-game-feel`, `gamedev-save-systems`, `gamedev-game-ai`).
   - Store bound skills into `docs/design/game_manifest.json`.
2. **Execute `game-design-critic` & `gameplay-atlas` (Phase 1: Mechanics)**:
   - Query [`gameplay-atlas`](../gameplay-atlas/SKILL.md) (`python scripts/gameplay_atlas.py search "<verbs>" --json`) to discover 4-stage loops, player dilemmas, and shipped reference game cases.
   - Run Socratic inquiry utilizing the genre-specific stress-test matrix from [`game-design-critic`](../game-design-critic/SKILL.md).
   - Evaluate the **10-second loop** (moment-to-moment verb satisfaction).
   - Evaluate the **30-second loop** (encounter tactics and risk/reward).
   - Evaluate the **5-minute loop** (session hook & reward).
   - Check for degenerate strategies (spamming 1 move, corner camping).
3. **Execute `genre-competitor-analysis` & Lock References**:
   - Identify 3–5 shipped reference games in the target genre/visual tier.
   - Save high-res screenshots to `refs-locked/` with provenance documented in `refs-locked/SOURCES.md`.
   - Author `art/BAR.md` defining the non-negotiable **Visual Bar** (Silhouette, Value Hierarchy, Palette Harmony, Resolution Density, Motion Polish).
4. **Execute `gdd-generator`, `json-canvas` & Author Foundations Matrix**:
   - Compile findings into `docs/design/GDD.md`, `docs/design/BRIEF.md`, and generate visual verb loops/quest trees into `docs/design/quest_graph.canvas`.
   - Read [`GAME_FOUNDATIONS_BASELINE.md`](GAME_FOUNDATIONS_BASELINE.md) and construct the **16-Pillar Foundations Baseline Matrix** with proposed defaults tailored to the target genre and explicit user override options.
5. **HITL Gate 1 Checkpoint (Interactive Proposal & Foundations Callout)**:
   - Present GDD summary, locked refs, Visual Bar (`art/BAR.md`), and the **Proposed Foundations Baseline Matrix**.
   - Explicitly prompt the user with the Foundations Callout: *"Review the proposed 16 baseline options. If your design requires modifications (e.g. permadeath instead of restart, timer instead of HP, or mouse-only controls), call out your overrides now before prototyping begins!"*
   - Record approved baseline parameters into `docs/design/game_manifest.json` under `foundations_config`.

---

### Stage B: Scope Carving & Playable Foundation (Autonomous $\rightarrow$ Gate B)
*Triggered immediately upon GDD approval.*

1. **Execute `scope-surgeon` & `gameplay-atlas` Prototyping Grounding**:
   - Query `python scripts/gameplay_atlas.py prototype-recipe <mechanic-id>` to ingest the micro-slice `firstStep` into the slice objective, `pitfall` into non-goals, and `test` directly into the playable verification checklist.
   - Strip non-essential meta-systems; isolate 1 arena, 1–2 verbs, and 1 enemy into `docs/design/VERTICAL_SLICE_SPEC.md`.
2. **Execute `game-prototype-builder` & Rapid Greybox Protocols**:
   - Apply [`gamedev-prototype-fast`](../gamedev-prototype-fast/SKILL.md), [`gamedev-physics-tuning`](../gamedev-physics-tuning/SKILL.md), and [`gamedev-input-systems`](../gamedev-input-systems/SKILL.md).
   - Build a self-contained, zero-dependency `prototypes/prototype.html` (HTML5 Canvas + Web Audio synth).
   - Use clean geometric placeholders (boxes/capsules) to focus purely on core loop feel.
   - Embed an on-screen Debug HUD and **Live Parameter Tuning Sliders** (e.g. `Speed`, `Cooldown`, `ParryWindow`).
   - *3D Prototyping Option*: For 3D titles, trigger `blender-developer` to generate blockout arenas, collision geometry, and export `.glb` to `prototypes/assets/`. Must pass `[GATE: BLENDER_VALIDATION]` (0 non-manifold edges, applied scale, min Z=0).
3. **Execute `game-systems-modeler` & `obsidian-bases`**:
   - Seed baseline variables with atlas parameters (`python scripts/gameplay_atlas.py get <mechanic-id> --json`).
   - Write `docs/design/balance.json` (canonical baseline curves), `docs/design/balance_simulator.html`, and dynamic property database `docs/design/balance.base`.
4. **Gate B (Loop Validation)**:
   - Critic verifies mechanics loop with strict verdict: `"B-PASS (loop only, NOT A VISUAL WIN)"`.
   - Prompt user for playtest feel feedback.

---

### Stage C: Staged Art Pipeline & Authoring Workbenches (Autonomous $\rightarrow$ HITL Gate 3)
*Triggered upon loop sign-off.*

1. **Execute `playtest-feedback-loop`**: Map qualitative feedback into parameter changes.
2. **Execute Staged Art Pipeline (C0..C5)**:
   - `C0 - Palettes & Shading`: Generate color ramps and lighting models using [`gamedev-shader-programming`](../gamedev-shader-programming/SKILL.md).
   - `C1 - Environment & Terrain`: Modular tilesets / backdrops into `assets/`. For 3D or isometric environments, use `blender-developer` to query [`polyhaven-assets`](../polyhaven-assets/SKILL.md) for CC0 textures/HDRIs or generate procedural blockouts and props (protected by `[GATE: BLENDER_VALIDATION]`).
   - `C2 - Hero & Enemy Sprites/Models`: Character layers, animations, or meshes via [`gamedev-create-game-assets`](../gamedev-create-game-assets/SKILL.md).
     - *For 3D Games*: Use `blender-developer` for procedural mesh modeling, Poly Pizza low-poly imports, armature rigging, and `.glb` exports. Every asset prompt/description is stored in `assets/metadata/<asset>.json`, and the asset must pass `[GATE: BLENDER_VALIDATION]`.
     - *For 2D Games*: Use `blender-developer` to render 8-directional isometric sprite sheets from 3D models at locked pixel resolutions and palette specs.
   - `C3 - VFX & Particles`: Impact sparks, hit trails, screen shake shaders via [`gamedev-game-feel`](../gamedev-game-feel/SKILL.md) and [`gamedev-camera-systems`](../gamedev-camera-systems/SKILL.md).
   - `C4 - Audio & UI HUD`: Procedural SFX, theme music, tactile HUD styling via [`gamedev-audio-design`](../gamedev-audio-design/SKILL.md) and [`gamedev-game-ui-ux`](../gamedev-game-ui-ux/SKILL.md).
   - `C5 - Asset Ledger`: Verify all assets match `art/BAR.md` resolution and palette specs, tracking deliverables in `docs/design/assets.base`. No asset may be entered without certified validation report.
3. **Execute `game-developer` (Tooling Architecture)**:
   - Build schema validators (`validate_data.py`) and browser workbenches (e.g. `tools/map_painter.html`, `tools/sound_workbench.html`).
   - *For TTRPG & Tactical Titles*: Execute `obsidian-atlas-vtt` to author `.atlasmap` test scenes, emit `.atlas-collection.zip` bundles, or ingest `.uvtt` maps for instant in-vault playtesting.
4. **HITL Gate 3 Checkpoint**: Verify authoring workbenches and asset ledger.

---

### Stage D: Side-by-Side (SxS) Visual Bar Parity Loop (Autonomous $\rightarrow$ Critic WIN)
*Triggered upon asset delivery.*

1. **The Parity Cycle (`Capture -> Critic -> Punch List -> Builder -> Re-capture`)**:
   - **Capture**: Automated headless browser / screen capture generates in-game stills (`captures/R<n>_frame.png`).
     - *For 3D in Blender*: invoke `look(mode="angles")` to generate 4-view contact sheets and `scripts/fetch_asset_references.py` to acquire web ground-truth reference images matching the asset description.
     - *For Obsidian / Atlas VTT*: invoke `obsidian dev:screenshot path=captures/R<n>_frame.png` for automated headless capture of the active vault canvas.
   - **SxS Composite**: Pair capture side-by-side with matched reference using `scripts/fetch_asset_references.py composite`.
   - **Execute `game-design-critic` (Phase 2: Visual Parity)**: Run critique against `art/BAR.md`.
     - *If FAIL*: Generate structured defect punch items (`[Still | Matched Ref | Region | Observed Defect | Ref Target | Done-When | BPY Fix]`).
     - *Builder Round*: Implement targeted visual fixes for punch items using in-scene BPY recipes.
     - *Re-capture & Re-score*: Log delta in `captures/rounds.log`.
2. **Stuck-Loop Diagnoser ($D^*$ Protocol)**:
   - If 3+ consecutive rounds fail the hard gate without visual convergence, pause Builder punches.
   - Spin up a Diagnoser subagent to inspect render traces, shader code, and draw order before resuming.
3. **Post-WIN Harsh Visual Read ($D^{**}$ Gate)**:
   - After Critic returns `WIN`, Orchestrator independently reviews full-res stills and SxS composites.
   - If visual cohesion, proportions, or perspective fail, void the WIN and continue iteration.

---

### Stage E: Autonomous Engine Build, Verification & Handoff
1. **Execute `architect` / `seikoclaw-architect`**: Decompose full engine implementation into `task.md` with explicit `[GATE: VISUAL_CRITIC]` and `[GATE: QA]` contracts.
2. **Execute `implement` / `seikoclaw-executor` + Engine Skills Loop**:
   - Automatically dispatches the detected engine skills resolved by `game-router`:
     - **Godot**: [`gamedev-godot-gdscript`](../gamedev-godot-gdscript/SKILL.md), [`gamedev-godot-nodes-scenes`](../gamedev-godot-nodes-scenes/SKILL.md), [`gamedev-godot-tilemap`](../gamedev-godot-tilemap/SKILL.md), [`gamedev-godot-gdscript-headless-testing`](../gamedev-godot-gdscript-headless-testing/SKILL.md), [`godot-developer`](../godot-developer/SKILL.md).
     - **Unity**: [`gamedev-unity-csharp-scripting`](../gamedev-unity-csharp-scripting/SKILL.md), [`gamedev-unity-input-system`](../gamedev-unity-input-system/SKILL.md), [`gamedev-unity-scriptableobjects`](../gamedev-unity-scriptableobjects/SKILL.md), [`unity-developer`](../unity-developer/SKILL.md).
     - **Unreal**: [`gamedev-unreal-blueprints`](../gamedev-unreal-blueprints/SKILL.md), [`gamedev-unreal-cpp-gameplay`](../gamedev-unreal-cpp-gameplay/SKILL.md), [`gamedev-unreal-niagara`](../gamedev-unreal-niagara/SKILL.md), [`unreal-developer`](../unreal-developer/SKILL.md).
     - **Rust / Bevy**: [`gamedev-bevy-ecs`](../gamedev-bevy-ecs/SKILL.md).
     - **Go / Ebitengine**: [`gamedev-ebitengine-game`](../gamedev-ebitengine-game/SKILL.md).
     - **Web Engines**: [`gamedev-phaser-core`](../gamedev-phaser-core/SKILL.md), [`gamedev-pixijs-rendering`](../gamedev-pixijs-rendering/SKILL.md), [`gamedev-threejs-scene-setup`](../gamedev-threejs-scene-setup/SKILL.md).
3. **Execute `seikojin-qa`**: Run full automated regression suites and visual defect certifications.
4. **Publish / Handoff**: Deploy to platform via [`gamedev-steam-publish`](../gamedev-steam-publish/SKILL.md) or [`gamedev-itch-publish`](../gamedev-itch-publish/SKILL.md), delivering verified game build, source tree, locked assets, and `rounds.log`.

---

## 3. Invocation Triggers

Use any of the following to start or resume Game Forge:
- `/game-forge`
- `/game-router`
- *"Let's build a video game about [idea]"*
- *"Run game-forge on [project]"*
- *"Resume game-forge stage"*
