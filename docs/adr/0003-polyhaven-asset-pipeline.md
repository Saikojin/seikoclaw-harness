# 3. Poly Haven Asset Ingestion Pipeline & Resolution Gating

We decided to integrate the Poly Haven API (`https://api.polyhaven.com/`) into the SeikoClaw Harness ecosystem via a dedicated skill (`polyhaven-assets`) and CLI tool (`scripts/polyhaven.py`). The pipeline enforces strict resolution gating defaulting to 2K resolution tier assets to safeguard local disk space, with seamless bidirectional connections to `blender-developer` (Blender MCP), `godot-developer`, `unity-developer`, and `unreal-developer`.

## Context

Poly Haven offers an unauthenticated public API serving over 2,387 CC0 HDRIs, PBR textures, and 3D models totaling 8.43 TB (7.67 TiB across 178,232 unique files). While master resolutions (8K textures and 16K–24K HDRIs) provide unmatched fidelity, downloading them indiscriminately consumes several gigabytes per asset and rapidly exhausts workstation storage.

Developers and autonomous game-development agents in SeikoClaw frequently require high-quality real-world PBR textures, skyboxes, and environmental props for Godot, Unity, Unreal, and Blender. A systematic, storage-conscious ingestion pipeline is needed to search, fetch, and configure these assets directly inside target game engine projects.

## Decisions

1. **Resolution Tier Default (2K Policy)**:
   - All asset queries and downloads default strictly to the **2K resolution tier** (`2k`), which provides an optimal balance between visual crispness and storage efficiency:
     - 2K Texture set (Diffuse, Normal, Roughness, AO/ARM): ~10–25 MB (vs. ~150–350 MB for 8K).
     - 2K HDRI (.exr/.hdr): ~5–15 MB (vs. ~300–800 MB for 16K).
   - Higher resolutions (`4k`, `8k`, `16k`) are supported via an explicit `--resolution` flag or agent parameter, reserved for hero props, close-up inspections, or cinematic skyboxes.

2. **Standalone Fetcher Utility (`scripts/polyhaven.py`)**:
   - Provide a zero-external-dependency Python script in the harness executing:
     - `search`: Query assets by keyword, category, and type with JSON/table output.
     - `info`: Display available maps, resolutions, and exact byte sizes before downloading.
     - `fetch`: Download exact maps for a specified asset and resolution.
     - `cache`: Manage local cache quota (default 10 GB LRU ceiling in `.scratch/polyhaven_cache/`).

3. **Game Engine & DCC Adapter Bridges**:
   - **Blender MCP Bridge**: Integrates with `blender-developer` and the `import_asset` tool (`source: "polyhaven"`, `resolution: "2k"`), or injects automated `bpy` material scripts linking Principled BSDF nodes.
   - **Godot Bridge (`--target godot`)**: Downloads to `res://assets/polyhaven/{slug}/`, selects `nor_gl` (OpenGL Normal format), and auto-generates Godot `.tres` `StandardMaterial3D` or `PanoramaSkyMaterial`.
   - **Unity Bridge (`--target unity`)**: Downloads to `Assets/PolyHaven/{slug}/`, selects `nor_dx` (DirectX Normal format), writes `.meta` configs setting Normal Map flags and linear color spaces for roughness/ARM, and outputs URP Lit materials.
   - **Unreal Bridge (`--target unreal`)**: Downloads to `Content/PolyHaven/{slug}/`, formats textures for Unreal MCP batch import, and hooks into PBR Master Material instances.

4. **Skill Router & Benchmark Alignment**:
   - Create `.agents/skills/polyhaven-assets/SKILL.md` indexed under Section 1 of `seikoclaw-harness`.
   - Add routing test cases to `evals/routing/routing_cases.json` ensuring pairwise collision similarity < 0.65 against `asset-generator` and `blender-developer`.

## Consequences

- Game Forge and engine developer skills can instantly pull photorealistic CC0 PBR assets without manual browser navigation.
- Local storage remains protected within a bounded footprint.
- Engine-specific texture conventions (DirectX vs OpenGL normal maps, channel packed ARM textures) are handled automatically at ingestion time.
