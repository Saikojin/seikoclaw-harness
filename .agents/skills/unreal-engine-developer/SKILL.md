---
name: unreal-engine-developer
description: Live Unreal Engine editor automation, Blueprint authoring, and MCP bridge orchestration.
author: Saikojin (SeikoClaw - Game Forge)
---

# Unreal Engine Developer & Editor MCP Orchestrator

The **Unreal Engine Developer** skill provides autonomous, bi-directional control over a live running Unreal Engine editor instance (UE 5.5, 5.7, 5.8+) via the Model Context Protocol (MCP). It translates high-level game architecture, design documents, and mathematical balance models directly into live Unreal assets, level geometry, and wired Blueprint graphs without manual editor friction.

---

## 1. System Architecture & Connection Protocol

```mermaid
flowchart TD
    subgraph Agent["AI Agent (Antigravity / Claude / SeikoClaw)"]
        direction TB
        Skill["unreal-engine-developer skill"]
        Tools["MCP Client ('unreal' server)"]
    end

    subgraph PythonBridge["Python MCP Server (D:\DevWorkspace\unreal-mcp\Python)"]
        FastMCP["FastMCP Server (stdio)"]
        SocketClient["TCP Socket Client"]
    end

    subgraph UnrealEditor["Unreal Engine Editor (Running Instance)"]
        Subsystem["UUnrealMCPBridge (UEditorSubsystem)"]
        TCPServer["TCP Listener (127.0.0.1:55557)"]
        EditorAPIs["Actor / Blueprint / Graph Subsystems"]
    end

    Skill --> Tools
    Tools <--> FastMCP
    FastMCP <--> SocketClient
    SocketClient <-->|TCP: 55557| TCPServer
    TCPServer <--> Subsystem
    Subsystem <--> EditorAPIs
```

### Connection Requirements:
1. **Unreal Editor Must Be Running**: The project (`.uproject`) must be open in the Unreal Editor.
2. **UnrealMCP Plugin Active**: The `UnrealMCP` plugin must be present in the project's `Plugins/UnrealMCP` folder (or installed as an engine plugin) and enabled.
3. **TCP Listener**: Upon editor startup, `UUnrealMCPBridge` automatically initializes and listens on `127.0.0.1:55557`.
4. **Agent MCP Server**: The `unreal` MCP server is registered in `~/.gemini/antigravity/mcp_config.json` via `uv run unreal_mcp_server.py`.

---

## 2. Core Tool Reference

All Unreal MCP tools are invoked via the `unreal` MCP server:

### A. Level Layout & Actor Management
- `find_actors_by_name(name)`: Query if an actor exists before creating or transforming it.
- `get_actors_in_level()`: List all actors currently populated in the active persistent level.
- `create_actor(name, type, location, rotation, scale)`: Spawn actors (`CUBE`, `SPHERE`, `PLANE`, `CYLINDER`, `CONE`, `CAMERA`, `LIGHT`, `POINT_LIGHT`, `SPOT_LIGHT`).
- `set_actor_transform(name, location, rotation, scale)`: Precision placement in Unreal units (cm) and degrees.
- `get_actor_properties(name)`: Read transform, tags, and actor properties.
- `delete_actor(name)`: Clean up obsolete or temporary actors.

### B. Blueprint Construction & Assembly
- `create_blueprint(name, parent_class)`: Generate new Blueprint classes (parent classes: `Actor`, `Pawn`, `Character`, `GameModeBase`).
- `add_component_to_blueprint(blueprint_name, component_type, component_name, location, rotation, scale)`: Add components (`StaticMeshComponent`, `BoxComponent`, `SphereComponent`, `CameraComponent`, `SpringArmComponent`).
- `set_static_mesh_properties(blueprint_name, component_name, mesh_path, material_path)`: Bind 3D mesh assets and materials.
- `set_physics_properties(blueprint_name, component_name, simulate_physics, gravity_enabled, mass, linear_damping, angular_damping)`: Configure rigid-body physics.
- `set_pawn_properties(blueprint_name, auto_possess_player, use_controller_rotation_yaw, ...)`: Configure player controller possession and rotation inheritance.
- `set_blueprint_property(blueprint_name, property_name, property_value)`: Update default class variable values.
- `compile_blueprint(blueprint_name)`: **Mandatory**: Recompile the Blueprint to bake changes.
- `spawn_blueprint_actor(blueprint_name, actor_name, location, rotation, scale)`: Spawn an instance of the compiled Blueprint into the level.

