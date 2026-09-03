# Game Tooling Catalog & Architectural Blueprints

This catalog provides concrete architectural blueprints, UI layouts, and CLI script patterns distilled from battle-tested game projects (including `Tactical-Adberrain`). Use these patterns to specify and implement developer tools that streamline game creation.

---

## 1. Biome & Map Generator Workbench (`generator_workbench.html`)

A zero-install, browser-based authoring tool for procedural world generation, terrain elevation, and climate distribution.

### Architecture & UI Layout
- **Left Panel (Parameters & Controls)**:
  - **Terrain Synthesis**: Seed input, Fractal Octaves, Persistence, Lacunarity, Sea Level slider.
  - **Climate Matrix**: Temperature gradient slider, Moisture/Precipitation slider, Whittaker Biome selector (e.g., Tundra, Boreal Forest, Temperate Grassland, Desert, Rain Forest).
  - **Technical Layers Toggle**: Checkboxes for Collision Grid, Elevation Contours, Friction Masks, and Asset Slot Overlays.
  - **Multi-Zoom LOD Preview**: Continuous slider from Adventure scale (5ft cells) to Continental scale (1000mi cells).
- **Center Canvas**:
  - High-performance HTML5 2D Canvas rendering terrain colors, water depths, and asset markers.
- **Top/Bottom Action Bar**:
  - "Randomize Seed", "Re-generate", "Export JSON Manifest & Object Image".

### Output Manifest Schema
```json
{
  "map_id": "map_valen_plains_01",
  "dimensions": { "width": 64, "height": 64, "cell_size_px": 32 },
  "coordinate_system": "hex_axial",
  "layers": {
    "elevation": [ ... ],
    "biome": [ ... ],
    "collision": [ ... ],
    "placed_slots": [
      { "id": "tree_oak_01", "q": 12, "r": 8, "type": "flora", "blocking": true }
    ]
  }
}
```

---

## 2. World Map Manager & Spatial Baking Pipeline (`world_map_manager.html`)

A dedicated visual tool to place, stitch, and bake multi-resolution map chunks into a unified planetary or regional world atlas.

### Key Components
1. **World Atlas Canvas**: Macro view of the world grid or continent where regional and local maps are arranged.
2. **Chunk Roster & Inspector**: Side panel listing available `.json` map manifests and companion PNG assets.
3. **Spatial Snapping & Coordinate Placement**: Drag-and-drop placement with snap-to-hex or snap-to-tile bounding boxes.
4. **Spatial Baking Pipeline (`world_atlas_service.py`)**:
   - Backend service using an **R-Tree** or QuadTree spatial index.
   - Bakes all placed chunks into `data/world_atlas/world_atlas_manifest.json`.
   - **REST Endpoints**:
     - `POST /api/v1/world_map/bake`: Serializes current spatial atlas.
     - `GET /api/v1/world_map/lookup?x=...&y=...&tier=...`: Returns the specific active map chunk for runtime rendering based on player position and zoom level.

---

## 3. Visual Soundscape & Audio Workbench (`sound_workbench.js`)

An interactive testing deck enabling designers to test, tweak, and catalog sound effects, foley, and atmospheric music without playing through the game.

### Architecture & Capabilities
- **Streaming & Synthesized Audio Player**: Supports both static sound assets (`.wav`, `.ogg`) and real-time Web Audio API procedural synthesizers.
- **Canvas 2D Oscilloscope & Spectrum Visualizer**: Real-time visual feedback of frequency bands and waveforms using `AnalyserNode`.
- **Bus Mixers & Channel Strips**:
  - Sliders for Master, Ambience/Environment, Foley/SFX, Music, and UI Channels.
  - Stereo panning sliders (`StereoPannerNode`) and distance roll-off simulation.
- **Procedural Sound Catalog**:
  - Built-in presets for game actions: Weapon Swings, Parries, Shield Blocks, Footsteps (Dirt/Stone/Wood), Explosions, UI Clicks, Ambient Wind, Creature Growls.
- **Export Config**: Generates `audio_manifest.json` mapping game event tags (e.g. `event.combat.parry`) to audio presets and volume gains.

---

## 4. 2D Skeletal Puppet & Rigging Studio (`rigging_studio.html`)

A web-based studio for authoring 2D modular characters, clothing/armor paperdoll stacking, bone hierarchies, and 60 FPS keyframe animations.

