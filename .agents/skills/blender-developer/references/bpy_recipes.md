# Blender Python (bpy) Procedural Recipes for Game Development

This reference contains production-ready Python scripts for use with `execute_blender_code`.

---

## 1. Scene Initialization & Studio Lighting

Clears existing objects and creates a three-point studio lighting setup with a ground plane:

```python
import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Add Ground Plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground_Plane"

# 3. Create Studio Lights
# Key Light
bpy.ops.object.light_add(type='AREA', location=(4, -4, 5))
key = bpy.context.active_object
key.name = "Light_Key"
key.data.energy = 300
key.data.size = 2.0

# Fill Light
bpy.ops.object.light_add(type='AREA', location=(-4, -2, 3))
fill = bpy.context.active_object
fill.name = "Light_Fill"
fill.data.energy = 100
fill.data.size = 3.0

# Rim / Back Light
bpy.ops.object.light_add(type='POINT', location=(0, 4, 4))
rim = bpy.context.active_object
rim.name = "Light_Rim"
rim.data.energy = 250

# 4. Setup Camera
bpy.ops.object.camera_add(location=(0, -6, 3), rotation=(1.1, 0, 0))
cam = bpy.context.active_object
cam.name = "Main_Camera"
bpy.context.scene.camera = cam
```

---

## 2. Low-Poly Stylized Dungeon Chest (Procedural Mesh & Bevel)

Creates a stylized chest with separate lid, metal bands, and gold clasp:

```python
import bpy

# Base Box
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
chest_base = bpy.context.active_object
chest_base.name = "Chest_Base"
chest_base.scale = (1.4, 0.9, 0.7)
bpy.ops.object.transform_apply(scale=True)

# Add Bevel Modifier for stylized edge highlight
bevel = chest_base.modifiers.new(name="Stylized_Bevel", type='BEVEL')
bevel.width = 0.04
bevel.segments = 2

# Apply Wood Material
mat_wood = bpy.data.materials.new(name="M_Chest_Wood")
mat_wood.use_nodes = True
p_wood = next(n for n in mat_wood.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
p_wood.inputs["Base Color"].default_value = (0.28, 0.15, 0.08, 1.0)
p_wood.inputs["Roughness"].default_value = 0.65
chest_base.data.materials.append(mat_wood)

# Metal Trim Frame
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
trim = bpy.context.active_object
trim.name = "Chest_Trim"
trim.scale = (1.42, 0.92, 0.72)
bpy.ops.object.transform_apply(scale=True)

mat_metal = bpy.data.materials.new(name="M_Chest_Metal")
mat_metal.use_nodes = True
p_metal = next(n for n in mat_metal.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
p_metal.inputs["Base Color"].default_value = (0.12, 0.12, 0.14, 1.0)
p_metal.inputs["Metallic"].default_value = 0.85
p_metal.inputs["Roughness"].default_value = 0.35
trim.data.materials.append(mat_metal)
```

---

## 3. Automated 8-Direction Isometric Sprite Renderer

Renders the active scene from 8 isometric angles (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°) to disk for 2D game engines:

```python
import bpy
import math
import os

output_dir = "d:/DevWorkspace/GameProject/assets/sprites/character_iso"
os.makedirs(output_dir, exist_ok=True)

scene = bpy.context.scene
scene.render.resolution_x = 128
scene.render.resolution_y = 128
scene.render.film_transparent = True  # Transparent PNG background

cam = scene.camera
if not cam:
    bpy.ops.object.camera_add(location=(0, -7, 5))
    cam = bpy.context.active_object
    scene.camera = cam

# Set Orthographic Camera for pure isometric rendering
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.5

# Standard Isometric Pitch: ~54.7 degrees (math.atan(math.sqrt(2)))
pitch = math.atan(math.sqrt(2))

directions = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]
angles = [0, 45, 90, 135, 180, 225, 270, 315]

dist = 8.0

for name, deg in zip(directions, angles):
    rad = math.radians(deg)
    cam.location.x = dist * math.sin(rad)
    cam.location.y = -dist * math.cos(rad)
    cam.location.z = dist * 0.707
    cam.rotation_euler = (pitch, 0, rad)
    
    scene.render.filepath = os.path.join(output_dir, f"walk_{name}.png")
    bpy.ops.render.render(write_still=True)
```

---

## 4. Production glTF/GLB Export with PBR Materials

Exports the selected 3D object as a self-contained binary GLB for Godot, WebGL, or Unreal Engine:

```python
import bpy

def export_active_as_glb(target_filepath):
    # Ensure active object is selected
    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.context.active_object
    if not obj:
        raise ValueError("No active object to export")
    obj.select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=target_filepath,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False,
        export_yup=True
    )

# Example usage:
# export_active_as_glb("d:/DevWorkspace/GameProject/assets/models/chest.glb")
```

---

## 5. Appending / Linking External `.blend` Assets (BlendSwap Pipeline)

Appends collections, hierarchies, and objects from an external `.blend` library into the active scene, preserving parent-child rigs, selecting new items, and automatically grounding to $Z=0$:

