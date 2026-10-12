# Universal Baseline Game Requirements & User Options Matrix (`GAME_FOUNDATIONS_BASELINE.md`)
**A Configurable Knowledge Store for `/game-forge`, `gdd-generator`, and `seikoclaw-architect`**

> [!IMPORTANT]
> **The Anti-Assumption Principle:** Every playable game requires foundational scaffolding (display, input, pause, audio, feedback, collisions, game-over, packaging). However, **treating defaults as rigid, unannounced assumptions wastes time and turns** (e.g. assuming numerical HP for a 1-hit-kill game, or assuming an instant Restart button for a permadeath roguelike).
> 
> Therefore, in **Stage A (Brief & GDD)** and **Stage B (Prototype Planning)**, `/game-forge` MUST present the **Foundations Baseline Matrix** as an interactive callout in the proposed plan. The agent presents recommended defaults for the genre, while explicitly inviting the user to call out any modifications before code is written.

---

## 1. The 12 Configurable Foundation Pillars

Each pillar defines the **Default Recommendation**, the **Design Rationale**, and the **User Modification Callout Options**:

### Pillar 1: Longevity & Damage Model
- **Proposed Default:** Numerical Airframe/Health Integrity bar (0–100%) with visual damage states.
- **Rationale:** Clear, fine-grained damage feedback suitable for combat simulators and action games.
- **User Modification Options:**
  - `[ ] Option 1A (Default)`: Numerical HP / Integrity Bar (0–100%).
  - `[ ] Option 1B`: One-Hit-Kill / Lethal Fragility (Hotline Miami, Divekick, Bushido Blade).
  - `[ ] Option 1C`: Lives / Stocks System (Super Smash Bros, classic arcade 3-lives).
  - `[ ] Option 1D`: Time-Survival / Countdown (Crazy Taxi, survival timers).
  - `[ ] Option 1E`: Sanity / Morale / Stamina Meter (Amnesia, Darkest Dungeon).
  - `[ ] Option 1F`: Non-Combat / Puzzle (No health, failure based on invalid moves or voluntary resets).

---

### Pillar 2: Defeat & Game Over Loop
- **Proposed Default:** Instant control freeze on 0 integrity $\rightarrow$ Time freeze (`timeScale = 0`) $\rightarrow$ Red Alert Defeat Banner $\rightarrow$ Prominent **`⚡ RESTART / RETRY ⚡`** button (with "Resume" hidden).
- **Rationale:** Fast-restart iteration cycle; never leaves the player in a broken "zombie" state.
- **User Modification Options:**
  - `[ ] Option 2A (Default)`: Instant In-Place Retry / Reload Level.
  - `[ ] Option 2B`: Permadeath / Roguelike Run End (Wipes run state, returns to Title/Hub).
  - `[ ] Option 2C`: Checkpoint / Respawn Anchor (Souls bonfires, Metroidvania save rooms).
  - `[ ] Option 2D`: Narrative Failure / Branching (Story adapts to loss without restarting).
  - `[ ] Option 2E`: Fail-Forward / No Game Over (Animal Crossing, narrative sandbox).

---

### Pillar 3: Pause & Time Control Stack
- **Proposed Default:** Universal `Escape` / Gamepad `Start/Menu` button pauses simulation time (`Time.timeScale = 0`), unlocks mouse cursor, and presents Resume / Restart / Settings / Quit.
- **Rationale:** Standard PC/console convention; respects player agency and prevents desktop lockups.
- **User Modification Options:**
  - `[ ] Option 3A (Default)`: Full Simulation Freeze (`timeScale = 0`, cursor unlocked).
  - `[ ] Option 3B`: Non-Pausable Real-Time (Dark Souls, Escape from Tarkov, live multiplayer).
  - `[ ] Option 3C`: Tactical Slow-Motion (Superhot, Fallout VATS, Transistor planning mode).
  - `[ ] Option 3D`: In-World Diegetic Menu (Dead Space holographic projection, character remains vulnerable).

---

