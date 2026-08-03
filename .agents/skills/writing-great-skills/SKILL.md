---
name: writing-great-skills
description: Reference for writing and editing skills well — the vocabulary, progressive disclosure model, design patterns, and principles that make a skill predictable.
disable-model-invocation: true
---

# Writing & Editing Great Agent Skills

A skill exists to wrangle determinism out of a stochastic system. **Predictability** — the agent taking the same _process_ every run, not producing the same output — is the root virtue.

---

## 1. The Progressive Disclosure Model

Skills use a three-stage progressive disclosure architecture:

- **Level 1 — Discovery (~100 tokens per skill, always in context)**:
  Only `name` + `description` from YAML frontmatter are injected into system context at startup. Agent knows the skill exists and when it applies.
- **Level 2 — Activation (<5,000 tokens, loaded on match)**:
  When a request matches a skill's description, the agent reads the full `SKILL.md` body.
- **Level 3 — Execution (unbounded, on demand)**:
  The agent reads referenced files in `references/` or executes scripts in `scripts/` only as needed.

---

## 2. Skill Design Taxonomy

Skills fall into two core design patterns:

### Pattern A: Capability Primitives (Tool Wrappers)
- Thin wrapper over a deterministic CLI, script, or API tool.
- Reliability enforced by shell code/tools, not prompt prose.
- Typical length: 30–80 lines.

### Pattern B: Process Primitives (Cognitive Disciplines)
- Encodes a methodology, workflow, or review framework (TDD, Code Review, Architecture).
- Reliability enforced via explicit steps, checklists, and validation loops.

---

## 3. Description as a Routing Contract

The `description` field is the **only** part visible during Level 1 Discovery. Format descriptions using the 3-element pattern:
1. **What** the skill does (one concise phrase).
2. **When** to use it (trigger phrases, scenarios).
3. **Differentiator** vs related skills (prevents routing ambiguity).

*YAML Gotcha*: Never put `: ` (colon + space) inside an unquoted description string. Single-quote descriptions containing colons.

---

## 4. Invocation Rules

- **Model-invoked**: Omit `disable-model-invocation`. Provide a rich, trigger-heavy description so the agent fires it autonomously.
- **User-invoked**: Set `disable-model-invocation: true`. Zero context load until explicitly invoked by user.

---

## 5. Failure Modes & Anti-Patterns

- **Premature Completion**: Ending a step before completion criteria are met.
- **Negation**: Steering by prohibition ("Don't do X"). Always phrase positively ("Do Y instead").
- **Sprawl**: Overly long `SKILL.md`. Cure by pushing detailed reference material down into `references/`.
- **Duplication**: The same rule repeated in multiple places.
