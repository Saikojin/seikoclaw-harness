Status: closed
Labels: wayfinder:grilling
Priority: P1
Blocked by: (none — frontier)
Assigned: agent

# GDD Generator — Game Design Document Skill

## Question

What should the Game Design Document generator produce, what inputs does it consume, and how does it differ from the Interviewer's Master Vision Plan?

## Resolution

Resolved as a **dedicated standalone skill** located at [`d:\DevWorkspace\SeikoClaw-Harness\.agents\skills\gdd-generator\SKILL.md`](file:///d:/DevWorkspace/SeikoClaw-Harness\.agents\skills\gdd-generator\SKILL.md).

### Key Architectural Decisions Made:
1. **Adaptive & Modular Schema**: Mandates core modules (Fantasy, Nested Loops, Verbs, Win/Loss, Platform) while including optional modules (Economy, Narrative, Multiplayer) only when relevant to the genre.
2. **Multi-Input Synthesis**: Ingests Game Design Critic reviews (`Game_Design_Review.md`), Interviewer vision plans (`project_vision.md`), `CONTEXT.md`, and raw ingested notes.
3. **Living Document Persistence**: Saves to `docs/design/GDD.md` as the canonical living specification, referencing `VERTICAL_SLICE_SPEC.md` for active micro-slice prototypes.

