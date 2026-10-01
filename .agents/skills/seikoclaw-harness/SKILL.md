---
name: seikoclaw-harness
description: Router and index for all SeikoClaw skills, workflows, and sidecar tools.
author: Saikojin (SeikoClaw)
---

# SeikoClaw Harness Router

Index of canonical developer, game-dev, and autonomous harness skills available in `.agents/skills/`:

## 1. Game Development & Visual Parity (Master Framework & Toolkit)
- [game-forge](../game-forge/SKILL.md) — Master autonomous game creation framework: coordinates Stage Gates A–E, locked reference pipeline (`refs-locked/`), zero-install prototyping, balance modeling, assets, developer workbenches, Side-by-Side (SxS) Visual Bar parity loops, and stuck-loop diagnoser ($D^*$).
- [game-design-critic](../game-design-critic/SKILL.md) — Dual-mode critic persona: **Mode 1 (Gameplay & Mechanics Socratic Critic)** for core loops and player feel; **Mode 2 (Visual Parity & SxS Critic)** for forensic reference comparison, Anti-Soft-Pass enforcement, and coordinate-mapped punch lists.
- [game-developer](../game-developer/SKILL.md) — Lead Tooling Architect: breaks down design reviews into linear creation pipelines with custom workbenches, asset scripts, and validators.
- [gdd-generator](../gdd-generator/SKILL.md) — Synthesizes vision plans, critic reviews, and ingested notes into living `docs/design/GDD.md` and `docs/design/BRIEF.md` specifications.
- [scope-surgeon](../scope-surgeon/SKILL.md) — Ruthlessly cuts game design scope to a testable 30–90 second vertical micro-slice in `VERTICAL_SLICE_SPEC.md` format.
- [game-prototype-builder](../game-prototype-builder/SKILL.md) — Builds zero-install single-file HTML5 Canvas games (`prototype.html`) with Web Audio API synth sounds, live tuning sliders, and telemetry HUDs.
- [game-systems-modeler](../game-systems-modeler/SKILL.md) — Interactive Chart.js simulators (`balance_simulator.html`) and canonical balance JSON storage (`docs/design/balance.json`).
- [playtest-feedback-loop](../playtest-feedback-loop/SKILL.md) — Translates qualitative feedback ("floaty", "bullet sponge") to parameter diffs and maintains `PLAYTEST_RUNBOOK.md`.
- [genre-competitor-analysis](../genre-competitor-analysis/SKILL.md) — Autonomous subagent executing 5-point competitor matrix research (`COMPETITIVE_LANDSCAPE.md`).
- [mood-board-curator](../mood-board-curator/SKILL.md) — Curates visual/audio reference galleries (`mood_board.html`) and extracts `style_markers.json`.
- [asset-generator](../asset-generator/SKILL.md) — On-demand 2D game asset creation (textures, sprites, layers, backdrops) via Gemini image generation.

