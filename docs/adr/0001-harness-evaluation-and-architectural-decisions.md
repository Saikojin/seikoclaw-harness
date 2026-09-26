# 1. Harness Evaluation, Intentional Decisions, and Architectural Consolidation

We evaluated the 3rd-party assessment of the SeikoClaw harness across 8 core subsystems. We decided to retain the intentional local-first and agent-scaffolding principles (local LLM for background compression, hybrid DAG gating, opt-in vault security) while eliminating monorepo hardcoding, consolidating duplicated persistence layers, and wiring live telemetry into the watchdog and ready frontier.

## Context
A 3rd-party audit identified several apparent gaps in SeikoClaw: a simulated autonomous loop, an unwired watchdog, uninvoked vault unlocks with missing tables, hardcoded developer paths, duplicated persistence engines (`engine.py` vs `memory_engine.py`), ungated ready frontier claims, missing dependency manifests, and tightly-coupled LocalMind imports.

## Decisions

1. **Scaffolding vs Autonomous Loop**: SeikoClaw remains primarily an in-context cognitive scaffold for external agents (Antigravity, Claude, Gemini). The simulated loop is retained as a token-budget verification mode (`seikoclaw simulate`), while a dedicated DAG worker mode (`seikoclaw loop --dag`) will be added for headless execution of claimed frontier tasks.
2. **Persistence Consolidation**: `openbrain/memory_engine.py` is established as the single canonical persistence engine. `openbrain/engine.py` is refactored into a compatibility wrapper for `MemoryEngine`.
3. **Pluggable LLM & Portable Paths**: Background cognitive operations (Smart Caveman memory compression, skill evolution) retain their local-first zero-cost design principle, but are decoupled from hardcoded paths into a pluggable `LLMProvider` interface (supporting LocalMind, LLMWorkbench MCP, Ollama, and Cloud fallbacks).
4. **Frontier Gate Enforcement**: The ready frontier will enforce gate status during automated worker claims (`claim_next_ready`) while retaining visual gate badges (`[GATE: QA]`) during inspection views.
5. **Watchdog Telemetry**: `HealthPatrol.record_action()` is hooked directly into `run_task`, `execute`, and `auto_capture.py` to enable active loop spin and consecutive failure detection.
6. **Schema & Packaging Standards**: `secrets_vault` is added to `MemoryEngine._init_sqlite()`, and standard `pyproject.toml` and `requirements.txt` manifests are maintained in the repository root.

## Consequences
- The harness becomes fully portable across developer machines, CI runners, and different OS platforms.
- Telemetry and watchdog circuits actively protect against infinite loops and agent stalls.
- Zero-cost memory compression works across various local LLM backends without brittle path coupling.
- Automated workers cannot accidentally claim tasks awaiting QA or human approval.