### Pillar 4: Input Scheme & Controller Ergonomics
- **Proposed Default:** Dual Gamepad (Xbox/PlayStation) + Keyboard/Mouse support with cubic thumbstick response curves ($x^{2.2}$), $0.12$ hardware deadzones, and live device detection banner.
- **Rationale:** Eliminates twitchy thumbstick oversteering and stick drift while maintaining full keyboard accessibility.
- **User Modification Options:**
  - `[ ] Option 4A (Default)`: Gamepad + Keyboard/Mouse with Cubic Curves & Deadzones.
  - `[ ] Option 4B`: Keyboard & Mouse Only (WASD movement + raw mouselook FPS).
  - `[ ] Option 4C`: Mouse-Only / Point-and-Click (RTS, MOBA, classic adventure).
  - `[ ] Option 4D`: Twin-Stick Arcade (Independent move stick + 360-degree aim stick).
  - `[ ] Option 4E`: Touch / Virtual Joystick (Mobile / tablet first).

---

### Pillar 5: Targeting, Crosshairs & Combat Feedback
- **Proposed Default:** Screen-space centered gunsight reticle + floating world-space enemy HP indicator + target distance telemetry + visual/audio hit sparks.
- **Rationale:** Player always knows where they are aiming and receives immediate sensory confirmation of damage dealt.
- **User Modification Options:**
  - `[ ] Option 5A (Default)`: Screen-Space Reticle + Target Intel HUD + Floating HP Bars.
  - `[ ] Option 5B`: Lock-On Target Camera & Soft Tracking Reticle (Ace Combat, Zelda Z-Targeting).
  - `[ ] Option 5C`: Minimalist / Diegetic HUD (No artificial floating bars; visual smoke, sparks, and physical damage only).
  - `[ ] Option 5D`: Trajectory Arc / Laser Sight (Angry Birds, sniper lasers, grenade arcs).
  - `[ ] Option 5E`: No Reticle (Hardcore tactical iron sights / hip-fire scatter).

---

### Pillar 6: Audio Architecture & Fallback Strategy
- **Proposed Default:** Real-time procedural audio synthesis (`OnAudioFilterRead` / WebAudio synth) for combustion engine hum, wind slipstream, and gunshots, backed by Master / SFX / Music volume sliders in settings.
- **Rationale:** Zero external asset dependencies; guarantees standalone builds never run silently due to missing `.wav` binary files.
- **User Modification Options:**
  - `[ ] Option 6A (Default)`: Zero-Dependency Procedural Synth Fallback + Settings Volume Sliders.
  - `[ ] Option 6B`: Pre-Bundled High-Fidelity Audio Clips (Curated `.wav`/`.ogg` stems with audio mixer buses).
  - `[ ] Option 6C`: Chiptune / 8-Bit Retro Synthesizer (WebAudio oscillators for arcade/retro games).
  - `[ ] Option 6D`: Ambient / Mute Mode (Atmospheric minimalism, horror silence).

---

### Pillar 7: World Physicality & Obstacle Collision
- **Proposed Default:** Solid colliders on all environmental props (trees, hangars, buildings, piers) dealing velocity-proportional airframe/hull damage on impact, with catastrophic wreckage at high speeds ($> 14\text{ m/s}$).
- **Rationale:** Eliminates immersion-breaking "ghost objects" and creates authentic spatial danger.
- **User Modification Options:**
  - `[ ] Option 7A (Default)`: Destructive Velocity Damage (High-speed crash = destruction).
  - `[ ] Option 7B`: Elastic Bumper Collisions (Arcade bounce-back without health loss, e.g. Micro Machines).
  - `[ ] Option 7C`: Trigger Overlaps Only (Ghost pass-through with pickup/checkpoint triggers).
  - `[ ] Option 7D`: Boundary Repulsion / Invisible Walls (Auto-banking or screen clamp).

---

### Pillar 8: Display, Windowing & Performance Discipline
- **Proposed Default:** Launch in **Windowed Mode** by default (1280x720 or 1920x1080) with a hard cap at **60 FPS** (`Application.targetFrameRate = 60` or VSync enabled), plus Fullscreen toggle in Settings.
- **Rationale:** Never traps user's desktop on boot; prevents GPU thermal runaway and physics divergence on 144Hz/240Hz monitors.
- **User Modification Options:**
  - `[ ] Option 8A (Default)`: Windowed Mode Default + 60 FPS Cap + Fullscreen Toggle.
  - `[ ] Option 8B`: Exclusive Fullscreen by Default (Competitive esports / cinematic default).
  - `[ ] Option 8C`: Uncapped High-Refresh (144 FPS / 240 FPS with sub-stepping physics).
  - `[ ] Option 8D`: Responsive WebGL Canvas (Embeds into browser viewport with resize handlers).

---

