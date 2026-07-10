---
name: prototype
description: "Design-it-twice spike loop: freeform prototype → write LOGIC/UI/DEEPENING docs, identify assumptions before committing"
disable-model-invocation: false
---

# Prototype

Spike out a quick solution to explore the domain or evaluate a design, without worrying about code quality or test suites. Then use the findings to write the production implementation plan.

## Workflow

1. **Freeform spike.** Build the fastest thing that could possibly work. Don't write tests. Let code drift from design system tokens.
2. **Draft design documentation.** Before rewriting for production, document the findings:
   - `LOGIC.md` - Explain core state machines, backend workflows, or algorithms.
   - `UI.md` - Document design token adherence, responsiveness, and selectors.
   - `DEEPENING.md` - Write down structural gotchas, trade-offs, and critical assumptions.
3. **Verify with Red Team.** Hand off the draft documentation and prototype to the `seikoclaw-red-team` checker to verify assumptions before starting production tasks.
