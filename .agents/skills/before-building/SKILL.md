---
name: before-building
description: Surfaces consequential choices before writing code or planning deeply.
author: Matt Pocock
---

# Before Building (Instant Gut-Check)

## Goal
To instantly surface the 1–3 most consequential, architectural, or product choices hidden in a user's building proposal *before* diving into file exploration, task planning, or code generation.

## Workflow

1. **Respond Instantly**: Do NOT read files, search codebase, or run background tools when this skill triggers.
2. **gut-Check Analysis**: Analyze the user's high-level request against system architecture principles.
3. **Surface Consequential Choices**:
   - Identify 1–3 choices that are hard to reverse later.
   - Highlight trade-offs and structural implications.
   - For each choice, provide a recommended default option.
4. **Handoff**: Once the user responds to the choices, proceed to `/architect` or `/grill-me` for deep design and task breakdown.

## Output Format
```markdown
### Consequential Choices Before Building

1. **[Choice 1 Title]**: [Brief explanation of trade-off]
   - *Recommendation*: [Your recommended path]

2. **[Choice 2 Title]**: [Brief explanation of trade-off]
   - *Recommendation*: [Your recommended path]
```