### Pillar 9: Distribution Packaging & Shipping Format
- **Proposed Default:** Standalone Windows 64-bit executable + compiled **Inno Setup 6 installer** (`WWUnity_Setup_v1.0.exe`, LZMA2 ultra compression, desktop shortcut, uninstaller).
- **Rationale:** Zero-friction installation for non-technical playtesters; keeps file sizes under 35 MB.
- **User Modification Options:**
  - `[ ] Option 9A (Default)`: Standalone Windows Installer (`.exe` setup with uninstaller).
  - `[ ] Option 9B`: Portable Archive (Stand-alone `.zip` folder, no installation required).
  - `[ ] Option 9C`: WebGL / HTML5 Single-Page Player (Zero install, hosted on Itch.io / browser).
  - `[ ] Option 9D`: Steam Depot / Platform Package (Steamworks SDK integration, cloud saves).

---

### Pillar 10: Multi-Modal Avatar & Vehicle Handover Protocol
- **Proposed Default:** Explicit state machine (`InCockpit` $\leftrightarrow$ `Parachute/Gliding` $\leftrightarrow$ `OnFoot` $\leftrightarrow$ `Swimming`) with engine-native coordinate standard (e.g. `-Z` forward in Godot: $\operatorname{atan2}(-x, -z)$), standardized diegetic anchor contracts (`Seat_Pilot`, `Harness_Ring`, `Muzzle_Flash`), camera pitch/yaw clamping, and context-swapped control maps (flight controls immediately yield to TPS/FPS ground controls on dismount/bailout).
- **Rationale:** Prevents avatar model clipping through fuselage, dangling parachute lines detaching from harnesses, inverse heading/movement direction bugs, and control scheme collisions when switching modes.
- **User Modification Options:**
  - `[ ] Option 10A (Default)`: Full Multi-Modal Handover (Vehicle $\leftrightarrow$ Parachute/Eject $\leftrightarrow$ On-Foot TPS/FPS with Anchor Nodes).
  - `[ ] Option 10B`: Vehicle-Only Isolation (Avatar is strictly part of vehicle cockpit mesh; no on-foot/eject state).
  - `[ ] Option 10C`: Instant Respawn / Death on Vehicle Loss (No eject/foot phase; immediate reload upon bailout/destruction).
  - `[ ] Option 10D`: Seamless GTA-Style Mount/Dismount (Vehicles parked in world, interact to enter/exit dynamically).

---

### Pillar 11: Spawn Equilibrium & Frame-Zero Physics Discipline
- **Proposed Default:** Parked/Resting vehicle spawn with verified 3-point resting stance (main gear + tailwheel/skid flush on ground), 0% throttle, engine idling or off, thrust-moment ground counterbalance, and minimum 500m clear runway clearance ahead before obstacles or water.
- **Rationale:** Spawning at high throttle or non-equilibrated pitch causes instant stalls, tail-strikes, propeller ground strikes, or careening into buildings/water before the player can react.
- **User Modification Options:**
  - `[ ] Option 11A (Default)`: Cold/Landed Runway Start (0% throttle, wheels resting on runway, clear takeoff vector).
  - `[ ] Option 11B`: Hot Airborne / In-Flight Start (Spawn in mid-air at cruising speed, level trim, balanced altitude).
  - `[ ] Option 11C`: Catapult / Carrier Deck Launch (Assisted acceleration run with arrestor hook recovery).
  - `[ ] Option 11D`: Suspended / Orbit Spawn (Space, anti-grav hover, zero initial velocity).

---

### Pillar 12: In-Game Sensitivity & Input Ergonomics
- **Proposed Default:** Pause/Settings menu includes dedicated Sensitivity Sliders for Pitch, Roll, Yaw, and Look/Aim (range 20%–200%, default 100%), exponential response curves ($x^{1.35}$), and automated non-conflict input checks (strict exclusion of dual D-Pad bindings e.g. D-Pad Up mapped to both Throttle Up and Pause).
- **Rationale:** Pitch and flight controls vary wildly across hardware, thumbsticks, and player preferences; un-tunable pitch causes aggressive pitch-up stall loops, while dual-mapped controls break gameplay flow.
- **User Modification Options:**
  - `[ ] Option 12A (Default)`: Full Sensitivity Sliders (Pitch/Roll/Yaw/Look) + Exponential Curves + Non-Conflict Validation.
  - `[ ] Option 12B`: Linear Raw Inputs (Direct 1:1 inputs with fixed sensitivity).
  - `[ ] Option 12C`: Simplified Arcade Steering (Auto-leveled steering with single sensitivity slider).
  - `[ ] Option 12D`: Full Keybinding Re-mapping UI (Custom user re-bindable keys and gamepad buttons).

