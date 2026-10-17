# Session Handoff: Poly Haven Asset Pipeline Integration

## 📌 Context & Objective
The user requested an architectural plan and handoff to integrate the [Poly Haven API](https://api.polyhaven.com/) into the `SeikoClaw-Harness` project. Key requirements:
1. **Disk Storage Discipline**: Workstation has limited free storage ("hundreds of gigs free, don't need hundreds of gigs"). The entire Poly Haven library across all tiers spans **8.43 TB (178,232 files)**.
2. **2K Resolution Default**: All queries and downloads must default to **2K resolution tier assets** (~10–25 MB per texture set or ~5–15 MB per HDRI), with on-demand capability to fetch larger (4K, 8K, 16K) when requested for hero assets.
3. **Cross-Engine Connections**: Direct bridge into `blender-developer` (Blender MCP), `godot-developer`, `unity-developer`, and `unreal-developer`.

---

## 🏛️ Architectural Decisions & Created Specs
- **ADR Created**: [docs/adr/0003-polyhaven-asset-pipeline.md](file:///D:/DevWorkspace/SeikoClaw-Harness/docs/adr/0003-polyhaven-asset-pipeline.md)
  - Enforces 2K default resolution policy.
  - Dictates zero-external-dependency CLI fetcher `scripts/polyhaven.py`.
  - Details engine-specific normal map conventions (OpenGL `nor_gl` for Godot/Blender, DirectX `nor_dx` for Unity/Unreal).
- **Master Plan Created**: [docs/POLYHAVEN_INTEGRATION_PLAN.md](file:///D:/DevWorkspace/SeikoClaw-Harness/docs/POLYHAVEN_INTEGRATION_PLAN.md)
  - Detailed system architecture diagram.
  - CLI command specifications (`search`, `info`, `fetch`, `cache`).
  - Phased roadmap with `[GATE: QA]` verification checkpoints.

---

## 📋 Ready Frontier Execution Checklist (Completed Milestones)

### Phase 1: Implement Core CLI Tool (`scripts/polyhaven.py`)
- [x] Implement `scripts/polyhaven.py` with:
  - `search` endpoint: `https://api.polyhaven.com/search?q={query}&t={type}`
  - `info` endpoint: `https://api.polyhaven.com/files/{id}`
  - `fetch` command:
    - Default `--resolution 2k`
    - Selective download: only pull specified map formats (avoids fetching redundant `.exr` + `.png` + `.jpg`)
    - `--target` adapter flags: `raw`, `godot`, `unity`, `unreal`, `blender`
  - `cache` manager: LRU eviction with `--max-size 10GB`
- [x] **[GATE: QA]**: Executed `python scripts/polyhaven.py fetch "brown_planks_03" --resolution 2k` and verified download directory is **24.14 MB** (under 30 MB threshold).

### Phase 2: Author Skill Specification
- [x] Created `.agents/skills/polyhaven-assets/SKILL.md` following SeikoClaw skill authoring standards.
- [x] Updated central router `.agents/skills/seikoclaw-harness/SKILL.md` (indexed under Section 1: Game Development & Visual Parity).
- [x] **[GATE: QA]**: Executed `python scripts/eval_skill_routing.py --check-lint` and verified YAML frontmatter schema compliance across all 94 skills.

### Phase 3: Engine Adapters Implementation
- [x] Added Godot `.tres` `StandardMaterial3D` and `PanoramaSkyMaterial` generator (auto-selects `nor_gl`).
- [x] Added Unity `.meta` texture importer generator (sets Normal Map flag, unchecks sRGB for linear masks, auto-selects `nor_dx`).
- [x] Added Blender MCP helper and companion `setup_material.py` linking downloaded textures to `Principled BSDF`.
- [x] Added Unreal Engine `material_manifest.json` adapter mapping `nor_dx` and PBR texture channels.
- [x] **[GATE: QA]**: Verified Godot `.tres`, Unity `.meta`/`.mat`, and Blender `setup_material.py` generated cleanly.

### Phase 4: Benchmark & Evaluation Suite
- [x] Added 8 routing test queries to `evals/routing/routing_cases.json` (achieved 50/50 - 100% routing accuracy).
- [x] Authored unit tests in `tests/test_polyhaven.py` (10/10 tests passed).
- [x] **[GATE: QA]**: Executed `python scripts/eval_skill_routing.py --detect-collisions` ensuring zero unexpected collisions (pairwise similarity < 0.65 against all skills). Run full pytest suite (56/56 passed).

### Phase 5: Global Antigravity Integration
- [x] Synchronized `polyhaven-assets` to Antigravity global skills directory `~/.gemini/config/skills/polyhaven-assets/`.
- [x] Verified discovery via `python scripts/export_skills.py --harness antigravity` and `python seikoclaw.py sync-global`.

---

## 🔍 Verification Commands for Incoming Agent
```bash
# 1. Run SeikoClaw system diagnostics
python seikoclaw.py doctor

# 2. Check skill routing & collisions
python scripts/eval_skill_routing.py --check-lint --detect-collisions

# 3. Test Poly Haven CLI after implementation
python scripts/polyhaven.py search "brick" --type textures
python scripts/polyhaven.py info "brick_wall_001"
python scripts/polyhaven.py fetch "brick_wall_001" --resolution 2k --target godot
```
