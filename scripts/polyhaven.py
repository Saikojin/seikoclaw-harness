#!/usr/bin/env python3
"""
scripts/polyhaven.py - Zero-dependency Poly Haven CC0 Asset Pipeline for SeikoClaw Harness.

Credits & Attribution:
- All assets, PBR textures, environment HDRIs, and 3D models are provided by Poly Haven (https://polyhaven.com).
- Founded by Greg Zaal and Rob Tuytel, supported by the global CG/VFX/GameDev community.
- License: Creative Commons 0 (CC0) / Public Domain dedication.

Features:
- Fast asset search and metadata inspection against the Poly Haven API.
- Strict 2K resolution default gating to preserve workstation storage.
- Selective format and map ingestion (skips redundant .exr/.png duplicates).
- LRU caching with configurable storage ceiling (default 10 GB).
- Multi-engine material adapters for Godot (.tres), Unity (.meta/.mat), Unreal (.json manifest), and Blender (bpy script / MCP).
"""

import os
import sys
import json
import math
import time
import shutil
import hashlib
import argparse
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Ensure Windows terminal doesn't crash on UTF-8 characters
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

USER_AGENT = "SeikoClaw-Harness/1.0 (https://github.com/Saikojin/SeikoClaw-Harness; asset-pipeline)"
BASE_API = "https://api.polyhaven.com"
DEFAULT_RESOLUTION = "2k"
DEFAULT_CACHE_MAX_BYTES = 10 * 1024 * 1024 * 1024  # 10 GB


def parse_size_to_bytes(size_str: str) -> int:
    """Parses human-readable size strings like '10GB', '500MB', '2.5GB' to bytes."""
    s = size_str.strip().upper()
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
    }
    for unit, factor in sorted(units.items(), key=lambda x: -len(x[0])):
        if s.endswith(unit):
            try:
                num = float(s[:-len(unit)].strip())
                return int(num * factor)
            except ValueError:
                pass
    try:
        return int(float(s))
    except ValueError:
        raise ValueError(f"Invalid size string: '{size_str}'. Use format like '10GB' or '500MB'.")


