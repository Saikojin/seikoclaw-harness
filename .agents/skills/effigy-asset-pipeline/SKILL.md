---
name: effigy-asset-pipeline
description: Offline local neural 2D/3D game asset generation foundry. Creates game-ready 3D meshes, PBR textures, auto-rigging, skinning, motion clips, and 2D sprite sheets on local GPU via Effigy MCP.
author: Saikojin (SeikoClaw - Game Forge)
triggers:
  - effigy
  - local 3d asset generation
  - offline 3d model
  - local neural mesh
  - auto-rig character
  - local sprite sheet
---

# Effigy Asset Pipeline: Local Neural 2D/3D Game Asset Foundry

The **`effigy-asset-pipeline`** skill connects the SeikoClaw Harness to **Effigy** ([`SifuInTheShell/Effigy`](https://github.com/SifuInTheShell/Effigy))—a 100% offline, local GPU asset generation foundry. It transforms text descriptions and concept images into game-ready 3D models, PBR materials, rigged characters, animations, and 2D pixel-art sprite sheets on a single 16 GB NVIDIA GPU without cloud dependencies, API subscriptions, or external uploads.

---

## 🏛️ Architectural Role in SeikoClaw

Effigy serves as the **Heavy Asset Foundry Subsystem** within the SeikoClaw ecosystem:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   LLMWORKBENCH (Local Prompt Engine)                   │
│   expand_game_prompt_local(mode="3d_character_rigging" | "parallax")   │
│   • Enforces A-poses, hollow cavities, chroma padding, seamless wraps  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Structured Prompt Contract
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               EFFIGY ASSET FOUNDRY (Local GPU Workstation)              │
│   create_asset() ➔ run_step("trellis2") ➔ clean ➔ remesh ➔ bake        │
│   ➔ rig_fit ➔ rig_skin ➔ anim ➔ sprites ➔ pixelize                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Exported Engine Assets (.glb / .tscn)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   SEIKOCLAW HARNESS (Master Engine)                    │
│   • Stage D: SxS Visual Bar Parity Loop (look() vs art/BAR.md)         │
│   • Multi-Engine MCPs: godot-developer, unity-developer, unreal-dev    │
│   • Seikojin QA: Non-Headless live windowed execution verification     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 MCP Bridge & Tool Overview

The Effigy MCP server (`mcp/effigy_server.py`) exposes tools over JSON-RPC (stdio or HTTP `:8000`). All asset operations are **append-only and non-destructive**: every step creates a new version folder (`001_upload`, `002_clean`, `003_remesh`) in `library/<asset>/`.

| Tool | Category | Purpose |
| :--- | :--- | :--- |
| **`create_asset(name, kind)`** | Asset Management | Creates an asset container (`kind=""` for 3D model, `"2d"` for 2D pictures/sheets, `"texture"` for standalone material). |
| **`import_file(path, ...)`** | Ingestion | Uploads reference images, turnarounds, existing meshes (`.glb`, `.fbx`, `.obj`), or mocap videos. |
| **`run_step(asset_id, parent, step, params)`** | Pipeline Execution | Dispatches a GPU or CPU pipeline step. Returns `{"status": "running", "job_id": "..."}` for heavy jobs. |
| **`job_status(job_id, wait_s)`** | Job Polling | Bounded polling for running GPU jobs (wait up to 40 seconds per call). |
| **`cancel_job(job_id)`** | Process Control | Safely terminates an active pipeline subprocess and frees VRAM. |
| **`look(asset_id, version, clip, size)`** | Visual Review | Generates a contact sheet or multi-angle preview image for visual critic review. |
| **`fit_check(asset_id, version)`** | Rig Inspection | Checks whether all skeletal joint markers are contained within the mesh boundaries. |
| **`validate(asset_id, version)`** | Geometric QA | Runs automated checklist (manifoldness, hole count, UV seam overlap, size drift). |
| **`export(asset_id, version, profile, options, to_folder)`** | Engine Delivery | Exports game-ready assets to Godot, Unreal, Unity, Web, or 3D print formats. |
| **`open_in_blender` / `pull_from_blender`** | DCC Live Link | Opens mesh in live Blender session via Blender MCP, then pulls edits back as a new version. |

---

## 🚀 3D Character & Prop Pipeline Progression

To produce a game-ready character or prop, execute the following steps in sequence:

### 1. Prompt Expansion via LLMWorkbench (Upstream)
Before calling Effigy, expand the concept using `llmworkbench` to enforce strict biomechanical rest-pose standards:
```json
{
  "ServerName": "llmworkbench",
  "ToolName": "expand_game_prompt_local",
  "Arguments": {
    "mode": "3d_character_rigging",
    "idea": "cyberpunk street samurai in carbon-fiber armor",
    "model": "gemma-3-1B-it-QAT-Q4_0.gguf"
  }
}
```

### 2. Creation & Concept Synthesis
```python
# 1. Initialize asset container
create_asset(name="cyber_samurai", kind="")

# 2. Generate brief
run_step(asset_id="cyber_samurai", parent=None, step="brief", params={
    "prompt": "<expanded_prompt_from_llmworkbench>",
    "category": "character"  # "character" | "prop" | "creature"
})

# 3. Generate 4 concept images (Z-Image-Turbo)
run_step(asset_id="cyber_samurai", parent="001_brief", step="concepts", params={})

# 4. Cut-out background and re-pose to A-pose
run_step(asset_id="cyber_samurai", parent="002_concepts", step="prep", params={"pick": 0})
run_step(asset_id="cyber_samurai", parent="003_prep", step="canon", params={})  # Symmetrical A-pose
run_step(asset_id="cyber_samurai", parent="004_canon", step="prep", params={})
```

### 3. Neural 3D Generation & Mesh Preparation
```python
# 5. Generate 3D Neural Mesh (TRELLIS.2 / Pixal3D)
run_step(asset_id="cyber_samurai", parent="005_prep", step="trellis2", params={
    "preset": "faithful",  # "faithful" (Pixal3D) or "fast" (TRELLIS.2)
    "texture_size": 2048
})

# 6. Clean geometry (heal non-manifold edges, level floor, rescale)
run_step(asset_id="cyber_samurai", parent="006_trellis2", step="clean", params={
    "height_m": 1.8,
    "level": "auto",
    "straighten": True
})

# 7. Remesh to game-ready polygon budget
run_step(asset_id="cyber_samurai", parent="007_clean", step="remesh", params={
    "faces": 15000,
    "topology": "quad",  # "quad" or "tri"
    "symmetry": "x"
})

# 8. Automatic UV Unwrap
run_step(asset_id="cyber_samurai", parent="008_remesh", step="uv", params={})

# 9. PBR Baking from Neural Volume (Albedo, Normal, Roughness, Metallic, AO)
run_step(asset_id="cyber_samurai", parent="009_uv", step="bake", params={
    "texture_size": 2048,
    "normal_map": True,
    "hi_denoise": 6,
    "ao_rays": 256
})
```

### 4. Skeletal Rigging, Skinning & Animation
```python
# 10. Fit 52-Joint Humanoid Skeleton (or creature template: fox, dragon, horse, spider)
run_step(asset_id="cyber_samurai", parent="010_bake", step="rig_fit", params={
    "template": "mixamo52"  # "mixamo52" | "fox" | "horse" | "bird" | "dragon" | "spider"
})

# 11. Containment check (verify all joints are inside the mesh)
fit_check(asset_id="cyber_samurai", version="011_rig_fit")

# 12. Skinning (SkinTokens neural skinning or Blender bone heat)
run_step(asset_id="cyber_samurai", parent="011_rig_fit", step="rig_skin", params={
    "engine": "auto"
})

# 13. Retarget Animation Clips (CC0 Mesh2Motion library or Kimodo text-to-motion)
run_step(asset_id="cyber_samurai", parent="012_rig_skin", step="anim", params={
    "clips": ["Idle_Sword", "Walk", "Jog", "Sword_Attack", "Jump_Start", "Death_A"]
})
```

---

## 🎨 2D Pixel-Art Sprite Sheet Projection

For 2D platformers, beat-'em-ups, and top-down RPGs, Effigy can project the 3D animated character directly into a 2D pixel-art sprite sheet:

```python
# 1. Render animated clips to orthographic side/isometric frames
run_step(asset_id="cyber_samurai", parent="013_anim", step="sprites", params={
    "height_px": 96,
    "yaws": [90],        # 90 = side profile, 0 = front, 180 = back
    "fps": 12,
    "shading": "flat"
})

# 2. Quantize into pixel art with palette & dither
run_step(asset_id="cyber_samurai", parent="014_sprites", step="pixelize", params={
    "scale": 1,
    "colors": 16,        # or "palette": "pico-8"
    "outline": "darkest",
    "dither": "bayer2"
})

# 3. Validate and Export to Godot 2D
validate(asset_id="cyber_samurai", version="015_pixelize")
export(
    asset_id="cyber_samurai",
    version="015_pixelize",
    profile="godot-2d",
    options={},
    to_folder="res://assets/characters/samurai/"
)
# Output: Writes <asset>.png sprite sheet + <asset>.tres (SpriteFrames) + <asset>.tscn (AnimatedSprite2D)
```

---

## 🛡️ Verification & Gate Integration

Assets produced through Effigy must pass through SeikoClaw's gatekeeping protocol before integration:

1. **Deterministic Geometry Gate (`[GATE: ASSET_QA]`)**:
   Call `validate(asset_id, version)`. Fails if non-manifold geometry, inverted normals, or missing UV coordinates are detected.
2. **Visual Parity Gate (`[GATE: VISUAL_CRITIC]`)**:
   Call `look(asset_id, version)` to retrieve rendered contact sheets. Composite side-by-side with locked references in `refs-locked/` via `python scripts/fetch_asset_references.py composite` and evaluate against `art/BAR.md` (Silhouette, Value Hierarchy, Palette Harmony, Resolution Density).
3. **Engine Import Verification**:
   Export to the project's asset directory (`res://assets/` for Godot, `Content/Assets/` for Unreal, `Assets/` for Unity) and execute the engine developer skill (`godot-developer`, `unreal-developer`, `unity-developer`) to build and instantiate the runtime scene.
