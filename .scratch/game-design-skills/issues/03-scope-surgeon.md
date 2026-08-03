Status: closed
Labels: wayfinder:grilling
Priority: P0
Blocked by: (none — frontier)
Assigned: agent

# Vertical Slice / Scope Surgeon — Minimum Fun Identifier

## Question

How should the Scope Surgeon skill work — what inputs does it take, what heuristics does it use to identify the minimum playable slice, and what does it output?

## Resolution

Resolved as a **dedicated standalone skill** located at [`d:\DevWorkspace\SeikoClaw-Harness\.agents\skills\scope-surgeon\SKILL.md`](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/scope-surgeon/SKILL.md).

### Key Architectural Decisions Made:
1. **Multi-Input Flexibility**: Ingests GDDs, `CONTEXT.md`, Master Vision Plans, or raw text descriptions.
2. **Interactive Socratic Pinpointing**: Asks the designer directly which core hypothesis/mechanic they are most uncertain about while proposing candidate slices.
3. **Micro-Slice Focus**: Enforces 30–90 second micro-loops with 1–2 player verbs max in 1 arena/room, explicitly stripping away menus, inventory, leveling, and lore.
4. **Structured Spec Output**: Outputs `VERTICAL_SLICE_SPEC.md` containing Core Hypothesis, In-Scope Verbs, Out-of-Scope Cuts, and Playtest Stop Conditions.
5. **Direct Handoff**: Unblocks Ticket 04 (**Game Prototype Builder**).

