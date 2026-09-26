# SeikoClaw Harness: 3rd-Party Evaluation & Architectural Rationale

This document addresses the findings from the 3rd-party evaluation of the **SeikoClaw Agentic Coding Harness**. It classifies each finding as an **Intentional Architectural Decision**, **Prototyping Shortcut / Tech Debt**, or **Integration Inconsistency**, documents why each choice was made, and defines the target state / evolution plan.

---

## Executive Summary & Comparison Chart

| # | Evaluation Finding / Gap | Classification | Why It Is This Way (Original Intent & Context) | Should It Be Different? (Target State & Rationale) |
|---|---|---|---|---|
| **1** | **Autonomous loop is mostly a stub** (`loop_until_goal` simulates turns without agent dispatch) | **Intentional Scaffolding / Incomplete Autonomous Driver** | SeikoClaw acts primarily as an *in-context cognitive scaffold* for human-in-the-loop agents (Antigravity, Claude, Gemini). The `loop` method was built as a token drift & handoff simulation benchmark rather than a headless outer-loop runner. | **Yes.** Clearly separate interactive scaffolding from headless execution. Provide a true DAG worker loop (`seikoclaw loop --dag`) that pulls ready frontier tasks and executes via the sandboxed command runner. |
| **2** | **Watchdog is disconnected** (`HealthPatrol.record_action` called in tests, not CLI) | **Integration Inconsistency** | `HealthPatrol` was implemented as a standalone state machine for cycle detection (3x identical hashes, consecutive failures, context ceiling) during Seikojin QA development. Telemetry ingestion was decoupled from core execution. | **Yes.** Hook `record_action()` into `run_task()`, `execute`, and `auto_capture.py`. Check `get_health_status()` on every iteration to trip circuit breakers on stalls. |
| **3** | **Vault is unused in main flow & missing table in `MemoryEngine`** | **Intentional Opt-In + Schema Sync Defect** | Interactive local developers rely on OS environment variables for keys. Vault was designed as an optional AES-GCM at-rest encryption layer for shared hosts. `secrets_vault` table was in `schema.sql` but missed in `MemoryEngine._init_sqlite()`. | **Yes.** Add `secrets_vault` creation to `MemoryEngine._init_sqlite()` and self-heal in `Vault`. Expose CLI commands (`seikoclaw vault set/get`) and allow graceful fallback from env vars. |
| **4** | **Hardcoded personal paths** (Tablebuddy, BookIngestion models, .master_wiki, agent-native) | **Prototyping Debt / Monorepo Coupling** | Rapid prototyping in the author's primary workstation environment (`d:/DevWorkspace/`) connecting the local multi-project ecosystem before packaging for general distribution. | **Yes.** Abstract to an environment/config hierarchy: Environment Variables -> `.seikoclaw.yaml` -> Relative workspace auto-discovery -> Graceful warnings/no-ops. |
| **5** | **Duplicate persistence layer** (`openbrain/engine.py` vs `memory_engine.py`) | **Deprecated Legacy Artifact** | `openbrain/engine.py` was the initial Phase 1 zero-dependency SQLite-only prototype. Phase 2 introduced vector embeddings (ChromaDB) and tiered context engines in `memory_engine.py`. | **Yes.** Consolidate completely into `memory_engine.py`. Turn `engine.py` into a backward-compatible alias or deprecate/remove it, and update README documentation. |
| **6** | **Gates not enforced on ready frontier** (`get_ready_frontier` ignores pending gates) | **Intentional Visibility Model / Incomplete Claim Guard** | The ready frontier was designed to display all tasks with cleared *dependency edges*. Gated tasks were badged (`[GATE: QA]`) so specialized agents/humans could see and claim them for certification. | **Yes.** Filter by default in automated worker dispatch (`claim_next_ready`) so general workers do not claim pending QA/Human gated tasks, while preserving visibility in inspection modes. |
| **7** | **No dependency manifest** (Missing `requirements.txt` / `pyproject.toml`) | **Packaging Debt** | Developed within a pre-configured global development environment containing `chromadb`, `tiktoken`, `cryptography`, and `pyyaml`. | **Yes.** Provide standard `pyproject.toml` and `requirements.txt` with clear separation between core dependencies and optional LLM backends. |
| **8** | **External LLM dependency for core features** (`LocalMind` coupling) | **Intentional Cost/Privacy Architecture + Brittle Binding** | Background cognitive tasks (Smart Caveman memory compression, post-task skill synthesis) were intentionally architected to run on local on-device models to prevent cloud API token drain and maintain data privacy. | **Yes.** Decouple `LocalMind` into a pluggable `LLMProvider` interface supporting Local GGUF, LLMWorkbench MCP (`query_local_model`), Ollama/vLLM endpoints, and cloud fallbacks. |