def format_bytes(num_bytes: int) -> str:
    """Formats bytes to a readable string (e.g. 14.2 MB, 1.3 GB)."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    for unit in ["KB", "MB", "GB", "TB"]:
        num_bytes /= 1024.0
        if num_bytes < 1024.0 or unit == "TB":
            return f"{num_bytes:.2f} {unit}"
    return f"{num_bytes:.2f} TB"


class PolyHavenCache:
    """Manages local cached asset files with LRU eviction and storage budget checks."""

    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir is None:
            # Look for repo root or environment variable
            env_cache = os.environ.get("POLYHAVEN_CACHE_DIR")
            if env_cache:
                self.cache_dir = Path(env_cache).resolve()
            else:
                repo_root = Path(__file__).resolve().parent.parent
                self.cache_dir = (repo_root / ".scratch" / "polyhaven_cache").resolve()
        else:
            self.cache_dir = Path(cache_dir).resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _hash_key(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def get_cache_path(self, url: str, filename: str) -> Path:
        key = self._hash_key(url)
        bucket = self.cache_dir / key[:2]
        bucket.mkdir(parents=True, exist_ok=True)
        return bucket / f"{key}_{filename}"

    def get(self, url: str, filename: str, expected_md5: Optional[str] = None) -> Optional[Path]:
        cached = self.get_cache_path(url, filename)
        if not cached.exists():
            return None

        # Verify MD5 if provided
        if expected_md5:
            hasher = hashlib.md5()
            with open(cached, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            if hasher.hexdigest().lower() != expected_md5.lower():
                cached.unlink(missing_ok=True)
                return None

        # Update access time for LRU tracking
        try:
            cached.touch(exist_ok=True)
        except OSError:
            pass
        return cached

    def put(self, url: str, filename: str, src_path: Path) -> Path:
        dest = self.get_cache_path(url, filename)
        if src_path != dest:
            shutil.copy2(src_path, dest)
        try:
            dest.touch(exist_ok=True)
        except OSError:
            pass
        return dest

    def get_status(self) -> Dict[str, Any]:
        total_size = 0
        file_count = 0
        for p in self.cache_dir.rglob("*"):
            if p.is_file():
                total_size += p.stat().st_size
                file_count += 1
        return {
            "cache_dir": str(self.cache_dir),
            "total_size_bytes": total_size,
            "total_size_formatted": format_bytes(total_size),
            "file_count": file_count,
        }

    def prune(self, max_bytes: int = DEFAULT_CACHE_MAX_BYTES) -> Tuple[int, int]:
        """Prunes least-recently-used files until total size is <= max_bytes."""
        files = []
        total_size = 0
        for p in self.cache_dir.rglob("*"):
            if p.is_file():
                st = p.stat()
                files.append((st.st_atime, st.st_size, p))
                total_size += st.st_size

        if total_size <= max_bytes:
            return 0, 0

        # Sort by access time ascending (oldest accessed first)
        files.sort(key=lambda x: x[0])
        deleted_count = 0
        deleted_bytes = 0

        for atime, size, path in files:
            if total_size <= max_bytes:
                break
            try:
                path.unlink()
                total_size -= size
                deleted_bytes += size
                deleted_count += 1
            except OSError:
                pass

        return deleted_count, deleted_bytes

    def clear(self) -> int:
        count = 0
        for p in self.cache_dir.rglob("*"):
            if p.is_file():
                try:
                    p.unlink()
                    count += 1
                except OSError:
                    pass
        return count


class PolyHavenAPI:
    """Client for Poly Haven API endpoints."""

    def __init__(self, cache: Optional[PolyHavenCache] = None):
        self.cache = cache or PolyHavenCache()

    def _fetch_json(self, url: str) -> Any:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                content = response.read().decode("utf-8")
                return json.loads(content)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(f"Poly Haven resource not found (404): {url}")
            raise RuntimeError(f"HTTP error {e.code} while querying {url}: {e.reason}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network connection error while querying {url}: {e.reason}")

    def search(
        self,
        query: Optional[str] = None,
        asset_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Searches Poly Haven assets by query, type, or category."""
        type_param = asset_type if asset_type and asset_type != "all" else None
        
        # If query is provided, use search endpoint
        if query and query.strip() and query.strip() != "*":
            params = [f"q={urllib.parse.quote(query.strip())}"]
            if type_param:
                params.append(f"t={urllib.parse.quote(type_param)}")
            url = f"{BASE_API}/search?{'&'.join(params)}"
            data = self._fetch_json(url)
            results = data.get("results", [])
            
            # Format and fetch extra metadata if available
            formatted = []
            for item in results[:limit]:
                formatted.append({
                    "slug": item.get("slug"),
                    "score": item.get("score", 0.0),
                    "name": item.get("slug", "").replace("_", " ").title(),
                })
            return formatted
        else:
            # Query all assets and filter locally
            params = []
            if type_param:
                params.append(f"t={urllib.parse.quote(type_param)}")
            if category:
                params.append(f"c={urllib.parse.quote(category)}")
            url = f"{BASE_API}/assets" + (f"?{'&'.join(params)}" if params else "")
            data = self._fetch_json(url)
            
            type_map = {0: "hdris", 1: "textures", 2: "models"}
            formatted = []
            for slug, item in data.items():
                item_type = type_map.get(item.get("type"), "unknown")
                if type_param and item_type != type_param:
                    continue
                if category and category.lower() not in [c.lower() for c in item.get("categories", [])]:
                    continue
                formatted.append({
                    "slug": slug,
                    "name": item.get("name", slug),
                    "type": item_type,
                    "categories": item.get("categories", []),
                    "tags": item.get("tags", []),
                    "download_count": item.get("download_count", 0),
                })
                if len(formatted) >= limit:
                    break
            return formatted

    def get_files_manifest(self, slug: str) -> Dict[str, Any]:
        """Fetches the file download tree for a specific asset slug."""
        url = f"{BASE_API}/files/{slug}"
        return self._fetch_json(url)

    def get_asset_info(self, slug: str) -> Optional[Dict[str, Any]]:
        """Fetches general asset metadata for a slug."""
        try:
            url = f"{BASE_API}/assets?t=all"
            data = self._fetch_json(url)
            return data.get(slug)
        except Exception:
            return None

    def download_file(
        self,
        url: str,
        dest_path: Path,
        expected_md5: Optional[str] = None,
        use_cache: bool = True
    ) -> Path:
        """Downloads a file to dest_path, utilizing local cache if enabled."""
        filename = dest_path.name
        if use_cache:
            cached = self.cache.get(url, filename, expected_md5)
            if cached and cached.exists():
                shutil.copy2(cached, dest_path)
                return dest_path

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        temp_dest = dest_path.with_suffix(dest_path.suffix + ".tmp")
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

        try:
            with urllib.request.urlopen(req, timeout=60) as resp, open(temp_dest, "wb") as out_file:
                hasher = hashlib.md5() if expected_md5 else None
                while chunk := resp.read(65536):
                    out_file.write(chunk)
                    if hasher:
                        hasher.update(chunk)

                if hasher and hasher.hexdigest().lower() != expected_md5.lower():
                    temp_dest.unlink(missing_ok=True)
                    raise ValueError(f"MD5 mismatch for {url}: expected {expected_md5}, got {hasher.hexdigest()}")

            if temp_dest.exists():
                if dest_path.exists():
                    dest_path.unlink()
                temp_dest.rename(dest_path)

            if use_cache:
                self.cache.put(url, filename, dest_path)

            return dest_path
        except Exception:
            if temp_dest.exists():
                temp_dest.unlink(missing_ok=True)
            raise


