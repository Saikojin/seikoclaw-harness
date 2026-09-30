Statu.agents/skills/.

### Key Architectural Decisions Made:
1. **Hybrid Ingestion**: Accepts freeform qualitative chat feedback ("jump feels floaty", "too hard") AND optional pasted JSON telemetry from `prototype.html`'s Debug HUD.
2. **Heuristic Dictionary Translation**: Maps subjective terms ("floaty", "sluggish", "clunky", "bullet sponge") directly to concrete game parameter adjustments using a built-in game design dictionary.
3. **Cumulative Runbook**: Maintains `.scratch/<project>/PLAYTEST_RUNBOOK.md` tracking all iteration versions (v1, v2, v3...), parameter diffs, and designer notes.
4. **Scope Pivot Trigger**: Automatically prompts the designer after 3 iterations to decide whether to expand the micro-slice via Scope Surgeon (Ticket 03) or pivot.

