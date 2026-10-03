# 24 First-Principle Engineering Directives

These principles govern all agent coding, architecture, refactoring, and verification tasks in SeikoClaw. They enforce zero-slop, verifiable, root-cause-focused engineering.

---

## 🏛️ Core Principles

### 1. Laziness Protocol (`principle-laziness-protocol`)
- **When**: Refactoring, sizing a diff, or tempted to add abstractions, layers, or signal threading.
- **Rule**: Bias toward deletion and the smallest change that solves the problem. Delete dead code and stubs before adding new logic. The best code is no code.

### 2. Foundational Thinking (`principle-foundational-thinking`)
- **When**: Before writing logic, choosing core types and data structures, sequencing scaffold-vs-feature work.
- **Rule**: Get the core data structures and types right first. When the data model matches domain reality, downstream logic becomes straightforward and obvious.

### 3. Redesign from First Principles (`principle-redesign-from-first-principles`)
- **When**: Integrating a new requirement into an existing design.
- **Rule**: Redesign as if the requirement had been a foundational assumption from day one, rather than bolting on special cases, extra boolean flags, and wrapper layers.

### 4. Attack the Premise (`principle-attack-the-premise`)
- **When**: Two or more fixes sharing a common premise have failed the same test or gate.
- **Rule**: Stop making incremental tweaks. Step back, state the underlying assumption explicitly, and challenge the premise before writing another fix.

### 5. Subtract Before You Add (`principle-subtract-before-you-add`)
- **When**: Sequencing an addition, refactor, or rewrite.
- **Rule**: Remove dead weight, redundant validators, and stub references first. Build the new capability on the simpler, cleaned base.

### 6. Minimize Reader Load (`principle-minimize-reader-load`)
- **When**: Reviewing or shaping code that is hard to follow.
- **Rule**: Collapse single-caller wrappers, eliminate redundant indirection, shrink mutable variable scopes, and keep the distance between question and answer as short as possible.

### 7. Outcome-Oriented Execution (`principle-outcome-oriented-execution`)
- **When**: Planned rewrites, migrations, and structural refactors.
- **Rule**: Converge directly on the target architecture. Do not build throwaway intermediate compatibility layers that will later need to be deleted.

### 8. Experience First (`principle-experience-first`)
- **When**: Product, UX, API ergonomics, or feature-scope tradeoffs.
- **Rule**: Prioritize user and developer experience over implementation convenience. Ship fewer polished features rather than many rough, half-finished ones.

### 9. Exhaust the Design Space (`principle-exhaust-the-design-space`)
- **When**: Facing novel interactions, non-trivial architectural forks, or complex state models.
- **Rule**: Build 2–3 competing prototypes or design alternatives (using `/arena` or spikes) and evaluate them side-by-side before committing.

### 10. Build the Lever (`principle-build-the-lever`)
- **When**: Any non-trivial, repetitive, or bulk task (migrations, codemods, bulk edits, checks).
- **Rule**: Build the reusable tool, script, codemod, or skill that performs or proves the work instead of doing it by hand. The tool is an auditable artifact reviewers can re-run.

---

## 🏗️ Architecture Principles

### 11. Model the Domain (`principle-model-the-domain`)
- **When**: Writing stateful logic, branching workflows, or repeating shape assumptions.
- **Rule**: Encode the domain structure explicitly (state machines, typed models, lookup tables, registries) instead of scattering conditional `if/else` checks across files.

### 12. Boundary Discipline (`principle-boundary-discipline`)
- **When**: Handling external input, CLI arguments, config parsing, network responses.
- **Rule**: Concentrate validation, sanitization, and error handling strictly at system boundaries. Trust internal domain types and keep core business logic in pure, predictable functions.

### 13. Type System Discipline (`principle-type-system-discipline`)
- **When**: Designing signatures, interfaces, and schemas in any typed language.
- **Rule**: Make illegal states unrepresentable. Brand semantic primitives, exhaust all enum/union variants, and derive types from authoritative schemas. Refuse `any` casts and compiler lies.

### 14. Make Operations Idempotent (`principle-make-operations-idempotent`)
- **When**: Designing CLI commands, lifecycle hooks, data migrations, or autonomous loops.
- **Rule**: Ensure operations converge safely to the exact same end state regardless of partial prior runs or retries.

### 15. Migrate Callers Then Delete Legacy APIs (`principle-migrate-callers-then-delete-legacy-apis`)
- **When**: Introducing a new API or signature while legacy callers exist.
- **Rule**: Migrate all callers and delete the legacy API in the same wave. Avoid keeping deprecated stubs and bridge code.

### 16. Separate Before Serializing Shared State (`principle-separate-before-serializing-shared-state`)
- **When**: Concurrent actors, subagents, or threads write to the same file, branch, or database.
- **Rule**: Eliminate shared state first by partitioning ownership lanes. Only introduce locks/mutexes when a single shared writer is a true invariant.

---

## 🧪 Verification Principles

### 17. Prove It Works (`principle-prove-it-works`)
- **When**: Completing any task before declaring done.
- **Rule**: Verify against the real artifact (execute the binary, inspect live runtime output, check the actual diff). Never accept "it compiles", mock-only checks, or agent self-reports as proof of completion.

### 18. Fix Root Causes (`principle-fix-root-causes`)
- **When**: Debugging, fixing defects, or addressing error logs.
- **Rule**: Trace every symptom to its root cause and fix it there. Strictly prohibit adding defensive nil-guards, empty `catch/except` blocks, or timeout padding that merely silences crashes.

### 19. Sequence Work into Verifiable Units (`principle-sequence-verifiable-units`)
- **When**: Multi-step work, DAG planning, and commit stacking.
- **Rule**: Break work into small units where each unit ends in an independently verifiable check. Verify each step before starting the next.

### 20. Test Behavior, Not Implementation (`principle-test-behavior-not-implementation`)
- **When**: Writing or modifying tests.
- **Rule**: Call the code through its public interface the way real users do, asserting observed outcomes against known-good literals. If a test still passes when all internal functions return dummy values, delete or rewrite it.

### 21. Explain the Number (`principle-explain-the-number`)
- **When**: Measuring or reporting performance, latency, throughput, or benchmark speedups.
- **Rule**: Identify the exact physical or architectural limiter. Prove that the measurement reflects real workload gains rather than caching artifacts or measurement noise.

---

## 🤖 Delegation & Meta Principles

### 22. Guard the Context Window (`principle-guard-the-context-window`)
- **When**: Processing large outputs, multi-file searches, or long run logs.
- **Rule**: Delegate bulk reading and heavy data transformations to subagents. Keep only high-density syntheses and structured summaries in the primary context window.

### 23. Never Block on the Human (`principle-never-block-on-the-human`)
- **When**: Handling reversible implementation decisions.
- **Rule**: Proceed autonomously, choose the most sensible path, present the result clearly, and let the operator course-correct after the fact. Reserve confirmation prompts strictly for irreversible actions.

### 24. Encode Lessons in Structure (`principle-encode-lessons-in-structure`)
- **When**: Capturing learnings, fixing recurring pitfalls, or updating team conventions.
- **Rule**: Encode the rule as a linter check, pre-commit hook, runtime assertion, schema validator, or automated test instead of adding passive text to documentation.