## 2. Quality Engineering & Gatekeeping
- [seikojin-qa](../seikojin-qa/SKILL.md) — Automated QA Gatekeeper: QA Strategist (RBT / Rabbit Path) and QA Engineer (100% automation pass rate, Clean Slate wipe, Visual Defect Punch Lists, and QA Constitution Rule #8 Anti-Soft-Pass).
- [seikoclaw-browser-qa-workflow](../seikoclaw-browser-qa-workflow/SKILL.md) — Browser automation, visual layout verification, and console error audits.
- [coverage-loop](../coverage-loop/SKILL.md) — Iteratively writes tests and runs coverage tools until target threshold is met.
- [code-review](../code-review/SKILL.md) — Two-axis parallel review (Standards + Spec) with Fowler smell baseline.
- [diagnosing-bugs](../diagnosing-bugs/SKILL.md) — Disciplined diagnosis loop for hard bugs: reproduce → minimize → hypothesize → instrument → fix → test.

## 3. Architecture & Task Orchestration
- [architect](../architect/SKILL.md) — Decomposes high-level goals into granular DAG tasks and `task.md` checklists with `[GATE: QA]` and `[GATE: VISUAL_CRITIC]` verification contracts.
- [implement](../implement/SKILL.md) — Builds work from specs, ticket lists, or DAG frontiers with automated verification *(aliases: `executor`)*.
- [tdd](../tdd/SKILL.md) — Test-driven development: red→green→refactor loop at pre-agreed seams.
- [codebase-design](../codebase-design/SKILL.md) — Domain modeling, context mapping, and deepening opportunities following design-it-twice principles *(aliases: `domain-modeling`, `improve-codebase-architecture`)*.
- [adr](../adr/SKILL.md) — Turn architectural decisions into Architecture Decision Records in `docs/adr/`.
- [seikoclaw-frontend-taste](../seikoclaw-frontend-taste/SKILL.md) — Enforces design systems, Emil Kowalski motion physics, optical alignment, and mobile-native ergonomics.
- [seikoclaw-operating-map](../seikoclaw-operating-map/SKILL.md) — Multi-agent concurrency map, ownership lanes, and blockers.
- [seikoclaw-goal-prompter](../seikoclaw-goal-prompter/SKILL.md) — Hardens executor prompts using the 7-field contract format.

## 4. Engineering Spec Pipeline & Productivity (Matt Pocock / David Andrej)
- [before-building](../before-building/SKILL.md) — Instant gut-check: surface 1–3 consequential choices hidden in an idea before coding.
- [to-spec](../to-spec/SKILL.md) — Synthesize discussion context into a detailed technical specification *(aliases: `to-prd`)*.
- [to-tickets](../to-tickets/SKILL.md) — Break plans or specs into tracer-bullet tickets with dependency edges *(aliases: `to-issues`)*.
- [wayfinder](../wayfinder/SKILL.md) — Plan large, foggy efforts across multiple sessions using a shared decision map.
- [prototype](../prototype/SKILL.md) — Build a throwaway prototype to answer a design or technical question.
- [grill-me](../grill-me/SKILL.md) — Relentless interview loop resolving decision trees and updating `CONTEXT.md` / ADRs inline *(aliases: `grilling`, `grill_with_docs`, `loop-me`, `wait-what`)*.
- [pr](../pr/SKILL.md) — Standardized fast-to-review PR body template with evidence pairs and risk analysis.
- [resolving-merge-conflicts](../resolving-merge-conflicts/SKILL.md) — Hunk-by-hunk resolution of in-progress git merge/rebase conflicts.
- [triage](../triage/SKILL.md) — Move raw issues and external requests through triage roles into agent-ready tickets.
- [handoff](../handoff/SKILL.md) — Compact conversation context into a structured handoff document for cross-session continuity.
- [wizard](../wizard/SKILL.md) — Generate interactive CLI wizards (PowerShell & Bash) to guide manual setups and credentials.
- [research](../research/SKILL.md) — Delegate primary-source investigation to a background research subagent.
- [agent-authoring](../agent-authoring/SKILL.md) — Comprehensive framework for writing and editing agent skills, workflows, and rules *(aliases: `writing-for-agents`, `writing-great-skills`, `teach`)*.
- [agent-guardrails](../agent-guardrails/SKILL.md) — Denylist of catastrophic shell commands enforced via cross-platform guard hooks.
- [agent-self-scheduling](../agent-self-scheduling/SKILL.md) — Schedule AI agent tasks on intervals, crons, or background heartbeats.
- [distribute-skills](../distribute-skills/SKILL.md) — Sync and distribute skills between local workspace and global/plugin locations.
- [sweep-loop](../sweep-loop/SKILL.md) — Sweeps entire codebase to apply architectural patterns and learnings.
- [status](../status/SKILL.md) — Displays current context health, iteration budget, and token utilization.
- [learnings](../learnings/SKILL.md) — Captures session-specific technical insights, mistakes, and patterns into OpenBrain *(aliases: `retro`)*.
- [modernize](../modernize/SKILL.md) — Performs structural migrations and modern design pattern updates.
- [interviewer](../interviewer/SKILL.md) — Synthesizes user ideas into a structured Master Vision Plan.
- [youtube-transcript](../youtube-transcript/SKILL.md) — Fetches and processes YouTube transcripts for documentation and ingestion.
- [seikoclaw-red-team](../seikoclaw-red-team/SKILL.md) — Audits implementation plans for load-bearing assumptions and risks.
- [seikoclaw-shipper](../seikoclaw-shipper/SKILL.md) — Generates pull request descriptions, release notes, and stakeholder updates.
- [seikoclaw-skill-extractor](../seikoclaw-skill-extractor/SKILL.md) — Actively generates reusable skills from completed sessions.
- [seikoclaw-test-memory](../seikoclaw-test-memory/SKILL.md) — Records successful testing procedures and DOM selectors into runbooks.
- [seikoclaw-ingestor](../seikoclaw-ingestor/SKILL.md) — Processes unstructured files (PDFs, transcripts, CSVs) into grounded context.
