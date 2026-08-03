Status: closed
Labels: wayfinder:grilling
Priority: P0
Blocked by: (none — frontier)
Assigned: agent

# Game Design Critic — Game-Aware Grilling Persona

## Question

What should the Game Design Critic skill look like — its persona, its question bank, its triggers, and how it differs from the generic grilling skill?

## Resolution

Resolved as a **dedicated standalone skill** located at [`d:\DevWorkspace\SeikoClaw-Harness\.agents\skills\game-design-critic\SKILL.md`](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/game-design-critic/SKILL.md).

### Key Architectural Decisions Made:
1. **Dedicated Skill**: Created as `game-design-critic` with a specialized Lead Game Designer persona prompt.
2. **Universal Focus**: Focused strictly on universal game design principles (Core Fantasy, 10s/30s/5m Core Loops, Player Psychology, Degenerate Strategies, Learnability, Scope).
3. **Dual Outputs**: Updates `CONTEXT.md` / `GDD.md` inline during sessions AND produces a structured `Game_Design_Review.md` artifact at wrap-up.
4. **Direct Handoff**: Formatted to feed directly into the GDD Generator (Ticket 02) and Scope Surgeon (Ticket 03).

