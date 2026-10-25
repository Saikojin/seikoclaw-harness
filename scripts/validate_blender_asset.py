#!/usr/bin/env python3
"""
validate_blender_asset.py - Deterministic 3D DCC & glTF Asset Validator

Provides comprehensive geometric, topological, transform, material, and binary
validation for 3D visual assets in the SeikoClaw Harness / Game Forge pipeline.

Can be executed in two modes:
1. Live inside Blender's bpy runtime (via execute_blender_code or blender --python)
2. Standalone CLI against exported .glb / .gltf files (zero dependencies, pure Python)
"""

import os
import sys
import json
import struct
import argparse
from typing import Dict, List, Any, Optional, Tuple

# Try importing bpy (only available inside live Blender)
try:
    import bpy
    import mathutils
    import bmesh
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


class ValidationResult:
    """Encapsulates the structured outcome of asset validation."""
    def __init__(self, target_name: str):
        self.target_name = target_name
        self.passed = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, Any] = {}

    def add_error(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def set_metric(self, key: str, value: Any) -> None:
        self.metrics[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target_name,
            "status": "PASS" if self.passed else "FAIL",
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ---------------------------------------------------------------------------
# In-Engine BPY Validation (Executes inside Blender)
# ---------------------------------------------------------------------------

def validate_bpy_mesh_object(
    obj: Any,
    max_tris: Optional[int] = None,
    allow_unapplied_scale: bool = False,
    allow_unapplied_rotation: bool = False,
    ground_tolerance: float = 0.005,
    check_manifold: bool = True,
    no_ngons: bool = False
) -> ValidationResult:
    """Validates a single Blender MESH object inside bpy runtime."""
    res = ValidationResult(target_name=obj.name)

    if obj.type != 'MESH':
        res.add_error(f"Object '{obj.name}' is of type '{obj.type}', expected 'MESH'")
        return res

    # 1. Transform & Scale Verification
    scale = obj.scale
    if not allow_unapplied_scale:
        if abs(scale.x - 1.0) > 1e-4 or abs(scale.y - 1.0) > 1e-4 or abs(scale.z - 1.0) > 1e-4:
            res.add_error(
                f"Unapplied scale: ({scale.x:.4f}, {scale.y:.4f}, {scale.z:.4f}). "
                f"Must apply transforms (bpy.ops.object.transform_apply(scale=True))."
            )

    rot = obj.rotation_euler
    if not allow_unapplied_rotation:
        if abs(rot.x) > 1e-4 or abs(rot.y) > 1e-4 or abs(rot.z) > 1e-4:
            res.add_warning(
                f"Non-zero rotation: ({rot.x:.4f}, {rot.y:.4f}, {rot.z:.4f}). "
                f"Ensure rotation is intentional or apply rotation."
            )

    # 2. Bounding Box & Ground Alignment
    if obj.bound_box:
        bbox_corners = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
        min_z = min(c.z for c in bbox_corners)
        max_z = max(c.z for c in bbox_corners)
        height = max_z - min_z
        res.set_metric("bounding_box_min_z", round(min_z, 5))
        res.set_metric("bounding_box_height", round(height, 5))

        if abs(min_z) > ground_tolerance:
            res.add_error(
                f"Asset not grounded: bounding box min-Z is {min_z:.4f}m (expected 0.0m +/- {ground_tolerance}m). "
                f"Snap lowest vertex to Z=0 ground plane."
            )

    mesh = obj.data
    # 3. Polygon & Triangle Metrics
    # Calculate triangles cleanly
    tri_count = sum(len(p.vertices) - 2 for p in mesh.polygons)
    poly_count = len(mesh.polygons)
    vert_count = len(mesh.vertices)
    res.set_metric("vertex_count", vert_count)
    res.set_metric("polygon_count", poly_count)
    res.set_metric("triangle_count", tri_count)

    if max_tris and tri_count > max_tris:
        res.add_error(f"Polygon budget exceeded: {tri_count} triangles (budget: {max_tris}).")

    # 4. Topology Invariants (Using BMesh)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Non-manifold checks
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    non_manifold_verts = [v for v in bm.verts if not v.is_manifold]
    loose_verts = [v for v in bm.verts if len(v.link_edges) == 0]
    loose_edges = [e for e in bm.edges if len(e.link_faces) == 0]

    res.set_metric("non_manifold_edges", len(non_manifold_edges))
    res.set_metric("non_manifold_verts", len(non_manifold_verts))
    res.set_metric("loose_verts", len(loose_verts))
    res.set_metric("loose_edges", len(loose_edges))

    if check_manifold and non_manifold_edges:
        res.add_error(f"Found {len(non_manifold_edges)} non-manifold edges. Mesh is not watertight.")

    if check_manifold and non_manifold_verts:
        res.add_error(f"Found {len(non_manifold_verts)} non-manifold vertices.")

    if loose_verts:
        res.add_error(f"Found {len(loose_verts)} loose/unconnected vertices.")

    if loose_edges:
        res.add_error(f"Found {len(loose_edges)} loose edges with no faces.")

    # Degenerate geometry (0-area faces, 0-length edges)
    zero_area_faces = [f for f in bm.faces if f.calc_area() < 1e-7]
    zero_length_edges = [e for e in bm.edges if e.calc_length() < 1e-6]

    if zero_area_faces:
        res.add_error(f"Found {len(zero_area_faces)} zero-area degenerate faces.")
    if zero_length_edges:
        res.add_error(f"Found {len(zero_length_edges)} zero-length degenerate edges.")

    # N-gon check
    if no_ngons:
        ngons = [f for f in bm.faces if len(f.verts) > 4]
        if ngons:
            res.add_error(f"Found {len(ngons)} n-gons (faces with > 4 vertices). Triangulate or quad-remesh.")

    bm.free()

    # 5. UV Mapping
    uv_layers = mesh.uv_layers
    res.set_metric("uv_layer_count", len(uv_layers))
    if not uv_layers or not uv_layers.active:
        res.add_warning("No active UV map found on mesh.")

    # 6. Materials & Shaders
    materials = mesh.materials
    res.set_metric("material_count", len(materials))
    if not materials or len(materials) == 0:
        res.add_warning("Mesh has no materials assigned.")
    else:
        for idx, mat in enumerate(materials):
            if mat is None:
                res.add_error(f"Material slot {idx} is empty/unassigned.")
                continue

            if not mat.use_nodes:
                res.add_warning(f"Material '{mat.name}' does not use shader nodes.")
                continue

            # Check for Principled BSDF
            principled_nodes = [n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED']
            if not principled_nodes:
                res.add_error(f"Material '{mat.name}' lacks a 'BSDF_PRINCIPLED' shader node.")
            else:
                p_node = principled_nodes[0]
                # Check for texture nodes and verify file paths
                tex_nodes = [n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE']
                for t_node in tex_nodes:
                    img = t_node.image
                    if not img:
                        res.add_error(f"Material '{mat.name}' texture node '{t_node.name}' has no image assigned.")
                    else:
                        img_path = bpy.path.abspath(img.filepath)
                        if img.source == 'FILE' and not os.path.exists(img_path) and not img.packed_file:
                            res.add_error(
                                f"Material '{mat.name}' references missing texture file: {img.filepath} "
                                f"(resolved: {img_path}). Fix texture path to avoid pink renders."
                            )

    return res


def validate_active_scene(
    max_tris: Optional[int] = None,
    allow_unapplied_scale: bool = False,
    allow_unapplied_rotation: bool = False,
    ground_tolerance: float = 0.005,
    check_manifold: bool = True,
    no_ngons: bool = False
) -> Dict[str, Any]:
    """Validates all MESH objects in the active Blender scene."""
    if not HAS_BPY:
        raise RuntimeError("validate_active_scene requires bpy runtime (run inside Blender).")

    scene = bpy.context.scene
    mesh_objects = [obj for obj in scene.objects if obj.type == 'MESH']
    
    total_tris = 0
    total_verts = 0
    all_passed = True
    object_reports = []

    for obj in mesh_objects:
        obj_report = validate_bpy_mesh_object(
            obj=obj,
            max_tris=max_tris,
            allow_unapplied_scale=allow_unapplied_scale,
            allow_unapplied_rotation=allow_unapplied_rotation,
            ground_tolerance=ground_tolerance,
            check_manifold=check_manifold,
            no_ngons=no_ngons
        )
        if not obj_report.passed:
            all_passed = False
        total_tris += obj_report.metrics.get("triangle_count", 0)
        total_verts += obj_report.metrics.get("vertex_count", 0)
        object_reports.append(obj_report.to_dict())

    overall_status = "PASS" if (all_passed and len(mesh_objects) > 0) else "FAIL"
    if len(mesh_objects) == 0:
        overall_status = "FAIL"

    return {
        "status": overall_status,
        "passed": overall_status == "PASS",
        "scene_name": scene.name,
        "mesh_object_count": len(mesh_objects),
        "total_triangle_count": total_tris,
        "total_vertex_count": total_verts,
        "objects": object_reports
    }


# ---------------------------------------------------------------------------
# Standalone glTF / GLB Binary Validation (Pure Python, No BPY Required)
# ---------------------------------------------------------------------------

def validate_glb_file(filepath: str, max_tris: Optional[int] = None) -> ValidationResult:
    """Validates a binary glTF (.glb) file against the glTF 2.0 specification."""
    res = ValidationResult(target_name=os.path.basename(filepath))

    if not os.path.exists(filepath):
        res.add_error(f"File not found: {filepath}")
        return res

    file_size = os.path.getsize(filepath)
    res.set_metric("file_size_bytes", file_size)

    if file_size < 12:
        res.add_error("File too small to contain valid glTF 2.0 header (< 12 bytes).")
        return res

    with open(filepath, "rb") as f:
        # Read 12-byte header: magic (4), version (4), length (4)
        magic, version, total_length = struct.unpack("<4sII", f.read(12))

        if magic != b"glTF":
            res.add_error(f"Invalid magic header: {magic!r}. Expected b'glTF' (0x46546C67).")
            return res

        res.set_metric("gltf_version", version)
        if version != 2:
            res.add_warning(f"Uncommon glTF version: {version}. Expected version 2.")

        if total_length != file_size:
            res.add_error(
                f"Header declared length {total_length} bytes does not match actual file size {file_size} bytes."
            )

        # Parse chunks
        chunk_index = 0
        json_data: Optional[Dict[str, Any]] = None

        while f.tell() < file_size:
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break

            chunk_len, chunk_type = struct.unpack("<I4s", chunk_header)
            chunk_bytes = f.read(chunk_len)

            if chunk_index == 0:
                # First chunk MUST be JSON (0x4E4F534A / b"JSON")
                if chunk_type != b"JSON":
                    res.add_error(f"First chunk must be JSON, found: {chunk_type!r}")
                    break
                try:
                    json_str = chunk_bytes.decode("utf-8").strip()
                    json_data = json.loads(json_str)
                except Exception as e:
                    res.add_error(f"Failed to decode or parse glTF JSON chunk: {e}")
                    break
            elif chunk_index == 1:
                # Second chunk is typically BIN (0x004E4942 / b"BIN\x00")
                if chunk_type not in (b"BIN\x00", b"BIN "):
                    res.add_warning(f"Second chunk has non-standard type: {chunk_type!r}")
                res.set_metric("bin_chunk_bytes", chunk_len)

            chunk_index += 1

    if json_data is None:
        res.add_error("glTF structure missing valid JSON content.")
        return res

    # Inspect JSON scene structure
    asset_info = json_data.get("asset", {})
    res.set_metric("generator", asset_info.get("generator", "Unknown"))

    meshes = json_data.get("meshes", [])
    materials = json_data.get("materials", [])
    accessors = json_data.get("accessors", [])

    res.set_metric("mesh_count", len(meshes))
    res.set_metric("material_count", len(materials))

    # Calculate total triangle count from accessors
    total_tris = 0
    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            indices_idx = prim.get("indices")
            if indices_idx is not None and indices_idx < len(accessors):
                acc = accessors[indices_idx]
                count = acc.get("count", 0)
                total_tris += count // 3
            else:
                # Non-indexed geometry
                pos_idx = prim.get("attributes", {}).get("POSITION")
                if pos_idx is not None and pos_idx < len(accessors):
                    acc = accessors[pos_idx]
                    count = acc.get("count", 0)
                    total_tris += count // 3

    res.set_metric("total_triangle_count", total_tris)

    if max_tris and total_tris > max_tris:
        res.add_error(f"glTF triangle count ({total_tris}) exceeds limit ({max_tris}).")

    if len(meshes) == 0:
        res.add_error("glTF contains 0 meshes.")

    return res


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic 3D DCC and glTF Asset Validator for SeikoClaw"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Path to .glb/.gltf file to validate (or omit if running inside live Blender scene)"
    )
    parser.add_argument(
        "--max-tris",
        type=int,
        default=None,
        help="Maximum allowable triangle budget"
    )
    parser.add_argument(
        "--allow-scale",
        action="store_true",
        help="Allow unapplied scale (default: False)"
    )
    parser.add_argument(
        "--allow-rotation",
        action="store_true",
        help="Allow non-zero rotation (default: False)"
    )
    parser.add_argument(
        "--no-ngons",
        action="store_true",
        help="Fail if n-gons (> 4 vertices) are present"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Force JSON output to stdout"
    )

    args = parser.parse_args()

    # Mode 1: File validation (.glb / .gltf)
    if args.target:
        if args.target.lower().endswith(".glb") or args.target.lower().endswith(".gltf"):
            report = validate_glb_file(args.target, max_tris=args.max_tris)
            print(report.to_json())
            return 0 if report.passed else 1
        else:
            print(json.dumps({"status": "FAIL", "error": f"Unsupported target format: {args.target}"}))
            return 1

    # Mode 2: Live Scene validation (Inside Blender)
    if HAS_BPY:
        scene_report = validate_active_scene(
            max_tris=args.max_tris,
            allow_unapplied_scale=args.allow_scale,
            allow_unapplied_rotation=args.allow_rotation,
            no_ngons=args.no_ngons
        )
        print(json.dumps(scene_report, indent=2))
        return 0 if scene_report["passed"] else 1

    # Neither file nor bpy available
    parser.print_help()
    print("\n[ERROR] No file specified and bpy is not available outside Blender.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
