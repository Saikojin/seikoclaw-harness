# Graph Report - SeikoClaw-Harness  (2026-10-01)

## Corpus Check
- 111 files · ~142,522 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 901 nodes · 1136 edges · 105 communities (92 shown, 13 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 51 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `51469ecb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 104|Community 104]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 106|Community 106]]
- [[_COMMUNITY_Community 107|Community 107]]
- [[_COMMUNITY_Community 109|Community 109]]
- [[_COMMUNITY_Community 110|Community 110]]
- [[_COMMUNITY_Community 111|Community 111]]
- [[_COMMUNITY_Community 112|Community 112]]
- [[_COMMUNITY_Community 115|Community 115]]
- [[_COMMUNITY_Community 116|Community 116]]
- [[_COMMUNITY_Community 117|Community 117]]
- [[_COMMUNITY_Community 118|Community 118]]
- [[_COMMUNITY_Community 120|Community 120]]
- [[_COMMUNITY_Community 121|Community 121]]
- [[_COMMUNITY_Community 122|Community 122]]
- [[_COMMUNITY_Community 123|Community 123]]
- [[_COMMUNITY_Community 125|Community 125]]
- [[_COMMUNITY_Community 127|Community 127]]
- [[_COMMUNITY_Community 129|Community 129]]
- [[_COMMUNITY_Community 130|Community 130]]
- [[_COMMUNITY_Community 135|Community 135]]
- [[_COMMUNITY_Community 136|Community 136]]

## God Nodes (most connected - your core abstractions)
1. `MemoryEngine` - 49 edges
2. `TaskGraph` - 36 edges
3. `SeikoClaw` - 36 edges
4. `HealthPatrol` - 28 edges
5. `ConversationHistorySyncer` - 21 edges
6. `main()` - 20 edges
7. `GateEngine` - 16 edges
8. `SkillGater` - 16 edges
9. `HeuristicFallbackProvider` - 15 edges
10. `get_llm_provider()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `AutoCapture` --uses--> `MemoryEngine`  [INFERRED]
  auto_capture.py → openbrain/memory_engine.py
- `AutoCapture` --uses--> `SeikoClaw`  [INFERRED]
  auto_capture.py → seikoclaw.py
- `MockNeuralLLMProvider` --uses--> `ContextEngine`  [INFERRED]
  tests/test_memory_compression.py → openbrain/context_engine.py
- `TestMemoryCompression` --uses--> `ContextEngine`  [INFERRED]
  tests/test_memory_compression.py → openbrain/context_engine.py
- `IterationBudget` --uses--> `GateEngine`  [INFERRED]
  seikoclaw.py → openbrain/gates.py

## Import Cycles
- 1-file cycle: `openbrain/history_sync.py -> openbrain/history_sync.py`
- 2-file cycle: `openbrain/history_sync.py -> openbrain/memory_engine.py -> openbrain/history_sync.py`
- 3-file cycle: `openbrain/context_engine.py -> openbrain/history_sync.py -> openbrain/memory_engine.py -> openbrain/context_engine.py`

## Communities (105 total, 13 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (18): IterationBudget, main(), Scans conversation history transcripts across projects and syncs new events into, Validates a command against dangerous regex patterns in .agents/hooks/dangerous-, Executes a single command with safety guard, usage oversight, and watchdog telem, Runs multiple tasks in parallel using a thread pool., Syncs local .agents and third-party skills to global locations., Analyzes a task file and synthesizes or evolves a skill using pluggable LLM prov (+10 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (18): MemoryEngine, Persists a structured record of a failure, mistake, or gotcha into Openbrain., Retrieves past mistake records matching a query., Records a generated asset and its parameters., Updates asset rating and adjusts underlying memory weights/tiers., Updates the tier of a memory in both stores., Ensures all necessary SQLite tables exist from schema.sql., Updates a specific task's status on the Kanban board stored in checkpoint_data. (+10 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (23): 1. Biome & Map Generator Workbench (`generator_workbench.html`), 2. World Map Manager & Spatial Baking Pipeline (`world_map_manager.html`), 3. Visual Soundscape & Audio Workbench (`sound_workbench.js`), 4. 2D Skeletal Puppet & Rigging Studio (`rigging_studio.html`), 5. Asset Preprocessing CLI Suite (Python / `uv run`), 6. Content Parsers, Schemas & Vault Validators, 7. Single-Command Dev Environment & Packaging, A. Alpha & Transparency Cleaner (`clean_sprite_transparency.py`) (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.17
Nodes (3): HeuristicFallbackProvider, Zero-dependency rule-based summarizer and fallback provider.     Operates offli, MockNeuralLLMProvider

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (11): Any, Runs regression checks on the proposed skill.         If evolving from an exist, Automated Skill Regression Gating Engine.     Validates candidate and evolved a, End-to-end gating check and transactional persistence:         1. Runs schema v, Lists all staged candidate skills pending review or promotion., Returns a unified diff between candidate skill and existing skill on disk., Parses YAML frontmatter and body markdown from a skill string.         Returns:, Promotes a candidate skill from staging to production. (+3 more)

### Community 5 - "Community 5"
Cohesion: 0.17
Nodes (11): 1. Task Execution & Sandboxing, 2. Autonomous Looping & DAG Pumping, 3. Skill Staging & Candidate Promotion, 4. Cross-Project History Synchronization, 🎖️ Attribution & Upstream Credits, 🚀 Core CLI Commands, 🎯 Highlights, 📜 License (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.22
Nodes (16): note(), open_url(), say(), step(), warn(), template.sh script, ask(), ask_secret() (+8 more)

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (10): HealthPatrol, LLMProvider, MemoryEngine, HealthPatrol, Any, Records an action signature into health patrol buffer and database., Checks if the last N actions have identical signatures or failure loops., Autonomous Watchdog & Health Patrol for SeikoClaw loops.     Detects loop spin, (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (13): Note(), Open-Url(), Warn(), Ask-SecretValue(), Ask-Value(), Clear-WizardScreen(), Finish-Wizard(), Get-ExistingEnv() (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.16
Nodes (9): AutoCapture, main(), Ensures the usage_stats table exists., Records API usage for the current day., UsageMonitor, get_session_context(), main(), print_progress_bar() (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (13): 1. Input Ingestion, 2. Second-Layer Technical Grilling Protocol, 3. Deliverable 1: `GAME_TOOLING_ARCHITECTURE.md`, 4. Deliverable 2: Wayfinder 4-Stage Linear Production Pipeline, 5. Tool Scaffolding & Starter Blueprints, 6. Boundaries & Relationships, Document Structure:, Game Developer & Tooling Architect (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.13
Nodes (6): GateEngine, Evaluates whether a task's gate is satisfied.         Returns (is_satisfied, st, Gates Engine for SeikoClaw Hybrid Architecture.     Evaluates and certifies exe, Certifies a QA gate according to Seikojin QA Rules:         - 100% Pass Rate Ma, TaskGraph, TestGates

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (13): 1. State the question and pick N, 2. Generate radically different variants, 3. Wire them together, 4. Build the floating switcher, 5. Hand it over, 6. Capture the answer and clean up, Anti-patterns, Process (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.14
Nodes (10): MemoryEngine, OpenbrainEngine, Backward-compatible alias for MemoryEngine.     Maintains support for legacy me, Creates the secrets_vault table from schema.sql if it does not exist., Derives the encryption key from the master password and a salt from the DB., Vault, test_memory_engine_vault_table_creation(), test_openbrain_engine_compatibility() (+2 more)

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (12): 1. Gather context & restate intent, 2. Explore the codebase (optional), 3. Draft vertical slices, 4. Quiz the user, 5. Publish the tickets to the configured tracker, Acceptance criteria, Blocked by, <NN> — <Ticket title> (+4 more)

### Community 15 - "Community 15"
Cohesion: 0.17
Nodes (11): 1. Autonomous Loop Architecture (`loop_until_goal`), 2. Watchdog & Circuit-Breaker Integration (`HealthPatrol`), 3. Secrets Vault & SQLite Schema Alignment, 4. Workspace Portability & Environment Configuration, 5. Persistence Layer Consolidation, 6. Hybrid DAG Gating Enforcement on Frontier, 7. Dependency Manifestation & Packaging, 8. LLM Abstraction for Background Cognitive Loops (+3 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (5): DAG-based Task Graph and Ready Frontier Engine for SeikoClaw.     Provides depe, Updates task status (open, in_progress, in_qa, blocked, closed, deferred)., Deletes all closed ephemeral wisps from database., Renders the task graph as a clean, hierarchical markdown checklist., TaskGraph

### Community 17 - "Community 17"
Cohesion: 0.17
Nodes (11): 1. State the question, 2. Pick the language, 3. Isolate the logic in a portable module, 4. Build the smallest TUI that exposes the state, 5. Make it runnable in one command, 6. Hand it over, 7. Capture the answer and the prototype, Anti-patterns (+3 more)

### Community 18 - "Community 18"
Cohesion: 0.29
Nodes (6): 1. Matt Pocock ([@mattpocockuk](https://github.com/mattpocock)), 2. David Andrej ([@davidandrej](https://github.com/davidandrej)), 3. Saikojin / SeikoClaw ([@Saikojin](https://github.com/Saikojin)), Credits & Upstream Attribution, 📜 License & Usage, 🎖️ Upstream Creators & Maintainers

### Community 19 - "Community 19"
Cohesion: 0.17
Nodes (11): Chart the map, Fog of war, Invocation, Out of scope, Plan, don't do, Refer by name, The Map, The map body (+3 more)

### Community 20 - "Community 20"
Cohesion: 0.33
Nodes (5): 1. Context Pointers & Trigger Discipline, 2. Progressive Disclosure Ladder, 3. Leading Words & Completion Criteria, 4. Writing Modes (Explore vs. Exploit), Agent Authoring: Writing Skills, Workflows & Documents for Agents

### Community 22 - "Community 22"
Cohesion: 0.27
Nodes (5): ContextEngine, Scans short-term memories and consolidates them if the threshold is met., Openbrain Persistence Engine (Compatibility Module).  This module provides bac, OpenBrain Package - Cognitive Architecture and Memory Infrastructure for SeikoCl, Pluggable LLM Provider System for SeikoClaw / Openbrain. Supports LocalMind GGU

### Community 23 - "Community 23"
Cohesion: 0.20
Nodes (9): 1. Seamless Ground Textures, 2. Modular Character Builder Layers (Hair, Headgear, Armor, Paperdoll Parts), 3. 2D Sprites, Tokens, and Props (Full Characters & Entities), 4. Backdrops, Map Views & Panoramas, 5. General / Custom Images, asset-generator, Quick Reference: Core Prompt Engineering Rules, Quota & Batch Protection Best Practices (+1 more)

### Community 24 - "Community 24"
Cohesion: 0.20
Nodes (9): Challenge against the glossary, Cross-reference with code, Discuss concrete scenarios, Domain awareness, During the session, File structure, Offer ADRs sparingly, Sharpen fuzzy language (+1 more)

### Community 25 - "Community 25"
Cohesion: 0.33
Nodes (3): Creates a new task node in the DAG., Creates an ephemeral wisp task., Generates a content-derived collision-free hash ID (e.g. sc-a1b2 or sc-a1b2.1).

### Community 26 - "Community 26"
Cohesion: 0.14
Nodes (17): clean_user_content(), ConversationHistorySyncer, parse_iso_datetime(), Any, Determines the project name from transcript steps or conversation directory., Parses a transcript file into segmented conversation turns,         filtering f, Parses various ISO-8601 or SQLite datetime string formats to a UTC-aware datetim, Formats a conversation turn into a structured memory markdown document. (+9 more)

### Community 28 - "Community 28"
Cohesion: 0.20
Nodes (9): 1. Project Manifest & State Tracking, 2. The 5-Stage Autonomous Pipeline, 3. Invocation Triggers, Game Forge: Master Autonomous Game Creation Framework, Stage A: Brief, Locked References & Deep Plan (Autonomous $\rightarrow$ HITL Gate 1), Stage B: Scope Carving & Playable Foundation (Autonomous $\rightarrow$ Gate B), Stage C: Staged Art Pipeline & Authoring Workbenches (Autonomous $\rightarrow$ HITL Gate 3), Stage D: Side-by-Side (SxS) Visual Bar Parity Loop (Autonomous $\rightarrow$ Critic WIN) (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (8): 1. Combat & TTK, 2. Progression Curves, Core Capabilities, Dashboard Features:, Game Systems Modeler, Output Specifications, Supported Math Domains & Formulas, Workflow

### Community 30 - "Community 30"
Cohesion: 0.32
Nodes (4): Any, Computes the claimable frontier:         Tasks with status = 'open' whose prere, Atomically claims a task for a worker., Atomically claims the highest-priority ready task from the frontier.         By

### Community 31 - "Community 31"
Cohesion: 0.20
Nodes (9): 1. The Rabbit Philosophy (E2E Coherence), 2. Risk-Based Prioritization (RBT), 3. The Clean Slate Mandate, 4. Anti-Flakiness: Wait State Mastery, 5. Surgical Testability, 6. The Handoff Protocol, 7. Seikojin-Compliant Stack, 8. Visual Parity Rigor (Anti-Soft-Pass Mandate) (+1 more)

### Community 32 - "Community 32"
Cohesion: 0.15
Nodes (12): 1. QA Strategist (Brain - Planning Phase), 2. QA Engineer (Hands - Execution & Gate Certification), Bad Verdict (Subjective, Non-Actionable — REJECTED), CLI Integration Reference, Core Rules (The QA Constitution), Good Verdict (Seikojin Compliant — ACCEPTED), Hybrid DAG Workflow, Overview (+4 more)

### Community 33 - "Community 33"
Cohesion: 0.22
Nodes (8): Core Intent & Problem Statement, Further Notes, Implementation Decisions, Out of Scope, Process, Solution, Testing Decisions, User Stories

### Community 35 - "Community 35"
Cohesion: 0.25
Nodes (7): 1. Pin the fixed point, 2. Identify the spec source, 3. Identify the standards sources, 4. Spawn both sub-agents in parallel, 5. Aggregate, Process, Why two axes

### Community 36 - "Community 36"
Cohesion: 0.25
Nodes (7): Adaptive Modules (Included Only When Relevant):, Core Required Modules:, GDD Generator (Game Design Document Skill), Inputs Ingested, Modular GDD Structure, Persona & Purpose, Workflow

### Community 37 - "Community 37"
Cohesion: 0.25
Nodes (7): Anti-Patterns, Checklists, Goal, Modernize Skill, Quick Start, The Migration Loop, Workflows

### Community 39 - "Community 39"
Cohesion: 0.25
Nodes (7): Pillar 1: Spatial & World Authoring, Pillar 2: Visual Asset Preprocessing & Generation, Pillar 3: Sensory & Audio Workbenches, Pillar 4: Animation, Puppets & Rigging, Pillar 5: Content, Lore & Data Validation, Pillar 6: Developer Staging, Math Simulators & Test Infrastructure, Second-Layer Technical Question Bank

### Community 41 - "Community 41"
Cohesion: 0.25
Nodes (7): Anti-Patterns, Checklists, Context Monitoring, Goal, Quick Start, Status Skill, Workflows

### Community 43 - "Community 43"
Cohesion: 0.25
Nodes (7): Goal, 🛠️ Phase 1: The Project Story (Lead: Product Visionary), 🔍 Phase 2: The Deep Dive (The Panel), 📋 Phase 3: The Vision Summary & Handoff, 🧭 Project Vision Template (`project_vision.md`), 🎙️ SeikoClaw Interviewer Workflow, The Panel of Interviewers

### Community 46 - "Community 46"
Cohesion: 0.29
Nodes (6): ADR Format, Numbering, Optional sections, Template, What qualifies, When to offer an ADR

### Community 47 - "Community 47"
Cohesion: 0.29
Nodes (6): 1. Linux / macOS / WSL (Cron or Loop), 2. Windows (PowerShell Scheduled Task or Loop), Agent Self-Scheduling & Recurring Heartbeats, Execution Wrappers, Goal, Universal Floor

### Community 51 - "Community 51"
Cohesion: 0.29
Nodes (6): Handoff, Inputs Accepted, Persona & Operating Principles, Scope Surgeon (Minimum Fun Identifier), `VERTICAL_SLICE_SPEC.md` Schema, Workflow

### Community 52 - "Community 52"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Browser QA Workflow, Workflow

### Community 53 - "Community 53"
Cohesion: 0.12
Nodes (15): 1. Surface & Component Craft, 2. Typography & Optical Discipline, 3. Motion & Animation Physics (Kowalski Standards), 4. Mobile-Web Native Ergonomics, 5. Execution & Audit Workflow, Easing & Trajectory Rules, Frequency Decision Matrix, GPU Acceleration & Zero-Reflow Performance (+7 more)

### Community 54 - "Community 54"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, SeikoClaw Goal Prompter & Contract Enforcer, The 7-Field Hardened Contract Structure, When to Use, Workflow

### Community 55 - "Community 55"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Ingestor (Heavy File Ingestion), Workflow

### Community 56 - "Community 56"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Operating Map, Workflow

### Community 57 - "Community 57"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Red Team (Assumption Checker), Workflow

### Community 58 - "Community 58"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Shipper, Workflow

### Community 59 - "Community 59"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Skill Extractor, Workflow

### Community 60 - "Community 60"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Test Memory, Workflow

### Community 61 - "Community 61"
Cohesion: 0.29
Nodes (6): Invocation, Perform triage on an issue, Reference docs, Roles, Show what needs attention, Triage

### Community 62 - "Community 62"
Cohesion: 0.29
Nodes (6): 1. Scope the procedure, 2. Map each stage's journey, 3. Author the wizard, 4. Verify and hand off, Process, Wizard

### Community 63 - "Community 63"
Cohesion: 0.33
Nodes (5): Conventions, Issue tracker: Local Markdown, Wayfinding operations, When a skill says "fetch the relevant ticket", When a skill says "publish to the issue tracker"

### Community 64 - "Community 64"
Cohesion: 0.33
Nodes (5): Architect Skill & Hybrid DAG Planner, Checklists, Goal, Handoff, Quick Start

### Community 66 - "Community 66"
Cohesion: 0.33
Nodes (5): Core Capabilities & Tech Stack, Game Prototype Builder, Inputs & Prerequisites, Output Specification, Workflow

### Community 70 - "Community 70"
Cohesion: 0.33
Nodes (5): Core Capabilities, Mood Board Curator (Reference & Mood Board Skill), Output Specifications, `style_markers.json` Schema, Workflow

### Community 71 - "Community 71"
Cohesion: 0.33
Nodes (5): Evidence, Guidance, Merge Danger, Sections, Summary

### Community 72 - "Community 72"
Cohesion: 0.33
Nodes (5): CTO, Expert Panel Personas, Game Designer, Product Visionary, QA Lead

### Community 74 - "Community 74"
Cohesion: 0.33
Nodes (5): Anti-patterns, Rules of the loop, Seams — where tests go, Test-Driven Development, What a good test is

### Community 76 - "Community 76"
Cohesion: 0.33
Nodes (5): Agent Brief Template, File Locations, Objective, Requirements, Verification

### Community 78 - "Community 78"
Cohesion: 0.40
Nodes (4): 1. Harness Evaluation, Intentional Decisions, and Architectural Consolidation, Consequences, Context, Decisions

### Community 79 - "Community 79"
Cohesion: 0.40
Nodes (4): Agent Guardrails & Command Denylist, Files & Components, Goal, Usage & Maintenance

### Community 81 - "Community 81"
Cohesion: 0.40
Nodes (4): Before Building (Instant Gut-Check), Goal, Output Format, Workflow

### Community 82 - "Community 82"
Cohesion: 0.40
Nodes (3): Connection, Adds a directed dependency edge: `from_id` blocks/precedes `to_id`.         Per, Checks if a directed path exists from start_id to target_id along blocking/waits

### Community 83 - "Community 83"
Cohesion: 0.18
Nodes (10): Core Heuristics & Questioning Pillars, Defect Punch List Schema, Game Design & Visual Parity Critic, Mode 1: Gameplay & Mechanics Critic (Phase 1), Mode 2: Visual Parity & SxS Critic (Phase 2), Output Artifacts, Persona & Philosophy, Persona & Stance (+2 more)

### Community 84 - "Community 84"
Cohesion: 0.40
Nodes (4): Genre & Competitor Analysis, Integration & Handoff, Persona & Execution Mode, Workflow

### Community 85 - "Community 85"
Cohesion: 0.40
Nodes (4): Checklists, Goal, Interviewer Skill, Workflow

### Community 94 - "Community 94"
Cohesion: 0.40
Nodes (4): Checklists, Goal, Learnings Skill, Workflow

### Community 96 - "Community 96"
Cohesion: 0.40
Nodes (4): Core Directives, Mission, Operating Modes, Persona: Seikojin QA Strategist (The Brain)

### Community 97 - "Community 97"
Cohesion: 0.40
Nodes (4): Core Capabilities, Playtest Dictionary (Qualitative Heuristics), Playtest Feedback Loop, Workflow

### Community 98 - "Community 98"
Cohesion: 0.40
Nodes (4): Goal, Research & Deep Investigation Skill, Research Prompt Structure, Workflow

### Community 100 - "Community 100"
Cohesion: 0.33
Nodes (5): 1. Game Development & Visual Parity (Master Framework & Toolkit), 2. Quality Engineering & Gatekeeping, 3. Architecture & Task Orchestration, 4. Engineering Spec Pipeline & Productivity (Matt Pocock / David Andrej), SeikoClaw Harness Router

### Community 104 - "Community 104"
Cohesion: 0.40
Nodes (4): Execution Tasks, Post-Completion Learning Trigger, Prerequisites & Grounding, Task Checklist: [Feature / Task Goal]

### Community 105 - "Community 105"
Cohesion: 0.40
Nodes (4): Architect Workflow, Goal, Prerequisites, Steps

### Community 106 - "Community 106"
Cohesion: 0.40
Nodes (4): Executor Workflow, Goal, Prerequisites, Steps

### Community 107 - "Community 107"
Cohesion: 0.40
Nodes (4): Overview, Prerequisites, Steps, Sync to Openbrain Workflow

### Community 109 - "Community 109"
Cohesion: 0.50
Nodes (3): ADR Skill, Goal, Steps

### Community 110 - "Community 110"
Cohesion: 0.50
Nodes (3): Coverage Loop Skill, Goal, Workflow

### Community 111 - "Community 111"
Cohesion: 0.50
Nodes (3): Goal, Skill Distribution & Sync Workflow, Workflow

### Community 112 - "Community 112"
Cohesion: 0.14
Nodes (5): BaseLLMProvider, get_llm_provider(), LocalMindProvider, OpenAICompatibleProvider, Returns the most capable available LLM provider:     1. LocalMind (Local GGUF v

### Community 115 - "Community 115"
Cohesion: 0.50
Nodes (3): Core Directives, Mission, Persona: Seikojin QA Engineer (The Hands)

### Community 116 - "Community 116"
Cohesion: 0.50
Nodes (3): Pick a branch, Prototype, Rules that apply to both

### Community 117 - "Community 117"
Cohesion: 0.50
Nodes (3): Changed Files, Code Walkthrough, SeikoClaw Task Recap

### Community 118 - "Community 118"
Cohesion: 0.50
Nodes (3): Goal, Sweep Loop Skill, Workflow

### Community 120 - "Community 120"
Cohesion: 0.50
Nodes (3): Goal, Workflow, YouTube Transcript Ingestion Skill

## Knowledge Gaps
- **348 isolated node(s):** `deny-dangerous.sh script`, `Connection`, `Any`, `Changed Files`, `Code Walkthrough` (+343 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MemoryEngine` connect `Community 1` to `Community 0`, `Community 3`, `Community 4`, `Community 7`, `Community 9`, `Community 11`, `Community 13`, `Community 21`, `Community 22`, `Community 26`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `TaskGraph` connect `Community 16` to `Community 0`, `Community 38`, `Community 11`, `Community 82`, `Community 21`, `Community 22`, `Community 25`, `Community 27`, `Community 30`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `SeikoClaw` connect `Community 0` to `Community 1`, `Community 4`, `Community 7`, `Community 9`, `Community 11`, `Community 13`, `Community 16`, `Community 21`, `Community 26`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `MemoryEngine` (e.g. with `AutoCapture` and `datetime`) actually correct?**
  _`MemoryEngine` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TaskGraph` (e.g. with `GateEngine` and `Any`) actually correct?**
  _`TaskGraph` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `SeikoClaw` (e.g. with `AutoCapture` and `GateEngine`) actually correct?**
  _`SeikoClaw` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `HealthPatrol` (e.g. with `datetime` and `HealthPatrol`) actually correct?**
  _`HealthPatrol` has 9 INFERRED edges - model-reasoned connections that need verification._