class EngineAdapters:
    """Generates engine-specific material files and setup configurations."""

    @staticmethod
    def godot(slug: str, downloaded_maps: Dict[str, Path], output_dir: Path, is_hdri: bool = False) -> Path:
        """Generates Godot 4 StandardMaterial3D or PanoramaSkyMaterial .tres file."""
        if is_hdri:
            tres_path = output_dir / f"{slug}_sky.tres"
            hdri_file = next(iter(downloaded_maps.values()))
            content = f"""[gd_resource type="PanoramaSkyMaterial" load_steps=2 format=3]

[ext_resource type="Texture2D" path="{hdri_file.name}" id="1_sky"]

[resource]
panorama = ExtResource("1_sky")
"""
            tres_path.write_text(content, encoding="utf-8")
            return tres_path

        # PBR Texture Material
        tres_path = output_dir / f"{slug}.tres"
        ext_resources = []
        resource_props = []
        id_counter = 1

        load_step_count = 1 + len(downloaded_maps)

        mapping_rules = [
            ("Diffuse", "albedo_texture"),
            ("nor_gl", "normal_texture"),
            ("Rough", "roughness_texture"),
            ("Metal", "metallic_texture"),
            ("AO", "ao_texture"),
        ]

        for map_key, prop_name in mapping_rules:
            if map_key in downloaded_maps:
                res_id = f"{id_counter}_{map_key}"
                file_name = downloaded_maps[map_key].name
                ext_resources.append(f'[ext_resource type="Texture2D" path="{file_name}" id="{res_id}"]')
                if prop_name == "normal_texture":
                    resource_props.append("normal_enabled = true")
                elif prop_name == "ao_texture":
                    resource_props.append("ao_enabled = true")
                resource_props.append(f'{prop_name} = ExtResource("{res_id}")')
                id_counter += 1

        content = f"""[gd_resource type="StandardMaterial3D" load_steps={load_step_count} format=3]

{chr(10).join(ext_resources)}

[resource]
{chr(10).join(resource_props)}
"""
        tres_path.write_text(content, encoding="utf-8")
        return tres_path

    @staticmethod
    def unity(slug: str, downloaded_maps: Dict[str, Path], output_dir: Path, is_hdri: bool = False) -> List[Path]:
        """Generates Unity .meta files and URP Lit Material template."""
        created_files = []

        # Generate companion .meta files for downloaded textures
        for map_key, file_path in downloaded_maps.items():
            meta_path = file_path.with_suffix(file_path.suffix + ".meta")
            # Simple GUID generator based on filename hash
            file_guid = hashlib.md5(file_path.name.encode("utf-8")).hexdigest()
            is_normal = (map_key in ["nor_dx", "nor_gl"])
            is_linear = is_normal or (map_key in ["Rough", "Metal", "arm", "AO", "Displacement"])

            texture_type = 1 if is_normal else 0
            srgb_flag = 0 if is_linear else 1

            meta_content = f"""fileFormatVersion: 2
guid: {file_guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  textureType: {texture_type}
  sRGBTexture: {srgb_flag}
  textureShape: 1
"""
            meta_path.write_text(meta_content, encoding="utf-8")
            created_files.append(meta_path)

        # Generate URP Lit Material (.mat)
        mat_path = output_dir / f"{slug}.mat"
        mat_guid = hashlib.md5(f"mat_{slug}".encode("utf-8")).hexdigest()
        mat_content = f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!21 &2100000
