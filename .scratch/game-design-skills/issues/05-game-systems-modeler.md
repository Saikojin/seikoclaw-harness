Statu.agents/skills/.

### Key Architectural Decisions Made:
1. **Interactive HTML Dashboards**: Generates `balance_simulator.html` with real-time sliders and Chart.js graphs (TTK, XP curves, drop rates) for visual tuning without code edits.
2. **Modular Math Domains**: Covers Combat (DPS/TTK/Armor), Progression (XP/Stat scaling), Economy (Sources/Sinks), and Probability (Loot/Crit/RNG).
3. **Canonical Config Storage**: Persists balance variables into `docs/design/balance.json`, which directly syncs with `game-prototype-builder` (`prototype.html`) and game engines.

