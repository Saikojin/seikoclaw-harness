---
description: "Interview Workflow: A panel-based project discovery and vision-building loop that feeds the Architect."
---

# 🎙️ SeikoClaw Interviewer Workflow

## Goal
To synthesize spontaneous user ideas into a structured **Master Vision Plan** through a series of panel-based expert interviews, culminating in a handoff to the `/architect` workflow.

## The Panel of Interviewers
- **The Product Visionary** (Phase 1): Focuses on the high-level 'Why', the Hook, and User Impact.
- **The Senior Game Designer** (Phase 2): Deep dives into mechanics, gameplay loops, and experience.
- **The Pragmatic CTO** (Phase 2): Analyzes technical stack, scalability, and complexity.
- **The QA Lead** (Phase 2): Probes for edge cases and defines verification strategies.

---

## 🛠️ Phase 1: The Project Story (Lead: Product Visionary)

**Objective**: Capture the raw energy and "Big Idea" while acknowledging existing progress.

0. **Deep Context Discovery**: 
   - **Scan**: Search the entire project tree for `.md` files, `package.json`, `requirements.txt`, and configuration headers. 
   - **Extract**: Look specifically for details on **Tech Stack**, **Features**, **Roadmap**, and **Pre-existing History** (e.g., `README.md`, `project_context.md`, `qa_todo.md`).
   - **Synthesize**: Before talking to the user, build a mental map of what is already built or planned.

1. **Check for State**: Check if `project_vision.md` exists in the root. If not, create it. **Pre-populate** it with any high-confidence architectural or feature details found during Step 0.
2. **The Prompt**: 
   - **If Documentation Exists**: Ask the user: *"I've reviewed your existing work (I see the [Found Stack/Feature] setup). Based on where the project is now, tell me the story of the next evolution of this vision. What is the core problem we are aiming to solve next?"*
   - **If Empty Project**: Ask the user: *"Tell me the story of this project. What problem does it solve, or what core experience does it provide? Imagine you are describing it to an excited investor."*
3. **Synthesis**: Update `project_vision.md` with the story.
4. **Transition**: Once the story is clear, increment to `Phase: 2`.

---

## 🔍 Phase 2: The Deep Dive (The Panel)

**Objective**: Uncover hidden features and define technical boundaries through iterative questioning.

1. **Round 1 (Game Designer)**: Ask 2-3 questions about mechanics, progression, or core loops.
   - *Example: "How does the player interact with the world?"*
2. **Round 2 (Pragmatic CTO)**: Ask 2-3 questions about tech, state management, or data.
   - *Example: "How are we handling persistence between sessions?"*
3. **Round 3 (QA Lead)**: Ask 1-2 questions about edge cases or automation rules.
   - *Example: "What happens if the user loses connection during a transaction?"*
4. **Iterative Loop**: After each answer, update `project_vision.md` with the new technical and design details. If there are ambiguities, remain in Phase 2 and loop to Step 1.
5. **Convergence**: If all panels are satisfied (or the user requests progress), move to Phase 3.

---

## 📋 Phase 3: The Vision Summary & Handoff

**Objective**: Confirm the master plan and kick off technical planning.

1. **Summarize**: Generate the **Master Vision Plan** based on the data in `project_vision.md`.
2. **Verification**: Present the summary to the user and ask: *"Does this capture the full vision? Are we ready to start the technical architecture?"*
3. **Handover**: If approved, automatically trigger the following:
   > "Vision Approved. Transitioning to **Architect Workflow**..."
   - Invoke `/architect` immediately using the `project_vision.md` as context.

---

## 🧭 Project Vision Template (`project_vision.md`)
```markdown
# 🗺️ Master Vision Plan: [Project Name]

**Current Phase:** [1/2/3]

## 💡 Core Concept (Visionary)
[The Story]

## 🎮 Mechanics & Loops (Designer)
[Discovered mechanics]

## 🏗️ Technical Blueprint (CTO)
[Tech stacks, architecture]

## 🛡️ Stability & QA (QA Lead)
[Edge cases, verification strategies]
```
