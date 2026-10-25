#!/usr/bin/env python3
"""
BlendSwap MCP Server (stdio)
----------------------------
A standalone Model Context Protocol (MCP) server providing BlendSwap asset search,
inspection, download, and Blender BPY ingestion capabilities to AI assistants.

Exposes tools:
- blendswap_get_balance: Check account credits and free downloads remaining today.
- blendswap_search_assets: Search BlendSwap catalog by query, category, license, blender_version, etc.
- blendswap_get_asset: Inspect metadata, author, counts, and live files for an asset ID.
- blendswap_download_asset: Download asset (.blend or archive) to local disk, returning file path and BPY code.
- blendswap_generate_append_code: Generate ready-to-run BPY script to append .blend asset into active scene.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Import the core client from the same directory
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from blendswap_client import BlendSwapClient, BlendSwapError, generate_bpy_append_snippet


TOOLS = [
    {
        "name": "blendswap_get_balance",
        "description": "Check BlendSwap credit balance, cost per download, and remaining free daily downloads.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "blendswap_search_assets",
        "description": "Search BlendSwap's catalog of free Blender assets (3D models, materials, tools, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Full-text search query (e.g. 'chair', 'wooden chest')."},
                "category": {"type": "string", "description": "Category slug (e.g. 'furniture', 'characters', 'architecture')."},
                "license": {"type": "string", "description": "License filter (e.g. 'cc0', 'cc_by', 'cc_by_sa')."},
                "asset_type": {"type": "string", "description": "Asset type: 'model_3d', 'material', 'tool', 'hdri', 'simulation'."},
                "file_format": {"type": "string", "description": "File format: 'blender', 'texture', 'fbx', 'gltf', 'obj'."},
                "blender_version": {"type": "string", "description": "Target Blender version (e.g. '4.2', '5.2')."},
                "render_engine": {"type": "string", "description": "Render engine: 'cycles', 'eevee', 'workbench'."},
                "sort": {"type": "string", "enum": ["newest", "downloads", "likes"], "default": "newest"},
                "page": {"type": "integer", "default": 1},
                "per_page": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "blendswap_get_asset",
        "description": "Fetch complete metadata, uploader info, license details, and file lists for a BlendSwap asset ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_id": {"type": ["integer", "string"], "description": "The BlendSwap numeric asset ID."}
            },
            "required": ["asset_id"]
        }
    },
    {
        "name": "blendswap_download_asset",
        "description": "Request a secure download URL, download the asset (.blend) to local disk, and generate Blender BPY append code.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_id": {"type": ["integer", "string"], "description": "The BlendSwap numeric asset ID."},
                "file_id": {"type": ["integer", "string"], "description": "Optional specific file ID from asset file list."},
                "dest_dir": {"type": "string", "default": "assets/blendswap", "description": "Local directory to store downloaded file."},
                "link": {"type": "boolean", "default": False, "description": "Whether to link library instead of appending."},
                "ground_to_z": {"type": "boolean", "default": True, "description": "Whether to snap mesh bottom to Z=0 ground plane."}
            },
            "required": ["asset_id"]
        }
    },
    {
        "name": "blendswap_generate_append_code",
        "description": "Generate executable Blender Python (bpy) code to append or link a downloaded .blend file into Blender.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "blend_filepath": {"type": "string", "description": "Absolute or relative path to local .blend file."},
                "link": {"type": "boolean", "default": False, "description": "Link instead of append."},
                "ground_to_z": {"type": "boolean", "default": True, "description": "Automatically ground mesh to Z=0."}
            },
            "required": ["blend_filepath"]
        }
    }
]


def send_response(response: Dict[str, Any]):
    """Write JSON-RPC message to stdout followed by newline and flush."""
    body = json.dumps(response)
    sys.stdout.write(body + "\n")
    sys.stdout.flush()


def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    client = BlendSwapClient()

    if name == "blendswap_get_balance":
        balance = client.get_balance()
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(balance, indent=2)
                }
            ]
        }

    elif name == "blendswap_search_assets":
        res = client.search_assets(
            query=arguments.get("query", ""),
            category=arguments.get("category"),
            license=arguments.get("license"),
            asset_type=arguments.get("asset_type"),
            file_format=arguments.get("file_format"),
            blender_version=arguments.get("blender_version"),
            render_engine=arguments.get("render_engine"),
            sort=arguments.get("sort", "newest"),
            page=arguments.get("page", 1),
            per_page=arguments.get("per_page", 10)
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(res, indent=2)
                }
            ]
        }

    elif name == "blendswap_get_asset":
        asset_id = arguments["asset_id"]
        info = client.get_asset(asset_id)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(info, indent=2)
                }
            ]
        }

    elif name == "blendswap_download_asset":
        asset_id = arguments["asset_id"]
        file_id = arguments.get("file_id")
        dest_dir = arguments.get("dest_dir", "assets/blendswap")
        link = arguments.get("link", False)
        ground_to_z = arguments.get("ground_to_z", True)

        download_res = client.get_asset_and_download(
            asset_id=asset_id,
            file_id=file_id,
            dest_dir=dest_dir
        )
        bpy_code = generate_bpy_append_snippet(
            blend_path=download_res["local_path"],
            link=link,
            ground_to_z=ground_to_z
        )
        download_res["bpy_append_code"] = bpy_code

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(download_res, indent=2)
                }
            ]
        }

    elif name == "blendswap_generate_append_code":
        blend_path = arguments["blend_filepath"]
        link = arguments.get("link", False)
        ground_to_z = arguments.get("ground_to_z", True)
        code = generate_bpy_append_snippet(
            blend_path=blend_path,
            link=link,
            ground_to_z=ground_to_z
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": code
                }
            ]
        }

    else:
        raise ValueError(f"Unknown tool: {name}")


def main():
    """Main JSON-RPC event loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except Exception as e:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "blendswap-mcp-server",
                        "version": "1.0.0"
                    }
                }
            })

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS
                }
            })

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                result = handle_call_tool(tool_name, tool_args)
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": result
                })
            except Exception as e:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                })

        elif method == "ping":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            })

        else:
            if req_id is not None:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                })


if __name__ == "__main__":
    main()
