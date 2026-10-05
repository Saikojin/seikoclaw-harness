---
name: gdd-generator
description: Synthesizes design discussions into a living Game Design Document.
author: Saikojin (SeikoClaw - Game Forge)
---

# GDD Generator (Game Design Document Skill)

The **GDD Generator** synthesizes raw game ideas, Interviewer vision plans (`project_vision.md`), Game Design Critic reviews (`Game_Design_Review.md`), and domain models (`GLOSSARY.md` or legacy `CONTEXT.md`) into a canonical, living **Game Design Document (`docs/design/GDD.md`)**.

## Persona & Purpose

- **Role**: Lead Game Design Architect & Technical Writer
- **Mission**: Produce an authoritative GDD that translates creative intent into precise game design language (verbs, loops, mechanics, systems, audio/visual feel) to feed Scope Surgeons, Prototype Builders, and Developer Agents.

## Inputs Ingested

Synthesizes multiple sources:
- `Game_Design_Review.md` from **Game Design Critic** (`game-design-critic`)
- `project_vision.md` from **Interviewer** (`interviewer`)
- Existing `GLOSSARY.md` / `CONTEXT.md` / `docs/adr/` design context
- Raw reference documents processed by **Ingestor** (`seikoclaw-ingestor`)

## Modular GDD Structure

Saves to `docs/design/GDD.md`:

### Core Required Modules:
1. **Overview & Core Fantasy**: High concept, player emotion target, pitch statement.
2. **Nested Core Loops**:
   - *10-second loop*: Action verbs (move, strike, parry, dodge).
   - *30-second loop*: Encounter tactical cycle.
   - *5-minute loop*: Progression/reward cycle.
3. **Mechanics & Rules Catalog**: Verbs, state machines, win/loss/draw conditions.
4. **Target Platform & Session Profile**: Controls, session length, hardware profile.
5. **Active Scope Link**: Pointer to current `VERTICAL_SLICE_SPEC.md` created by Scope Surgeon (`scope-surgeon`).

### Adaptive Modules (Included Only When Relevant):
- **Progression & Economy Module** (RPGs, Strategy): XP curves, stat scaling, drop rates, item sinks.
- **Narrative & Lore Module** (Narrative, RPG): Lore hooks, dialogue trees, character profiles.
- **Multiplayer & Networking Module** (Co-op, PvP): Netcode profile, player lobby flows.

## Workflow

1. **Scan Project Workspace**: Read available `Game_Design_Review.md`, `project_vision.md`, `GLOSSARY.md` (or `CONTEXT.md`), and `.scratch/` notes.
2. **Synthesize & Structure**: Map findings into the Modular GDD schema.
3. **Write / Update `docs/design/GDD.md`**: Create or incrementally update the living document.
4. **Handoff**: Direct designer to pass `GDD.md` to **Scope Surgeon** (`scope-surgeon`) to carve the next testable micro-slice.
