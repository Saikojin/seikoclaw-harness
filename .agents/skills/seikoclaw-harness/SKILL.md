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
- [blender-developer](../blender-developer/SKILL.md) — Autonomous live Blender 3D procedural modeling, PBR material creation, Poly Haven / Poly Pizza asset ingestion, 8-directional isometric sprite rendering, and visual self-verification via Blender MCP.
- [obsidian-atlas-vtt](../obsidian-atlas-vtt/SKILL.md) — Virtual Tabletop scene authoring inside Obsidian with Atlas VTT: `.atlasmap` JSON scenes, Universal VTT (`.uvtt`) map imports, note pins with inline dice rolling, and modular `.atlas-collection.zip` bundles.

## 2. Quality Engineering & Gatekeeping
- [seikojin-qa](../seikojin-qa/SKILL.md) — Automated QA Gatekeeper: QA Strategist (RBT / Rabbit Path) and QA Engineer (100% automation pass rate, Clean Slate wipe, Visual Defect Punch Lists, and QA Constitution Rule #8 Anti-Soft-Pass).
- [break-ui](../break-ui/SKILL.md) — Adversarial UI stress-testing: feeds components worst-case realistic data (long names, missing avatars, extreme counts, non-Latin text) behind a dev-only toggle to catch layout breaking before production.
- [review-animations](../review-animations/SKILL.md) — 10 non-negotiable motion standards gatekeeper (justification, sub-300ms budget, origin-aware popovers, exit faster than enter, zero reflow) with companion `STANDARDS.md`.
- [seikoclaw-browser-qa-workflow](../seikoclaw-browser-qa-workflow/SKILL.md) — Browser automation, visual layout verification, and console error audits.
- [coverage-loop](../coverage-loop/SKILL.md) — Iteratively writes tests and runs coverage tools until target threshold is met.
- [code-review](../code-review/SKILL.md) — Two-axis parallel review (Standards + Spec) with Fowler smell baseline.
- [diagnosing-bugs](../diagnosing-bugs/SKILL.md) — Disciplined diagnosis loop for hard bugs: tight feedback loop → minimize → hypothesize → instrument → fix → regression test → retro.
- [retro](../retro/SKILL.md) — Session retrospective optimizing the agent environment: pushes mechanical errors to deterministic checks (linters, hooks, CI) and judgment calls to coding standards.

## 3. Architecture & Task Orchestration
- [architect](../architect/SKILL.md) — Decomposes high-level goals into granular DAG tasks and `task.md` checklists with `[GATE: QA]` and `[GATE: VISUAL_CRITIC]` verification contracts.
- [implement](../implement/SKILL.md) — Builds work per ticket or spec with automated verification *(aliases: `executor`)*.
- [implement-spec](../implement-spec/SKILL.md) — Whole-spec parallel DAG orchestrator: runs concurrent implementer subagents across Git worktrees against a shared integration branch.
- [tdd](../tdd/SKILL.md) — Test-driven development: red→green loop at pre-agreed seams.
- [codebase-design](../codebase-design/SKILL.md) — Domain modeling, context mapping, and deepening opportunities following design-it-twice principles *(aliases: `domain-modeling`, `improve-codebase-architecture`)*.
- [setup-ts-deep-modules](../setup-ts-deep-modules/SKILL.md) — Enforces deep module boundaries in TypeScript repos via dependency-cruiser (public root entry points, private subfolders, no barrel files).
- [adr](../adr/SKILL.md) — Turn architectural decisions into Architecture Decision Records in `docs/adr/`.
- [seikoclaw-frontend-taste](../seikoclaw-frontend-taste/SKILL.md) — Enforces design systems, Emil Kowalski motion physics, optical alignment, and mobile-native ergonomics.
- [animate](../animate/SKILL.md) — Builds animations from scratch with frequency gating, hardware-accelerated transforms, and `RECIPES.md` (accordions, modals, tabs, drag).
- [mobile-native](../mobile-native/SKILL.md) — Eradicates web-on-mobile tells: `100dvh`, iOS 16px input auto-zoom, tap highlight color, sticky touch hover states, and safe-area insets.
- [apple-design](../apple-design/SKILL.md) — Fluid interaction and momentum physics translated for the web: pointer-down instant feedback, momentum projection, continuous velocity, and interruptible springs.
- [pick-ui-library](../pick-ui-library/SKILL.md) — Curated dependency whitelist (Base UI, cmdk, Sonner, NumberFlow, motion, input-otp) preventing agents from picking abandoned packages.
- [improve-animations](../improve-animations/SKILL.md) — Scans existing codebases for animations and generates prioritized, self-contained implementation tickets.
- [find-animation-opportunities](../find-animation-opportunities/SKILL.md) — Identifies high-leverage UI locations where motion aids comprehension vs what never to animate.
- [animation-vocabulary](../animation-vocabulary/SKILL.md) — Reverse-lookup glossary translating sensory descriptions ("bouncy pop-in", "rubber-band") into exact technical primitives.
- [seikoclaw-operating-map](../seikoclaw-operating-map/SKILL.md) — Multi-agent concurrency map, ownership lanes, and blockers.
- [seikoclaw-goal-prompter](../seikoclaw-goal-prompter/SKILL.md) — Hardens executor prompts using the 7-field contract format.

## 4. Engineering Spec Pipeline & Productivity (Matt Pocock / David Andrej)
- [before-building](../before-building/SKILL.md) — Instant gut-check: surface 1–3 consequential choices hidden in an idea before coding.
- [to-spec](../to-spec/SKILL.md) — Synthesize discussion context into a detailed technical specification *(aliases: `to-prd`)*.
- [to-tickets](../to-tickets/SKILL.md) — Break plans or specs into tracer-bullet tickets with dependency edges *(aliases: `to-issues`)*.
- [wayfinder](../wayfinder/SKILL.md) — Plan large, foggy efforts across multiple sessions using a shared decision map.
- [prototype](../prototype/SKILL.md) — Build a throwaway prototype to answer a design or technical question.
- [grill-me](../grill-me/SKILL.md) — Relentless interview loop resolving decision trees and updating `GLOSSARY.md` (or `CONTEXT.md`) and ADRs inline *(aliases: `grilling`, `grill_with_docs`, `wait-what`)*.
- [loop-me](../loop-me/SKILL.md) — Grilling interview identifying repeated personal/dev routines and formalizing them as `workflows/*.md` specs.
- [pr](../pr/SKILL.md) — Standardized fast-to-review PR body template with evidence pairs and risk analysis.
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
- [learnings](../learnings/SKILL.md) — Captures session-specific technical insights, mistakes, and patterns into OpenBrain.
- [modernize](../modernize/SKILL.md) — Performs structural migrations and modern design pattern updates.
- [interviewer](../interviewer/SKILL.md) — Synthesizes user ideas into a structured Master Vision Plan.
- [youtube-transcript](../youtube-transcript/SKILL.md) — Fetches and processes YouTube transcripts for documentation and ingestion.
- [seikoclaw-red-team](../seikoclaw-red-team/SKILL.md) — Audits implementation plans for load-bearing assumptions and risks.
- [seikoclaw-shipper](../seikoclaw-shipper/SKILL.md) — Generates pull request descriptions, release notes, and stakeholder updates.
- [seikoclaw-skill-extractor](../seikoclaw-skill-extractor/SKILL.md) — Actively generates reusable skills from completed sessions.
- [seikoclaw-test-memory](../seikoclaw-test-memory/SKILL.md) — Records successful testing procedures and DOM selectors into runbooks.
- [seikoclaw-ingestor](../seikoclaw-ingestor/SKILL.md) — Processes unstructured files (PDFs, transcripts, CSVs) into grounded context.
- [book-to-skill](../book-to-skill/SKILL.md) — Compiles technical books, TTRPG rulebooks, and design bibles (PDF, EPUB, DOCX) into on-demand queryable agent skills (SKILL.md, chapters, cheatsheet, patterns, glossary).

## 5. Knowledge Vaults, Obsidian & TTRPG Tooling
- [obsidian-cli](../obsidian-cli/SKILL.md) — Direct command-line automation of a running Obsidian vault: note CRUD, frontmatter property manipulation, plugin debugging, DOM queries, code eval, and headless `dev:screenshot` capture.
- [obsidian-markdown](../obsidian-markdown/SKILL.md) — Authoring valid Obsidian Flavored Markdown with wikilinks `[[Note]]`, block transclusions, callouts, and frontmatter properties.
- [json-canvas](../json-canvas/SKILL.md) — Interactive visual mind-maps, decision trees, and quest webs in `.canvas` (JSON Canvas 1.0) format.
- [obsidian-bases](../obsidian-bases/SKILL.md) — Dynamic database views (`.base`) with calculated formulas, sorting, and aggregations for game balance curves and asset ledgers.
