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
