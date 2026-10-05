---
name: adr
description: Turn decisions into Architecture Decision Records in docs/adr/.
author: Matt Pocock / David Andrej
---

# ADR Skill

## Goal
To capture a significant architectural decision from the current conversation and record it in a structured ADR.

## Steps
1. **Explore the codebase**: Understand the current context and existing ADRs in `docs/adr/`.
2. **Synthesize the decision**: Extract the context, the decision, and the rationale from the conversation.
3. **Check criteria**: Ensure the decision meets the ADR criteria:
    - **Hard to reverse**: The cost of changing your mind later is meaningful.
    - **Surprising without context**: A future reader will wonder "why did they do it this way?".
    - **The result of a real trade-off**: There were genuine alternatives and you picked one for specific reasons.
4. **Determine the number**: Scan `docs/adr/` for the highest existing number and increment by one (e.g., `0001`, `0002`).
5. **Format the ADR**: Use the following lightweight format:
    ```md
    # {Short title of the decision}

    {1-3 sentences: what's the context, what did we decide, and why.}
    ```
6. **Save the file**: Create `docs/adr/NNNN-slug.md`.
7. **Update GLOSSARY.md**: If any new terminology was established, update the project's domain glossary (`GLOSSARY.md`, or `CONTEXT.md` if legacy).
