Statu.agents/skills/.

### Key Architectural Decisions Made:
1. **Multi-Input Ingestion**: Accepts local image/audio files, web URLs, shorthand game title references ("Darkest Dungeon style"), and descriptive text prompts.
2. **Dual Output & ArtistAgent RAG Link**: Generates interactive HTML galleries (`mood_board.html`) AND extracts structured `style_markers.json` (Form/Anatomy, Color Theory, Shading/Lighting) to directly feed ArtistAgent's RAG prompt injection pipeline.
3. **Strict Project Style Isolation**: Enforces project-level style subsets (`Adberrain` Dark Fantasy vs `Tablebuddy` VTT UI) to prevent style bleed per `project_vision.md`.

