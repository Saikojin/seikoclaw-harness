# Graph Report - SeikoClaw-Harness  (2026-10-04)

## Corpus Check
- 241 files · ~288,770 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .tsv 1, .example 1)

## Summary
- 2072 nodes · 2844 edges · 176 communities (142 shown, 34 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 59 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3bc2deb4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SeikoClaw
- MemoryEngine
- Glossary of Terms
- HeuristicFallbackProvider
- SkillGater
- SeikoClaw: Agentic Coding Harness
- Game Tooling Catalog & Architectural Blueprints
- source-playbook.md
- book-to-skill/README.md
- 8. Task specifications
- Animation Recipes
- GateEngine
- Book-to-Skill Converter
- Vault
- MAP.md
- sys
- TaskGraph
- 🏛️ Core Principles
- Process
- rationale-template.md
- Seikojin Rules: The QA Constitution
- Animation Audit Playbook
- ContextEngine
- Apple Design
- The Fixes
- scan_generated_skill.py
- ConversationHistorySyncer
- TestTaskGraph
- Glossary
- Breaking UI
- template.sh
- HealthPatrol
- extract_single_file
- template.ps1
- Finding Animation Opportunities
- Animation Standards Reference
- feature-map-example/README.md
- Recurring skip candidates
- Seikoclaw Frontend Taste System
- seikoclaw.py
- discovery_tax.py
- Diagnosing Bugs
- Triage
- references/patterns.md
- seikoclaw-harness/SKILL.md
- codex-tools.md
- ExtractionError
- Process
- Steps
- wayfinder/SKILL.md
- Why
- dependencies.py
- _match_chapter_number
- re
- Worst-Case Catalog
- Mode 2: Visual Parity & SxS Critic (Phase 2)
- Output Format
- Output
- The list
- Patterns to detect and fix
- Supported Slash Commands & Syntaxes
- 2. The 5-Stage Autonomous Pipeline
- During the session
- How
- os
- Filtering Principles
- Reviewing Animations
- Show me your work
- Game Systems Modeler
- reviewer-prompt.md
- pi-tools.md
- Swarm
- to-spec/SKILL.md
- synthesizer-prompt.md
- Output Format
- BaseLLMProvider
- TestSkillGater
- _HTMLTextExtractor
- Process
- Figure it out
- GDD Generator (Game Design Document Skill)
- Interrogate
- Output Format
- Modernize Skill
- Status Skill
- investigator-prompt.md
- Output Format
- Process
- 🎙️ SeikoClaw Interviewer Workflow
- ADR Format
- Agent Self-Scheduling & Recurring Heartbeats
- Create a verification skill
- rubric.md
- Scope Surgeon (Minimum Fun Identifier)
- Seikoclaw Browser QA Workflow
- SeikoClaw Goal Prompter & Contract Enforcer
- Seikoclaw Ingestor (Heavy File Ingestion)
- Seikoclaw Operating Map
- Seikoclaw Red Team (Assumption Checker)
- Seikoclaw Shipper
- Seikoclaw Skill Extractor
- Seikoclaw Test Memory
- Task Checklist: [Feature / Task Goal]
- Agent Authoring: Writing Skills, Workflows & Documents for Agents
- Benchmark checklist
- Blast radius
- Game Prototype Builder
- code-quality-review.md
- Expert Panel Personas
- Mood Board Curator (Reference & Mood Board Skill)
- LocalMindProvider
- Sections
- Test-Driven Development
- epistemics.md
- Confidence Tiers
- Issue tracker: Local Markdown
- OpenAICompatibleProvider
- Agent Guardrails & Command Denylist
- design-red-flags.md
- Before Building (Instant Gut-Check)
- Genre & Competitor Analysis
- Interviewer Skill
- Learnings Skill
- loop-me/SKILL.md
- Maintain a verification skill
- Playtest Feedback Loop
- Research & Deep Investigation Skill
- retro/SKILL.md
- SeikoClaw Harness Router
- Persona: Seikojin QA Strategist (The Brain)
- Phrasing Guide
- Architect Workflow
- Executor Workflow
- Sync to Openbrain Workflow
- SeikoClaw High-Rigor Operating Directive
- SeikoClaw Task Recap
- ADR Skill
- Coverage Loop Skill
- Remove AI code slop
- hitl-loop.template.sh
- Skill Distribution & Sync Workflow
- No comments
- merge-safety.md
- synthesizer.md
- Persona: Seikojin QA Engineer (The Hands)
- Sweep Loop Skill
- Step 3. Spawn Parallel Investigators (default posture)
- YouTube Transcript Ingestion Skill
- 1. Harness Evaluation, Intentional Decisions, and Architectural Consolidation
- check
- tooling-reviewer.md
- deny-dangerous.sh script
- session-start.sh script
- comment-sicko.md
- NOTICE.md
- pr/CREDITS.md
- divergent-reviewer.md
- judgment-reviewer.md
- pdf_inspector_integration.py
- utils.py
- replay.py
- manifest.py
- epub.py
- rtf.py
- book-to-skill
- seikoclaw-harness

## God Nodes (most connected - your core abstractions)
1. `MemoryEngine` - 50 edges
2. `TaskGraph` - 38 edges
3. `SeikoClaw` - 36 edges
4. `extract_single_file()` - 29 edges
5. `HealthPatrol` - 25 edges
6. `Apple Design` - 21 edges
7. `ConversationHistorySyncer` - 20 edges
8. `Book-to-Skill Converter` - 19 edges
9. `ExtractionError` - 18 edges
10. `GateEngine` - 18 edges

## Surprising Connections (you probably didn't know these)
- `5. Persistence Layer Consolidation` --references--> `OpenbrainEngine`  [INFERRED]
  docs/ARCHITECTURE_EVALUATION.md → openbrain/engine.py
- `Executive Summary & Comparison Chart` --references--> `Vault`  [INFERRED]
  docs/ARCHITECTURE_EVALUATION.md → openbrain/vault.py
- `2. Watchdog & Circuit-Breaker Integration (`HealthPatrol`)` --references--> `HealthPatrol`  [INFERRED]
  docs/ARCHITECTURE_EVALUATION.md → openbrain/watchdog.py
- `Executive Summary & Comparison Chart` --references--> `HealthPatrol`  [INFERRED]
  docs/ARCHITECTURE_EVALUATION.md → openbrain/watchdog.py
- `Extending` --references--> `extract_single_file()`  [INFERRED]
  .agents/skills/book-to-skill/docs/architecture.md → .agents/skills/book-to-skill/book_to_skill/utils.py

## Import Cycles
- None detected.

## Communities (176 total, 34 thin omitted)

### Community 1 - "MemoryEngine"
Cohesion: 0.04
Nodes (12): Decisions, 1. Autonomous Loop Architecture (`loop_until_goal`), 2. Watchdog & Circuit-Breaker Integration (`HealthPatrol`), 4. Workspace Portability & Environment Configuration, 5. Persistence Layer Consolidation, 6. Hybrid DAG Gating Enforcement on Frontier, 7. Dependency Manifestation & Packaging, 8. LLM Abstraction for Background Cognitive Loops (+4 more)

### Community 2 - "Glossary of Terms"
Cohesion: 0.04
Nodes (43): Bard Talents (2d6 Table), Bard Titles, Bardic Arts, Chapter 1: The Bard Class, Class Fundamentals, Core Features & Abilities, Magical Dabbler, Presence (+35 more)

### Community 5 - "SeikoClaw: Agentic Coding Harness"
Cohesion: 0.09
Nodes (20): 1. Matt Pocock ([@mattpocockuk](https://github.com/mattpocock)), 2. David Andrej ([@davidandrej](https://github.com/davidandrej)), 3. Lauren Tan ([@poteto](https://github.com/poteto)) & Cursor Team, 4. Michael Denyer ([@michael-denyer](https://github.com/michael-denyer)), 5. Saikojin / SeikoClaw ([@Saikojin](https://github.com/Saikojin)), Credits & Upstream Attribution, 📜 License & Usage, 🎖️ Upstream Creators & Maintainers (+12 more)

### Community 6 - "Game Tooling Catalog & Architectural Blueprints"
Cohesion: 0.04
Nodes (43): Pillar 1: Spatial & World Authoring, Pillar 2: Visual Asset Preprocessing & Generation, Pillar 3: Sensory & Audio Workbenches, Pillar 4: Animation, Puppets & Rigging, Pillar 5: Content, Lore & Data Validation, Pillar 6: Developer Staging, Math Simulators & Test Infrastructure, Second-Layer Technical Question Bank, 1. Biome & Map Generator Workbench (`generator_workbench.html`) (+35 more)

### Community 7 - "source-playbook.md"
Cohesion: 0.04
Nodes (36): Common pitfalls, How to search it, What good evidence looks like here, What this source contains, What to return, Common pitfalls, How to search it, Investigation patterns that tend to pay off (+28 more)

### Community 8 - "book-to-skill/README.md"
Cohesion: 0.06
Nodes (31): 404 — this page turned to a blank chapter, Architecture, Design principles, Extending, Key components, Security, ❓ FAQ, ⚙️ How it works (+23 more)

### Community 9 - "8. Task specifications"
Cohesion: 0.06
Nodes (33): 10. Claims guardrail, 11. Agent instruction compatibility, 12. Definition of complete, 1. Why this work exists, 2. What the paper supports vs. what remains open, 3. Research rules: keep causal questions separable, 4. Cost discipline: no more expensive runs without a decision they can change, 5. Planned repository shape (+25 more)

### Community 10 - "Animation Recipes"
Cohesion: 0.06
Nodes (31): Accordion / collapse, Animation Recipes, Button press, Drag to dismiss, Drawer / sheet, Dropdown, popover, menu, select, Hold to confirm, Masking a crossfade that won't settle (+23 more)

### Community 12 - "Book-to-Skill Converter"
Cohesion: 0.06
Nodes (30): reuse_is_safe(), 1. Full Conversion (Default), 2. Analyze Only, 3. Generate from Prior Analysis, 4. Update / Fold-in (Existing Skill), Book-to-Skill Converter, cheatsheet.md, glossary.md (+22 more)

### Community 13 - "Vault"
Cohesion: 0.09
Nodes (7): 3. Secrets Vault & SQLite Schema Alignment, OpenbrainEngine, Vault, test_memory_engine_vault_table_creation(), test_openbrain_engine_compatibility(), test_vault_fresh_database(), test_vault_wrong_password()

### Community 14 - "MAP.md"
Cohesion: 0.06
Nodes (23): Game Design Critic — Game-Aware Grilling Persona, Key Architectural Decisions Made:, Question, Resolution, Key Architectural Decisions Made:, Key Architectural Decisions Made:, Question, Resolution (+15 more)

### Community 15 - "sys"
Cohesion: 0.11
Nodes (10): find_harness_root(), main(), AutoCapture, main(), UsageMonitor, get_session_context(), main(), print_progress_bar() (+2 more)

### Community 17 - "🏛️ Core Principles"
Cohesion: 0.07
Nodes (29): 10. Build the Lever (`principle-build-the-lever`), 11. Model the Domain (`principle-model-the-domain`), 12. Boundary Discipline (`principle-boundary-discipline`), 13. Type System Discipline (`principle-type-system-discipline`), 14. Make Operations Idempotent (`principle-make-operations-idempotent`), 15. Migrate Callers Then Delete Legacy APIs (`principle-migrate-callers-then-delete-legacy-apis`), 16. Separate Before Serializing Shared State (`principle-separate-before-serializing-shared-state`), 17. Prove It Works (`principle-prove-it-works`) (+21 more)

### Community 18 - "Process"
Cohesion: 0.07
Nodes (27): 1. State the question, 2. Pick the language, 3. Isolate the logic in a portable module, 4. Build the smallest TUI that exposes the state, 5. Make it runnable in one command, 6. Hand it over, 7. Capture the answer and the prototype, Anti-patterns (+19 more)

### Community 19 - "rationale-template.md"
Cohesion: 0.07
Nodes (25): Alternatives considered, Implementation reconciliation, Next implementation step, Open questions and risks, Problem, Shape, Synthesis decision, Tradeoffs accepted (+17 more)

### Community 20 - "Seikojin Rules: The QA Constitution"
Cohesion: 0.08
Nodes (24): 1. The Rabbit Philosophy (E2E Coherence), 2. Risk-Based Prioritization (RBT), 3. The Clean Slate Mandate, 4. Anti-Flakiness: Wait State Mastery, 5. Surgical Testability, 6. The Handoff Protocol, 7. Seikojin-Compliant Stack, 8. Visual Parity Rigor (Anti-Soft-Pass Mandate) (+16 more)

### Community 21 - "Animation Audit Playbook"
Cohesion: 0.08
Nodes (22): 1. Purpose & frequency, 2. Easing & duration, 3. Physicality & origin, 4. Interruptibility, 5. Performance, 6. Accessibility, 7. Cohesion & tokens, 8. Missed opportunities (+14 more)

### Community 23 - "Apple Design"
Cohesion: 0.10
Nodes (21): 10. Gesture design details (the "feel" checklist), 11. Frame-level smoothness, 12. Materials & depth — translucency conveys hierarchy, 13. Multimodal feedback — motion + sound + haptics, 14. Reduced motion & accessibility, 15. Typography — optical sizing, tracking, leading, 16. Design foundations — the eight principles, 17. Process (+13 more)

### Community 24 - "The Fixes"
Cohesion: 0.10
Nodes (21): 10. Status bar color doesn't match, 11. Right in Chrome, wrong on phone, 1. Hover state stuck after tap, 2. Gray/blue flash on tap, 3. Layout has the wrong height, 4. Page zooms into the input, 5. Tap feels laggy, 6. Pull-to-refresh hijacks scroll (+13 more)

### Community 25 - "scan_generated_skill.py"
Cohesion: 0.15
Nodes (14): is_invisible_codepoint(), sanitize_extracted_text(), _collect_skill_files(), Finding, _frontmatter_line_numbers(), _is_invisible(), main(), _read_skill_files() (+6 more)

### Community 26 - "ConversationHistorySyncer"
Cohesion: 0.15
Nodes (6): clean_user_content(), ConversationHistorySyncer, parse_iso_datetime(), test_clean_user_content(), test_extract_project_name(), test_parse_iso_datetime()

### Community 28 - "Glossary"
Cohesion: 0.11
Nodes (18): Animation Vocabulary, Easing — how speed changes over an animation, Entrances & Exits — how elements appear and disappear, Examples, Feedback & Interaction — responding to the user's actions, Glossary, Initial Response, Instructions (+10 more)

### Community 29 - "Breaking UI"
Cohesion: 0.11
Nodes (19): Breaking UI, Failure signatures, Hard Rules, Initial Response, Invocation Variants, Operating Posture, Part 1 — What broke, Part 2 — Decisions for you (+11 more)

### Community 30 - "template.sh"
Cohesion: 0.23
Nodes (17): ask(), ask_secret(), banner(), _clear(), _existing(), finish(), pause(), set_secret() (+9 more)

### Community 32 - "extract_single_file"
Cohesion: 0.22
Nodes (9): extract_with_ebook_convert(), clean_pdftotext(), count_pages(), extract_with_docling(), extract_with_pdfminer(), extract_with_pdftotext(), extract_with_pypdf(), looks_image_only() (+1 more)

### Community 33 - "template.ps1"
Cohesion: 0.18
Nodes (13): Ask-SecretValue(), Ask-Value(), Clear-WizardScreen(), Finish-Wizard(), Get-ExistingEnv(), Pause-Wizard(), Note(), Open-Url() (+5 more)

### Community 34 - "Finding Animation Opportunities"
Cohesion: 0.12
Nodes (16): 1. Frequency — how often will a user see this?, 2. Purpose — why does this animate?, 3. Speed — can it stay inside budget?, 4. Function — does motion help or hinder here?, Finding Animation Opportunities, Hard Rules, Initial Response, Operating Posture (+8 more)

### Community 35 - "Animation Standards Reference"
Cohesion: 0.12
Nodes (16): Accessibility, Animation Standards Reference, Asymmetric timing, Cohesion, Debugging (recommend in reviews when feel is uncertain), Duration, Easing, Gestures & drag (+8 more)

### Community 36 - "feature-map-example/README.md"
Cohesion: 0.12
Nodes (13): Driving it with control-notes, Gotchas, How to get to it (user POV), Sub-features, Baseline preconditions, Driving conventions, Feature entry contract, Features (+5 more)

### Community 37 - "Recurring skip candidates"
Cohesion: 0.12
Nodes (15): Ask by default, Candidate learnings from recent babysits, Contract-test drift claims are cheaply verifiable — run the test first, Decision rubric, Existing framework or component invariant covers the warning, Intentional UI or design-system visual changes, Learned pattern format, Manual reimplementations of native browser behavior (+7 more)

### Community 38 - "Seikoclaw Frontend Taste System"
Cohesion: 0.12
Nodes (16): 1. Surface & Component Craft, 2. Typography & Optical Discipline, 3. Motion & Animation Physics (Kowalski Standards), 4. The Sonner Principles (Loved Component Craft), 5. Mobile-Web Native Ergonomics, 6. Execution & Audit Workflow, Easing & Trajectory Rules, Frequency Decision Matrix (+8 more)

### Community 39 - "seikoclaw.py"
Cohesion: 0.14
Nodes (4): get_llm_provider(), IterationBudget, main(), validate_command_safety()

### Community 40 - "discovery_tax.py"
Cohesion: 0.19
Nodes (7): _chapter_number(), best_chapter(), count_tokens(), extract_toc(), main(), split_chapters(), token_method()

### Community 41 - "Diagnosing Bugs"
Cohesion: 0.13
Nodes (14): Completion criterion: a tight loop that goes red, Diagnosing Bugs, Minimise, Non-deterministic bugs, Phase 1: Build a feedback loop, Phase 2: Reproduce + minimise, Phase 3: Hypothesise, Phase 4: Instrument (+6 more)

### Community 42 - "Triage"
Cohesion: 0.13
Nodes (12): Agent Brief Template, File Locations, Objective, Requirements, Verification, Out of Scope Rules, Invocation, Perform triage on an issue (+4 more)

### Community 43 - "references/patterns.md"
Cohesion: 0.13
Nodes (14): Boundary validation, Branded types, Constructive modeling, Discriminated unions, Exhaustiveness, Narrowing hierarchy, No `as` casts, Object args (+6 more)

### Community 44 - "seikoclaw-harness/SKILL.md"
Cohesion: 0.19
Nodes (4): Codebase Design, Workflow, Handoff, Steps

### Community 45 - "codex-tools.md"
Cohesion: 0.14
Nodes (11): Driver and bundled skills pstack references, Instructions file, Model names, Per-skill notes, Session routing hook, Subagent policy, Tool actions, Vendored scripts (+3 more)

### Community 46 - "ExtractionError"
Cohesion: 0.28
Nodes (7): ExtractionError, extract_docx(), extract_docx_with_python_docx(), extract_docx_with_zipfile(), emit_block(), inline_text(), validate_docx_xml_safety()

### Community 47 - "Process"
Cohesion: 0.15
Nodes (12): 1. Gather context & restate intent, 2. Explore the codebase (optional), 3. Draft vertical slices, 4. Quiz the user, 5. Publish the tickets to the configured tracker, Acceptance criteria, Blocked by, <NN> — <Ticket title> (+4 more)

### Community 48 - "Steps"
Cohesion: 0.17
Nodes (11): 1. Detect the environment, 2. Install dependency-cruiser, 3. Write the config, 4. Wire it into the checks, 5. Scaffold the example package, 6. Prove the rules bite, 7. Document the convention, Notes (+3 more)

### Community 49 - "wayfinder/SKILL.md"
Cohesion: 0.17
Nodes (11): Chart the map, Fog of war, Invocation, Out of scope, Plan, don't do, Refer by name, The Map, The map body (+3 more)

### Community 50 - "Why"
Cohesion: 0.17
Nodes (11): Common Failure Modes to Avoid, Models, Operating Posture, Output Format, Reasoning effort, Reference Files, Step 1. Understand the Target and the Question, Step 2. Establish the Code Anchor (+3 more)

### Community 51 - "dependencies.py"
Cohesion: 0.29
Nodes (7): install_python_packages(), isolated_install_hint(), missing_python_packages(), offer_dependency_install(), prepare_dependencies(), python_module_available(), run_dependency_check()

### Community 52 - "_match_chapter_number"
Cohesion: 0.18
Nodes (6): _cn_numeral_to_int(), _fa_chapter_number(), _int_to_roman(), _is_prose_period_tail(), _match_chapter_number(), _roman_to_int()

### Community 53 - "re"
Cohesion: 0.36
Nodes (7): audit(), get_list_items(), get_scalar(), main(), parse_frontmatter(), tool_base(), top_level_keys()

### Community 54 - "Worst-Case Catalog"
Cohesion: 0.18
Nodes (10): Collections, Emails, URLs, identifiers, Environment, Images and media, Labels, titles, and copy from data, Numbers and money, People and names, States (+2 more)

### Community 55 - "Mode 2: Visual Parity & SxS Critic (Phase 2)"
Cohesion: 0.18
Nodes (10): Core Heuristics & Questioning Pillars, Defect Punch List Schema, Game Design & Visual Parity Critic, Mode 1: Gameplay & Mechanics Critic (Phase 1), Mode 2: Visual Parity & SxS Critic (Phase 2), Output Artifacts, Persona & Philosophy, Persona & Stance (+2 more)

### Community 56 - "Output Format"
Cohesion: 0.18
Nodes (10): Communication Style, Explorer Findings, Gotchas, How It Works, Instructions, Key Concepts, Original Question, Output Format (+2 more)

### Community 57 - "Output"
Cohesion: 0.18
Nodes (10): Boundaries, Components Found, Exploration Instructions, Files Read, Flow, Non-Obvious Things, Open Questions, Output (+2 more)

### Community 58 - "The list"
Cohesion: 0.18
Nodes (10): Charts, Common mismatches to catch, How to use this, Initial Response, Interaction & performance, Motion & visuals, Picking The Right Library, State & styling (+2 more)

### Community 59 - "Patterns to detect and fix"
Cohesion: 0.18
Nodes (10): Communication artifacts, Content, Filler, Jargon, Language, Patterns to detect and fix, Plain speech, Process (+2 more)

### Community 61 - "Supported Slash Commands & Syntaxes"
Cohesion: 0.20
Nodes (9): 1. Seamless Ground Textures, 2. Modular Character Builder Layers (Hair, Headgear, Armor, Paperdoll Parts), 3. 2D Sprites, Tokens, and Props (Full Characters & Entities), 4. Backdrops, Map Views & Panoramas, 5. General / Custom Images, asset-generator, Quick Reference: Core Prompt Engineering Rules, Quota & Batch Protection Best Practices (+1 more)

### Community 62 - "2. The 5-Stage Autonomous Pipeline"
Cohesion: 0.20
Nodes (9): 1. Project Manifest & State Tracking, 2. The 5-Stage Autonomous Pipeline, 3. Invocation Triggers, Game Forge: Master Autonomous Game Creation Framework, Stage A: Brief, Locked References & Deep Plan (Autonomous $\rightarrow$ HITL Gate 1), Stage B: Scope Carving & Playable Foundation (Autonomous $\rightarrow$ Gate B), Stage C: Staged Art Pipeline & Authoring Workbenches (Autonomous $\rightarrow$ HITL Gate 3), Stage D: Side-by-Side (SxS) Visual Bar Parity Loop (Autonomous $\rightarrow$ Critic WIN) (+1 more)

### Community 63 - "During the session"
Cohesion: 0.20
Nodes (9): Challenge against the glossary, Cross-reference with code, Discuss concrete scenarios, Domain awareness, During the session, File structure, Offer ADRs sparingly, Sharpen fuzzy language (+1 more)

### Community 64 - "How"
Cohesion: 0.20
Nodes (9): How, Models, Output Format, Reasoning effort, Step 1. Assess Complexity, Step 2a. Explore (complex questions only), Step 2b. Direct Explain (simple questions), Step 3. Synthesize (complex questions only) (+1 more)

### Community 65 - "os"
Cohesion: 0.10
Nodes (9): default_output_dir(), get_playbook(), list_playbooks(), setup(), test_record_and_ingest_decision_trail(), test_conversation_sync_lifecycle(), test_adversarial_gate_lifecycle(), test_playbook_expansion_creates_sequential_dag() (+1 more)

### Community 66 - "Filtering Principles"
Cohesion: 0.20
Nodes (9): Filtering Principles, Hypothetical vs. Actual, "I Would Have Done It Differently", Missing Context Signals, Nitpick Gravity, Premature Abstraction Warnings, Verdict Calibration, When Reviewers Are Right (+1 more)

### Community 67 - "Reviewing Animations"
Cohesion: 0.20
Nodes (10): Aggressive Escalation Triggers, Guidelines, Initial Response, Operating Posture, Part 1 — Findings table (REQUIRED), Part 2 — Verdict (REQUIRED), Remedial Preference Hierarchy, Required Output Format (+2 more)

### Community 68 - "Show me your work"
Cohesion: 0.20
Nodes (9): Audit the log against the transcript, Composing this skill, Cross-model review of the trail, Logging a row, Reviewing the trail, Rules, Show me your work, The format (+1 more)

### Community 69 - "Game Systems Modeler"
Cohesion: 0.22
Nodes (8): 1. Combat & TTK, 2. Progression Curves, Core Capabilities, Dashboard Features:, Game Systems Modeler, Output Specifications, Supported Math Domains & Formulas, Workflow

### Community 70 - "reviewer-prompt.md"
Cohesion: 0.22
Nodes (8): Code Quality Lens, Code Under Review, Instructions, Intent, Output, Review Rubric, What Makes a Good Finding, What to Avoid

### Community 71 - "pi-tools.md"
Cohesion: 0.22
Nodes (8): Driver and bundled skills pstack references, Instructions file, Model names, Per-skill notes, Session routing, Subagent policy, Tool actions, Vendored scripts

### Community 72 - "Swarm"
Cohesion: 0.22
Nodes (8): Models, Phase A: Frame, Phase B: Fan out, Phase C: Aggregate, Phase D: Report, Reasoning effort, Start, Swarm

### Community 73 - "to-spec/SKILL.md"
Cohesion: 0.22
Nodes (8): Core Intent & Problem Statement, Further Notes, Implementation Decisions, Out of Scope, Process, Solution, Testing Decisions, User Stories

### Community 74 - "synthesizer-prompt.md"
Cohesion: 0.22
Nodes (8): A Final Note, Epistemics Framework, Instructions, Investigator Findings, Quality Check Before Returning, Sources That Weren't Searched, The Code Anchor, The Question

### Community 75 - "Output Format"
Cohesion: 0.22
Nodes (9): Competing Hypotheses, Confidence Summary, Output Format, Sources Consulted, The Code in Question, The Question, What We Can Reasonably Infer, What We Don't Know (+1 more)

### Community 79 - "Process"
Cohesion: 0.25
Nodes (7): 1. Pin the fixed point, 2. Identify the spec source, 3. Identify the standards sources, 4. Spawn both sub-agents in parallel, 5. Aggregate, Process, Why two axes

### Community 80 - "Figure it out"
Cohesion: 0.25
Nodes (7): Figure it out, Phase A: Frame, Phase B: Design the workflow, Phase C: Run the loop, Phase D: Keep the audit trail, Phase E: Verify and hand back, Start

### Community 81 - "GDD Generator (Game Design Document Skill)"
Cohesion: 0.25
Nodes (7): Adaptive Modules (Included Only When Relevant):, Core Required Modules:, GDD Generator (Game Design Document Skill), Inputs Ingested, Modular GDD Structure, Persona & Purpose, Workflow

### Community 83 - "Interrogate"
Cohesion: 0.25
Nodes (7): Interrogate, Reasoning effort, Step 1, Determine Scope, Step 2, State the Intent, Step 3, Spawn Reviewers, Step 4, Synthesize, Step 5, Lead Judgment

### Community 84 - "Output Format"
Cohesion: 0.25
Nodes (8): Act On, Agreement Map, Consider, Dismissed, Intent, Noted, Output Format, Reviewers

### Community 85 - "Modernize Skill"
Cohesion: 0.25
Nodes (7): Anti-Patterns, Checklists, Goal, Modernize Skill, Quick Start, The Migration Loop, Workflows

### Community 86 - "Status Skill"
Cohesion: 0.25
Nodes (7): Anti-Patterns, Checklists, Context Monitoring, Goal, Quick Start, Status Skill, Workflows

### Community 87 - "investigator-prompt.md"
Cohesion: 0.25
Nodes (7): Epistemic Discipline, Investigation Instructions, Operating Posture, The Code Anchor, The Question, What You're Not Doing, Your Assigned Source

### Community 88 - "Output Format"
Cohesion: 0.25
Nodes (8): Additional Leads, Contradictions, Direct Evidence Found, Gaps, Indirect / Circumstantial Evidence, Output Format, Source, What I Searched

### Community 89 - "Process"
Cohesion: 0.29
Nodes (6): 1. Scope the procedure, 2. Map each stage's journey, 3. Author the wizard, 4. Verify and hand off, Process, Wizard

### Community 90 - "🎙️ SeikoClaw Interviewer Workflow"
Cohesion: 0.25
Nodes (7): Goal, 🛠️ Phase 1: The Project Story (Lead: Product Visionary), 🔍 Phase 2: The Deep Dive (The Panel), 📋 Phase 3: The Vision Summary & Handoff, 🧭 Project Vision Template (`project_vision.md`), 🎙️ SeikoClaw Interviewer Workflow, The Panel of Interviewers

### Community 91 - "ADR Format"
Cohesion: 0.29
Nodes (6): ADR Format, Numbering, Optional sections, Template, What qualifies, When to offer an ADR

### Community 92 - "Agent Self-Scheduling & Recurring Heartbeats"
Cohesion: 0.29
Nodes (6): 1. Linux / macOS / WSL (Cron or Loop), 2. Windows (PowerShell Scheduled Task or Loop), Agent Self-Scheduling & Recurring Heartbeats, Execution Wrappers, Goal, Universal Floor

### Community 93 - "Create a verification skill"
Cohesion: 0.29
Nodes (6): 1. Interview the repo, not the user, 2. Generate the skill, 3. Seed the feature map, 4. Prove the generated skill before handing it over, 5. Offer the maintenance loop, Create a verification skill

### Community 94 - "rubric.md"
Cohesion: 0.29
Nodes (6): Complexity Budget, Correctness, Root Causes vs. Symptoms, Security, Structural Integrity, Verification

### Community 95 - "Scope Surgeon (Minimum Fun Identifier)"
Cohesion: 0.29
Nodes (6): Handoff, Inputs Accepted, Persona & Operating Principles, Scope Surgeon (Minimum Fun Identifier), `VERTICAL_SLICE_SPEC.md` Schema, Workflow

### Community 96 - "Seikoclaw Browser QA Workflow"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Browser QA Workflow, Workflow

### Community 97 - "SeikoClaw Goal Prompter & Contract Enforcer"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, SeikoClaw Goal Prompter & Contract Enforcer, The 7-Field Hardened Contract Structure, When to Use, Workflow

### Community 98 - "Seikoclaw Ingestor (Heavy File Ingestion)"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Ingestor (Heavy File Ingestion), Workflow

### Community 99 - "Seikoclaw Operating Map"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Operating Map, Workflow

### Community 100 - "Seikoclaw Red Team (Assumption Checker)"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Red Team (Assumption Checker), Workflow

### Community 101 - "Seikoclaw Shipper"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Shipper, Workflow

### Community 102 - "Seikoclaw Skill Extractor"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Skill Extractor, Workflow

### Community 103 - "Seikoclaw Test Memory"
Cohesion: 0.29
Nodes (6): Boundaries, Goal, Output Format, Required Inputs, Seikoclaw Test Memory, Workflow

### Community 104 - "Task Checklist: [Feature / Task Goal]"
Cohesion: 0.40
Nodes (4): Execution Tasks, Post-Completion Learning Trigger, Prerequisites & Grounding, Task Checklist: [Feature / Task Goal]

### Community 105 - "Agent Authoring: Writing Skills, Workflows & Documents for Agents"
Cohesion: 0.33
Nodes (5): 1. Context Pointers & Trigger Discipline, 2. Progressive Disclosure Ladder, 3. Leading Words & Completion Criteria, 4. Writing Modes (Explore vs. Exploit), Agent Authoring: Writing Skills, Workflows & Documents for Agents

### Community 106 - "Benchmark checklist"
Cohesion: 0.33
Nodes (5): Before you run anything, Benchmark checklist, How this fits the other perf material, Report, The questions

### Community 107 - "Blast radius"
Cohesion: 0.33
Nodes (5): Blast radius, Don't trust your own writeup, How sure are you, Steps, What to hand back

### Community 108 - "Game Prototype Builder"
Cohesion: 0.33
Nodes (5): Core Capabilities & Tech Stack, Game Prototype Builder, Inputs & Prerequisites, Output Specification, Workflow

### Community 109 - "code-quality-review.md"
Cohesion: 0.33
Nodes (5): Approval Bar, Core Prompt, Dimensions, Output Expectations, Review Tone

### Community 110 - "Expert Panel Personas"
Cohesion: 0.33
Nodes (5): CTO, Expert Panel Personas, Game Designer, Product Visionary, QA Lead

### Community 111 - "Mood Board Curator (Reference & Mood Board Skill)"
Cohesion: 0.33
Nodes (5): Core Capabilities, Mood Board Curator (Reference & Mood Board Skill), Output Specifications, `style_markers.json` Schema, Workflow

### Community 113 - "Sections"
Cohesion: 0.33
Nodes (5): Evidence, Guidance, Merge Danger, Sections, Summary

### Community 114 - "Test-Driven Development"
Cohesion: 0.33
Nodes (5): Anti-patterns, Rules of the loop, Seams — where tests go, Test-Driven Development, What a good test is

### Community 115 - "epistemics.md"
Cohesion: 0.33
Nodes (5): Calibration Check Before Finalizing, Claims about human decisions, The Sycophancy Trap, When Evidence Contradicts, When Evidence Is Missing

### Community 116 - "Confidence Tiers"
Cohesion: 0.33
Nodes (6): 1. Direct, 2. Supported, 3. Inferred, 4. Speculative, 5. Unknown, Confidence Tiers

### Community 117 - "Issue tracker: Local Markdown"
Cohesion: 0.33
Nodes (5): Conventions, Issue tracker: Local Markdown, Wayfinding operations, When a skill says "fetch the relevant ticket", When a skill says "publish to the issue tracker"

### Community 120 - "Agent Guardrails & Command Denylist"
Cohesion: 0.40
Nodes (4): Agent Guardrails & Command Denylist, Files & Components, Goal, Usage & Maintenance

### Community 121 - "design-red-flags.md"
Cohesion: 0.40
Nodes (4): Information leakage, Pass-through method, Shallow module, Temporal decomposition

### Community 122 - "Before Building (Instant Gut-Check)"
Cohesion: 0.40
Nodes (4): Before Building (Instant Gut-Check), Goal, Output Format, Workflow

### Community 123 - "Genre & Competitor Analysis"
Cohesion: 0.40
Nodes (4): Genre & Competitor Analysis, Integration & Handoff, Persona & Execution Mode, Workflow

### Community 124 - "Interviewer Skill"
Cohesion: 0.40
Nodes (4): Checklists, Goal, Interviewer Skill, Workflow

### Community 125 - "Learnings Skill"
Cohesion: 0.40
Nodes (4): Checklists, Goal, Learnings Skill, Workflow

### Community 126 - "loop-me/SKILL.md"
Cohesion: 0.40
Nodes (4): Definition of done, The loop lens, The workspace, Vocabulary

### Community 127 - "Maintain a verification skill"
Cohesion: 0.40
Nodes (4): Edit scope, Maintain a verification skill, Outcomes, Pass

### Community 128 - "Playtest Feedback Loop"
Cohesion: 0.40
Nodes (4): Core Capabilities, Playtest Dictionary (Qualitative Heuristics), Playtest Feedback Loop, Workflow

### Community 129 - "Research & Deep Investigation Skill"
Cohesion: 0.40
Nodes (4): Goal, Research & Deep Investigation Skill, Research Prompt Structure, Workflow

### Community 130 - "retro/SKILL.md"
Cohesion: 0.40
Nodes (4): Files, Implementation vs Review, Reference, Steps

### Community 131 - "SeikoClaw Harness Router"
Cohesion: 0.40
Nodes (5): 1. Game Development & Visual Parity (Master Framework & Toolkit), 2. Quality Engineering & Gatekeeping, 3. Architecture & Task Orchestration, 4. Engineering Spec Pipeline & Productivity (Matt Pocock / David Andrej), SeikoClaw Harness Router

### Community 132 - "Persona: Seikojin QA Strategist (The Brain)"
Cohesion: 0.40
Nodes (4): Core Directives, Mission, Operating Modes, Persona: Seikojin QA Strategist (The Brain)

### Community 133 - "Phrasing Guide"
Cohesion: 0.40
Nodes (5): Avoid rationalization, Phrasing Guide, Words that carry confidence. Use carefully, Words that hedge. Use for inferences, Words to avoid

### Community 134 - "Architect Workflow"
Cohesion: 0.40
Nodes (4): Architect Workflow, Goal, Prerequisites, Steps

### Community 135 - "Executor Workflow"
Cohesion: 0.40
Nodes (4): Executor Workflow, Goal, Prerequisites, Steps

### Community 136 - "Sync to Openbrain Workflow"
Cohesion: 0.40
Nodes (4): Overview, Prerequisites, Steps, Sync to Openbrain Workflow

### Community 137 - "SeikoClaw High-Rigor Operating Directive"
Cohesion: 0.50
Nodes (3): Automatic Playbook Routing, Mandatory Posture, SeikoClaw High-Rigor Operating Directive

### Community 138 - "SeikoClaw Task Recap"
Cohesion: 0.50
Nodes (3): Changed Files, Code Walkthrough, SeikoClaw Task Recap

### Community 139 - "ADR Skill"
Cohesion: 0.50
Nodes (3): ADR Skill, Goal, Steps

### Community 140 - "Coverage Loop Skill"
Cohesion: 0.50
Nodes (3): Coverage Loop Skill, Goal, Workflow

### Community 141 - "Remove AI code slop"
Cohesion: 0.50
Nodes (3): Focus Areas, Guardrails, Remove AI code slop

### Community 142 - "hitl-loop.template.sh"
Cohesion: 0.83
Nodes (3): capture(), hitl-loop.template.sh script, step()

### Community 143 - "Skill Distribution & Sync Workflow"
Cohesion: 0.50
Nodes (3): Goal, Skill Distribution & Sync Workflow, Workflow

### Community 144 - "No comments"
Cohesion: 0.50
Nodes (3): No comments, Scope, Steps

### Community 145 - "merge-safety.md"
Cohesion: 0.50
Nodes (3): Preserve concurrent writes and child changes, Read both pending mechanisms, What the service guards

### Community 146 - "synthesizer.md"
Cohesion: 0.50
Nodes (3): Accepted, Backlog, Rejected

### Community 147 - "Persona: Seikojin QA Engineer (The Hands)"
Cohesion: 0.50
Nodes (3): Core Directives, Mission, Persona: Seikojin QA Engineer (The Hands)

### Community 148 - "Sweep Loop Skill"
Cohesion: 0.50
Nodes (3): Goal, Sweep Loop Skill, Workflow

### Community 149 - "Step 3. Spawn Parallel Investigators (default posture)"
Cohesion: 0.50
Nodes (4): Discovery, Investigator roster. One per available evidence category, Step 3. Spawn Parallel Investigators (default posture), When to skip an investigator

### Community 150 - "YouTube Transcript Ingestion Skill"
Cohesion: 0.50
Nodes (3): Goal, Workflow, YouTube Transcript Ingestion Skill

### Community 151 - "1. Harness Evaluation, Intentional Decisions, and Architectural Consolidation"
Cohesion: 0.50
Nodes (3): 1. Harness Evaluation, Intentional Decisions, and Architectural Consolidation, Consequences, Context

### Community 163 - "pdf_inspector_integration.py"
Cohesion: 0.15
Nodes (12): main(), enrich_pdf_inspector_metadata(), _fallback_reason(), inspect_pdf(), install_pdf_inspector_hook(), wrapped(), _looks_like_pdf(), _normalise_pdf_type() (+4 more)

### Community 164 - "utils.py"
Cohesion: 0.10
Nodes (15): supported_formats_message(), normalize_install_mode(), _closed_fence_line_numbers(), detect_structure(), estimate_tokens(), _fa_ordinal_map(), main(), _numbered_titles_are_structural() (+7 more)

### Community 165 - "replay.py"
Cohesion: 0.17
Nodes (9): canonical_json(), load_fixture(), main(), replay(), aggregate(), _count(), score(), score_trajectory() (+1 more)

### Community 166 - "manifest.py"
Cohesion: 0.11
Nodes (17): _budgets(), build_manifest(), canonical_json(), _commit(), _fail(), _hashes(), _identifier(), main() (+9 more)

### Community 169 - "epub.py"
Cohesion: 0.18
Nodes (7): count_epub_chapters(), count_epub_images(), extract_with_ebooklib(), extract_with_zipfile(), _find_opf_path(), _opf_opening_tags(), _resolve_manifest_href()

### Community 173 - "rtf.py"
Cohesion: 0.22
Nodes (9): extract_html_content(), extract_html_file(), _decode_hex_run(), extract_rtf(), _rtf_ansi_encoding(), _rtf_unicode_repl(), _strip_destination_groups(), strip_rtf_fallback() (+1 more)

## Knowledge Gaps
- **996 isolated node(s):** `deny-dangerous.sh script`, `session-start.sh script`, `book-to-skill`, `seikoclaw-harness`, `Mandatory Posture` (+991 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1282 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `reuse_is_safe()` connect `Book-to-Skill Converter` to `utils.py`?**
  _High betweenness centrality (0.226) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `MemoryEngine` (e.g. with `AutoCapture` and `Decisions`) actually correct?**
  _`MemoryEngine` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `deny-dangerous.sh script`, `session-start.sh script`, `book-to-skill` to the rest of the system?**
  _996 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SeikoClaw` be split into smaller, more focused modules?**
  _Cohesion score 0.0960591133004926 - nodes in this community are weakly interconnected._
- **Are the 4 inferred relationships involving `TaskGraph` (e.g. with `GateEngine` and `SeikoClaw`) actually correct?**
  _`TaskGraph` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `MemoryEngine` be split into smaller, more focused modules?**
  _Cohesion score 0.044162129461584994 - nodes in this community are weakly interconnected._
- **Are the 9 inferred relationships involving `SeikoClaw` (e.g. with `AutoCapture` and `GateEngine`) actually correct?**
  _`SeikoClaw` has 9 INFERRED edges - model-reasoned connections that need verification._