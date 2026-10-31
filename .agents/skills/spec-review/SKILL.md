---
name: spec-review
description: 5-stage isolated Goldfish review pipeline for technical specifications and design documents (Zoom Out, Comprehension, Critic, Intermediate Zoom Out, Implementation Readiness).
author: Saikojin (SeikoClaw)
aliases:
  - egm-review
  - review-spec
  - sdd-review
---

# Spec Review & 5-Stage Isolated Subagent Pipeline

## Goal
To rigorously stress-test technical specifications, design documents (`docs/designs/*.md`), and architectural PRDs using the **Goldfish Pattern** (isolated subagents with zero conversational context or conversational bias) across 5 disciplined review stages before code execution begins.

This skill operationalizes the document review mechanics from the **Elephant-Goldfish Model (EGM)** and enforces SeikoClaw's First Principles (Principle 1: Laziness Protocol, Principle 3: Redesign from First Principles, Principle 6: Minimize Reader Load, Principle 9: Exhaust the Design Space, Principle 19: Sequence Work into Verifiable Units).

---

## The Goldfish Protocol (Stateless Review Isolation)

1. **Strict Context Isolation**: When evaluating a specification, the reviewer MUST operate with zero historical chat memory. If running inside a conversational agent, subagents are spawned with fresh contexts containing ONLY:
   - The target specification markdown file.
   - The specific document standard being evaluated (`references/standards/*.md`).
   - Relevant codebase file slices referenced directly in the specification.
2. **Read-Only Invariant**: Reviewers never write code or patch the workspace directly. They produce structured findings reports.
3. **Paraphrase Mandate**: Reviewers must independently paraphrase the proposed design and existing system. If an isolated reviewer cannot articulate what the system does from the text alone, the specification fails comprehension.

---

## The 5 Review Stages

Each stage evaluates the document against its corresponding standard in `references/standards/`:

```
Stage 1: Zoom Out (Simplicity & YAGNI)
    ↓
Stage 2: Comprehension (Self-Containment & Clarity)
    ↓
Stage 3: Design Critic (State Models, Bottlenecks, Alternatives)
    ↓
Stage 4: Intermediate Zoom Out (Anti-Scope-Creep on Stage 2/3 additions)
    ↓
Stage 5: Implementation Readiness (Concrete File Paths, Signatures, Test Plans)
```

### Stage 1: Zoom Out Review (`references/standards/zoom-out-standard.md`)
- **Focus**: High-altitude perspective, simplicity, and architecture alignment.
- **Checks**:
  - Does the design solve the root cause or merely patch a symptom?
  - Does it violate YAGNI or introduce premature complexity (queues, caching, sharding) before bottlenecks are proven?
  - Does it leverage existing codebase modules, utilities, and patterns instead of reinventing them?
  - Is new logic placed in the correct architectural layer?

### Stage 2: Comprehension Test (`references/standards/comprehension-standard.md`)
- **Focus**: Naive reader clarity and zero unstated tribal knowledge.
- **Checks**:
  - Independent Paraphrase: Summarize *what is proposed* and *how the current system works*.
  - Are all domain-specific acronyms, services, or internal concepts defined inline or linked?
  - Are there vague hand-waving phrases (e.g. "handled automatically") without concrete mechanisms?
  - Are Critical User Journeys (CUJs) step-by-step and unambiguous?

### Stage 3: Critic Review (`references/standards/feature-spec-standard.md`)
- **Focus**: Exhausting the design space, failure modes, and system bottlenecks.
- **Checks**:
  - **Mandatory Alternatives Rule**: Were at least 1–2 viable alternative architectures evaluated and rejected with documented trade-offs?
  - Domain state model completeness: Are illegal states unrepresentable? Are edge cases exhausted?
  - Security, authorization boundaries, and failure recovery during timeouts/errors.

### Stage 4: Intermediate Zoom Out Review
- **Focus**: Anti-creep check on additions from Stages 2 and 3.
- **Checks**:
  - Did the clarifications or edge-case handling added during Comprehension and Critic reviews bloat the scope?
  - Re-verify simplicity and minimal data flow.

### Stage 5: Implementation Readiness Test (`references/standards/implementation-readiness-standard.md`)
- **Focus**: Concrete work decomposition and executable task sizing.
- **Checks**:
  - **Zero-Decision Rule**: Does the plan leave zero architectural or schema decisions to the implementer?
  - Concrete target scope: Exact repo file paths to create, modify, or delete.
  - Test plan: Specific behavioral unit/integration tests and automated verification commands (`pytest ...`, headed non-headless E2E contracts).
  - Verifiable unit slicing: Each task ends in an independently verifiable check.

---

## Execution Workflow

1. **Target Identification**:
   - Determine target design document path (e.g. `docs/designs/<feature>.md`).
2. **Execute Review Passes**:
   - Read the relevant standard from `references/standards/`.
   - Audit the target document section-by-section.
   - For multi-agent orchestrations, delegate stages to stateless subagents (`invoke_subagent`).
3. **Synthesize Findings Report**:
   - Classify findings into:
     - 🔴 **Blocker (P0)**: Architectural contradiction, unhandled core edge case, missing alternative analysis, or violation of Zero-Decision Rule. Blocks downstream execution.
     - 🟡 **Major (P1)**: Ambiguity, missing definition, non-optimal reuse opportunity, or vague test seam.
     - 🟢 **Nit (P2)**: Typo, stylistic polish, or minor documentation suggestion.
   - Write consolidated report to `docs/designs/reviews/<feature>_review.md`.
4. **Triage & Certification**:
   - Work with user to resolve findings (`/grill-me`).
   - Once all P0 blockers are resolved, certify the task gate via CLI:
     ```bash
     python seikoclaw.py gate --task <task_id> --certify-spec-review --spec docs/designs/<feature>.md --worker <reviewer_name> --notes "All 5 review stages passed with 0 blockers."
     ```
   - Downstream implementation tasks on the ready frontier are unlocked.
