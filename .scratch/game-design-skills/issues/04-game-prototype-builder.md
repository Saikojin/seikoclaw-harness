Status: closed
Labels: wayfinder:grilling
Priority: P0
Blocked by: (none — frontier)
Assigned: agent

# Game Prototype Builder — Browser-Playable Output

## Question

What technology should the Game Prototype Builder use, how does it interface with existing skills (prototype, executor, godot-mcp), and what does "playable by a non-coder" concretely mean?

## Resolution

Resolved as a **dedicated standalone skill** located at [`d:\DevWorkspace\SeikoClaw-Harness\.agents\skills\game-prototype-builder\SKILL.md`](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/game-prototype-builder/SKILL.md).

### Key Architectural Decisions Made:
1. **Browser-First (HTML5 Single-File)**: Strictly outputs zero-dependency, single-file HTML5 Canvas games (`prototype.html`) for 100% friction-free double-click testing in any web browser.
2. **Procedural Web Audio**: Uses Web Audio API synthesis for zero-external-asset retro sound effects (jumps, hits, lasers, explosions).
3. **Live Parameter Tuning & Instrumentation**: Embeds an on-screen collapsible Debug HUD with live sliders (`Gravity`, `Speed`, `Cooldowns`) so non-coders can tweak feel in real time without code edits, plus a "Copy Playtest Log" JSON exporter.
4. **Input Contract**: Consumes `VERTICAL_SLICE_SPEC.md` from Scope Surgeon (Ticket 03).
5. **Direct Handoff**: Unblocks Ticket 06 (**Playtest Feedback Loop**).

