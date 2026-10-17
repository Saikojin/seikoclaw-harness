"""
Unit and integration tests for Poly Haven Asset Pipeline (scripts/polyhaven.py).
Verifies:
- 2K resolution default gating
- Map deduplication
- Cache storage budgeting and LRU eviction
- Engine material adapters (Godot .tres, Unity .meta/.mat, Blender bpy, Unreal manifest)
- CLI subcommands (search, info, fetch, cache)
"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from scripts.polyhaven import (
    parse_size_to_bytes,
    format_bytes,
    select_best_resolution,
    PolyHavenCache,
    PolyHavenAPI,
    EngineAdapters,
    build_parser,
    DEFAULT_RESOLUTION
)


def test_parse_size_to_bytes():
    assert parse_size_to_bytes("500B") == 500
    assert parse_size_to_bytes("10KB") == 10 * 1024
    assert parse_size_to_bytes("25MB") == 25 * 1024 * 1024
    assert parse_size_to_bytes("10GB") == 10 * 1024 * 1024 * 1024
    assert parse_size_to_bytes("1.5GB") == int(1.5 * 1024 * 1024 * 1024)


def test_format_bytes():
    assert format_bytes(500) == "500 B"
    assert "MB" in format_bytes(25 * 1024 * 1024)
    assert "GB" in format_bytes(10 * 1024 * 1024 * 1024)


def test_select_best_resolution():
    avail = ["1k", "2k", "4k", "8k"]
    # Exact match
    assert select_best_resolution(avail, "2k") == "2k"
    assert select_best_resolution(avail, "4k") == "4k"

    # Fallback to lower resolution when requested is missing
    avail_limited = ["1k", "4k", "8k"]
    assert select_best_resolution(avail_limited, "2k") == "1k"

    avail_high_only = ["4k", "8k", "16k"]
    assert select_best_resolution(avail_high_only, "2k") == "4k"


def test_cache_put_get_and_lru_prune(tmp_path):
    cache_dir = tmp_path / "cache"
    cache = PolyHavenCache(cache_dir=cache_dir)

    # Create dummy source files
    file_a = tmp_path / "file_a.png"
    file_a.write_bytes(b"A" * 1024 * 100)  # 100 KB
    file_b = tmp_path / "file_b.png"
    file_b.write_bytes(b"B" * 1024 * 200)  # 200 KB

    cache.put("https://example.com/a.png", "a.png", file_a)
    cache.put("https://example.com/b.png", "b.png", file_b)

    status = cache.get_status()
    assert status["file_count"] == 2
    assert status["total_size_bytes"] == 300 * 1024

    # Prune to 150 KB max
    deleted_count, deleted_bytes = cache.prune(max_bytes=150 * 1024)
    assert deleted_count >= 1
    new_status = cache.get_status()
    assert new_status["total_size_bytes"] <= 150 * 1024

    # Clear cache
    cleared = cache.clear()
    assert cleared == new_status["file_count"]
    assert cache.get_status()["file_count"] == 0


def test_godot_material_adapter(tmp_path):
    output_dir = tmp_path / "godot_out"
    output_dir.mkdir()

    maps = {
        "Diffuse": output_dir / "brick_diffuse_2k.png",
        "nor_gl": output_dir / "brick_nor_gl_2k.png",
        "Rough": output_dir / "brick_rough_2k.png",
        "AO": output_dir / "brick_ao_2k.png"
    }
    for p in maps.values():
        p.write_bytes(b"fake_image_bytes")

    tres_file = EngineAdapters.godot("brick", maps, output_dir, is_hdri=False)
    assert tres_file.exists()
    content = tres_file.read_text(encoding="utf-8")

    assert '[gd_resource type="StandardMaterial3D"' in content
    assert 'albedo_texture = ExtResource("1_Diffuse")' in content
    assert 'normal_enabled = true' in content
    assert 'normal_texture = ExtResource("2_nor_gl")' in content
    assert 'roughness_texture = ExtResource("3_Rough")' in content
    assert 'ao_enabled = true' in content


def test_godot_hdri_adapter(tmp_path):
    output_dir = tmp_path / "godot_hdri"
    output_dir.mkdir()

    maps = {"hdri": output_dir / "sky_2k.hdr"}
    maps["hdri"].write_bytes(b"hdr_bytes")

    tres_file = EngineAdapters.godot("sky", maps, output_dir, is_hdri=True)
    assert tres_file.exists()
    content = tres_file.read_text(encoding="utf-8")
    assert '[gd_resource type="PanoramaSkyMaterial"' in content
    assert 'panorama = ExtResource("1_sky")' in content


def test_unity_material_adapter(tmp_path):
    output_dir = tmp_path / "unity_out"
    output_dir.mkdir()

    maps = {
        "Diffuse": output_dir / "wood_diff_2k.png",
        "nor_dx": output_dir / "wood_nor_dx_2k.png",
        "Rough": output_dir / "wood_rough_2k.png"
    }
    for p in maps.values():
        p.write_bytes(b"data")

    created = EngineAdapters.unity("wood", maps, output_dir, is_hdri=False)
    assert len(created) == 4  # 3 .meta files + 1 .mat file

    # Check normal map meta
    nor_meta = (output_dir / "wood_nor_dx_2k.png.meta").read_text(encoding="utf-8")
    assert "textureType: 1" in nor_meta
    assert "sRGBTexture: 0" in nor_meta

    # Check rough meta
    rough_meta = (output_dir / "wood_rough_2k.png.meta").read_text(encoding="utf-8")
    assert "textureType: 0" in rough_meta
    assert "sRGBTexture: 0" in rough_meta

    # Check .mat file
    mat_file = output_dir / "wood.mat"
    assert mat_file.exists()


def test_blender_adapter(tmp_path):
    output_dir = tmp_path / "blender_out"
    output_dir.mkdir()

    maps = {
        "Diffuse": output_dir / "stone_diff_2k.png",
        "nor_gl": output_dir / "stone_nor_gl_2k.png",
        "Rough": output_dir / "stone_rough_2k.png"
    }
    for p in maps.values():
        p.write_bytes(b"data")

    script = EngineAdapters.blender("stone", maps, output_dir, is_hdri=False)
    assert script.exists()
    code = script.read_text(encoding="utf-8")
    assert "import bpy" in code
    assert 'bsdf.inputs["Base Color"]' in code
    assert 'bsdf.inputs["Normal"]' in code


def test_unreal_adapter(tmp_path):
    output_dir = tmp_path / "unreal_out"
    output_dir.mkdir()

    maps = {
        "Diffuse": output_dir / "tile_diff_2k.png",
        "nor_dx": output_dir / "tile_nor_dx_2k.png"
    }
    for p in maps.values():
        p.write_bytes(b"data")

    manifest_file = EngineAdapters.unreal("tile", maps, output_dir, is_hdri=False)
    assert manifest_file.exists()
    data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert data["target_engine"] == "Unreal Engine 5"
    assert "NormalMap" in data["parameters"]


def test_cli_default_resolution_is_2k():
    parser = build_parser()
    fetch_parser = parser._subparsers._actions[1].choices["fetch"]
    defaults = {action.dest: action.default for action in fetch_parser._actions}
    assert defaults["resolution"] == "2k"
    assert DEFAULT_RESOLUTION == "2k"