### C. Visual Scripting & Node Graph Wiring
- `add_blueprint_event_node(blueprint_name, event_type, node_position)`: Add lifecycle hooks (`BeginPlay`, `Tick`, custom events).
- `add_blueprint_input_action_node(blueprint_name, action_name, node_position)`: Add input execution pins.
- `add_blueprint_function_node(blueprint_name, target, function_name, params, node_position)`: Add callable function nodes (`PrintString`, `SetActorLocation`, `ApplyDamage`).
- `connect_blueprint_nodes(blueprint_name, source_node_id, source_pin, target_node_id, target_pin)`: Connect execution or data lines between graph nodes.
- `add_blueprint_variable(blueprint_name, variable_name, variable_type, default_value, is_exposed)`: Declare typed variables (`Boolean`, `Integer`, `Float`, `Vector`, `String`).
- `create_input_mapping(action_name, key, input_type)`: Bind keyboard/mouse/gamepad inputs to action names.
- `find_blueprint_nodes(blueprint_name, node_type, event_type)`: Inspect node IDs in the event graph for connection wiring.

### D. Viewport & Camera Diagnostics
- `focus_viewport(target, location, distance, orientation)`: Frame target actors or locations in the active editor camera viewport.

---

## 3. Production Pipelines

### Pipeline 1: Full Game Forge Integration (`game-forge` Stage E)
When executing Stage E of `/game-forge` targeting Unreal Engine:
1. **Ingest Game Design & Specs**: Read `docs/design/GDD.md` and `docs/design/micro_slice.md`.
2. **Scaffold World Geometry**: Spawn arena bounds, collision boundaries, player spawn point, and environment lighting using `create_actor` and `set_actor_transform`.
3. **Build Player Character**:
   - `create_blueprint(name="BP_PlayerCharacter", parent_class="Character")`
   - Add camera and spring arm components.
   - Configure Enhanced Input mappings using `create_input_mapping`.
   - Wire movement logic into the Event Graph via `add_blueprint_function_node` and `connect_blueprint_nodes`.
   - `compile_blueprint("BP_PlayerCharacter")`
4. **Build Enemy Entities**:
   - Create `BP_EnemyBase` with static mesh/skeletal mesh and collision box.
   - Add health, attack damage, and aggro radius variables via `add_blueprint_variable`.
   - Wire damage reception logic (`Event AnyDamage` -> update health).
   - Compile and spawn into combat patrol zones.
5. **Compile & Spawn**: Place instances into the scene and frame them with `focus_viewport`.