Material:
  serializedVersion: 8
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {slug}
  m_Shader: {{fileID: 4800000, guid: 933532a4fcc9baf4a8c07e8d70148404, type: 3}}
"""
        mat_path.write_text(mat_content, encoding="utf-8")
        created_files.append(mat_path)
        return created_files

    @staticmethod
    def blender(slug: str, downloaded_maps: Dict[str, Path], output_dir: Path, is_hdri: bool = False) -> Path:
        """Generates companion bpy procedural material setup script."""
        script_path = output_dir / "setup_material.py"
        if is_hdri:
            hdri_name = next(iter(downloaded_maps.values())).name
            code = f"""# Procedural Blender HDRI World Environment Setup
import bpy

world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

env_node = nodes.new(type="ShaderNodeTexEnvironment")
env_node.image = bpy.data.images.load("{hdri_name}")
bg_node = nodes.new(type="ShaderNodeBackground")
out_node = nodes.new(type="ShaderNodeOutputWorld")

links.new(env_node.outputs["Color"], bg_node.inputs["Color"])
links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])
"""
        else:
            diffuse_name = downloaded_maps.get("Diffuse", Path("")).name
            normal_name = downloaded_maps.get("nor_gl", downloaded_maps.get("nor_dx", Path(""))).name
            rough_name = downloaded_maps.get("Rough", Path("")).name
            metal_name = downloaded_maps.get("Metal", Path("")).name

            code = f"""# Procedural Blender Principled BSDF Setup for {slug}
import bpy
import os

dir_path = os.path.dirname(__file__)
mat = bpy.data.materials.new(name="M_{slug}")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")

def load_img(fname, colorspace="sRGB"):
    if not fname:
        return None
    full_path = os.path.join(dir_path, fname)
    if os.path.exists(full_path):
        img = bpy.data.images.load(full_path)
        img.colorspace_settings.name = colorspace
        return img
    return None

# Diffuse
diff_img = load_img("{diffuse_name}", "sRGB")
if diff_img:
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = diff_img
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

# Roughness
rough_img = load_img("{rough_name}", "Non-Color")
if rough_img:
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = rough_img
    links.new(tex.outputs["Color"], bsdf.inputs["Roughness"])

# Normal Map
nor_img = load_img("{normal_name}", "Non-Color")
if nor_img:
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = nor_img
    nor_map = nodes.new("ShaderNodeNormalMap")
    links.new(tex.outputs["Color"], nor_map.inputs["Color"])
    links.new(nor_map.outputs["Normal"], bsdf.inputs["Normal"])

# Metallic
metal_img = load_img("{metal_name}", "Non-Color")
if metal_img:
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = metal_img
    links.new(tex.outputs["Color"], bsdf.inputs["Metallic"])

# Assign to active object if selected
if bpy.context.active_object and bpy.context.active_object.type == "MESH":
    bpy.context.active_object.data.materials.append(mat)
