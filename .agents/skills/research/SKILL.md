---
name: research
description: Investigate a question against high-trust primary sources and capture findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or deep research conducted.
disable-model-invocation: false
---

# Research & Deep Investigation Skill

## Goal
To delegate research to a background subagent to conduct rigorous, primary-source-backed investigations without clogging the main thread.

## Research Prompt Structure

When delegating or formulating the research task, construct a single self-contained research prompt containing:
1. **Leading Objective**: State the core question and the end decision/use case it informs.
2. **Context & Background**: Embed necessary context so the subagent can work autonomously without back-and-forth.
3. **Sub-Questions**: List 3–6 numbered sub-questions focusing on key technical parameters or mechanisms.
4. **Constraints**: State explicit include/avoid bounds.
5. **Primary Source Discipline**: Mandate official documentation, source code, RFCs, specs, or primary APIs over secondary summaries.
6. **Fact vs. Inference**: Explicitly separate empirical findings from inferences.

## Workflow

1. Spin up a **background subagent** (`subagent_type=research` or `general-purpose`).
2. Pass the structured research prompt to the subagent.
3. Subagent investigates primary sources (official docs, source code, first-party specs).
4. Subagent synthesizes findings into a Markdown artifact with inline citations.
5. Save artifact to local workspace docs/research directory or output location.
