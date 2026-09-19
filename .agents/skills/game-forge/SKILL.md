---
name: game-forge
description: Master autonomous framework for end-to-end game creation. Orchestrates design critique, GDD authoring, micro-slice slicing, zero-install HTML5 prototyping, asset generation, developer tooling, and autonomous engine builds without requiring manual skill invocations.
disable-model-invocation: false
---

# Game Forge: Master Autonomous Game Creation Framework

The **Game Forge** framework is an end-to-end game creation orchestrator. It unifies all modular game design, prototyping, asset generation, developer tooling, and execution skills into an automated, sequential pipeline with strict Human-in-the-Loop (HITL) checkpoints.

Instead of manually typing separate skills at every step, **Game Forge** manages the entire lifecycle autonomously:

```
[Pitch / Idea] ──► (Stage 1: Design & GDD) ──► (Stage 2: 30s Micro-Slice & Prototype)
                           │                                  │
                           ▼                                  ▼
                 [HITL Gate 1: GDD Review]          [HITL Gate 2: Playtest & Feel]
                                                              │
                                                              ▼
[Shipped Game] ◄── (Stage 4: Engine & QA) ◄── (Stage 3: Assets & Tooling Workbenches)
```

---

## 1. Project Manifest & State Tracking

Game Forge maintains a single canonical manifest at `docs/design/game_manifest.json` (or `.scratch/<project>/game_manifest.json`):

```json
{
  "project_name": "GameTitle",
  "current_stage": "STAGE_1_DESIGN",
  "active_hypothesis": "Parrying telegraphed attacks creates high-risk tension in 30s encounters",
  "core_verbs": ["move", "parry", "strike"],
  "artifacts": {
    "gdd": "docs/design/GDD.md",
    "vertical_slice": "docs/design/VERTICAL_SLICE_SPEC.md",
    "prototype_html": "prototypes/prototype.html",
    "balance_json": "docs/design/balance.json",
    "balance_simulator": "docs/design/balance_simulator.html",
    "tooling_architecture": "docs/design/GAME_TOOLING_ARCHITECTURE.md",
    "task_list": "task.md"
  },
  "stage_history": []
}
```

---

## 2. The 4-Stage Autonomous Pipeline

### Stage 1: Design & Core Loop Synthesis (Autonomous $\rightarrow$ HITL Gate 1)
1. **Intake Pitch**: Receive the user's game idea, genre, or theme.
2. **Execute `game-design-critic` Heuristics**:
   - Evaluate the **10-second loop** (moment-to-moment verb satisfaction).
   - Evaluate the **30-second loop** (encounter tactics and risk/reward).
   - Evaluate the **5-minute loop** (session hook & reward).
   - Check for degenerate strategies (spamming 1 move, corner camping).
   - Ask 2–3 targeted Socratic questions if the core fantasy is ambiguous.
3. **Execute `genre-competitor-analysis`**: Identify 3 competitor games and extract market gaps.
4. **Execute `gdd-generator`**: Compile findings into a living `docs/design/GDD.md`.
5. **HITL Gate 1 Checkpoint**: Present the 1-page GDD executive summary to the user for approval.

---

### Stage 2: Scope Carving & Zero-Install Prototyping (Autonomous $\rightarrow$ HITL Gate 2)
*Triggered immediately upon GDD approval.*

1. **Execute `scope-surgeon`**:
   - Strip all non-essential systems (inventory, XP curves, multi-room campaigns, complex UI).
   - Isolate 1 arena, 1–2 verbs, and 1 enemy into `docs/design/VERTICAL_SLICE_SPEC.md`.
2. **Execute `game-prototype-builder`**:
   - Write a self-contained, zero-dependency `prototypes/prototype.html` (HTML5 Canvas + Vanilla JS).
   - Embed procedural sound effects via Web Audio API synth (jumps, hits, explosions).
   - Embed an on-screen Debug HUD and **Live Parameter Tuning Sliders** (e.g. `Speed`, `Cooldown`, `ParryWindow`).
3. **Execute `game-systems-modeler`**:
   - Write `docs/design/balance.json` (canonical baseline curves).
   - Write `docs/design/balance_simulator.html` (interactive Chart.js dashboard).
4. **HITL Gate 2 Checkpoint (Playtest)**:
   - Provide the file path to `prototypes/prototype.html`.
   - Prompt the user: *"Double-click `prototype.html` to open in your browser. Play 5 rounds, tweak the live sliders, and share your feedback on the game feel."*

---

### Stage 3: Feel Tuning, Assets & Developer Tooling (Autonomous $\rightarrow$ HITL Gate 3)
*Triggered upon receiving user playtest feedback.*

1. **Execute `playtest-feedback-loop`**:
   - Translate qualitative user notes (*"jump feels floaty"*, *"boss is bullet-spongey"*) into exact parameter diffs in `balance.json` and `prototype.html`.
2. **Execute `mood-board-curator` & `asset-generator`**:
   - Generate visual style markers in `docs/design/style_markers.json`.
   - Generate required modular sprites, seamless textures, and isometric tiles into `assets/`.
3. **Execute `game-developer` (Tooling Architecture)**:
   - Scaffold data schemas and schema validators (`validate_data.py`).
   - Scaffold custom browser authoring workbenches (e.g., `tools/map_painter.html`, `tools/sound_workbench.html`, `tools/rigging_studio.html`).
   - Create developer orchestration scripts (`start_dev.bat` / `start_dev.ps1`).
4. **HITL Gate 3 Checkpoint**: Verify the authoring workbenches and asset pipeline.

---

### Stage 4: Autonomous Engine Build & QA
*Triggered upon tooling sign-off.*

1. **Execute `seikoclaw-architect`**: Decompose full engine implementation into `task.md` with explicit evidence contracts.
2. **Execute `seikoclaw-executor` + `tdd` Loop**:
   - Build runtime engine / framework modules (Godot, WebGL, PixiJS, or custom engine).
   - Enforce red-green-refactor test loops.
3. **Execute `seikojin-qa` & `seikoclaw-browser-qa-workflow`**:
   - Execute automated visual regression and balance sanity tests.
4. **Stage Completion**: Deliver the finished, verified game build.

---

## 3. Invocation Triggers

Use any of the following to start or resume Game Forge:
- `/game-forge`
- *"Let's build a video game about [idea]"*
- *"Run game-forge on [project]"*
- *"Resume game-forge stage"*
