"""
test_blender_validator.py - Comprehensive Unit & Integration Tests for Blender Asset Validation
"""

import os
import struct
import json
import tempfile
import pytest
from PIL import Image

from scripts.validate_blender_asset import (
    ValidationResult,
    validate_glb_file,
    HAS_BPY
)
from scripts.fetch_asset_references import (
    clean_query_keywords,
    build_sxs_composite
)


class TestValidationResult:
    def test_default_state(self):
        res = ValidationResult("test_asset")
        assert res.passed is True
        assert len(res.errors) == 0
        assert len(res.warnings) == 0
        d = res.to_dict()
        assert d["status"] == "PASS"

    def test_error_sets_failure(self):
        res = ValidationResult("test_asset")
        res.add_error("Scale unapplied")
        assert res.passed is False
        assert len(res.errors) == 1
        d = res.to_dict()
        assert d["status"] == "FAIL"

    def test_warning_keeps_pass(self):
        res = ValidationResult("test_asset")
        res.add_warning("Uncommon material name")
        assert res.passed is True
        assert len(res.warnings) == 1
        d = res.to_dict()
        assert d["status"] == "PASS"


class TestGLBValidator:
    def _create_synthetic_glb(
        self,
        json_content: dict,
        bin_content: bytes = b"",
        magic: bytes = b"glTF",
        version: int = 2,
        corrupt_length: bool = False
    ) -> bytes:
        """Helper to assemble a binary glTF 2.0 file in memory."""
        json_str = json.dumps(json_content)
        # Pad JSON to 4-byte boundary with spaces (0x20)
        padding_len = (4 - (len(json_str) % 4)) % 4
        json_bytes = json_str.encode("utf-8") + (b" " * padding_len)

        # Pad BIN to 4-byte boundary with 0x00
        bin_pad_len = (4 - (len(bin_content) % 4)) % 4
        padded_bin = bin_content + (b"\x00" * bin_pad_len)

        chunk0_header = struct.pack("<II", len(json_bytes), 0x4E4F534A)  # "JSON"
        chunk0 = chunk0_header + json_bytes

        chunk1 = b""
        if padded_bin:
            chunk1_header = struct.pack("<II", len(padded_bin), 0x004E4942)  # "BIN\x00"
            chunk1 = chunk1_header + padded_bin

        total_length = 12 + len(chunk0) + len(chunk1)
        if corrupt_length:
            header_length = total_length + 100
        else:
            header_length = total_length

        header = struct.pack("<4sII", magic, version, header_length)
        return header + chunk0 + chunk1

    def test_valid_minimal_glb(self, tmp_path):
        manifest = {
            "asset": {"version": "2.0", "generator": "TestGLBGenerator"},
            "meshes": [
                {
                    "primitives": [
                        {
                            "attributes": {"POSITION": 0},
                            "indices": 1
                        }
                    ]
                }
            ],
            "accessors": [
                {"count": 8, "type": "VEC3"},     # Positions
                {"count": 12, "type": "SCALAR"}   # Indices: 12 indices = 4 triangles
            ]
        }
        glb_bytes = self._create_synthetic_glb(manifest)
        filepath = os.path.join(tmp_path, "cube.glb")
        with open(filepath, "wb") as f:
            f.write(glb_bytes)

        report = validate_glb_file(filepath, max_tris=10)
        assert report.passed is True
        assert report.metrics["total_triangle_count"] == 4
        assert report.metrics["gltf_version"] == 2
        assert report.metrics["mesh_count"] == 1

    def test_exceed_triangle_budget(self, tmp_path):
        manifest = {
            "asset": {"version": "2.0"},
            "meshes": [
                {
                    "primitives": [{"indices": 0}]
                }
            ],
            "accessors": [
                {"count": 300, "type": "SCALAR"}  # 300 indices = 100 triangles
            ]
        }
        glb_bytes = self._create_synthetic_glb(manifest)
        filepath = os.path.join(tmp_path, "dense.glb")
        with open(filepath, "wb") as f:
            f.write(glb_bytes)

        report = validate_glb_file(filepath, max_tris=50)
        assert report.passed is False
        assert any("exceeds limit" in err for err in report.errors)
        assert report.metrics["total_triangle_count"] == 100

    def test_bad_magic_header(self, tmp_path):
        manifest = {"asset": {"version": "2.0"}}
        glb_bytes = self._create_synthetic_glb(manifest, magic=b"BAD!")
        filepath = os.path.join(tmp_path, "corrupt.glb")
        with open(filepath, "wb") as f:
            f.write(glb_bytes)

        report = validate_glb_file(filepath)
        assert report.passed is False
        assert any("Invalid magic header" in err for err in report.errors)

    def test_corrupt_file_length(self, tmp_path):
        manifest = {"asset": {"version": "2.0"}}
        glb_bytes = self._create_synthetic_glb(manifest, corrupt_length=True)
        filepath = os.path.join(tmp_path, "mismatch.glb")
        with open(filepath, "wb") as f:
            f.write(glb_bytes)

        report = validate_glb_file(filepath)
        assert report.passed is False
        assert any("does not match actual file size" in err for err in report.errors)

    def test_missing_file(self):
        report = validate_glb_file("non_existent_file.glb")
        assert report.passed is False
        assert any("File not found" in err for err in report.errors)


class TestReferenceAcquisitionAndSxS:
    def test_clean_keywords_extraction(self):
        prompt = "Create a detailed medieval iron-banded wooden treasure chest with brass latch"
        keywords = clean_query_keywords(prompt)
        # Should drop 'create', 'a', 'detailed', 'with' and retain nouns/adjectives
        assert "medieval" in keywords
        assert "iron-banded" in keywords or "wooden" in keywords

    def test_build_sxs_composite(self, tmp_path):
        # Create synthetic test images
        ref_path = os.path.join(tmp_path, "test_ref.png")
        cap_path = os.path.join(tmp_path, "test_cap.png")
        out_path = os.path.join(tmp_path, "composite.png")

        img1 = Image.new("RGB", (400, 300), color=(180, 50, 50))
        img1.save(ref_path)

        img2 = Image.new("RGB", (600, 400), color=(50, 150, 200))
        img2.save(cap_path)

        result_path = build_sxs_composite(
            ref_image_path=ref_path,
            capture_image_path=cap_path,
            output_path=out_path,
            ref_label="Museum Sample",
            capture_label="Blender Model"
        )

        assert os.path.exists(result_path)
        comp_img = Image.open(result_path)
        # Height should be target_height (600) + header_height (60) = 660
        assert comp_img.height == 660
        assert comp_img.width > 1000