### Architecture
- **24-Slot Modular Puppet Hierarchy**:
  - `Root -> Pelvis -> Torso -> Neck -> Head`
  - `Torso -> Shoulder.L/R -> UpperArm.L/R -> Forearm.L/R -> Hand.L/R -> WeaponSlot`
  - `Pelvis -> Thigh.L/R -> Shin.L/R -> Foot.L/R`
- **Slot Attachment Inspector**:
  - Allows equipping modular sprite layers (helmets, cuirasses, cloaks, main-hand weapons, shields) to verify alignment and depth z-sorting.
- **Keyframe Animation Timeline**:
  - Playback controls (Play, Pause, Loop, Scrub).
  - Keyframe tracks for bone rotation, translation, and sprite switching.
  - Standard animation states: `idle`, `walk`, `attack_slash`, `cast_spell`, `hit_react`, `death`.
- **Export Format**: Exports standard JSON animation clips compatible with the runtime sprite rendering engine.

---

## 5. Asset Preprocessing CLI Suite (Python / `uv run`)

A collection of fast, deterministic scripts that standardize art assets before they enter the game engine.

### Essential Preprocessor Scripts

#### A. Alpha & Transparency Cleaner (`clean_sprite_transparency.py`)
- **Problem**: Generated or cropped sprites often have semi-transparent white/black halos, fringe pixels, or solid background squares.
- **Operation**:
  - Scans target folder for PNG files.
  - Uses `PIL` / `cv2` to detect corner colors, flood-fill backgrounds to alpha 0, and applies a luminance threshold on edges to strip dark halos.
  - Command: `uv run scripts/clean_sprite_transparency.py --input-dir assets/raw --output-dir assets/cleaned --threshold 15`

#### B. Seamless Texture Tile Maker (`make_seamless_tile.py`)
- **Problem**: Ground textures produce visible repeating seams when tiled across large terrains.
- **Operation**:
  - Wraps the image horizontally and vertically by 50% (toroidal shift).
  - Applies a feathered cross-fade blend down the center seams.
  - Command: `uv run scripts/make_seamless_tile.py --image assets/textures/dirt.png --blend-width 32 --output assets/textures/dirt_seamless.png`

#### C. Local Image & Prompt Manifest Runner (`generate_local_images.py`)
- **Operation**:
  - Reads a structured `asset_prompts_manifest.json` containing asset names, prompt text, negative prompts, and target dimensions.
  - Feeds prompts to local Stable Diffusion / GGUF endpoints or image generators, auto-naming output files into designated asset subdirectories.

---

## 6. Content Parsers, Schemas & Vault Validators

Tools to ensure game lore, dialogues, quests, and rules can be authored freely without crashing the game engine.

### Core Patterns

#### A. Structured JSON Schemas (`docs/*_schema.json`)
- Define strict JSON schemas using Draft 7 / Draft 2020-12 for:
  - `quest_schema.json`: Objectives, prerequisites, reward tables, failure states, branch outcomes.
  - `dialogue_template_schema.json`: Nodes, speaker IDs, conditions, response options, trait checks, event triggers.
  - `item_schema.json`: Stats, slot types, requirements, lore descriptions.

#### B. Vault / SRD Ingestor (`srd_parser.py`, `hierarchical_ingestor.py`)
- Reads raw tabletop SRD files, markdown vaults, or design notes.
- Extracts structured entities (Classes, Spells, Monsters, Feats, Historical Eras) using regex patterns and AST parsing, exporting into clean, indexed JSON databases in `data/game_definitions/`.

#### C. Vault & Content Integrity Auditor (`validate_vault.py`)
- Automated validation script run in CI or pre-commit:
  - Verifies all foreign key IDs match existing records (no dangling dialogue links).
  - Checks for duplicate item/quest IDs.
  - Validates that referenced image and audio paths exist on disk.
  - Returns exit code 0 on success, exit code 1 with detailed failure reports.

---

## 7. Single-Command Dev Environment & Packaging

### Local Orchestration
- **`start_dev.bat` / `start_dev_environment.ps1`**:
  - Checks port availability (e.g. 8080 for Web Client, 5001 for Game API).
  - Starts backend services (Flask/Node/SpacetimeDB).
  - Starts local frontend HTTP server.
  - Launches browser directly to game URL or tools menu (`/tools/`).
- **`stop_dev.bat` / `stop_dev_environment.ps1`**:
  - Gracefully kills background processes by PID/port.

### Desktop Standalone Packaging (`game_standalone.spec`)
- PyInstaller / Electron packaging configuration bundling backend Python runtime, static assets, and WebGL engine into a single executable installer or folder.
