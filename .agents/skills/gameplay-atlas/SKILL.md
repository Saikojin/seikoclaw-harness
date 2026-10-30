---
name: gameplay-atlas
description: Offline field guide to 280 game mechanics across 28 systems with loops, player dilemmas, parameters, shipped game cases, and rapid prototyping recipes.
author: Saikojin (SeikoClaw - Game Forge)
---

# Gameplay Atlas

The **Gameplay Atlas** is an offline field guide containing **280 structured game mechanics across 28 systems and 16 tags**, indexed locally in `data/gameplay_atlas.db` (SQLite + FTS5) with raw JSON payloads in `data/gameplay_atlas/raw/`.

It powers **Game Forge** (`game-forge`), **Game Router** (`game-router`), **Game Design Critic** (`game-design-critic`), and **Scope Surgeon** (`scope-surgeon`) with empirical game loops, player dilemma analyses, shipped reference cases, and micro-slice prototyping recipes.

---

## 🎛️ The CLI Query Lever (`scripts/gameplay_atlas.py`)

Agents and developers query the offline atlas instantly via `python scripts/gameplay_atlas.py`:

```bash
# 1. Full-text search with optional filters
python scripts/gameplay_atlas.py search "stamina" --system combat
python scripts/gameplay_atlas.py search "conveyor" --tag optimization
python scripts/gameplay_atlas.py search "deck" --scope small --json

# 2. Inspect complete mechanic card (rules, loop, dilemmas, parameters, cases)
python scripts/gameplay_atlas.py get combat-stamina-budget
python scripts/gameplay_atlas.py get automation-belt-routing --json

# 3. Extract rapid prototyping recipe for Stage B (firstStep, pitfall, test criteria)
python scripts/gameplay_atlas.py prototype-recipe automation-belt-routing

# 4. Cross-system mechanic combinations & synergy ideation
python scripts/gameplay_atlas.py combine combat farming
python scripts/gameplay_atlas.py combine automation --json

# 5. Lookup mechanics implemented by a specific shipped game
python scripts/gameplay_atlas.py cases "Factorio"
python scripts/gameplay_atlas.py cases "Celeste"
python scripts/gameplay_atlas.py cases "Hades"

# 6. List catalog systems and tags
python scripts/gameplay_atlas.py systems
python scripts/gameplay_atlas.py tags

# 7. Serendipitous random mechanic ideation
python scripts/gameplay_atlas.py random --system survival
```

---

## 🏗️ Structure of an Atlas Mechanic

Every mechanic in the atlas provides production-ready gamedev data:

1. **4-Stage Core Loop**: Step-by-step player loop (e.g. `Read window ──► Budget stamina ──► Attack or guard ──► Recover & re-engage`).
2. **Player Dilemmas & Trade-offs**: Core psychological tensions the player actively weighs up (e.g. *Finish a weakened enemy or save a roll?*).
3. **Tunable Parameters & Impact**: Specific design variables and their documented effects on pacing and player behavior.
4. **Real Shipped Game Cases**: Production implementations with references, wiki links, and screenshots (e.g. Dark Souls III, Elden Ring, Factorio, Satisfactory).
5. **Cross-System Combinations**: Innovative design prompts that fuse disparate gameplay genres.
6. **Rapid Prototyping Recipe**:
   - `Scope` (small/medium) & `Interaction` (solo/co-op).
   - `First Step`: Concrete 1-sentence micro-slice implementation recipe.
   - `Pitfall`: Anti-patterns to strictly avoid during the first hour.
   - `Test`: Empirical playtest verification criteria.

---

## 🚀 Game Forge Integration Protocols

### Stage A: Brief, GDD & Locked References
- When writing `docs/design/GDD.md`, query the atlas to discover 4-stage loops and player dilemmas:
  ```bash
  python scripts/gameplay_atlas.py search "<verbs or genre>" --json
  ```
- Use `cases` to find real shipped games with image URLs and wiki citations for `refs-locked/SOURCES.md`.

### Stage B: Scope Carving & Playable Foundation (`scope-surgeon`)
- When defining `docs/design/VERTICAL_SLICE_SPEC.md`, run:
  ```bash
  python scripts/gameplay_atlas.py prototype-recipe <mechanic-id>
  ```
- Copy `firstStep` into the slice objective and `pitfall` into non-goals.
- Copy `test` directly into `prototypes/prototype.html` as the verification checklist.

### Stage C: Balance & Systems Modeling (`game-systems-modeler`)
- When creating `docs/design/balance.json`, extract the mechanic's `parameters`:
  ```bash
  python scripts/gameplay_atlas.py get <mechanic-id> --json
  ```
- Pre-populate live dashboard sliders using these parameters.

---

## 🔄 Refreshing / Synchronizing the Catalog

The local database and raw cache can be refreshed in ~5 seconds at any time:

```bash
python scripts/sync_gameplay_atlas.py
```

This dynamically resolves the latest asset bundle hash on `gameplayatlas.loopyhop.com`, concurrently downloads all 280 mechanics, and rebuilds the SQLite FTS5 database and raw JSON cache.
