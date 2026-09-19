---
name: asset-generator
description: >
  On-demand game asset generation using Gemini's cloud generate_image tool.
  Triggered by: /gen-asset, /asset-gen, /texture, /sprite, /layer, /hair, /paperdoll, /backdrop, /gen-image, "generate asset", "make a texture for", "create a sprite", "character layer", "hair sprite", "modular sprite".
  Automatically applies fantasy RPG art direction, isometric top-down perspective, strict exclusion rules (no face/head/body/mannequin), grayscale palettes for recoloring, handles seamless tiling or alpha keying post-processing, and deploys directly into the project assets folder.
disable-model-invocation: false
---

# asset-generator

This skill automates the creation of high-fidelity 2D game assets using Gemini's native `generate_image` tool with project-tailored style templates, seamless boundary synthesis, and alpha background extraction.

---

## Supported Slash Commands & Syntaxes

### 1. Seamless Ground Textures
**Commands**: `/texture <name> <description>` or `/texture <biome> <variation_name> <description>`  
**Example**: `/texture volcanic obsidian_crust molten basalt rocks with glowing orange magma fissures`

**Behavior**:
1. **Aspect Ratio**: `1:1`
2. **Prompt Template**:
   ```
   Top-down flat 2D game map texture of [DESCRIPTION], hand-painted digital art style matching fantasy RPG battlemaps, dense organic details, completely seamless tileable pattern, orthographic flat view, no borders, no frames, high resolution detailed texture art
   ```
3. **Tool Call**:
   ```json
   {
     "Prompt": "<formatted_prompt>",
     "ImageName": "<name_or_biome>",
     "AspectRatio": "1:1"
   }
   ```
4. **Post-Processing (Mandatory)**:
   Run the seamless tiling script to guarantee 100% boundary wrap:
   ```bash
   python scripts/make_seamless_tile.py "<GENERATED_JPG_PATH>" "web_client/assets/ground_textures/<biome>/<name>.png"
   ```
5. If creating a biome set, synthesize 12 variations locally using `scripts/deploy_master_ground_textures.py` to save API quota.

---

### 2. Modular Character Builder Layers (Hair, Headgear, Armor, Paperdoll Parts)
**Commands**: `/hair <name> <description>`, `/layer <part_type> <name> <description>`, or `/paperdoll <part> <name> <description>`  
**Example**: `/hair short_spiked short, spiked hairdo in an isometric top down front facing view, 2D anime cel-shaded`  
**Example**: `/layer armor knight_pauldrons heavy steel spiked shoulder pauldrons with leather straps`

**Behavior**:
1. **Aspect Ratio**: `1:1`
2. **Perspective & View Standards**:
   - **Isometric Top-Down Front View**: `isometric, top down, front facing view` (high-angle front 3/4 isometric perspective).
   - This exact view angle aligns modular items (hair, helmets, shoulders, chest pieces) precisely over base character tokens and paperdoll mannequins.
3. **Negative Constraints & Exclusion Language (Mandatory)**:
   - **Strict Anatomical Exclusion**: Explicitly declare `absolutely NO face, NO head, NO skin, NO eyes, NO neck, NO body, NO mannequin, NO dummy, NO jawline/chin`.
   - **Hollow Cavity / Fitting Void**: Require an `open hollow center cavity where the character face/head fits underneath`.
   - **Single Item Isolation**: Enforce `single isolated object centered on canvas, NOT a sprite sheet, NO grid, NO multiple angles/views`.
   - **Clean High-Contrast Background**: Isolate on `solid plain pure white background` or `solid plain pure black background` with razor-sharp silhouette edges.
4. **Palette & Shading Strategy (Greyscale for Customizer Tinting)**:
   - **Greyscale Value Convention**: Specify `simple greyscale palette` / `clean monochromatic grayscale tones (pure white highlights, neutral gray midtones, deep gray shadow accents, crisp black contour lineart)`.
   - **Purpose**: A pure grayscale base allows character creator UIs and game shaders to dynamically tint, recolor, or palette-swap the asset without color bleed or hue distortion.
5. **Prompt Template**:
   ```
   A 2D anime cel-shaded modular character [PART_TYPE] sprite of [DESCRIPTION], viewed from an isometric top-down front-facing perspective (high angle 3/4 front view for a 2D RPG character builder). Crisp clean black lineart, simple greyscale shading palette with monochrome tones (white highlights, neutral gray midtones, deep gray shadows) designed for character customizer tinting. Isolated [PART_TYPE] object only: just the [PART_TYPE], hollow open cavity where the face/head fits, absolutely NO face, NO head, NO skin, NO eyes, NO neck, NO body, NO mannequin, NO dummy, NO jawline. Single centered asset, NOT a sprite sheet, NO grid, NO multiple views, isolated on solid plain pure white background with razor-sharp clean edges.
   ```
6. **Tool Call**:
   ```json
   {
     "Prompt": "<formatted_prompt>",
     "ImageName": "<name>_<part_type>",
     "AspectRatio": "1:1"
   }
   ```
