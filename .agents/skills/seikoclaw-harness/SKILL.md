---
name: seikoclaw-harness
description: Router and index for all SeikoClaw skills. Use when you want to know which skill to invoke.
disable-model-invocation: false
---

# SeikoClaw Harness Router

Index of available SeikoClaw and Matt Pocock skills:

## Core Engineering & Workflow
- [ask-matt](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/ask-matt/SKILL.md) — Ask which skill or flow fits your situation; complete router over engineering and productivity skills.
- [before-building](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/before-building/SKILL.md) — Instant gut-check: surface 1–3 consequential choices hidden in an idea before writing code.
- [wayfinder](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/wayfinder/SKILL.md) — Plan large, foggy efforts across multiple sessions using a shared decision map on your issue tracker.
- [prototype](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/prototype/SKILL.md) — Build a throwaway prototype (Logic TUI or UI multi-variant search params) to answer a design question.
- [implement](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/implement/SKILL.md) — Build work described by a spec or set of tickets, driving /tdd and /code-review.
- [triage](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/triage/SKILL.md) — Move raw issues and external requests through triage roles into agent-ready tickets.
- [diagnosing-bugs](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/diagnosing-bugs/SKILL.md) — Disciplined diagnosis loop for hard bugs and regressions: reproduce → minimize → hypothesize → instrument → fix → test.
- [codebase-design](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/codebase-design/SKILL.md) — Shared discipline and vocabulary for designing deep modules with simple interfaces.
- [domain-modeling](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/domain-modeling/SKILL.md) — Actively build and sharpen project domain models, updating CONTEXT.md and ADRs.
- [tdd](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/tdd/SKILL.md) — Test-driven development: red→green loop at pre-agreed seams, with anti-pattern guards and vertical-slice discipline.
- [to-tickets](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/to-tickets/SKILL.md) — Break plans or specs into tracer-bullet tickets with blocking edges.
- [to-spec](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/to-spec/SKILL.md) — Synthesize discussion context into a detailed technical specification.
- [code-review](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/code-review/SKILL.md) — Two-axis parallel review (Standards + Spec) with Fowler smell baseline. Driven by `/implement`; also standalone for branch/PR review.
- [research](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/research/SKILL.md) — Delegate primary-source investigation to a background research subagent.
- [resolving-merge-conflicts](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/resolving-merge-conflicts/SKILL.md) — Hunk-by-hunk resolution of in-progress git merge/rebase conflicts.
- [improve-codebase-architecture](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/improve-codebase-architecture/SKILL.md) — Scan codebase for deepening opportunities and produce architectural improvements.
- [agent-guardrails](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/agent-guardrails/SKILL.md) — Command denylist and safety guard hooks for pre-execution interception.
- [agent-self-scheduling](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/agent-self-scheduling/SKILL.md) — Schedule recurring agent tasks or heartbeats with PowerShell and Bash wrappers.
- [youtube-transcript](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/youtube-transcript/SKILL.md) — Extract YouTube video transcripts for ingestion and research notes.

## Game Development & Prototyping (Non-Coder Loop)
- [game-design-critic](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/game-design-critic/SKILL.md) — Lead Game Designer persona for Socratic grilling on core feel, 10s/30s/5m loops, and player psychology.
- [game-developer](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/game-developer/SKILL.md) — Lead Tooling Architect: breaks down design reviews and Wayfinder roadmaps into linear creation pipelines with custom workbenches, asset scripts, and validators.
- [gdd-generator](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/gdd-generator/SKILL.md) — Synthesize vision plans, critic reviews, and ingested notes into living `docs/design/GDD.md` specifications.
- [scope-surgeon](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/scope-surgeon/SKILL.md) — Ruthlessly cut game scope down to 30–90 second micro-slices in `VERTICAL_SLICE_SPEC.md` format.
- [game-prototype-builder](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/game-prototype-builder/SKILL.md) — Build zero-install single-file HTML5 Canvas games (`prototype.html`) with Web Audio API synth sounds, live tuning sliders, and telemetry HUDs.
- [game-systems-modeler](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/game-systems-modeler/SKILL.md) — Interactive Chart.js dashboards (`balance_simulator.html`) and canonical balance JSON storage (`docs/design/balance.json`).
- [playtest-feedback-loop](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/playtest-feedback-loop.md) — Translate qualitative feedback ("floaty", "bullet sponge") to parameter diffs and maintain `PLAYTEST_RUNBOOK.md`.
- [genre-competitor-analysis](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/genre-competitor-analysis/SKILL.md) — Autonomous research subagent executing 5-point competitive matrix research (`COMPETITIVE_LANDSCAPE.md`).
- [mood-board-curator](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/mood-board-curator/SKILL.md) — Curate visual/audio reference galleries (`mood_board.html`) and extract `style_markers.json` for ArtistAgent RAG prompt injection.

## Productivity & Meta
- [grill-with-docs](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/grill_with_docs/SKILL.md) — Relentless interview loop that builds project domain model and updates CONTEXT.md and ADRs.
- [grill-me](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/grill-me/SKILL.md) — Relentless Q&A interview to resolve decision trees for non-code/stateless efforts.
- [grilling](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/grilling/SKILL.md) — Relentless Q&A primitive: facts are looked up, decisions are asked; confirmation gate before acting.
- [handoff](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/handoff/SKILL.md) — Compact conversation context into a handoff document for cross-session continuity.
- [teach](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/teach/SKILL.md) — Stateful multi-session learning workspace for teaching user concepts and skills.
- [writing-great-skills](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/writing-great-skills/SKILL.md) — Principles, progressive disclosure model, and guidelines for authoring predictable agent skills.
- [distribute-skills](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/distribute-skills/SKILL.md) — Synchronize skills between local workspace and global/plugin directories.