---

### Pillar 13: Projectile Safety & Weapon Aim Convergence (The "Don't Shoot Yourself" Rule)
- **Proposed Default:** High-speed micro-projectiles use query-only swept raycasts (`NoCollision` on rigid bodies, explicit `AddIgnoredActor(Owner)`), two-point camera-to-world aim convergence through screen-center reticle, and forward velocity boost projected strictly along barrel forward axis (never raw transverse velocity addition).
- **Rationale:** Prevents catastrophic Chaos/PhysX physics depenetration explosions (e.g. 1200 mph physics spikes when bullets hit player's own mesh), eliminates 3rd-person self-damage, and stops bullets from veering sideways during banked turns.
- **User Modification Options:**
  - `[ ] Option 13A (Default)`: Sweep-Only Raycasts + Owner Exclusion + Screen-Center Aim Convergence.
  - `[ ] Option 13B`: Rigid Body Simulated Projectiles with Spatially Offset Muzzle Spawners.
  - `[ ] Option 13C`: Instant Hitscan (Zero travel time, raycast straight from camera/muzzle).
  - `[ ] Option 13D`: Non-Damaging Non-Lethal Projectiles (Paint, tagger, sonar).

---

### Pillar 14: Input Debouncing & Single-Frame Latch Protocol (The "Dead Key" Rule)
- **Proposed Default:** All discrete state toggles (Pause menu, Camera view mode, Flashlight, Landing Gear) enforce a single-frame latch check (`if (LastToggleFrame == GFrameCounter) return; LastToggleFrame = GFrameCounter;`).
- **Rationale:** Dual input routing (Enhanced Input action mapping + raw hardware polling in tick) executes twice in the same frame ($0\text{ms}$), immediately toggling open and closed, presenting to the player as an unresponsive "dead key".
- **User Modification Options:**
  - `[ ] Option 14A (Default)`: Hardware Frame-Latch / Timestamp Debounce on all state toggles.
  - `[ ] Option 14B`: Hold-to-Toggle (Requires 0.3s continuous hold before firing).
  - `[ ] Option 14C`: Modal Menu State Machine with Explicit Focus Transition (Input mode UI-only).

---

### Pillar 15: Multiplayer Discovery & 1-Click Dual-Instance Spawning
- **Proposed Default:** Every multiplayer project generates three 1-click batch launchers on Day 1: (1) `Launch_Local_2Player_Duel.bat` (side-by-side host & client windows on 127.0.0.1 at 1280x720); (2) `Launch_Host_ListenServer.bat` (hosting on UDP port 7777); (3) `Launch_Join_LAN.bat` (interactive prompt for host IP).
- **Rationale:** Eliminates player confusion over "how does a second player connect?" and enables single-developer instant validation of multiplayer synchronization without needing two physical PCs.
- **User Modification Options:**
  - `[ ] Option 15A (Default)`: 1-Click Dual-Instance Local Test Script + Listen Server LAN Scripts.
  - `[ ] Option 15B`: In-Engine Dedicated Server Lobby Browser UI.
  - `[ ] Option 15C`: Steamworks / Epic Online Services (EOS) Matchmaking Integration.
  - `[ ] Option 15D`: Local Split-Screen on Single Viewport (Shared screen or split viewport).

---

### Pillar 16: Package Footprint & Shipping Optimization (The "No PDBs in Shipping" Rule)
- **Proposed Default:** Standalone installer scripts explicitly exclude debug databases (`Excludes: "*.pdb,*.log,*.obj"`), compile targets using `Shipping` configuration (stripping Vulkan/D3D debug layers and shrinking binaries by 75%), cook only referenced map assets (`bCookAll=False`), and enable Oodle package compression.
- **Rationale:** Prevents bloated 1 GB installs where 320 MB is unneeded Visual Studio debug symbols, and shrinks installer download sizes by 80% (e.g. from 357 MB down to 65 MB).
- **User Modification Options:**
  - `[ ] Option 16A (Default)`: Stripped Shipping Binary + PDB Exclusion + Referenced Asset Cooking.
  - `[ ] Option 16B`: Development Build with Symbols Included (Internal playtesting / QA builds).
  - `[ ] Option 16C`: Minimal WebGL/HTML5 Build (Aggressive texture downscaling for web delivery).

---

## 2. Interactive Foundations Plan Template for `/game-forge`

Whenever `/game-forge` or `seikoclaw-architect` presents the Stage A plan at **HITL Gate 1**, it MUST embed this formatted callout block into the plan:

```markdown
### 📋 Proposed Baseline Foundations Matrix
The following operational scaffolding is proposed for this game. 
> 💬 **USER CLARIFICATION CALLOUT:**
> Review the proposed options below. If your design requires modifications (e.g. permadeath instead of restart, timer instead of HP, or mouse-only controls), **call out your overrides now** before we begin prototyping!

| # | Foundation Pillar | Proposed Default | User Override Options |
|---|---|---|---|
| **1** | **Longevity / Health** | `[x]` Numerical HP (0-100%) | `[ ]` One-Hit-Kill \| `[ ]` Stocks/Lives \| `[ ]` Timer \| `[ ]` Puzzle/None |
| **2** | **Defeat & Game Over** | `[x]` Instant Retry / Restart | `[ ]` Permadeath \| `[ ]` Checkpoints \| `[ ]` Narrative Branch \| `[ ]` Fail-Forward |
| **3** | **Pause & Time Stack** | `[x]` Universal Esc/Start Freeze | `[ ]` Real-Time / Non-Pausable \| `[ ]` Tactical Slow-Mo \| `[ ]` Diegetic |
| **4** | **Input & Ergonomics** | `[x]` Gamepad (Cubic Curve) + KBM | `[ ]` Mouse-Only \| `[ ]` KBM Raw \| `[ ]` Twin-Stick \| `[ ]` Touch |
| **5** | **Combat Feedback** | `[x]` Reticle + Floating HP + Sparks | `[ ]` Lock-On Target \| `[ ]` Minimalist / Diegetic \| `[ ]` Trajectory Arc |
| **6** | **Audio Delivery** | `[x]` Procedural Synth Fallback | `[ ]` Bundled Audio Clips \| `[ ]` Chiptune 8-Bit \| `[ ]` Ambient Only |
| **7** | **World Physicality** | `[x]` Solid Colliders + Crash Damage | `[ ]` Elastic Bounce \| `[ ]` Overlap Only \| `[ ]` Invisible Walls |
| **8** | **Display & Window** | `[x]` Windowed Mode (60 FPS Cap) | `[ ]` Exclusive Fullscreen \| `[ ]` Uncapped \| `[ ]` Responsive WebGL |
| **9** | **Distribution Format** | `[x]` Inno Setup Windows Installer | `[ ]` Portable Zip \| `[ ]` Browser WebGL \| `[ ]` Steam Package |
| **10** | **Multi-Modal Handover** | `[x]` Vehicle/Chute/Foot State Machine | `[ ]` Vehicle-Only \| `[ ]` Instant Respawn on Bailout \| `[ ]` GTA-Style |
| **11** | **Spawn Equilibrium** | `[x]` 0% Throttle Runway Rest + Clear Vector | `[ ]` Hot Airborne Start \| `[ ]` Catapult Launch \| `[ ]` Orbit/Hover |
| **12** | **Sensitivity & Binding** | `[x]` Sliders (Pitch/Roll/Yaw) + Conflict Check | `[ ]` Linear Raw Inputs \| `[ ]` Simple Arcade \| `[ ]` Full Custom Re-mapping |
| **13** | **Projectile Safety & Aim**| `[x]` Sweep Raycast + Owner Immunity + Center Aim | `[ ]` Rigid Simulated Bullet \| `[ ]` Instant Hitscan \| `[ ]` Non-Lethal |
| **14** | **Input Debounce / Latch** | `[x]` Single-Frame Latch (`GFrameCounter`) | `[ ]` Hold-to-Toggle (0.3s) \| `[ ]` Modal Focus Switch |
| **15** | **Multiplayer Launchers** | `[x]` 1-Click Dual Window + Listen Server Bat | `[ ]` Dedicated Server Lobby \| `[ ]` Steam/EOS \| `[ ]` Split-Screen |
| **16** | **Package Optimization**  | `[x]` Shipping Target + Exclude PDBs + Oodle | `[ ]` Dev Build with Symbols \| `[ ]` WebGL Aggressive Strip |

*Awaiting your approval or overrides to proceed to Stage B.*
```
