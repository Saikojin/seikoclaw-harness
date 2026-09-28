---
name: agent-authoring
description: Comprehensive framework for writing and editing agent skills, workflows,
  and rules.
author: Matt Pocock
aliases:
- writing-for-agents
- writing-great-skills
- writing-beats
- writing-fragments
- writing-shape
- teach
- ask-matt
- setup-matt-pocock-skills
- to-questionnaire
---

# Agent Authoring: Writing Skills, Workflows & Documents for Agents

Reference for writing any document an agent consumes: a skill, an AGENTS.md / CLAUDE.md, or a doc reached by a pointer.

## 1. Context Pointers & Trigger Discipline
A **context pointer** is a reference held in the agent context that names an out-of-context document and encodes the conditions to trigger it.
- **Front-load the leading word**: triggers must appear first.
- **One trigger per distinct branch**: collapse synonyms into single canonical triggers.
- **Prune redundant metadata**: keep pointer descriptions compact and actionable.

## 2. Progressive Disclosure Ladder
1. **In-file step**: Immediate sequence of actions to perform.
2. **In-file reference**: Flat reference definitions consulted on demand.
3. **Disclosed reference**: Detailed sub-guides stored in sibling files or linked markdown, loaded only when relevant.

## 3. Leading Words & Completion Criteria
- **Leading Words**: Anchor behaviors with rich pretrained concepts (*tight*, *red-green-refactor*, *tracer bullets*, *relentless*).
- **Completion Criteria**: Clear, checkable, and exhaustive bounds that prevent premature step completion.

## 4. Writing Modes (Explore vs. Exploit)
- **Fragments (Explore)**: Mine raw unorganized technical material and observations.
- **Beats (Structure)**: Order fragments into a logical narrative spine and decision flow.
- **Shape (Exploit)**: Polish paragraphs, tighten prose, and enforce positive instruction rules.