### Pipeline 2: Sorceress 3D Asset Pipeline
Connect assets generated by the [`sorceress`](file:///C:/Users/saiko/.gemini/config/skills/sorceress/SKILL.md) MCP server directly into Unreal Engine:
```mermaid
flowchart LR
    S1["sorceress_generate_3d_model"] --> S2["sorceress_rig_3d_model"]
    S2 --> S3["sorceress_generate_animation"]
    S3 --> UE1["Unreal Python Ingestion Script"]
    UE1 --> UE2["Content/Characters Asset"]
    UE2 --> UE3["add_component_to_blueprint / set_static_mesh_properties"]
```
1. Generate model with `sorceress_generate_3d_model` and download `.glb`/`.fbx`.
2. Ingest into Unreal `/Game/Content/` using the Unreal Python scripting module:
   ```python
   import unreal
   task = unreal.AssetImportTask()
   task.filename = "D:/path/to/character.fbx"
   task.destination_path = "/Game/Characters"
   unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
   ```
3. Assign imported mesh to the character Blueprint using `set_static_mesh_properties`.

### Pipeline 3: Systems Modeler Balance Synchronization
Connect mathematical models from [`game-systems-modeler`](file:///d:/DevWorkspace/SeikoClaw-Harness/.agents/skills/game-systems-modeler/SKILL.md) (`docs/design/balance.json`):
1. Parse authoritative combat formulas (TTK, Damage scaling, XP curves).
2. Generate Unreal `DataTable` JSON / CSV schemas matching `FCombatBalanceRow` or `FProgressionRow`.
3. Import into Unreal DataTables or populate Blueprint default properties via `set_blueprint_property`.

---

## 4. Execution Rules & Best Practices

1. **Existence Verification First**:
   - Always run `find_actors_by_name` before modifying or deleting an actor.
   - Always verify if a Blueprint already exists before calling `create_blueprint`.
2. **Strict Compilation Discipline**:
   - Every modification to components, variables, or graph nodes leaves the Blueprint in a dirty state.
   - **Always call `compile_blueprint(blueprint_name)`** immediately after completing a batch of graph or component edits before attempting to spawn it.
3. **Coordinate Conventions**:
   - Unreal Engine units are **centimeters** ($100\text{ units} = 1\text{ meter}$).
   - World coordinates: $+X$ is Forward, $+Y$ is Right, $+Z$ is Up.
   - Rotations: `[Pitch, Yaw, Roll]` in degrees.
4. **Node Layout Discipline**:
   - Provide spaced grid positions for `node_position: [X, Y]` when adding event nodes and function nodes (e.g. step by $+250$ on $X$ for sequential flow) so graphs remain clean for human designers.

---

---

## 5. Production Guardrails & Gameplay Architecture Patterns

The following engineering rules address critical failure modes identified during production flight simulation builds:

### A. Chaos Physics & Projectile Collision Discipline
- **Rule:** High-speed micro-projectiles spawned by or near pawns must **never have rigid body collision enabled**.
  ```cpp
  // WWPProjectile constructor
  CollisionSphere->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  ```
- **Rationale:** In Chaos Physics, overlapping collision volumes between fast-moving projectiles and complex vehicle/skeletal meshes generate astronomical depenetration impulses, flinging pawns at Mach 1.5 (e.g. 1200 mph physics spikes) and destroying joints/spars.
- **Implementation:** Use swept line traces (`SweepMultiByChannel` / `LineTraceSingleByChannel`) exclusively, and always add `QueryParams.AddIgnoredActor(GetOwner())` to guarantee 3rd-person camera traces never damage the shooter's own airframe.

### B. Enhanced Input Debouncing & Single-Frame Latch Protocol
- **Rule:** Never poll hardware key state in `PlayerTick()` while simultaneously listening to an Enhanced Input Action mapping for discrete state toggles (Pause menu, camera view mode, landing gear).
- **Rationale:** Processing the same keypress across both listeners causes a 0ms double-execution on the exact same frame (`GFrameCounter`), toggling open and immediately closed. To the player, the button behaves as a dead key.
- **Implementation:** Always guard toggles with a frame-counter latch:
  ```cpp
  void AMyPlayerController::TogglePauseMenu()
  {
      if (LastPauseToggleFrame == GFrameCounter) return;
      LastPauseToggleFrame = GFrameCounter;
      // Toggle menu logic...
  }
  ```

### C. Audio Submix & Master Volume Synchronization
- **Rule:** Modifying a local volume variable in PlayerController or GameInstance does **not** attenuate engine audio.
- **Implementation:** Interface directly with Unreal's audio engine via transient volume scaling:
  ```cpp
  if (GEngine && GEngine->GetMainAudioDevice())
  {
      GEngine->GetMainAudioDevice()->SetTransientPrimaryVolume(NewVolumeScalar);
  }
  ```
  Ensure all procedural sound components or MetaSound synthesizers synchronize their attenuation and volume multipliers when settings cycle.

### D. Camera-to-Muzzle Aim Convergence & Momentum Projection
- **Rule:** Gun muzzle traces in 3D combat games must never fire along raw socket forward vectors without camera convergence.
- **Implementation:**
  1. **Two-Point Convergence:** Raycast forward 600m from the active camera viewpoint through the screen-center reticle into world space. Calculate muzzle trajectory vector pointing from physical gun muzzle directly toward that hit coordinate.
  2. **Forward Momentum Inheritance:** When transferring vehicle velocity to bullets, project speed strictly along the barrel forward vector (`FVector::DotProduct(AircraftVelocity, MuzzleDir) * MuzzleDir`). Never add raw transverse velocity vectors, which blow bullets sideways during banked turns.

### E. Asset Coordinate Standard & Pre-Flight DCC Alignment
- **Rule:** Unreal Engine world space is $+X$ Forward, $+Y$ Right, $+Z$ Up.
- **Implementation:** Blender and Maya DCC assets default to $+Y$ or $-Y$ forward. Always inspect FBX import options and enforce a $-90^\circ$ yaw adjustment during import if models fly sideways ("crabbing"), if cockpit cameras stare into wing struts, or if propellers spin on the side of the fuselage.

### F. Packaging Hygiene, Shipping Config & PDB Stripping
- **Rule:** Never distribute development packages with unstripped debug symbol databases.
- **Implementation:**
  1. Build using `-clientconfig=Shipping` to strip Vulkan/D3D debug validation layers and reduce monolithic binary sizes by ~75%.
  2. In Inno Setup scripts, explicitly exclude symbol databases:
     ```pascal
     Source: "..\Saved\Package\Windows\*"; DestDir: "{app}"; Excludes: "*.pdb,*.log,*.obj,*.tmp"; Flags: ignoreversion recursesubdirs createallsubdirs
     ```
  3. In `Config/DefaultGame.ini`, disable `bCookAll=True` and specify `+MapsToCook=(FilePath="...")` to avoid packaging unreferenced test assets.
  4. Disable unused heavy plugins in `.uproject` (e.g. `ChaosVehiclesPlugin`, `NNERuntimeORT`, `EditorScriptingUtilities`).

### G. Day-One 1-Click Multiplayer Launchers
- **Rule:** Every multiplayer-enabled Unreal project must generate 1-click batch scripts in the packaged directory:
  1. `Launch_Local_2Player_Duel.bat`: Spawns two windowed instances side-by-side (`1280x720`) connecting via `127.0.0.1` for instant single-machine testing.
  2. `Launch_Host_ListenServer.bat`: Hosts on UDP port 7777 (`Map?listen -WINDOWED -ResX=1600 -ResY=900`).
  3. `Launch_Join_LAN.bat`: Prompts for host IP and connects.

---

## 6. Troubleshooting & Common Failure Modes

| Symptom | Root Cause | Remediation |
| :--- | :--- | :--- |
| **`ConnectionRefusedError: [WinError 10061]`** | Unreal Editor is closed or plugin not initialized | Open `.uproject` in Unreal Editor. Check that `UnrealMCP` plugin is enabled in `Edit > Plugins`. |
| **`Socket timeout during receive`** | Editor frozen in heavy compile or modal dialog open | Dismiss blocking modal dialogs in editor viewport; check `Saved/Logs` in project root. |
| **Vehicle speed jumps to 1200 mph (Mach 1.5) & auto-resets** | Chaos depenetration explosion from rigid bullet colliding with own pawn | Set projectile collision to `NoCollision`; use swept raycasts with `AddIgnoredActor(Owner)`. |
| **Escape or Gamepad Start fails to open pause menu** | Double-trigger on exact same frame (Action mapping + Tick polling) | Implement `if (LastPauseToggleFrame == GFrameCounter) return;` latch in PlayerController. |
| **Master volume controls do not change sound levels** | Setting variable modified without calling Unreal audio device | Call `FAudioDevice::SetTransientPrimaryVolume(Volume)` or apply SoundClass mix override. |
| **Bullets veer wildly sideways during banked turns** | Raw aircraft velocity vector added to projectile velocity | Project velocity along barrel forward vector: `FVector::DotProduct(Vel, Dir) * Dir`. |
| **Aircraft flies sideways ("crabbing") or camera looks into strut** | FBX coordinate mismatch (+Y forward in DCC vs +X forward in UE) | Re-import FBX with Yaw offset `-90.0°` to align nose with Unreal $+X$ forward axis. |
| **Inno Setup compilation fails with Error 32** | Output installer executable is locked by running process | Auto-increment version (e.g. `v1.1`) or terminate hanging installer tasks before compiling. |
| **Packaged game occupies ~1 GB on disk** | Visual Studio PDB symbols (320+ MB) and unused plugins included | Add `Excludes: "*.pdb,*.log"` in Inno Setup; compile with `-clientconfig=Shipping`. |

