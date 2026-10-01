---
name: game-forge
description: Master autonomous framework for end-to-end game creation. Orchestrates design critique, GDD authoring, micro-slice slicing, zero-install HTML5 prototyping, asset generation, developer tooling, Visual Bar parity loops, and autonomous engine builds without requiring manual skill invocations.
author: Saikojin (SeikoClaw - Game Forge)
---

# Game Forge: Master Autonomous Game Creation Framework

The **Game Forge** framework is an end-to-end game creation orchestrator. It unifies modular game design, prototyping, asset generation, developer tooling, visual parity critic loops, and execution skills into an automated, sequential pipeline with strict Human-in-the-Loop (HITL) checkpoints and Stage-Gated Visual Parity validation.

Instead of manually typing separate skills at every step, **Game Forge** manages the entire lifecycle autonomously:

```
[Pitch / Idea] ──► (Stage A: Design & Locked Refs) ──► (Stage B: 30s Foundation Prototype)
                             │                                         │
                             ▼                                         ▼
                   [HITL Gate 1: GDD Review]                 [Gate B: Playable Loop Check]
                                                                       │
                                                                       ▼
[Shipped Game] ◄── (Stage D: SxS Visual Bar Loop) ◄── (Stage C: Assets & Tooling Workbenches)
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
1. **Intake Pitch**: Receive the user's game idea, genre, and aesthetic direction.
2. **Execute `game-design-critic` (Phase 1: Mechanics)**:
   - Evaluate the **10-second loop** (moment-to-moment verb satisfaction).
   - Evaluate the **30-second loop** (encounter tactics and risk/reward).
   - Evaluate the **5-minute loop** (session hook & reward).
   - Check for degenerate strategies (spamming 1 move, corner camping).
3. **Execute `genre-competitor-analysis` & Lock References**:
   - Identify 3–5 shipped reference games in the target genre/visual tier.
   - Save high-res screenshots to `refs-locked/` with provenance documented in `refs-locked/SOURCES.md`.
   - Author `art/BAR.md` defining the non-negotiable **Visual Bar** (Silhouette, Value Hierarchy, Palette Harmony, Resolution Density, Motion Polish).
4. **Execute `gdd-generator`**: Compile findings into `docs/design/GDD.md` and `docs/design/BRIEF.md`.
5. **HITL Gate 1 Checkpoint**: Present GDD summary, locked refs, and Visual Bar to user for approval.

---

### Stage B: Scope Carving & Playable Foundation (Autonomous $\rightarrow$ Gate B)
*Triggered immediately upon GDD approval.*

1. **Execute `scope-surgeon`**:
   - Strip non-essential meta-systems; isolate 1 arena, 1–2 verbs, and 1 enemy into `docs/design/VERTICAL_SLICE_SPEC.md`.
2. **Execute `game-prototype-builder`**:
   - Build a self-contained, zero-dependency `prototypes/prototype.html` (HTML5 Canvas + Web Audio synth).
   - Use clean geometric placeholders (boxes/capsules) to focus purely on core loop feel.
   - Embed an on-screen Debug HUD and **Live Parameter Tuning Sliders** (e.g. `Speed`, `Cooldown`, `ParryWindow`).
3. **Execute `game-systems-modeler`**:
   - Write `docs/design/balance.json` (canonical baseline curves) and `docs/design/balance_simulator.html`.
4. **Gate B (Loop Validation)**:
   - Critic verifies mechanics loop with strict verdict: `"B-PASS (loop only, NOT A VISUAL WIN)"`.
   - Prompt user for playtest feel feedback.

---

### Stage C: Staged Art Pipeline & Authoring Workbenches (Autonomous $\rightarrow$ HITL Gate 3)
*Triggered upon loop sign-off.*

1. **Execute `playtest-feedback-loop`**: Map qualitative feedback into parameter changes.
2. **Execute Staged Art Pipeline (C0..C5)**:
   - `C0 - Palettes & Shading`: Generate color ramps and lighting models.
   - `C1 - Environment & Terrain`: Modular tilesets / backdrops into `assets/`.
   - `C2 - Hero & Enemy Sprites/Models`: Character layers, animations, or Blender meshes.
   - `C3 - VFX & Particles`: Impact sparks, hit trails, screen shake shaders.
   - `C4 - Audio & UI HUD`: Procedural SFX, theme music, tactile HUD styling.
   - `C5 - Asset Ledger`: Verify all assets match `art/BAR.md` resolution and palette specs.
3. **Execute `game-developer` (Tooling Architecture)**:
   - Build schema validators (`validate_data.py`) and browser workbenches (e.g. `tools/map_painter.html`, `tools/sound_workbench.html`).
4. **HITL Gate 3 Checkpoint**: Verify authoring workbenches and asset ledger.

---

### Stage D: Side-by-Side (SxS) Visual Bar Parity Loop (Autonomous $\rightarrow$ Critic WIN)
*Triggered upon asset delivery.*

1. **The Parity Cycle (`Capture -> Critic -> Punch List -> Builder -> Re-capture`)**:
   - **Capture**: Automated headless browser / screen capture generates in-game stills (`captures/R<n>_frame.png`).
   - **SxS Composite**: Pair capture side-by-side with matched reference from `refs-locked/`.
   - **Execute `game-design-critic` (Phase 2: Visual Parity)**: Run critique against `art/BAR.md`.
     - *If FAIL*: Generate structured defect punch items (`[Still | Matched Ref | Region | Observed Defect | Ref Target | Done-When]`).
     - *Builder Round*: Implement targeted visual fixes for punch items.
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
2. **Execute `implement` / `seikoclaw-executor` + `tdd` Loop**: Build runtime engine modules (WebGL, PixiJS, Godot, or custom engine).
3. **Execute `seikojin-qa`**: Run full automated regression suites and visual defect certifications.
4. **Publish / Handoff**: Deliver verified game build, source tree, locked assets, and `rounds.log`.

---

## 3. Invocation Triggers

Use any of the following to start or resume Game Forge:
- `/game-forge`
- *"Let's build a video game about [idea]"*
- *"Run game-forge on [project]"*
- *"Resume game-forge stage"*
