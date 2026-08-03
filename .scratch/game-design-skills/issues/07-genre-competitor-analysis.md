Status: closed
Labels: wayfinder:research
Priority: P2
Blocked by: (none — frontier)
Assigned: agent

# Genre & Competitor Analysis — Market Positioning Skill

## Question

What should a game-specific competitor analysis skill produce, and how does it differ from the generic `research` skill?

## Resolution

Resolved as a **dedicated standalone skill** located at [`d:\DevWorkspace\SeikoClaw-Harness\.agents\skills\genre-competitor-analysis\SKILL.md`](file:///d:/DevWorkspace/SeikoClaw-Harness\.agents\skills\genre-competitor-analysis\SKILL.md).

### Key Architectural Decisions Made:
1. **Comprehensive 5-Point Matrix**: Outputs `docs/design/COMPETITIVE_LANDSCAPE.md` covering Genre Conventions, 3-5 Game Feature Matrix, Player Pain Points/Reviews, Unmet Market Gaps, and a 2D Positioning Strategy map.
2. **AFK Subagent Execution**: Designed for autonomous background research using web tools to analyze reviews, wiki breakdowns, and player discussions.
3. **Workflow Integration**: Automatically feeds into `docs/design/GDD.md` (GDD Generator) and provides context for `game-design-critic`.

