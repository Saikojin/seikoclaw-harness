---
name: polyhaven-assets
description: Search, inspect, and download CC0 textures, HDRIs, and models from Poly Haven with strict 2K resolution gating and multi-engine material adapters.
author: Saikojin (SeikoClaw - Game Forge)
triggers:
  - polyhaven
  - poly haven
  - cc0 textures
  - download hdri
---

# Poly Haven Asset Pipeline & Cross-Engine Bridge

The **`polyhaven-assets`** skill provides zero-dependency searching, metadata inspection, and downloading of public domain (CC0) PBR textures, environment HDRIs, and 3D models from [Poly Haven](https://polyhaven.com/) directly into the SeikoClaw Harness.

All queries and downloads enforce **strict 2K resolution gating** by default to protect workstation storage, with automated transpilation for Godot, Unity, Unreal, and Blender.

---

## 1. Storage Discipline & 2K Resolution Policy

Poly Haven's complete catalog spans over **8.43 TB (178,000+ files)**. Unregulated 8K/16K downloads rapidly consume hundreds of gigabytes. This pipeline strictly enforces a **2K Resolution Default Tier**:

| Tier | Texture Set (Avg) | HDRI (Avg) | SeikoClaw Policy | Target Use Case |
| :---: | :---: | :---: | :---: | :--- |
| **1k** | 2–5 MB | 1–3 MB | Fast Prototyping | Mobile games, background props, low-spec targets |
| **2k** | **10–25 MB** | **5–15 MB** | **DEFAULT** | **Standard game-ready production, realtime rendering** |
| **4k** | 40–90 MB | 20–45 MB | On-Demand (`-r 4k`) | Hero props, player hands/weapons, primary vista lighting |
| **8k** | 150–350 MB | 80–180 MB | Explicit Override | Cinematic stills, offline architectural pre-renders |
| **16k** | N/A | 300–800 MB | Explicit Override | High-end visual effects skydomes |

### Mandatory Storage Guardrails
1. **Implicit 2K Default**: Omitting `--resolution` or `-r` automatically fetches the **2K variant**.
2. **Selective Map Ingestion**: Downloads only active channels (`Diffuse`, normal, `Rough`, `Metal`, `AO`), discarding unselected duplicates (e.g., skips redundant `.exr` when `.png`/`.jpg` is selected).
3. **Local LRU Cache Cap**: The local cache directory (`.scratch/polyhaven_cache/`) enforces a **10 GB ceiling**, evicting least-recently used assets automatically.

---

## 2. CLI Command Workflows (`scripts/polyhaven.py`)

### A. Search Assets
Search the Poly Haven catalog by keyword, asset type, or category:
```bash
# Search for textures matching "brick"
python scripts/polyhaven.py search "brick" --type textures --limit 10

# Search for HDRIs in outdoor/nature category
python scripts/polyhaven.py search "forest" --type hdris --limit 5

# Output machine-readable JSON for subagents
python scripts/polyhaven.py search "wood" --type textures --json
```

### B. Inspect Asset Metadata & File Sizes
Inspect available resolutions and channels before downloading:
```bash
python scripts/polyhaven.py info "brown_planks_03"
python scripts/polyhaven.py info "kloofendal_48d_partly_cloudy" --json
```

### C. Fetch Asset (2K Default)
Fetch and transpile directly for your engine:
```bash
# Fetch texture set for Godot (auto-maps OpenGL nor_gl and emits .tres StandardMaterial3D)
python scripts/polyhaven.py fetch "brown_planks_03" --target godot --output "res://assets/textures/wood/"

# Fetch texture set for Unity (auto-maps DirectX nor_dx, emits .meta and URP Lit .mat)
python scripts/polyhaven.py fetch "brown_planks_03" --target unity --output "Assets/PolyHaven/Wood/"

# Fetch HDRI for Blender (downloads 2K HDR and generates setup_material.py)
python scripts/polyhaven.py fetch "kloofendal_48d_partly_cloudy" --target blender --output ".scratch/sky/"

# Fetch raw textures without engine files
python scripts/polyhaven.py fetch "brick_wall_001" --resolution 2k --target raw --output "textures/brick/"
```

### D. Manage Local Cache
```bash
# Check cache usage and file count
python scripts/polyhaven.py cache --status

# Prune cache to enforce 10 GB (or custom) budget
python scripts/polyhaven.py cache --prune --max-size 10GB

# Clear entire cache
python scripts/polyhaven.py cache --clear
```

---

## 3. Multi-Engine Target Adapters

### 🤖 Godot Engine (`--target godot`)
- **Normal Map**: Auto-selects OpenGL **`nor_gl`** (Godot standard).
- **Resource Transpilation**: Generates Godot 4 `StandardMaterial3D` (`.tres`) for textures or `PanoramaSkyMaterial` for HDRIs:
  ```ini
  [gd_resource type="StandardMaterial3D" load_steps=5 format=3]
  [ext_resource type="Texture2D" path="wood_diffuse_2k.png" id="1_Diffuse"]
  [ext_resource type="Texture2D" path="wood_nor_gl_2k.png" id="2_nor_gl"]
  [ext_resource type="Texture2D" path="wood_rough_2k.png" id="3_Rough"]
  [resource]
  albedo_texture = ExtResource("1_Diffuse")
  normal_enabled = true
  normal_texture = ExtResource("2_nor_gl")
  roughness_texture = ExtResource("3_Rough")
  ```

### ⚡ Unity Engine (`--target unity`)
- **Normal Map**: Auto-selects DirectX **`nor_dx`** (Unity standard).
- **Metadata Management**: Generates companion `.meta` files setting `textureType: 1` (Normal Map) and `sRGBTexture: 0` for linear maps (`nor_dx`, `Rough`, `Metal`, `AO`, `arm`).
- **Material Template**: Generates a URP Lit Material (`.mat`) ready for immediate assignment.

### 🌐 Unreal Engine (`--target unreal`)
- **Normal Map**: Auto-selects DirectX **`nor_dx`** (Unreal standard).
- **Material Manifest**: Emits `material_manifest.json` parameterizing `BaseColorMap`, `NormalMap`, `RoughnessMap`, and `MetallicMap` for instantiating the project's PBR Master Material (`MI_{slug}`).

### 🎨 Blender DCC (`--target blender`)
- **Direct MCP Integration**: When `blender` MCP is active, call:
  ```json
  {
    "ServerName": "blender",
    "ToolName": "import_asset",
    "Arguments": {
      "source": "polyhaven",
      "id": "brown_planks_03",
      "asset_type": "textures",
      "resolution": "2k",
      "apply_to": ["ActiveObject"]
    }
  }
  ```
- **BPY Fallback**: Emits `setup_material.py` which loads textures, configures colorspace (`sRGB` for Diffuse, `Non-Color` for Normal/Roughness/Metallic), and links them to the `Principled BSDF` node.

---

## 4. Integration with Game Forge & Agent Workflows

- **Stage Gate B (Prototyping)**: Use `polyhaven.py fetch <slug> --resolution 2k` to rapidly pull terrain, floor, and skybox assets without asset authoring latency.
- **Stage Gate C (Production Parity)**: Pair with `blender-developer` and engine skills (`godot-developer`, `unity-developer`, `unreal-developer`) for zero-manual-import pipelines.
- **Visual Critic Parity**: Poly Haven CC0 assets provide photorealistic PBR grounding to ensure parity against reference targets.

---

## 5. Credits & Upstream Attribution

All textures, environment HDRIs, and 3D models fetched by this skill are created and maintained by the **[Poly Haven](https://polyhaven.com/)** community, founded by Greg Zaal and Rob Tuytel.

- **License**: 100% [Creative Commons 0 (CC0)](https://creativecommons.org/publicdomain/zero/1.0/) public domain dedication. Assets are free to use in any personal, commercial, or educational project with zero royalty, account, or paywall obligations.
- **Patreon Support**: Poly Haven is completely funded by the community. You can support their work on [Patreon](https://www.patreon.com/polyhaven).

