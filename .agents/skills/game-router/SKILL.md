---
name: game-router
description: Unified game development and game design dispatcher for SeikoClaw. Automatically fingerprints the game engine, classifies genres and mechanics, and composes the exact high-signal gamedev skills for design critique, prototyping, or engine builds in one call.
author: Saikojin (SeikoClaw - Game Forge)
---

# Unified Game Router — Game Dev Dispatcher & Intelligence Gateway

The single entry-point for all game design, architecture, mechanics, and engine implementation in SeikoClaw.

Instead of requiring designers or developers to memorize 77+ individual skills (`gamedev-godot-2d-movement`, `gamedev-roguelike`, `gamedev-save-systems`, etc.), **`game-router`** resolves your engine, genre, and disciplines automatically in a single call, then dispatches directly to [`game-design-critic`](../game-design-critic/SKILL.md) or [`game-forge`](../game-forge/SKILL.md).

---

## 🚀 When to Use

- When starting any new game project, pitch, or prototype.
- When asking any game design question ("How do I tune jump arc?", "Best save system structure?", "How to handle proc-gen seeds?").
- When implementing a gameplay feature in any engine (Godot, Unity, Unreal, Bevy, Ebitengine, Web engines, Roblox).
- Called automatically by **`game-forge`** at Stage A (Design) and Stage E (Engine Build).

---

## 🧠 One-Call Dispatch Algorithm

When a request arrives, `game-router` executes 4 steps:

### 1. Engine Fingerprinting (Exclusive: 1 Engine)
Scans the project tree for root entry points:

| Primary File Signal | Detected Engine | Pinned Engine Suite |
| :--- | :--- | :--- |
| `project.godot` | Godot 4.7 | `gamedev-godot-gdscript`, `gamedev-godot-nodes-scenes`, `gamedev-godot-physics` |
| `Assets/` + `ProjectSettings/` | Unity 6.3 LTS | `gamedev-unity-csharp-scripting`, `gamedev-unity-input-system` |
| `*.uproject` | Unreal Engine 5.8 | `gamedev-unreal-blueprints`, `gamedev-unreal-cpp-gameplay` |
| `go.mod` (with `ebiten/v2`) | Ebitengine v2.10 | `gamedev-ebitengine-game` |
| `Cargo.toml` (with `bevy`) | Bevy 0.15 | `gamedev-bevy-ecs` |
| `package.json` (`phaser`) | Phaser 4.2 | `gamedev-phaser-core`, `gamedev-phaser-arcade-physics` |
| `package.json` (`three`) | Three.js r186 | `gamedev-threejs-scene-setup`, `gamedev-threejs-materials-lighting` |
| `package.json` (`pixi.js`) | PixiJS 8.22 | `gamedev-pixijs-rendering` |
| `game.project` | Defold | `gamedev-defold-core` |
| `main.lua` (`love.*`) | LÖVE 11.5 | `gamedev-love2d-core` |
| `import pygame` | Pygame-ce | `gamedev-pygame-core` |
| `*.rbxl` / `default.project.json` | Roblox Luau | `gamedev-roblox-luau`, `gamedev-roblox-studio-workflow` |

*If no engine fingerprint is found and none is specified, defaults to zero-install HTML5 Canvas for Stage B prototyping, or Godot 4.7 for full production.*

---

### 2. Genre Classification (Additive: at most 1 primary genre)
Identifies core mechanics taxonomy and maps to the dedicated playbook:

- **Platformer**: `gamedev-platformer` (jump arc, coyote time, jump buffering, tile hazards)
- **Roguelike**: `gamedev-roguelike` (turn queues, FOV, permadeath, metaprogression, proc-gen)
- **RPG**: `gamedev-rpg` (stat curves, inventory, quest state, dialogue trees)
- **FPS / Shooter**: `gamedev-fps-shooter` (mouselook, projectile vs hitscan, recoil decay)
- **Tower Defense**: `gamedev-tower-defense` (waypoint grid, targeting priorities, creep economy)
- **Card Game / Deckbuilder**: `gamedev-card-game` (draw/discard zones, card resolution stack, RNG mitigation)
- **Visual Novel**: `gamedev-visual-novel` (dialogue branching, character portraits, choice history)
- **Survival / Crafting**: `gamedev-survival-crafting` (vital drain curves, recipe matrices, storage slots)
- **Puzzle**: `gamedev-puzzle` (grid state, deterministic rule checks, undo buffer)

---

### 3. Cross-Engine Disciplines (Additive: 1–3 skills)
Injects modular gameplay fundamentals:

- **Mechanic Intelligence & Loops**: [`gameplay-atlas`](../gameplay-atlas/SKILL.md) (280 proven mechanics across 28 systems, 4-stage loops, player dilemmas, parameters, shipped game cases, and Stage B prototyping recipes)
- **AI & Behavior**: `gamedev-game-ai`, `gamedev-ai-behavior-trees-utility-ai`
- **Game Feel & Juice**: `gamedev-game-feel`, `gamedev-physics-tuning`
- **Cameras**: `gamedev-camera-systems` (deadzones, look-ahead, screen shake)
- **State & Saves**: `gamedev-save-systems` (schema migrations, cloud/slot serialization)
- **Audio Design**: `gamedev-audio-design` (buses, ducking, adaptive layers)
- **Shaders & VFX**: `gamedev-shader-programming`, `gamedev-godot-shaders` / `gamedev-unreal-niagara`
- **Asset Production**: `gamedev-create-game-assets` + [`polyhaven-assets`](../polyhaven-assets/SKILL.md) + [`blender-developer`](../blender-developer/SKILL.md)

---

### 4. Direct Handoff & Pipeline Execution

Depending on the nature of the request, `game-router` directs execution cleanly:

1. **For Design Pitches & Socratic Questions**:
   Dispatches directly to **[`game-design-critic`](../game-design-critic/SKILL.md)** Mode 1 with the composed genre/discipline rules loaded as the critique context.
2. **For Full Game Creation Cycles**:
   Invokes **[`game-forge`](../game-forge/SKILL.md)** and populates `docs/design/game_manifest.json` with the detected engine and composed skill bindings.
3. **For Direct Implementation Tasks**:
   Provides the exact 2–3 skill links and syntax patterns directly to the developer or ready frontier task executor.

---

## 💬 Worked Example Dispatches

| User Request | Router Resolution | Handoff |
| :--- | :--- | :--- |
| *"I want to make a turn-based deckbuilder in Godot"* | `gamedev-godot-nodes-scenes` + `gamedev-card-game` + `gamedev-save-systems` | Passes to `game-forge` Stage A with deckbuilder questions |
| *"How should I balance jump arc and dash in my 2D game?"* | `gamedev-platformer` + `gamedev-game-feel` + `gamedev-physics-tuning` | Passes to `game-design-critic` Mode 1 |
| *"Implement an inventory system for my Unity project"* | `gamedev-unity-scriptableobjects` + `gamedev-rpg` + `gamedev-save-systems` | Dispatches C# ScriptableObject architecture |
| *"Add procedural dungeon generation to my Bevy game"* | `gamedev-bevy-ecs` + `gamedev-procedural-gen` + `gamedev-roguelike` | Dispatches Rust ECS query & grid generators |
