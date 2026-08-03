---
name: genre-competitor-analysis
description: Autonomous background research skill that analyzes 3-5 competitor games in a genre, identifies player pain points and market gaps, and outputs a structured COMPETITIVE_LANDSCAPE.md.
---

# Genre & Competitor Analysis

The **Genre & Competitor Analysis** skill performs structured game design research on existing titles within a target genre. It analyzes 3–5 key competitor games, identifies player expectations vs. common review complaints, surfaces market gaps, and maps out a 2D positioning strategy for non-coding game designers.

## Persona & Execution Mode

- **Role**: Game Industry Market Analyst & Systems Researcher
- **Execution Mode**: **AFK** (Autonomous subagent execution via web search and web reading tools)

## Workflow

1. **Target Identification**: Take a game genre or 3 anchor titles provided by the user/GDD (e.g. "Tactical RPG: Into the Breach, Fire Emblem: Three Houses, XCOM 2").
2. **Autonomous Investigation**:
   - Query web resources for mechanics breakdowns, Steam review summaries, GDC postmortems, and player Reddit discussions.
   - Extract player pain points (e.g. "Too much RNG in combat", "Excessive grind", "Pacing bogs down between battles").
3. **Synthesize 5-Point Analysis**:
   - **Section 1: Genre Conventions**: Standard expectations players demand.
   - **Section 2: Feature Matrix**: Side-by-side table comparing 3–5 anchor games across mechanics, camera, turn structure, RNG, and progression.
   - **Section 3: Player Pain Points & Reviews**: Common negative feedback and frustrations in the genre.
   - **Section 4: Unmet Market Gaps**: Opportunities to innovate or simplify.
   - **Section 5: 2D Positioning Strategy**: Visual ASCII/Markdown grid mapping out your game's unique spot (e.g. High Pacing vs High Tactical Depth).
4. **Output Artifact**: Save to `docs/design/COMPETITIVE_LANDSCAPE.md`.

## Integration & Handoff

Outputs directly feed:
- **GDD Generator** (`gdd-generator`): Populates the Competitive Positioning module in `docs/design/GDD.md`.
- **Game Design Critic** (`game-design-critic`): Provides background context when grilling on "what do you steal, what do you reject?"
