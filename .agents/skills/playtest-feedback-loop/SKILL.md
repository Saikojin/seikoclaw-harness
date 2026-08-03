---
name: playtest-feedback-loop
description: Captures qualitative designer playtest feedback and telemetry, mapping subjective terms ("floaty", "bullet sponge") into parameter changes and cumulative iteration logs.
---

# Playtest Feedback Loop

The **Playtest Feedback Loop** closes the iteration cycle for non-coding game designers. It ingests subjective feedback ("the jump feels floaty", "enemy has too much health") along with optional telemetry from `prototype.html`, maps those complaints to game parameter adjustments, and outputs an actionable modification plan for the Game Prototype Builder or Executor.

## Core Capabilities

1. **Hybrid Ingestion**: Accepts raw qualitative notes (chat text) + optional JSON telemetry logs copied from `prototype.html`'s Debug HUD.
2. **Qualitative Game Design Dictionary**: Translates subjective player complaints into parameter adjustments:
   - *"Floaty jump"* → Increase gravity constant by 25%, increase fall multiplier, decrease jump air-control.
   - *"Sluggish controls"* → Reduce acceleration time (instant velocity), decrease attack windup frames.
   - *"Bullet sponge enemy"* → Reduce enemy max HP by 30%, increase player damage or add hit-stop freeze frames.
   - *"Clunky parry"* → Widen parry active window from 150ms to 250ms, add visual flash indicator.
3. **Cumulative Iteration Log**: Maintains `.scratch/<project>/PLAYTEST_RUNBOOK.md` tracking all iterations (v1, v2, v3...), parameter diffs, and designer satisfaction ratings.
4. **Scope Pivot Trigger**: Automatically prompts the designer after 3 consecutive iterations to evaluate whether to:
   - Lock down the current micro-slice and invoke **Scope Surgeon** (`scope-surgeon`) to expand to the next slice.
   - Pivot the core hypothesis if satisfaction remains low.

## Playtest Dictionary (Qualitative Heuristics)

| Complaint Term | Inferred Game Parameter Adjustment |
|---|---|
| **Floaty** | `gravity += 25%`, `fallSpeedMultiplier += 0.5`, `jumpCutoff = true` |
| **Sluggish / Heavy** | `moveSpeed += 20%`, `accelTime = 0`, `dashCooldown -= 30%` |
| **Clunky / Stiff** | Add `coyoteTime = 100ms`, add `jumpBuffer = 100ms`, add `hitStop = 50ms` |
| **Bullet Sponge** | `enemyHP -= 30%`, `knockbackForce += 50%`, `critMultiplier += 0.5` |
| **Overwhelming** | `enemySpawnRate -= 40%`, `attackTelegraphTime += 200ms` |
| **Boring / Flat** | Add screenshake on hit, add particle burst, increase move speed |

## Workflow

1. **Ingest Feedback**: Prompt designer for their reaction after playing `prototype.html`:
   > *"How did the 30-second loop feel? Share any freeform thoughts or paste your Playtest Log JSON."*
2. **Translate to Parameter Diffs**: Match feedback against the Heuristic Dictionary and generate proposed parameter edits.
3. **Update `PLAYTEST_RUNBOOK.md`**: Append a new iteration entry with before/after parameter values.
4. **Re-Invoke Prototype Builder**: Pass updated parameters back to `game-prototype-builder` to update `prototype.html`.
