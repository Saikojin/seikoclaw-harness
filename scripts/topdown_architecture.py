#!/usr/bin/env python3
"""
SeikoClaw Sidecar Bridge: Parametric Top-Down Pixel Architecture
Wraps Zengkailin/parametric-topdown-pixel-architecture (cli/tb.js)
Provides both an importable Python API and a CLI wrapper for Godot/Blender workflows.
"""

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path

# Base paths
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SIDECAR_DIR = WORKSPACE_DIR / "sidecars" / "parametric-topdown-pixel-architecture"
TB_JS = SIDECAR_DIR / "cli" / "tb.js"

def find_node() -> str:
    """Ensure Node.js 18+ is available on PATH."""
    node_bin = shutil.which("node")
    if not node_bin:
        raise RuntimeError("Node.js 18+ is required to execute parametric-topdown-pixel-architecture (node not found on PATH).")
    return node_bin

def run_tb(args: list[str], cwd: Path | None = None) -> dict:
    """Execute tb.js with given arguments and return parsed JSON stdout."""
    node_bin = find_node()
    if not TB_JS.exists():
        raise FileNotFoundError(f"Parametric topdown architecture CLI not found at: {TB_JS}")
    
    cmd = [node_bin, str(TB_JS)] + args
    result = subprocess.run(
        cmd,
        cwd=str(cwd or WORKSPACE_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    
    if result.returncode != 0:
        err_msg = result.stderr.strip() or result.stdout.strip() or f"Process exited with code {result.returncode}"
        try:
            err_json = json.loads(err_msg)
            raise RuntimeError(f"tb.js error: {err_json.get('error', err_msg)} (hint: {err_json.get('hint', '')})")
        except json.JSONDecodeError:
            raise RuntimeError(f"tb.js command failed: {err_msg}")
    
    out = result.stdout.strip()
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"ok": True, "output": out}

def render(
    style: str = "jiangnan",
    building_type: str = "house",
    out: str | Path | None = None,
    pitch: int = 45,
    dirs: int = 1,
    proj: str = "ortho",
    size: int | str = 512,
    sheet: bool = False,
    thumb: bool = False,
    no_aa: bool = False,
    godot_project: str | Path | None = None,
    godot_prefab: str | None = None,
    godot_texture: str | None = None,
    params: dict[str, any] | None = None,
    parts: dict[str, str] | None = None,
    extra_flags: list[str] | None = None
) -> dict:
    """Render a parametric building to 2D PNG / spritesheet / Godot prefab."""
    args = ["render", style, building_type]
    
    if out:
        out_p = Path(out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        args.extend(["-o", str(out_p).replace("\\", "/")])
        
    if pitch != 45:
        args.extend(["--pitch", str(pitch)])
    if dirs != 1:
        args.extend(["-d", str(dirs)])
    if proj != "ortho":
        args.extend(["--proj", proj])
    if size != 512:
        args.extend(["--size", str(size)])
    if sheet:
        args.append("--sheet")
    if thumb:
        args.append("--thumb")
    if no_aa:
        args.append("--no-aa")
        
    if godot_project:
        args.extend(["--godot-project", str(godot_project).replace("\\", "/")])
    if godot_prefab:
        args.extend(["--godot-prefab", godot_prefab])
    if godot_texture:
        args.extend(["--godot-texture", godot_texture])
        
    if params:
        for k, v in params.items():
            args.extend(["--param", f"{k}={v}"])
            
    if parts:
        for k, v in parts.items():
            args.extend(["--part", f"{k}={v}"])
            
    if extra_flags:
        args.extend(extra_flags)
        
    return run_tb(args)

def batch(jobs_file: str | Path) -> dict:
    """Run a single-process batch render manifest."""
    return run_tb(["batch", str(jobs_file).replace("\\", "/")])

def get_schema(full: bool = False) -> dict:
    """Return the schema dictionary for styles, types, and parameters."""
    args = ["schema", "--full"] if full else ["schema"]
    return run_tb(args)

def inspect_png(png_path: str | Path, full: bool = False) -> dict:
    """Inspect embedded metadata & recipe in a rendered PNG."""
    args = ["inspect", str(png_path).replace("\\", "/")]
    if full:
        args.append("--full")
    return run_tb(args)

def check_atlas(atlas_png: str | Path) -> dict:
    """Validate that a 4x4 PNG complies with the 16-role atlas specification."""
    return run_tb(["atlas", "check", str(atlas_png).replace("\\", "/")])

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python scripts/topdown_architecture.py <command> [args...]")
        print("Commands:")
        print("  render <style> <type> [-o <out>] [--pitch <deg>] [-d <dirs>] [--sheet] [--godot-project <p>]")
        print("  batch <jobs.json>")
        print("  schema [--full]")
        print("  inspect <png> [--full]")
        print("  atlas-check <atlas.png>")
        print("  styles <styles-subcommand> [args...]")
        sys.exit(0)
        
    cmd = sys.argv[1]
    raw_args = sys.argv[2:]
    
    if cmd == "atlas-check":
        if not raw_args:
            print("Error: atlas-check requires an atlas image path")
            sys.exit(1)
        res = check_atlas(raw_args[0])
    elif cmd in ("render", "batch", "schema", "inspect", "styles", "list", "rec", "preset"):
        res = run_tb([cmd] + raw_args)
    else:
        # Fallback to passing all args to tb.js
        res = run_tb(sys.argv[1:])
        
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
