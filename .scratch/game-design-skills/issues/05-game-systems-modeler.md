Status: closed
Labels: wayfinder:grilling
Priority: P2
Blocked by: (none — frontier)
Assigned: agent

# Game Systems Modeler — Balance Simulator & Economy Architect

## Question

What should the Game Systems Modeler produce, how does a non-coder interact with it, and what game math domains does it need to cover?

## Resolution

Resolved as a **dedicated standalone skill** located at [`d:\DevWorkspace\SeikoClaw-Harness\.agents\skills\game-systems-modeler\SKILL.md`](file:///d:/DevWorkspace/SeikoClaw-Harness\.agents\skills\game-systems-modeler\SKILL.md).

### Key Architectural Decisions Made:
1. **Interactive HTML Dashboards**: Generates `balance_simulator.html` with real-time sliders and Chart.js graphs (TTK, XP curves, drop rates) for visual tuning without code edits.
2. **Modular Math Domains**: Covers Combat (DPS/TTK/Armor), Progression (XP/Stat scaling), Economy (Sources/Sinks), and Probability (Loot/Crit/RNG).
3. **Canonical Config Storage**: Persists balance variables into `docs/design/balance.json`, which directly syncs with `game-prototype-builder` (`prototype.html`) and game engines.

