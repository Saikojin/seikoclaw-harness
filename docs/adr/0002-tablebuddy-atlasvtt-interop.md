# 2. Tablebuddy & Atlas VTT Interoperability Architecture

We decided to establish bidirectional interoperability between Tablebuddy and the Atlas VTT / Obsidian ecosystem. This is achieved by creating a standalone Python ingestion engine in Tablebuddy that parses Universal VTT (`.uvtt`), Atlas scenes (`.atlasmap`), and modular campaign archives (`.atlas-collection.zip`), mapping them into Tablebuddy's per-campaign SQLite schema and React/PixiJS renderer.

## Context

Tablebuddy is a standalone virtual tabletop utilizing a FastAPI backend and a hardware-accelerated React/PixiJS frontend. Tablebuddy's roadmap includes Markdown Journals/Handouts (Phase 13) and Rulebook Ingestion (Phase 14/15). Atlas VTT is an open-source, local-first VTT operating within Obsidian that packages battlemaps, notes, statblocks, and tokens into `.atlasmap` and `.atlas-collection.zip` files.

Both systems share identical rendering primitives (React + PixiJS), but serve complementary gameplay modes:
- **Obsidian / Atlas VTT**: Ideal for solitary GM worldbuilding, session preparation, note linking, and local second-screen play.
- **Tablebuddy**: Ideal for live remote multiplayer sessions featuring WebSockets, dynamic RBAC, token ownership locks, and zero-config Cloudflare tunnels.

## Decisions

1. **Schema Mapping**:
   - `.atlasmap` scenes map directly to Tablebuddy's `maps` table (`name`, `file_path`, `grid_size`, `grid_type`).
   - `objects.tokens` map to Tablebuddy's `tokens` table (`t_id`, `name`, `x`, `y`, `size`, `image_url`, `stats_json`).
   - `objects.pins` and collection Markdown notes map to Tablebuddy's `journals` table (`title`, `content`, `is_public`).
2. **Universal VTT (.uvtt) Ingestion**:
   - Implement a pure Python parser `parse_uvtt()` that extracts base64 map images, grid geometry (`resolution.pixels_per_grid`), walls (`line_of_sight`), portals (`portals`), and light emitters (`lights`).
3. **Modular Collection Import (`.atlas-collection.zip`)**:
   - Provide `import_atlas_collection(zip_path, campaign_id)` to unpack scenes, extract WebP assets to `Tablebuddy_Data/campaigns/{id}/`, register tokens, and import creature statblocks into Tablebuddy's `entities` and `tokens` tables.
4. **Renderer Optimization**:
   - Adopt Atlas VTT's memory-bounded image worker design pattern (`OffscreenCanvas` in Web Workers) to prevent main-thread freezing during high-resolution map decoding in Tablebuddy's React frontend.

## Consequences

- Tablebuddy can instantly import turnkey modules like Cairn v2 (`atlas-vtt-cairn`) and Dungeondraft maps without manual recreation.
- GMs can use Obsidian for writing lore and dungeon prep, then export or sync their campaign directly to Tablebuddy for multiplayer game nights.
- Eliminates the need to develop a closed, proprietary note system in Tablebuddy, standardizing on Obsidian Flavored Markdown.