7. **Post-Processing (Mandatory Cavity-Aware Alpha Extraction)**:
   Extract alpha transparency for **both** the outer background and internal cavities (e.g. face/neck opening):
   ```bash
   python scripts/clean_sprite_transparency.py "<GENERATED_JPG_PATH>" "web_client/assets/taxonomy/character_hair/<name>.png" --clear-cavities
   ```

---

### 3. 2D Sprites, Tokens, and Props (Full Characters & Entities)
**Commands**: `/sprite <name> <description>`  
**Example**: `/sprite rogue_assassin female dark elf shadow rogue in leather armor wielding twin glowing daggers`

**Behavior**:
1. **Aspect Ratio**: `1:1`
2. **Perspective & Exclusions**:
   - Specify `isometric top-down front 3/4 angle, dynamic RPG combat stance`.
   - Exclude multiples: `isolated single character/creature only, absolutely NO multiple characters, NO sprite sheet, NO UI, NO floor shadow`.
3. **Prompt Template**:
   ```
   Full-body 2D anime fantasy game sprite of [DESCRIPTION], viewed from an isometric top-down front 3/4 angle, crisp cel-shaded anime lineart, vibrant fantasy colors, dynamic RPG stance, isolated single entity, absolutely NO multiple characters, NO sprite sheet, NO UI, isolated on plain solid black background, high resolution 2D sprite asset
   ```
4. **Tool Call**:
   ```json
   {
     "Prompt": "<formatted_prompt>",
     "ImageName": "<name>_sprite",
     "AspectRatio": "1:1"
   }
   ```
5. **Post-Processing (Mandatory)**:
   Extract alpha transparency from the solid background:
   ```bash
   python scripts/clean_sprite_transparency.py "<GENERATED_JPG_PATH>" "web_client/assets/sprites/<name>.png"
   ```

---

### 4. Backdrops, Map Views & Panoramas
**Commands**: `/backdrop <name> <description>`  
**Example**: `/backdrop oakhaven_sunset panoramic aerial view of a medieval fantasy town at sunset with wooden shingle roofs and river`

**Behavior**:
1. **Aspect Ratio**: `16:9` (or `4:3` / `3:2` if specified)
2. **Prompt Template**:
   ```
   Cinematic wide-angle fantasy environment digital painting of [DESCRIPTION], rich atmospheric lighting, breathtaking scenic depth, hand-painted anime fantasy concept art style, high resolution, no text, no UI, no borders
   ```
3. **Tool Call**:
   ```json
   {
     "Prompt": "<formatted_prompt>",
     "ImageName": "<name>_backdrop",
     "AspectRatio": "16:9"
   }
   ```
4. **Post-Processing**:
   Copy and optimize into `web_client/assets/maps/<name>.png` or `web_client/assets/backdrops/<name>.png`.

---

### 5. General / Custom Images
**Commands**: `/gen-image <name> [aspect_ratio] <description>`  
**Example**: `/gen-image dragon_crest 1:1 glowing gold and emerald heraldic crest for royal banner`

**Behavior**:
1. Use the user's custom aspect ratio (default `1:1`).
2. Pass reference images (`ImagePaths`) if provided by the user.
3. Save to the requested output directory or display the generated image artifact.

---

## Quick Reference: Core Prompt Engineering Rules

| Asset Category | View / Perspective Keyword | Exclusion Language Formula | Palette Strategy |
| :--- | :--- | :--- | :--- |
| **Character Layers (Hair/Gear)** | `isometric, top down, front facing view (high angle 3/4 front view)` | `Isolated [PART] object only, hollow open cavity for face/head, absolutely NO face, NO head, NO skin, NO eyes, NO neck, NO body, NO mannequin, NO dummy, single centered asset, NOT a sprite sheet, NO grid` | `Simple greyscale palette (pure white highlights, neutral gray midtones, deep gray shadows, crisp black contour outlines)` for customizer tinting |
| **Entities & Monsters** | `isometric top-down front 3/4 angle, dynamic RPG combat stance` | `Isolated single character/creature only, NO background elements, NO floor, NO shadows on ground, NOT a sprite sheet, NO multiple views` | Full vibrant anime cel-shaded palette matching faction art guidelines |
| **Ground Textures** | `top-down flat orthographic view, 90-degree bird's eye angle` | `Completely seamless tileable texture, NO borders, NO frames, NO vignetting, NO perspective tilting, NO objects casting horizon shadows` | Material-accurate hand-painted digital texture palette |

---

## Quota & Batch Protection Best Practices
- **Never blast >10 requests concurrently**: Cloud image generation limits burst traffic (429 `RESOURCE_EXHAUSTED`).
- If generating multi-item batches:
  - Add a **3 to 5-second interval** between successive `generate_image` calls.
  - For texture variations, generate **1 master tile** via Gemini and synthesize permutations (rotations, flips, color shifts) with Python instead of calling the API for every single variation.