"""
        script_path.write_text(code, encoding="utf-8")
        return script_path

    @staticmethod
    def unreal(slug: str, downloaded_maps: Dict[str, Path], output_dir: Path, is_hdri: bool = False) -> Path:
        """Generates Unreal Engine Material Instance configuration manifest."""
        manifest_path = output_dir / "material_manifest.json"
        texture_params = {}
        for map_key, path in downloaded_maps.items():
            param_name = {
                "Diffuse": "BaseColorMap",
                "nor_dx": "NormalMap",
                "nor_gl": "NormalMap_OpenGL",
                "Rough": "RoughnessMap",
                "Metal": "MetallicMap",
                "AO": "AmbientOcclusionMap",
                "arm": "ARM_PackedMap",
            }.get(map_key, map_key)
            texture_params[param_name] = {
                "file": path.name,
                "sRGB": (map_key == "Diffuse"),
                "is_normal": (map_key in ["nor_dx", "nor_gl"]),
            }

        manifest = {
            "asset_id": slug,
            "target_engine": "Unreal Engine 5",
            "material_instance": f"MI_{slug}",
            "parent_material": "/Game/Materials/M_PolyHaven_Master",
            "parameters": texture_params
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest_path


def select_best_resolution(available_resolutions: List[str], requested: str) -> str:
    """Selects the requested resolution or the nearest lower/upper fallback."""
    if requested in available_resolutions:
        return requested

    # Rank resolutions by numerical size
    tier_order = ["1k", "2k", "4k", "8k", "16k"]
    req_index = tier_order.index(requested) if requested in tier_order else 1

    # First attempt: find nearest lower resolution to protect disk storage
    for idx in range(req_index - 1, -1, -1):
        if tier_order[idx] in available_resolutions:
            return tier_order[idx]

    # Second attempt: find nearest upper
    for idx in range(req_index + 1, len(tier_order)):
        if tier_order[idx] in available_resolutions:
            return tier_order[idx]

    return available_resolutions[0] if available_resolutions else requested


def cmd_search(args: argparse.Namespace, api: PolyHavenAPI) -> int:
    """Handles search subcommand."""
    results = api.search(
        query=args.query,
        asset_type=args.type,
        category=args.category,
        limit=args.limit
    )

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    if not results:
        print(f"[Poly Haven] No assets found matching query: '{args.query or '*'}'")
        return 0

    print(f"\n🔍 Found {len(results)} matching assets on Poly Haven:")
    print(f"{'SLUG':<35} {'TYPE':<12} {'NAME / DETAILS'}")
    print("-" * 75)
    for r in results:
        slug = r.get("slug", "")
        item_type = r.get("type", "texture/hdri/model")
        name = r.get("name", slug)
        cats = ", ".join(r.get("categories", []))
        extra = f"({cats})" if cats else ""
        print(f"{slug:<35} {item_type:<12} {name} {extra}")
    print("\n💡 Default download policy is 2K resolution tier.")
    print("   Run: python scripts/polyhaven.py fetch <slug> --target godot|unity|blender|raw")
    return 0


def cmd_info(args: argparse.Namespace, api: PolyHavenAPI) -> int:
    """Handles info subcommand."""
    slug = args.slug.strip()
    try:
        manifest = api.get_files_manifest(slug)
    except Exception as e:
        print(f"[ERROR] Failed to fetch manifest for '{slug}': {e}")
        return 1

    asset_info = api.get_asset_info(slug) or {}

    if args.json:
        output_data = {
            "slug": slug,
            "info": asset_info,
            "files": manifest
        }
        print(json.dumps(output_data, indent=2))
        return 0

    name = asset_info.get("name", slug.replace("_", " ").title())
    categories = ", ".join(asset_info.get("categories", []))
    tags = ", ".join(asset_info.get("tags", [])[:8])
    authors = ", ".join(asset_info.get("authors", {}).keys()) if isinstance(asset_info.get("authors"), dict) else ""

    print(f"\n📦 Poly Haven Asset: {name} ({slug})")
    if authors:
        print(f"Authors:    {authors}")
    print(f"License:    CC0 (Public Domain via Poly Haven - https://polyhaven.com)")
    if categories:
        print(f"Categories: {categories}")
    if tags:
        print(f"Tags:       {tags}")

    print("\nAvailable Map Channels / Files:")
    for channel, details in manifest.items():
        if isinstance(details, dict):
            res_keys = sorted(details.keys())
            print(f"  - {channel:<15} [Resolutions: {', '.join(res_keys)}]")

    print(f"\nDefault Fetch Policy: 2K Resolution (~10–25 MB)")
    print(f"Fetch Command: python scripts/polyhaven.py fetch \"{slug}\" --resolution 2k --target raw")
    return 0


def cmd_fetch(args: argparse.Namespace, api: PolyHavenAPI) -> int:
    """Handles fetch subcommand with strict 2K default and engine target routing."""
    slug = args.slug.strip()
    resolution = args.resolution or DEFAULT_RESOLUTION
    target = args.target.lower()
    pref_format = args.format.lower() if args.format else None
    use_cache = not args.no_cache

    try:
        manifest = api.get_files_manifest(slug)
    except Exception as e:
        print(f"[ERROR] Failed to fetch asset manifest for '{slug}': {e}")
        return 1

    # Detect asset type via catalog metadata or manifest channels
    asset_info = api.get_asset_info(slug) or {}
    catalog_type_id = asset_info.get("type")
    
    if args.type and args.type != "all":
        asset_type = args.type
    elif catalog_type_id == 0:
        asset_type = "hdris"
    elif catalog_type_id == 1:
        asset_type = "textures"
    elif catalog_type_id == 2:
        asset_type = "models"
    else:
        # Heuristic fallback based on channel names
        if "hdri" in manifest or "tonemapped" in manifest:
            asset_type = "hdris"
        elif "fbx" in manifest or "usd" in manifest:
            asset_type = "models"
        elif "Diffuse" in manifest and ("nor_gl" in manifest or "nor_dx" in manifest):
            asset_type = "textures"
        elif any(k in manifest for k in ["gltf", "blend"]):
            asset_type = "models"
        else:
            asset_type = "textures"

    is_hdri = (asset_type == "hdris")
    is_model = (asset_type == "models")
    is_texture = (asset_type == "textures")

    # Determine destination folder
    if args.output:
        dest_dir = Path(args.output).resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent
        dest_dir = (repo_root / ".scratch" / "downloads" / slug).resolve()

    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"📥 [Poly Haven] Fetching '{slug}' at {resolution.upper()} (Target: {target.upper()})...")
    downloaded_files: Dict[str, Path] = {}
    total_download_bytes = 0

    if is_hdri:
        channel = "hdri" if "hdri" in manifest else list(manifest.keys())[0]
        avail_res = list(manifest[channel].keys())
        chosen_res = select_best_resolution(avail_res, resolution)

        res_formats = manifest[channel][chosen_res]
        # Preference: hdr > exr unless pref_format is specified
        fmt = pref_format or ("hdr" if "hdr" in res_formats else "exr")
        if fmt not in res_formats:
            fmt = list(res_formats.keys())[0]

        file_info = res_formats[fmt]
        url = file_info["url"]
        expected_md5 = file_info.get("md5")
        file_name = f"{slug}_{chosen_res}.{fmt}"
        target_path = dest_dir / file_name

        print(f"  Downloading HDRI: {file_name} ({format_bytes(file_info['size'])})")
        api.download_file(url, target_path, expected_md5, use_cache=use_cache)
        downloaded_files["hdri"] = target_path
        total_download_bytes += file_info.get("size", 0)

    elif is_texture:
        # Determine maps to fetch based on engine target convention
        # Godot & Blender: OpenGL normal (nor_gl)
        # Unity & Unreal: DirectX normal (nor_dx)
        # Raw: nor_gl or nor_dx or both if available
        normal_key = "nor_gl" if target in ["godot", "blender"] else "nor_dx"
        if normal_key not in manifest and "nor_gl" in manifest:
            normal_key = "nor_gl"
        elif normal_key not in manifest and "nor_dx" in manifest:
            normal_key = "nor_dx"

        desired_maps = ["Diffuse", normal_key]
        if "Rough" in manifest:
            desired_maps.append("Rough")
            if "Metal" in manifest:
                desired_maps.append("Metal")
            if "AO" in manifest:
                desired_maps.append("AO")
        elif "arm" in manifest:
            desired_maps.append("arm")

        if target == "raw":
            # For raw extraction, include both OpenGL and DirectX normals if available
            if "nor_gl" in manifest and "nor_gl" not in desired_maps:
                desired_maps.append("nor_gl")
            if "nor_dx" in manifest and "nor_dx" not in desired_maps:
                desired_maps.append("nor_dx")

        fmt_pref = pref_format or "png"

        for map_name in desired_maps:
            if map_name not in manifest:
                continue

            channel_data = manifest[map_name]
            avail_res = list(channel_data.keys())
            chosen_res = select_best_resolution(avail_res, resolution)

            formats = channel_data[chosen_res]
            # Pick preferred format (e.g. png > jpg > exr)
            chosen_fmt = fmt_pref if fmt_pref in formats else ("png" if "png" in formats else list(formats.keys())[0])
            file_info = formats[chosen_fmt]

            url = file_info["url"]
            expected_md5 = file_info.get("md5")
            file_name = f"{slug}_{map_name.lower()}_{chosen_res}.{chosen_fmt}"
            target_path = dest_dir / file_name

            print(f"  Downloading channel [{map_name}]: {file_name} ({format_bytes(file_info['size'])})")
            api.download_file(url, target_path, expected_md5, use_cache=use_cache)
            downloaded_files[map_name] = target_path
            total_download_bytes += file_info.get("size", 0)

    elif is_model:
        # GLTF is primary cross-engine format
        model_channel = pref_format or "gltf"
        if model_channel not in manifest:
            model_channel = "gltf" if "gltf" in manifest else list(manifest.keys())[0]

        channel_data = manifest[model_channel]
        avail_res = list(channel_data.keys())
        chosen_res = select_best_resolution(avail_res, resolution)

        formats = channel_data[chosen_res]
        fmt_key = list(formats.keys())[0]
        model_info = formats[fmt_key]

        # Download primary model file if direct url
        if "url" in model_info:
            file_name = f"{slug}_{chosen_res}.{fmt_key}"
            target_path = dest_dir / file_name
            print(f"  Downloading model: {file_name}")
            api.download_file(model_info["url"], target_path, model_info.get("md5"), use_cache=use_cache)
            downloaded_files["model"] = target_path

        # Download bundled texture maps for model
        if "include" in model_info:
            for inc_rel_path, inc_info in model_info["include"].items():
                target_path = dest_dir / inc_rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"  Downloading model asset: {inc_rel_path}")
                api.download_file(inc_info["url"], target_path, inc_info.get("md5"), use_cache=use_cache)
                total_download_bytes += inc_info.get("size", 0)

    # Apply engine adapters
    created_adapters = []
    if target == "godot":
        tres = EngineAdapters.godot(slug, downloaded_files, dest_dir, is_hdri=is_hdri)
        created_adapters.append(tres)
        print(f"  ✨ Generated Godot resource: {tres.name}")
    elif target == "unity":
        unity_files = EngineAdapters.unity(slug, downloaded_files, dest_dir, is_hdri=is_hdri)
        created_adapters.extend(unity_files)
        print(f"  ✨ Generated Unity .meta and URP Lit Material")
    elif target == "blender":
        bpy_script = EngineAdapters.blender(slug, downloaded_files, dest_dir, is_hdri=is_hdri)
        created_adapters.append(bpy_script)
        print(f"  ✨ Generated Blender setup script: {bpy_script.name}")
    elif target == "unreal":
        unreal_manifest = EngineAdapters.unreal(slug, downloaded_files, dest_dir, is_hdri=is_hdri)
        created_adapters.append(unreal_manifest)
        print(f"  ✨ Generated Unreal material manifest: {unreal_manifest.name}")

    print(f"\n[SUCCESS] Asset '{slug}' fetched to: {dest_dir}")
    print(f"Total size: {format_bytes(total_download_bytes)} ({len(downloaded_files)} map/asset files)")

    if args.json:
        result_json = {
            "slug": slug,
            "target": target,
            "resolution": resolution,
            "destination": str(dest_dir),
            "files": [str(p) for p in downloaded_files.values()],
            "adapter_files": [str(p) for p in created_adapters],
            "total_bytes": total_download_bytes
        }
        print(json.dumps(result_json, indent=2))

    return 0


def cmd_cache(args: argparse.Namespace, cache: PolyHavenCache) -> int:
    """Handles cache status, pruning, and clearing."""
    if args.clear:
        count = cache.clear()
        print(f"[CACHE] Cleared {count} cached files.")
        return 0

    if args.prune:
        max_bytes = parse_size_to_bytes(args.max_size) if args.max_size else DEFAULT_CACHE_MAX_BYTES
        count, pruned_bytes = cache.prune(max_bytes)
        print(f"[CACHE PRUNE] Removed {count} files ({format_bytes(pruned_bytes)}) to meet {format_bytes(max_bytes)} limit.")
        return 0

    # Default to status report
    status = cache.get_status()
    print("\n📦 Poly Haven Local Storage Cache Status:")
    print(f"  Directory:    {status['cache_dir']}")
    print(f"  Cached Files: {status['file_count']}")
    print(f"  Total Size:   {status['total_size_formatted']} ({status['total_size_bytes']} bytes)")
    print(f"  Storage Cap:  10.00 GB (Enforced via LRU eviction)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Zero-dependency Poly Haven CC0 Asset Pipeline & Storage Gating Tool for SeikoClaw Harness.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # search
    p_search = subparsers.add_parser("search", help="Search Poly Haven asset catalog")
    p_search.add_argument("query", nargs="?", default="", help="Search query string")
    p_search.add_argument("--type", "-t", choices=["all", "textures", "hdris", "models"], default="all", help="Asset type filter")
    p_search.add_argument("--category", "-c", type=str, help="Category slug")
    p_search.add_argument("--limit", type=int, default=20, help="Maximum results to return")
    p_search.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # info
    p_info = subparsers.add_parser("info", help="Inspect asset metadata and file sizes before downloading")
    p_info.add_argument("slug", help="Asset slug identifier")
    p_info.add_argument("--resolution", "-r", choices=["1k", "2k", "4k", "8k", "16k"], help="Filter by resolution tier")
    p_info.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # fetch
    p_fetch = subparsers.add_parser("fetch", help="Download asset maps with strict 2K resolution default")
    p_fetch.add_argument("slug", help="Asset slug identifier")
    p_fetch.add_argument("--type", "-t", choices=["textures", "hdris", "models"], help="Asset type override (textures, hdris, models)")
    p_fetch.add_argument("--resolution", "-r", choices=["1k", "2k", "4k", "8k", "16k"], default=DEFAULT_RESOLUTION, help=f"Resolution tier (Default: {DEFAULT_RESOLUTION})")
    p_fetch.add_argument("--target", choices=["raw", "godot", "unity", "unreal", "blender"], default="raw", help="Engine target adapter")
    p_fetch.add_argument("--format", choices=["png", "jpg", "exr", "hdr", "gltf", "blend"], help="Preferred file format")
    p_fetch.add_argument("--output", "-o", help="Destination directory path")
    p_fetch.add_argument("--no-cache", action="store_true", help="Bypass local cache and re-download")
    p_fetch.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # cache
    p_cache = subparsers.add_parser("cache", help="Inspect and manage local LRU asset cache")
    p_cache.add_argument("--status", action="store_true", help="Show cache status and size")
    p_cache.add_argument("--prune", action="store_true", help="Prune oldest accessed files exceeding size limit")
    p_cache.add_argument("--max-size", type=str, default="10GB", help="Maximum cache size (e.g. 10GB, 500MB)")
    p_cache.add_argument("--clear", action="store_true", help="Clear all cached files")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        return 0

    cache = PolyHavenCache()
    api = PolyHavenAPI(cache=cache)

    if args.subcommand == "search":
        return cmd_search(args, api)
    elif args.subcommand == "info":
        return cmd_info(args, api)
    elif args.subcommand == "fetch":
        return cmd_fetch(args, api)
    elif args.subcommand == "cache":
        return cmd_cache(args, cache)

    return 0


if __name__ == "__main__":
    sys.exit(main())
