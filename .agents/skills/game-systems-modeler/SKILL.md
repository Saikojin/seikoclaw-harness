---
name: game-systems-modeler
description: Generates interactive balance simulators (balance_simulator.html) and maintains canonical balance parameters (balance.json) for combat, progression, economy, and probability tuning.
---

# Game Systems Modeler

The **Game Systems Modeler** empowers non-coding game designers to visualize, model, and balance complex game math (damage formulas, XP curves, drop rates, resource sinks) using single-file interactive HTML dashboards (`balance_simulator.html`) equipped with live sliders and Chart.js graphs.

## Core Capabilities

1. **Interactive Dashboard Generation**: Produces zero-dependency `.html` balance simulators with live interactive sliders and real-time Chart.js visual graphs.
2. **Modular Math Domains**:
   - **Combat & TTK**: Damage mitigation formulas, Time-To-Kill (TTK) vs enemy tiers, DPS scaling, attack speed breakpoints.
   - **Progression & XP**: Level-up curves (exponential, polynomial, flat), stat allocation scaling, player power growth vs enemy stat scaling.
   - **Economy & Sinks**: Resource generation rates vs gold/sink drains, inflation prediction over session length.
   - **Probability & Loot**: Drop rate tables, critical hit variance, expected attempts to acquire rare items, gacha/lootbox simulations.
3. **Canonical Data Storage**: Persists all parameters into a clean, human-readable `docs/design/balance.json` file.
4. **Direct Engine Bridge**: `balance.json` is automatically read by `game-prototype-builder` (`prototype.html`) and Godot engines, allowing balance adjustments to take effect immediately without code changes.

## Supported Math Domains & Formulas

### 1. Combat & TTK
$$\text{Effective DPS} = \frac{\text{Base Damage} \times (1 + \text{Crit Chance} \times (\text{Crit Multiplier} - 1))}{\text{Attack Cooldown}}$$
$$\text{Damage Received} = \text{Raw Damage} \times \left(\frac{100}{100 + \text{Armor}}\right)$$
$$\text{Time to Kill (TTK)} = \frac{\text{Target HP}}{\text{Effective DPS}}$$

### 2. Progression Curves
$$\text{XP Required for Level } L = \text{Base XP} \times L^{\text{Exponent}}$$

## Output Specifications

Generates:
- `docs/design/balance.json` — Authoritative parameter data.
- `docs/design/balance_simulator.html` — Interactive visual dashboard for non-coders.

### Dashboard Features:
- Collapsible parameter control panels with live sliders.
- Real-time Chart.js line and bar graphs showing curves (Level 1–100 TTK, XP curve, Drop rate confidence).
- "Save to balance.json" & "Export Config JSON" buttons.

## Workflow

1. **Scan Existing Design**: Read `docs/design/GDD.md` or `CONTEXT.md` for combat/economy rules.
2. **Formulate Math Model**: Map game rules to combat, progression, economy, or probability formulas.
3. **Generate Dashboard & Config**: Create `balance_simulator.html` and write initial `balance.json`.
4. **Designer Tuning Session**: Designer opens `balance_simulator.html` in a web browser, adjusts sliders, reviews live visual graphs, and saves `balance.json`.
5. **Engine Synchronization**: `game-prototype-builder` or Godot engine reloads `balance.json` to update prototype values.
