---
name: mood-board-curator
description: Curates visual, audio, and mood references into interactive galleries (mood_board.html) and extracts structured style markers (style_markers.json) for ArtistAgent RAG art generation.
---

# Mood Board Curator (Reference & Mood Board Skill)

The **Mood Board Curator** translates non-coding designers' visual and audio inspirations ("feels like Hades meets Darkest Dungeon", dark fantasy color palettes, retro synth audio) into curated interactive reference galleries (`mood_board.html`) and structured style marker schemas (`style_markers.json`) for the localized **ArtistAgent** AI art generation engine.

## Core Capabilities

1. **Flexible Reference Ingestion**:
   - Local image/audio files and folder paths.
   - External web image/video URLs.
   - Shorthand game title references ("Darkest Dungeon UI", "Hades lighting").
   - Freeform text prompts describing color theory, lighting, and anatomy.
2. **Category Organization**:
   - Environment / World
   - Characters / Creatures
   - UI / HUD Elements
   - VFX & Particle Systems
   - Color Palette & Lighting
   - Audio / Music / SFX Mood
3. **ArtistAgent RAG Integration**:
   - Extracts descriptive style markers (Form & Anatomy, Color Theory, Shading/Lighting) into `docs/design/style_markers.json`.
   - Directly feeds ArtistAgent's vision-description retrieval RAG pipeline.
4. **Strict Project Style Isolation**:
   - Enforces project-level style subsets (e.g. `Adberrain` Dark Fantasy vs `Tablebuddy` VTT Clean UI) to eliminate cross-project "style bleed" as required by `project_vision.md`.

## Output Specifications

Produces:
1. `docs/design/mood_board.html`: Single-file interactive HTML gallery with image carousels, color palette swatches, and audio preview links.
2. `docs/design/style_markers.json`: JSON schema for ArtistAgent RAG prompt injection.

### `style_markers.json` Schema

```json
{
  "projectName": "Adberrain",
  "styleSubset": "dark_fantasy_combat",
  "colorPalette": ["#1a0003", "#4a121a", "#8c242b", "#d9822b", "#f2e3c9"],
  "styleMarkers": {
    "formAndAnatomy": "Rigid geometric armor silhouette paired with organic, frayed cloth edges",
    "colorTheory": "Desaturated grimdark base with high-contrast amber fire highlights",
    "shadingAndLighting": "Chiaroscuro heavy cast shadows with directional torch rim lighting"
  },
  "referenceAssets": [
    { "category": "character", "source": "Darkest Dungeon Bounty Hunter", "notes": "Heavy leather coat and hidden facial features" }
  ]
}
```

## Workflow

1. **Ingest Inspirations**: Ask the designer for their visual/audio reference sources or shorthand title comparisons.
2. **Catalog & Categorize**: Group assets into Environment, Character, UI, VFX, Palette, and Audio pillars.
3. **Enforce Style Isolation**: Verify that assets map strictly to the active project context (`Adberrain` vs `Tablebuddy`).
4. **Generate Output**: Write `mood_board.html` gallery and export `style_markers.json`.
5. **Handoff**: Link output to **ArtistAgent** for image generation and **GDD Generator** (`gdd-generator`) for the Art & Audio Direction module.