```python
import bpy
import mathutils
from pathlib import Path

def append_blend_asset(blend_filepath, link=False, ground_to_z=True):
    blend_path = Path(blend_filepath).resolve().as_posix()
    if not Path(blend_path).exists():
        raise FileNotFoundError(f"Asset file not found: {blend_path}")

    # Deselect all objects in current scene
    bpy.ops.object.select_all(action='DESELECT')

    # 1. Inspect and load data-blocks
    with bpy.data.libraries.load(blend_path, link=link) as (data_from, data_to):
        if data_from.collections:
            # Prefer collections: preserves hierarchies, armatures, and group transforms
            data_to.collections = list(data_from.collections)
        elif data_from.objects:
            data_to.objects = list(data_from.objects)
        elif data_from.materials:
            data_to.materials = list(data_from.materials)

    # 2. Link newly loaded collections/objects to active scene collection
    appended_objects = []
    if hasattr(data_to, 'collections') and data_to.collections:
        for coll in data_to.collections:
            if coll:
                bpy.context.scene.collection.children.link(coll)
                appended_objects.extend(coll.all_objects)
    elif hasattr(data_to, 'objects') and data_to.objects:
        for obj in data_to.objects:
            if obj:
                bpy.context.scene.collection.objects.link(obj)
                appended_objects.append(obj)

    # 3. Grounding and View Selection
    if appended_objects:
        for obj in appended_objects:
            if obj:
                obj.select_set(True)

        if ground_to_z:
            mesh_objs = [o for o in appended_objects if o and o.type == 'MESH']
            if mesh_objs:
                all_min_z = []
                for obj in mesh_objs:
                    bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
                    all_min_z.append(min(corner.z for corner in bbox_corners))
                global_min_z = min(all_min_z)
                # Translate root parent objects only
                for root in [o for o in appended_objects if o and o.parent is None]:
                    root.location.z -= global_min_z

        bpy.context.view_layer.objects.active = appended_objects[0]
        print(f"Loaded {len(appended_objects)} objects from {blend_path}")
        return appended_objects

    return []

# Example usage:
# append_blend_asset("d:/DevWorkspace/SeikoClaw-Harness/assets/blendswap/chest.blend")
```

---

## 6. In-Scene DCC Validation & Punch Remediation Recipes

### A. Quick In-Scene Assertion Script (Execute via `execute_blender_code`)
```python
import bpy, bmesh, mathutils

def validate_active_model(max_tris=15000):
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        return {"status": "FAIL", "error": "No active mesh object"}

    errors = []
    
    # 1. Scale applied check
    if any(abs(s - 1.0) > 1e-4 for s in obj.scale):
        errors.append(f"Unapplied scale: {tuple(round(s, 4) for s in obj.scale)}. Run bpy.ops.object.transform_apply(scale=True)")

    # 2. Ground check
    bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    min_z = min(c.z for c in bbox)
    if abs(min_z) > 0.005:
        errors.append(f"Not grounded: min Z is {min_z:.4f}m. Lowest vertex must rest on Z=0")

    # 3. Manifold check
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    loose_verts = [v for v in bm.verts if len(v.link_edges) == 0]
    bm.free()

    if non_manifold_edges:
        errors.append(f"Mesh has {len(non_manifold_edges)} non-manifold edges")
    if loose_verts:
        errors.append(f"Mesh has {len(loose_verts)} loose vertices")

    # 4. Triangle budget
    tri_count = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    if tri_count > max_tris:
        errors.append(f"Poly count {tri_count} exceeds budget of {max_tris}")

    status = "PASS" if not errors else "FAIL"
    print(f"[{status}] Validation for '{obj.name}': {errors if errors else '0 defects'}")
    return {"status": status, "triangles": tri_count, "errors": errors}

# Run assertion
validate_active_model(max_tris=15000)
```

### B. Common Actionable Remediation Snippets

#### 1. Instant Transform & Grounding Fix
```python
import bpy, mathutils

obj = bpy.context.active_object
# Apply scale and rotation
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Snap minimum Z to 0.0
bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
min_z = min(c.z for c in bbox)
obj.location.z -= min_z
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
```

#### 2. Clean Non-Manifold Geometry & Remove Doubles
```python
import bpy, bmesh

obj = bpy.context.active_object
bm = bmesh.new()
bm.from_mesh(obj.data)

# Merge duplicate vertices within 0.1mm
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

# Recalculate face normals outward
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Delete loose isolated geometry
loose_verts = [v for v in bm.verts if len(v.link_edges) == 0]
bmesh.ops.delete(bm, geom=loose_verts, context='VERTS')

bm.to_mesh(obj.data)
bm.free()
obj.data.update()
```

#### 3. PBR Material Metallicity & Roughness Punch Fix
```python
import bpy

mat = bpy.context.active_object.active_material
if mat and mat.use_nodes:
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    # Brass/Gold: Metallic 1.0, Roughness 0.2-0.3, Golden Base Color
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.25
    bsdf.inputs["Base Color"].default_value = (0.78, 0.57, 0.22, 1.0)
```


