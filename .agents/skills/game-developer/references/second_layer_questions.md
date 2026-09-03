# Second-Layer Technical Question Bank

This question bank is used by the **`game-developer`** skill during the **Second-Layer Technical Grilling** phase. Its goal is to uncover the hidden tooling, pipelines, authoring workbenches, and data validators needed before building game features, ensuring a linear and predictable development process.

---

## Pillar 1: Spatial & World Authoring

1. **Map Geometry & Coordinate Space**:
   - Is your world grid-based (Hexagonal, Orthogonal 2D grid, Isometric) or continuous coordinate space?
   - If hex, which orientation (pointy-topped or flat-topped) and coordinate system (axial, cubic, offset)?
   - Do you need a visual **Snap Grid & Collision Offset Tuner** to align sprites with physical hitboxes?

2. **World Scale & LOD Hierarchy**:
   - Does the world span multiple scales (e.g., room/tactical, settlement/town, province/regional, continental/celestial)?
   - How does the camera transition between scales (discrete scene loads vs. continuous zoom LOD cross-fading)?
   - Do you need a **World Map Manager** with a spatial baking pipeline (R-Tree / QuadTree indexing) to assemble regional chunks into a unified atlas?

3. **Map Creation Methodology**:
   - Will maps be hand-painted, procedurally generated, or hybrid (designer stamps assets onto procedurally generated terrain)?
   - If procedural, what climate/terrain model is used (e.g., Whittaker diagram, Donjon fractal heightmaps, Voronoi noise)?
   - Do designers need an interactive **Generator Workbench** with live parameter sliders (roughness, sea level, moisture, biome distribution) and instant export?

4. **Layer Slots & Collision Masks**:
   - How many spatial layers exist per tile/hex (e.g., Ground terrain, Floor decals, Structural walls, Roofs/Canopies, Props, Light anchors)?
   - Do you need a dedicated **Map Painter** tool to author passability masks, elevation contours, and interaction hotspots?

---

## Pillar 2: Visual Asset Preprocessing & Generation

1. **Asset Pipeline & Sourcing**:
   - Where do visual assets originate (commercial sprite packs, hand-drawn art, 3D renders, or local AI diffusion pipelines like Stable Diffusion / GGUF)?
   - If generated locally, do you need an automated prompt manifest runner and asset deployment script (e.g., `generate_local_images.py`, `deploy_cloud_asset.py`)?

2. **Edge & Transparency Cleaning**:
   - Do imported or generated sprites have noisy borders, dark halos, or solid background colors?
   - Do you need an automated alpha thresholding and edge-cleaning script (e.g., `clean_sprite_transparency.py`) to run across your asset directories?

3. **Ground & Environment Textures**:
   - Are environment tiles repeating/seamless?
   - Do you need an image-offset and edge-feathering script (e.g., `make_seamless_tile.py`) to generate seamless ground textures from raw images?

4. **Sprite Sheets & Atlas Packing**:
   - How are sprites served to the game engine (individual files, texture atlases, or sprite sheets)?
   - Do you need an asset extractor or sprite sheet packer script to slice multi-frame sheets or package sprites for runtime memory optimization?

---

## Pillar 3: Sensory & Audio Workbenches

1. **Audio Architecture**:
   - How will audio be generated and played (Web Audio API procedural synthesis, static WAV/MP3/OGG files, or hybrid)?
   - What channels/buses exist (Master, Music, Ambient/Atmospheric, Combat Foley, UI Clicks, Voice)?

2. **Audio Authoring & Preview**:
   - Can designers test sounds in isolation without loading the full game and triggering specific gameplay states?
   - Do you need a standalone **Sound Workbench** equipped with an interactive audio player, real-time Canvas oscilloscope/spectrum visualizer, looping controls, channel volume sliders, and stereo panning?

3. **Dynamic & State-Driven Soundscapes**:
   - Does ambient audio adapt to game state (e.g., wildlife going dead silent before enemy ambushes, harmonic darkening during low morale)?
   - Do you need procedural audio generator scripts (e.g., `generate_local_audio.py`) to batch-synthesize foley effects for quick iteration?

---

## Pillar 4: Animation, Puppets & Rigging

1. **Character Architecture**:
   - Are characters static sprites, multi-directional sprite sheets, modular paperdolls (layered clothing/armor/weapons), or 2D skeletal puppets?
   - If modular or skeletal, how many attachment slots exist (Head, Torso, Main Hand, Offhand, Legs, Cloak, Mount)?

2. **Rigging & Keyframing Tools**:
   - How are animations authored and previewed?
   - Do designers need a web-based **Rigging Studio** with bone hierarchies, pivot adjustments, slot parenting, and 60 FPS keyframe previews before importing into the runtime engine?

3. **Visual Occlusion & Roof Dissolve**:
   - When characters walk behind trees or inside buildings, how does the engine handle occlusion?
   - Do you need shader/stencil tools or alpha masks for automatic roof dissolve and radial canopy transparency?

---

## Pillar 5: Content, Lore & Data Validation

1. **Data Formats & Storage**:
   - How are game rules, characters, items, quests, dialogue, and faction standings defined (JSON, YAML, SQLite, Markdown)?
   - Are there external rulebooks, system reference documents (SRD), or Obsidian vaults to ingest?

2. **Parsers & Ingestion Scripts**:
   - Do you need automated parsers (e.g., `srd_parser.py`, `extract_backgrounds.py`, `hierarchical_ingestor.py`) to convert markdown or PDF rule sets into game-ready JSON structures?
   - Do you need vault consolidation or sanitization tools (`consolidate_vault.py`, `sanitize_vault.py`) to ensure clean formatting?

3. **Schema Enforcement & Integrity Auditing**:
   - Are there strict JSON schemas for quests, events, timelines, and dialogue trees?
   - Do you need a pre-commit or CI data auditor (e.g., `validate_vault.py`, `audit_vault.py`) to detect missing IDs, broken references, dangling dialogue links, or illegal stat ranges?

4. **In-Client Content Inspection**:
   - Can designers and writers browse game content and lore visually during development?
   - Do you need a lightweight **Wiki Browser** or **Asset Browser** tool to inspect entities, relations, and art without opening raw JSON files?

---

## Pillar 6: Developer Staging, Math Simulators & Test Infrastructure

1. **Dev Environment Orchestration**:
   - What services comprise the game (frontend web client, backend game loader API, database, asset server)?
   - Do you have single-command environment startup and teardown scripts (e.g., `start_dev.bat`, `stop_dev.bat`, `start_dev_environment.ps1`)?

2. **Headless Math & Balance Testbeds**:
   - Can game math (combat mitigation formulas, TTK, economy sinks, XP curves) be tested headlessly?
   - Do you need a balance simulator (integrating with `game-systems-modeler`) or a command-line battle simulator to run 10,000 simulated encounters before UI integration?

3. **Packaging & Desktop Distribution**:
   - Is the game web-only, desktop-standalone (PyInstaller, Electron, Tauri), or mobile?
   - Do you need automated build specs (e.g., `game_standalone.spec`) and smoke test routines to verify zero missing dependencies?

4. **Automated Quality Assurance**:
   - How will game systems be verified against regressions (Jest for frontend math/state, Pytest for backend APIs, Playwright/Karate for E2E scenarios)?
   - Do you need a standardized QA playbook and automated feature test runner?
