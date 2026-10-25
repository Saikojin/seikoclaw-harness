#!/usr/bin/env python3
"""
BlendSwap API & Asset Acquisition Client for Blender
----------------------------------------------------
Provides programmatic access to the BlendSwap REST API (v1) and asset downloading
pipeline for integration with Blender MCP (mcp-for-blender) and autonomous agents.

Usage:
  python blendswap_client.py balance
  python blendswap_client.py search --query "chair" --license "cc0"
  python blendswap_client.py info --id 12345
  python blendswap_client.py download --id 12345 --output-dir ./assets/blendswap
  python blendswap_client.py append-code --file ./assets/blendswap/model.blend
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


BLENDSWAP_API_BASE = "https://blendswap.com/api/v1"
BLENDSWAP_MCP_ENDPOINT = "https://blendswap.com/api/mcp"
DEFAULT_USER_AGENT = "BlendSwap-Blender-Client/1.0 (SeikoClaw)"


class BlendSwapError(Exception):
    """Exception raised for BlendSwap API errors."""

    def __init__(self, message: str, status_code: int = 0, error_code: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code

    def __str__(self):
        code_info = f" [HTTP {self.status_code}]" if self.status_code else ""
        err_info = f" ({self.error_code})" if self.error_code else ""
        return f"{super().__str__()}{code_info}{err_info}"


class BlendSwapClient:
    """Client for interacting with BlendSwap REST API v1."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = BLENDSWAP_API_BASE):
        self.api_key = api_key or os.environ.get("BLENDSWAP_API_KEY", "").strip()
        self.base_url = base_url.rstrip("/")

    def _require_api_key(self):
        if not self.api_key:
            raise BlendSwapError(
                "Missing API key. Set the BLENDSWAP_API_KEY environment variable or pass --api-key. "
                "You can generate an API key at https://blendswap.com/dashboard/api",
                status_code=401,
                error_code="missing_key"
            )

    def _request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an authenticated HTTP request to the BlendSwap API."""
        self._require_api_key()

        url = f"{self.base_url}{endpoint}"
        if params:
            filtered_params = {k: v for k, v in params.items() if v is not None}
            if filtered_params:
                query_string = urllib.parse.urlencode(filtered_params)
                url = f"{url}?{query_string}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/json"
        }

        body_bytes = None
        if data is not None:
            headers["Content-Type"] = "application/json"
            body_bytes = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode("utf-8")
                return json.loads(content) if content else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            error_code = ""
            message = f"HTTP {e.code}: {e.reason}"
            try:
                err_json = json.loads(err_body)
                error_code = err_json.get("error", "")
                message = err_json.get("message", message)
            except Exception:
                if err_body:
                    message = f"{message} - {err_body[:200]}"

            if e.code == 401:
                message = (
                    f"{message}. Please verify your BlendSwap API key at https://blendswap.com/dashboard/api "
                    "(format: bsk_live_...)."
                )
            elif e.code == 402:
                message = (
                    f"Insufficient credits: {message}. "
                    "Daily free downloads exhausted. Add credits at https://blendswap.com/plans."
                )

            raise BlendSwapError(message, status_code=e.code, error_code=error_code) from e
        except urllib.error.URLError as e:
            raise BlendSwapError(f"Network error connecting to BlendSwap: {e.reason}") from e

    def get_me(self) -> Dict[str, Any]:
        """Fetch account information, credit balance, and free download allowance."""
        return self._request("/me")

    def get_balance(self) -> Dict[str, Any]:
        """Convenience method returning account balance details."""
        me_data = self.get_me()
        return me_data.get("data", me_data)

    def search_assets(
        self,
        query: str = "",
        category: Optional[str] = None,
        license: Optional[str] = None,
        asset_type: Optional[str] = None,
        file_format: Optional[str] = None,
        blender_version: Optional[str] = None,
        render_engine: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        per_page: int = 25
    ) -> Dict[str, Any]:
        """
        Search and filter the catalog of free Blender assets.

        Args:
            query: Full-text search over title, description, and tags.
            category: Category slug from /api/v1/categories.
            license: Comma-separated: cc0, cc_by, cc_by_sa, cc_by_nc, etc.
            asset_type: Comma-separated: model_3d, material, tool, hdri, simulation.
            file_format: File format: blender, texture, fbx, gltf, obj.
            blender_version: Exact blender version (e.g. '4.2', '5.2').
            render_engine: cycles, eevee, workbench, etc.
            sort: 'newest', 'downloads', 'likes'.
            page: 1-based page number.
            per_page: Number of items per page (default 25, max 100).
        """
        params = {
            "q": query or None,
            "category": category,
            "license": license,
            "type": asset_type,
            "format": file_format,
            "blender_version": blender_version,
            "render_engine": render_engine,
            "sort": sort,
            "page": page,
            "per_page": per_page
        }
        return self._request("/assets", params=params)

    def get_asset(self, asset_id: int | str) -> Dict[str, Any]:
        """Fetch full metadata for one asset."""
        return self._request(f"/assets/{asset_id}")

    def get_asset_files(self, asset_id: int | str) -> Dict[str, Any]:
        """Fetch live files for an asset."""
        return self._request(f"/assets/{asset_id}/files")

    def get_categories(self) -> Dict[str, Any]:
        """List subject categories of the 3D model type with slugs."""
        return self._request("/categories")

    def get_licenses(self) -> Dict[str, Any]:
        """List valid license keys, display names, and URLs."""
        return self._request("/licenses")

    def request_download_url(
        self,
        asset_id: int | str,
        file_id: Optional[int | str] = None
    ) -> Dict[str, Any]:
        """
        Request a 1-hour secure download URL for an asset file.

        Body: { "asset_id": int, "file_id": int (optional) }
        """
        payload: Dict[str, Any] = {"asset_id": int(asset_id)}
        if file_id is not None:
            payload["file_id"] = int(file_id)
        return self._request("/downloads", method="POST", data=payload)

    def download_file(
        self,
        download_url: str,
        dest_dir: Path | str,
        filename_hint: Optional[str] = None
    ) -> Path:
        """Download binary file from signed URL to dest_dir, extracting .zip if needed."""
        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)

        req = urllib.request.Request(download_url, headers={"User-Agent": DEFAULT_USER_AGENT})

        with urllib.request.urlopen(req, timeout=120) as response:
            # Determine filename from headers or url
            filename = filename_hint
            if not filename:
                cd = response.headers.get("Content-Disposition", "")
                if "filename=" in cd:
                    filename = cd.split("filename=")[-1].strip('"\'; ')
                else:
                    path_part = urllib.parse.urlparse(download_url).path
                    filename = os.path.basename(path_part) or "blendswap_asset.bin"

            out_file = dest_path / filename
            with open(out_file, "wb") as f:
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)

        # If downloaded file is a zip archive, extract it and find the .blend file
        if out_file.suffix.lower() == ".zip":
            extract_folder = dest_path / out_file.stem
            extract_folder.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(out_file, "r") as zip_ref:
                zip_ref.extractall(extract_folder)

            # Find .blend file inside
            blend_files = list(extract_folder.rglob("*.blend"))
            if blend_files:
                return blend_files[0]
            return extract_folder

        return out_file

    def get_asset_and_download(
        self,
        asset_id: int | str,
        file_id: Optional[int | str] = None,
        dest_dir: str = "assets/blendswap"
    ) -> Dict[str, Any]:
        """
        Complete pipeline: Check metadata, request download URL, save file, and return info.
        """
        # 1. Fetch metadata
        asset_info = self.get_asset(asset_id)
        asset_data = asset_info.get("data", asset_info)
        title = asset_data.get("title", f"asset_{asset_id}")
        license_info = asset_data.get("license", {})

        # 2. Request download URL
        dl_res = self.request_download_url(asset_id, file_id)
        download_url = dl_res.get("download_url")
        if not download_url:
            raise BlendSwapError("No download_url returned by BlendSwap API.")

        # 3. Determine file name
        file_meta = dl_res.get("file", {})
        filename = file_meta.get("filename") or f"{title}.blend"

        # 4. Download file
        local_path = self.download_file(download_url, dest_dir=dest_dir, filename_hint=filename)

        return {
            "asset_id": asset_id,
            "title": title,
            "license": license_info.get("name", "Unknown"),
            "charged": dl_res.get("charged", False),
            "credits_spent": dl_res.get("credits_spent", 0),
            "credits_remaining": dl_res.get("credits_remaining"),
            "reason": dl_res.get("reason"),
            "local_path": str(local_path.resolve()),
            "preview_urls": dl_res.get("preview_urls", [])
        }


def generate_bpy_append_snippet(
    blend_path: str,
    link: bool = False,
    ground_to_z: bool = True,
    select_appended: bool = True
) -> str:
    """
    Generate executable Blender Python (bpy) code to append/link collections or
    objects from an external .blend file into the active Blender scene.
    """
    normalized_path = Path(blend_path).resolve().as_posix()
    action_type = "LINK" if link else "APPEND"

    return f'''# Auto-generated Blender Asset Ingestion Script (BlendSwap)
import bpy
import mathutils
from pathlib import Path

blend_path = "{normalized_path}"

if not Path(blend_path).exists():
    raise FileNotFoundError(f"Target .blend file not found: {{blend_path}}")

# Deselect everything first
bpy.ops.object.select_all(action='DESELECT')
existing_objects = set(bpy.data.objects)

# 1. Inspect data-blocks inside the .blend file
with bpy.data.libraries.load(blend_path, link={link}) as (data_from, data_to):
    # Prefer Collections (maintains complete hierarchy, parenting, rigs)
    if data_from.collections:
        data_to.collections = list(data_from.collections)
    elif data_from.objects:
        data_to.objects = list(data_from.objects)
    elif data_from.materials:
        data_to.materials = list(data_from.materials)

# 2. Link appended collections or objects into active scene
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

# 3. Grounding & Selection
if appended_objects:
    for obj in appended_objects:
        if obj and {select_appended}:
            obj.select_set(True)
    
    # Ground mesh objects to Z=0 if requested
    if {ground_to_z}:
        mesh_objs = [o for o in appended_objects if o and o.type == 'MESH']
        if mesh_objs:
            all_min_z = []
            for obj in mesh_objs:
                bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
                all_min_z.append(min(corner.z for corner in bbox_corners))
            global_min_z = min(all_min_z)
            # Offset all root appended objects
            root_objs = [o for o in appended_objects if o and o.parent is None]
            for root in root_objs:
                root.location.z -= global_min_z

    # Set the first object active
    bpy.context.view_layer.objects.active = appended_objects[0]
    print(f"Successfully {action_type.lower()}ed {{len(appended_objects)}} objects from {{blend_path}}")
else:
    print(f"Data appended from {{blend_path}} (materials/data-blocks added to bpy.data).")
'''


def main():
    parser = argparse.ArgumentParser(
        description="BlendSwap API & Asset Pipeline CLI for Blender MCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python blendswap_client.py balance
  python blendswap_client.py search --query "medieval house" --license cc0
  python blendswap_client.py info --id 12345
  python blendswap_client.py download --id 12345 --output-dir ./assets/blendswap
  python blendswap_client.py append-code --file ./assets/blendswap/house.blend
        """
    )
    parser.add_argument("--api-key", help="BlendSwap API Key (bsk_live_...). Can also use BLENDSWAP_API_KEY env var.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Balance
    subparsers.add_parser("balance", help="Check credit balance and remaining free daily downloads.")

    # Search
    search_p = subparsers.add_parser("search", help="Search the BlendSwap catalog.")
    search_p.add_argument("--query", "-q", default="", help="Search query string.")
    search_p.add_argument("--category", help="Category slug (e.g. furniture, architecture, characters).")
    search_p.add_argument("--license", help="License key filter (e.g. cc0, cc_by, cc_by_sa).")
    search_p.add_argument("--type", help="Asset type (model_3d, material, tool, hdri, simulation).")
    search_p.add_argument("--format", help="File format filter (blender, texture, fbx, gltf, obj).")
    search_p.add_argument("--blender-version", help="Blender version (e.g. '4.2', '5.2').")
    search_p.add_argument("--render-engine", help="Render engine (cycles, eevee, workbench).")
    search_p.add_argument("--sort", default="newest", choices=["newest", "downloads", "likes"], help="Sort order.")
    search_p.add_argument("--page", type=int, default=1, help="Page number (1-based).")
    search_p.add_argument("--per-page", type=int, default=10, help="Results per page (max 100).")

    # Info
    info_p = subparsers.add_parser("info", help="Get metadata and files for a specific asset.")
    info_p.add_argument("--id", required=True, help="Asset ID.")

    # Categories
    subparsers.add_parser("categories", help="List available model categories.")

    # Licenses
    subparsers.add_parser("licenses", help="List available Creative Commons and commercial licenses.")

    # Download
    dl_p = subparsers.add_parser("download", help="Download an asset and output Blender BPY append code.")
    dl_p.add_argument("--id", required=True, help="Asset ID.")
    dl_p.add_argument("--file-id", help="Optional specific file ID.")
    dl_p.add_argument("--output-dir", default="assets/blendswap", help="Output directory to save the file.")
    dl_p.add_argument("--link", action="store_true", help="Generate bpy linking script instead of append.")
    dl_p.add_argument("--no-ground", action="store_true", help="Do not snap bottom of mesh to Z=0 ground.")

    # Append Code
    code_p = subparsers.add_parser("append-code", help="Generate BPY Python snippet to append a local .blend file.")
    code_p.add_argument("--file", required=True, help="Path to local .blend file.")
    code_p.add_argument("--link", action="store_true", help="Link instead of append.")
    code_p.add_argument("--no-ground", action="store_true", help="Do not snap bottom of mesh to Z=0 ground.")

    args = parser.parse_args()

    client = BlendSwapClient(api_key=args.api_key)

    try:
        if args.command == "balance":
            bal = client.get_balance()
            print("\n=== BlendSwap Account Balance ===")
            print(json.dumps(bal, indent=2))

        elif args.command == "search":
            results = client.search_assets(
                query=args.query,
                category=args.category,
                license=args.license,
                asset_type=args.type,
                file_format=args.format,
                blender_version=args.blender_version,
                render_engine=args.render_engine,
                sort=args.sort,
                page=args.page,
                per_page=args.per_page
            )
            items = results.get("data", [])
            pagination = results.get("pagination", {})
            print(f"\nFound {pagination.get('count', len(items))} assets (Page {pagination.get('page', 1)}/{pagination.get('pages', 1)}):")
            for item in items:
                asset_id = item.get("id")
                title = item.get("title")
                lic = item.get("license", {}).get("name", "Unknown")
                versions = ", ".join(item.get("blender_versions", [])) or "Any"
                size_mb = round(item.get("size_bytes", 0) / (1024 * 1024), 2)
                author = item.get("author", {}).get("username", "Unknown")
                print(f"  [{asset_id}] {title} | Author: {author} | License: {lic} | Blender: {versions} | Size: {size_mb} MB")

        elif args.command == "info":
            info = client.get_asset(args.id)
            print("\n=== Asset Metadata ===")
            print(json.dumps(info, indent=2))

        elif args.command == "categories":
            cats = client.get_categories()
            print("\n=== BlendSwap Categories ===")
            print(json.dumps(cats, indent=2))

        elif args.command == "licenses":
            lics = client.get_licenses()
            print("\n=== BlendSwap Licenses ===")
            print(json.dumps(lics, indent=2))

        elif args.command == "download":
            print(f"Requesting download for asset ID {args.id}...")
            res = client.get_asset_and_download(
                asset_id=args.id,
                file_id=args.file_id,
                dest_dir=args.output_dir
            )
            print("\n=== Download Complete ===")
            print(f"Title: {res['title']}")
            print(f"License: {res['license']}")
            print(f"Charged: {res['charged']} (Credits Spent: {res['credits_spent']})")
            print(f"Local Path: {res['local_path']}")
            if res.get("preview_urls"):
                print(f"Previews: {', '.join(res['preview_urls'])}")

            print("\n=== Ready-to-Run Blender BPY Append Code ===")
            bpy_code = generate_bpy_append_snippet(
                blend_path=res["local_path"],
                link=args.link,
                ground_to_z=not args.no_ground
            )
            print(bpy_code)

        elif args.command == "append-code":
            bpy_code = generate_bpy_append_snippet(
                blend_path=args.file,
                link=args.link,
                ground_to_z=not args.no_ground
            )
            print(bpy_code)

    except BlendSwapError as e:
        print(f"\n[ERROR] BlendSwap API Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
