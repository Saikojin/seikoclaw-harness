"""
Test Suite: Parametric Topdown Pixel Architecture Integration
Validates CLI wrapper, recipe replay, Godot prefab export, and atlas baking.
"""

import os
import shutil
from pathlib import Path
import pytest
from scripts import topdown_architecture
from scripts import bake_topdown_atlas

TEST_OUT_DIR = Path("tests/out")

@pytest.fixture(scope="session", autouse=True)
def setup_test_dir():
    TEST_OUT_DIR.mkdir(parents=True, exist_ok=True)
    yield
    # Cleanup generated test directories
    # shutil.rmtree(TEST_OUT_DIR, ignore_errors=True)

def test_schema_introspection():
    schema = topdown_architecture.get_schema()
    assert schema.get("tool") == "topdown-building-studio-cli"
    assert "styles" in schema
    assert len(schema["styles"]) >= 10
    assert "jiangnan" in schema["styles"]
    assert "forest" in schema["styles"]
    assert "types" in schema
    assert len(schema["types"]) >= 46
    assert "inn" in schema["types"]
    assert "house" in schema["types"]

def test_render_single_and_inspect():
    out_file = TEST_OUT_DIR / "test_inn.png"
    res = topdown_architecture.render(
        style="forest",
        building_type="inn",
        out=out_file,
        pitch=45,
        dirs=1,
        no_aa=True
    )
    assert res.get("ok") is True
    assert out_file.exists()
    assert out_file.stat().st_size > 0

    # Inspect embedded metadata
    meta = topdown_architecture.inspect_png(out_file)
    assert meta.get("ok") is True
    assert meta.get("style") == "forest"
    assert meta.get("type") == "inn"
    assert "params" in meta
    assert meta["params"]["floors"] == 2

def test_render_multi_direction_sheet():
    out_dir = TEST_OUT_DIR / "sheet_test"
    res = topdown_architecture.render(
        style="jiangnan",
        building_type="house",
        out=out_dir,
        dirs=4,
        sheet=True
    )
    assert res.get("ok") is True
    sheet_png = out_dir / "sheet.png"
    assert sheet_png.exists()
    assert (out_dir / "dir_0.png").exists()
    assert (out_dir / "dir_3.png").exists()

def test_godot_prefab_export():
    godot_proj = TEST_OUT_DIR / "dummy_godot"
    godot_proj.mkdir(parents=True, exist_ok=True)
    (godot_proj / "project.godot").write_text("; Godot Project Config\nconfig_version=5\n", encoding="utf-8")

    preview_png = TEST_OUT_DIR / "godot_preview.png"
    res = topdown_architecture.render(
        style="forest",
        building_type="inn",
        out=preview_png,
        godot_project=godot_proj,
        godot_texture="res://prefabs/inn.png",
        godot_prefab="res://prefabs/inn.tscn"
    )
    assert res.get("ok") is True

    prefab_tscn = godot_proj / "prefabs" / "inn.tscn"
    prefab_png = godot_proj / "prefabs" / "inn.png"

    assert prefab_tscn.exists(), "Godot .tscn file was not created"
    assert prefab_png.exists(), "Godot trimmed texture PNG was not created"

    content = prefab_tscn.read_text(encoding="utf-8")
    assert "[gd_scene" in content
    assert 'type="StaticBody2D"' in content
    assert 'type="CollisionPolygon2D"' in content
    assert 'type="Sprite2D"' in content
    assert 'type="Area2D"' in content
    assert 'res://prefabs/inn.png' in content

def test_bake_topdown_atlas_pil():
    atlas_png = TEST_OUT_DIR / "test_baked_atlas.png"
    bake_topdown_atlas.bake_with_pil(str(atlas_png), resolution=512)
    assert atlas_png.exists()

    report = topdown_architecture.check_atlas(atlas_png)
    assert report.get("ok") is True
    assert report.get("size") == 512
    assert report.get("cell") == 128
    assert len(report.get("errors", [])) == 0
    assert len(report.get("roles", [])) == 16