---

## Deep Dive: Analysis & Remediation Plan

### 1. Autonomous Loop Architecture (`loop_until_goal`)
- **Code Pointer**: [`seikoclaw.py#L485-L536`](file:///d:/DevWorkspace/SeikoClaw-Harness/seikoclaw.py#L485-L536)
- **Current Behavior**: Loops for `max_turns`, checks token estimation against `context_limit`, prints `[ACTION] Implementing next step...`, and terminates if `"complete" in goal.lower()`.
- **Architectural Rationale**: 
  SeikoClaw's primary paradigm is **Agent-in-the-Loop Scaffolding**. The external AI agent (e.g. Antigravity IDE, Claude Desktop, Gemini CLI) is the actual cognitive engine. The `loop_until_goal` method was written as a test harness to validate token estimation, context ceiling alarms (`handoff.md`), and memory compression triggers under simulated multi-turn loads without burning LLM API quotas.
- **Remediation**:
  1. Add a headless task execution mode where each loop turn queries `self.graph.claim_next_ready(worker_id="autonomous-loop")`, runs the task's command, executes its verification script, and updates DAG node status.
  2. If the goal is free-form (non-DAG), route turns to a pluggable LLM provider or yield structured steps back to the host IDE agent.

---

### 2. Watchdog & Circuit-Breaker Integration (`HealthPatrol`)
- **Code Pointer**: [`openbrain/watchdog.py`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/watchdog.py), [`seikoclaw.py#L567-L582`](file:///d:/DevWorkspace/SeikoClaw-Harness/seikoclaw.py#L567-L582)
- **Current Behavior**: `HealthPatrol.record_action()` tracks SHA-256 action signatures and detects 3x duplicate actions or consecutive failures. However, `seikoclaw.py` never calls `record_action()` during command execution.
- **Architectural Rationale**:
  `HealthPatrol` was developed during the Seikojin QA integration as a pure diagnostic library. The execution harness and health patrol were left decoupled during the initial testing phase.
- **Remediation**:
  1. In `run_task()` and `execute`:
     ```python
     self.watchdog.record_action(
         action_type="command",
         target=command,
         result_snippet=output_text[:200],
         success=(result.returncode == 0)
     )
     ```
  2. In `loop_until_goal()`: Call `self.watchdog.get_health_status()` at the start of each iteration. If `status == "STALLED"`, abort loop execution and generate a diagnostic blocker in Openbrain.

---

### 3. Secrets Vault & SQLite Schema Alignment
- **Code Pointer**: [`openbrain/vault.py`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/vault.py), [`openbrain/memory_engine.py#L17-L84`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/memory_engine.py#L17-L84), [`openbrain/schema.sql#L36-L41`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/schema.sql#L36-L41)
- **Current Behavior**: `Vault.unlock()` assumes `secrets_vault` exists. `MemoryEngine._init_sqlite()` does not create `secrets_vault`. `unlock_vault()` is never invoked in `main()`.
- **Architectural Rationale**:
  Interactive developer workflows already inherit API keys via `.env` or system environment variables. Requiring `SEIKOCLAW_MASTER_PASS` on every CLI invocation would degrade developer ergonomics. Vault was intended for automated/unattended multi-tenant deployments.
- **Remediation**:
  1. Add table definition in `MemoryEngine._init_sqlite()`:
     ```sql
     CREATE TABLE IF NOT EXISTS secrets_vault (
         secret_key TEXT PRIMARY KEY,
         encrypted_value TEXT NOT NULL,
         salt TEXT NOT NULL,
         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     );
     ```
  2. Add self-healing table creation in `Vault.__init__()` if connecting to a blank DB.
  3. Expose CLI subcommands: `python seikoclaw.py vault --set KEY VALUE` and `python seikoclaw.py vault --get KEY`.

---

### 4. Workspace Portability & Environment Configuration
- **Code Pointer**: [`seikoclaw.py#L269, L357, L433, L637`](file:///d:/DevWorkspace/SeikoClaw-Harness/seikoclaw.py#L269), [`openbrain/context_engine.py#L40`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/context_engine.py#L40)
- **Current Behavior**: Absolute paths `d:/DevWorkspace/...` for Tablebuddy, LocalMind models, Master Wiki, and agent-native binaries.
- **Architectural Rationale**:
  Hardcoded paths were a rapid prototyping mechanism to tie together sibling repositories on the author's local workstation.
- **Remediation**:
  Implement unified path resolution via environment variables with relative directory fallbacks:
  - `SEIKOCLAW_WIKI_DIR`: Defaults to `../.master_wiki` or `./.master_wiki`.
  - `SEIKOCLAW_MODEL_DIR`: Defaults to `~/.localmind/models` or `os.getenv("LOCALMIND_MODEL_DIR")`.
  - `AGENT_NATIVE_CMD`: Discovered via `shutil.which("agent-native")` or `npx @agent-native/core`.
  - Remove hardcoded `Tablebuddy` runner in favor of generic test task execution via configuration.

---

### 5. Persistence Layer Consolidation
- **Code Pointer**: [`openbrain/engine.py`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/engine.py) vs [`openbrain/memory_engine.py`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/memory_engine.py)
- **Current Behavior**: `engine.py` defines `OpenbrainEngine` (SQLite only). `memory_engine.py` defines `MemoryEngine` (SQLite + ChromaDB + ContextEngine). `engine.py` is dead code.
- **Architectural Rationale**:
  `engine.py` was the minimal V1 engine before vector embeddings were introduced. When ChromaDB was added in `memory_engine.py`, `engine.py` was retained for zero-dependency environments.
- **Remediation**:
  1. Make `MemoryEngine` gracefully degrade if ChromaDB is not installed (pure SQLite fallback).
  2. Replace `OpenbrainEngine` in `engine.py` with an alias: `OpenbrainEngine = MemoryEngine`.
  3. Update `README.md` to reference `MemoryEngine` / CLI commands.

---

### 6. Hybrid DAG Gating Enforcement on Frontier
- **Code Pointer**: [`openbrain/task_graph.py#L260-L292`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/task_graph.py#L260-L292), [`openbrain/gates.py`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/gates.py)
- **Current Behavior**: `get_ready_frontier()` returns all open tasks whose blocker tasks are closed. It does not check if the task itself has an unsatisfied in-situ gate (`gate_type` is set and `gate_status != 'passed'`).
- **Architectural Rationale**:
  In human-supervised hybrid workflows, gated tasks need to remain visible on the task board so that QA agents or human operators can see them and certify them (`seikoclaw gate --certify-qa`).
- **Remediation**:
  1. Add an explicit parameter `get_ready_frontier(filter_gates=True)` for automated worker dispatch:
     ```sql
     AND (t.gate_type IS NULL OR t.gate_status IN ('passed', 'bypassed'))
     ```
  2. For human/QA inspection views (`seikoclaw ready`), display gated tasks with their required certifier badge.
  3. In `claim_next_ready(worker_id)`: Ensure workers only claim tasks whose gates match the worker's capability or are already passed.

---

### 7. Dependency Manifestation & Packaging
- **Code Pointer**: Root directory
- **Current Behavior**: No `pyproject.toml` or `requirements.txt`.
- **Architectural Rationale**:
  Project was operated out of a global developer environment.
- **Remediation**:
  Create `pyproject.toml` and `requirements.txt`:
  ```toml
  [project]
  name = "seikoclaw-harness"
  version = "1.0.0"
  dependencies = [
      "chromadb>=0.4.0",
      "tiktoken>=0.5.0",
      "cryptography>=41.0.0",
      "pyyaml>=6.0.0",
  ]
  [project.optional-dependencies]
  localmind = ["llama-cpp-python>=0.2.0"]
  dev = ["pytest>=7.0.0"]
  ```

---

### 8. LLM Abstraction for Background Cognitive Loops
- **Code Pointer**: [`seikoclaw.py#L354-L398`](file:///d:/DevWorkspace/SeikoClaw-Harness/seikoclaw.py#L354-L398), [`openbrain/context_engine.py#L7-L44`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/context_engine.py#L7-L44)
- **Current Behavior**: Direct import of `LocalMindEngine` with hardcoded model path. Silent no-op if absent.
- **Architectural Rationale**:
  Background cognitive maintenance (memory summarization, skill evolution) was intentionally offloaded to local on-device models to prevent cloud token consumption, maintain low latency, and keep codebase knowledge private.
- **Remediation**:
  1. Introduce an `LLMClient` adapter interface:
     - **Provider 1**: LocalMind / local GGUF weights.
     - **Provider 2**: LLMWorkbench MCP tool (`query_local_model`).
     - **Provider 3**: OpenAI-compatible local endpoints (Ollama, LM Studio, vLLM).
     - **Provider 4**: Cloud API fallback (Gemini / Anthropic / OpenAI).
     - **Provider 5**: Rule-based heuristic compression (fallback if no LLM is configured).
  2. Replace silent failure with clear logging and diagnostic reporting in `seikoclaw doctor`.
