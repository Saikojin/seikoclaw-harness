---
name: seikoclaw-skill-extractor
description: Actively generates reusable .md skills from completed sessions.
---

# Seikoclaw Skill Extractor

## Goal
To capture repetitive, non-obvious, and codifiable procedures from a completed session and convert them into reusable `SKILL.md` files.

## Workflow
1. **Transcript Review**: Analyze the session transcript or summary for recurring workflows.
2. **Candidate Evaluation**: Check if the workflow relies on non-obvious steps, specific prompts, or rigid rules that future agents would struggle to guess.
3. **Skill Drafting**: If a candidate passes, draft a `SKILL.md` following the standard skill schema.
4. **Placement**: Save the drafted skill into the local workspace `.agents/skills/` directory (or global `config/skills/` if requested).

## Required Inputs
- The transcript or `walkthrough.md` of a completed session.

## Output Format
A valid `SKILL.md` with:
- `name` and `description` frontmatter.
- `# Goal`, `## Workflow`, `## Required Inputs`, `## Output Format`, `## Boundaries`.

## Boundaries
- Reject ordinary preferences (e.g., "always use black for formatting"). This is a rule, not a skill.
