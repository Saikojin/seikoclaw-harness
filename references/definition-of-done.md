# Core Engineering Reference: Definition of Done (DoD)

> **Mandate**: Every pull request, task execution, and codebase change must clear this standing quality bar before merging or closing.

---

## 🛡️ 1. Empirical Verification & Correctness
- [ ] **Empirical Proof**: Every assertion ("fixed bug X", "optimized query Y") is backed by executed commands, passing tests, or measured trace logs—not speculation.
- [ ] **Automated Test Suite**: 100% test pass rate across unit, integration, and contract tests. Zero skipped or silenced tests to get green.
- [ ] **Root-Cause Resolution**: Fix addresses the underlying mechanical failure rather than masking symptoms with defensive null checks or catch-all exception swallows.
- [ ] **No Regressions**: Existing test suite and surrounding integration smoke tests run without regressions.

---

## 🧹 2. Code Hygiene & Anti-Slop Standards
- [ ] **Minimal Diff Discipline**: The diff touches only what is strictly required to satisfy the specification. Zero speculative abstractions, gratuitous refactors, or formatting thrash.
- [ ] **Zero AI Slop**:
  - No conversational comments ("Here we handle...", "TODO: in future...").
  - No defensive try-catch wrappers around trusted internal functions.
  - No type escapes (`as any`, `@ts-ignore`, `# type: ignore`) used as short-cuts.
- [ ] **Comment Sicko (`no-comments`)**: Comments explain *why* non-obvious constraints exist, never *what* self-explanatory code is already doing.
- [ ] **Boundary Discipline**: Code changes remain strictly within designated package/module ownership boundaries without leaking private internals.

---

## 🔒 3. Security & Safety Guarantees
- [ ] **Zero Hardcoded Secrets**: No API keys, tokens, passwords, or connection strings in source code. All sensitive variables are sourced from environment or AES-GCM Vault (`python seikoclaw.py vault`).
- [ ] **Input Validation & Sanitization**: All untrusted user inputs are validated at system boundaries before consumption or database persistence.
- [ ] **Safety Hooks Clearance**: Changes pass cross-platform pre-execution hooks (`deny-dangerous.sh` / `.ps1`) with zero risky bypass attempts.

---

## 🎨 4. Visual Bar & User Experience (For UI / Frontends)
- [ ] **Visual Parity**: Passes side-by-side comparison against locked design references (`refs-locked/`).
- [ ] **Zero Visual Defect Punches**: Inspected for optical alignment, layout jitter, font scaling, and smooth motion curves.
- [ ] **Accessibility (a11y)**: Conforms to `references/accessibility-checklist.md` (keyboard navigation, focus rings, semantic markup).
- [ ] **Performance (CWV)**: Meets budgets defined in `references/performance-checklist.md`.

---

## 📝 5. Documentation & Traceability
- [ ] **Architectural Integrity**: Load-bearing architectural decisions are captured as ADRs in `docs/adr/`.
- [ ] **Decision Trail Log**: Autonomous or multi-phase runs record a reviewable TSV decision trail via `/show-me-your-work`.
- [ ] **Knowledge Update**: Learnings and pitfalls encountered during the task are recorded in OpenBrain memory.
