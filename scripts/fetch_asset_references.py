#!/usr/bin/env python3
"""
fetch_asset_references.py - Automated Visual Reference Acquisition & SxS Compositor

Intakes a plain English description of a 3D asset, searches public visual reference
archives (Wikimedia Commons / museum collections), downloads ground-truth sample images,
and composites them side-by-side with Blender 3D renders for visual parity review.
"""

import os
import sys
import json
import re
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

USER_AGENT = "SeikoClaw-Harness-Visual-Validator/1.0 (https://github.com/saikojin/seikoclaw; contact@saikojin.dev)"


def clean_query_keywords(description: str) -> str:
    """Extracts high-signal visual search terms from a descriptive prompt."""
    # Remove common filler words and instructions
    stop_words = {
        "a", "an", "the", "and", "or", "with", "of", "in", "on", "for", "by", "at",
        "to", "from", "create", "make", "generate", "render", "model", "3d", "asset",
        "game", "detailed", "high", "quality", "stylized", "pbr", "low", "poly",
        "photorealistic", "clean", "beautiful", "isometric", "view", "top", "down"
    }
    words = re.findall(r"\b[A-Za-z0-9_-]+\b", description.lower())
    filtered = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Take top 3-4 keywords
    selected = filtered[:4]
    return " ".join(selected) if selected else description[:30]


def search_wikimedia_references(query: str, limit: int = 3) -> List[Dict[str, str]]:
    """Searches Wikimedia Commons API for high-resolution reference images."""
    encoded_query = urllib.parse.quote(query.strip())
    endpoint = (
        f"https://commons.wikimedia.org/w/api.php?action=query"
        f"&generator=search&gsrsearch={encoded_query}&gsrnamespace=6"
        f"&prop=imageinfo&iiprop=url|mime|size&format=json"
    )

    req = urllib.request.Request(endpoint, headers={"User-Agent": USER_AGENT})
    results = []

    for attempt in range(4):
        try:
            time.sleep(1.0)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                pages = data.get("query", {}).get("pages", {})

                for page_id, page in pages.items():
                    imageinfo = page.get("imageinfo", [])
                    if not imageinfo:
                        continue
                    info = imageinfo[0]
                    mime = info.get("mime", "")
                    url = info.get("url", "")

                    # Only include standard photographic/renderable formats
                    if mime in ("image/jpeg", "image/png", "image/webp") and url:
                        results.append({
                            "title": page.get("title", ""),
                            "url": url,
                            "mime": mime,
                            "width": info.get("width", 0),
                            "height": info.get("height", 0)
                        })

                    if len(results) >= limit:
                        break
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = 2.5 * (attempt + 1)
                sys.stderr.write(f"[INFO] HTTP 429 rate limit hit. Backing off {wait_time:.1f}s (attempt {attempt+1}/4)...\n")
                time.sleep(wait_time)
                continue
            sys.stderr.write(f"[WARN] Wikimedia reference query failed: {e}\n")
            break
        except Exception as e:
            sys.stderr.write(f"[WARN] Wikimedia reference query failed: {e}\n")
            break

    return results


def download_reference_images(
    description: str,
    asset_name: str,
    output_dir: str = "captures/refs",
    limit: int = 2
) -> List[str]:
    """Fetches reference images based on description and saves them locally."""
    target_dir = os.path.join(output_dir, asset_name)
    os.makedirs(target_dir, exist_ok=True)

    keywords = clean_query_keywords(description)
    refs = search_wikimedia_references(keywords, limit=limit)

    downloaded_paths = []
    for idx, ref in enumerate(refs, start=1):
        ext = ".jpg" if "jpeg" in ref["mime"] else ".png"
        dest_file = os.path.join(target_dir, f"ref_{idx:02d}{ext}")
        req = urllib.request.Request(ref["url"], headers={"User-Agent": USER_AGENT})

        for attempt in range(4):
            try:
                time.sleep(1.5)
                with urllib.request.urlopen(req, timeout=20) as resp, open(dest_file, "wb") as out:
                    out.write(resp.read())
                downloaded_paths.append(dest_file)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait_time = 3.0 * (attempt + 1)
                    sys.stderr.write(f"[INFO] HTTP 429 on download. Backing off {wait_time:.1f}s (attempt {attempt+1}/4)...\n")
                    time.sleep(wait_time)
                    continue
                sys.stderr.write(f"[WARN] Failed downloading {ref['url']}: {e}\n")
                break
            except Exception as e:
                sys.stderr.write(f"[WARN] Failed downloading {ref['url']}: {e}\n")
                break

    # Save prompt metadata alongside references
    meta_path = os.path.join(target_dir, "prompt.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "asset_name": asset_name,
            "description": description,
            "search_keywords": keywords,
            "downloaded_references": downloaded_paths
        }, f, indent=2)

    return downloaded_paths


def build_sxs_composite(
    ref_image_path: str,
    capture_image_path: str,
    output_path: str,
    ref_label: str = "Ground Truth Reference",
    capture_label: str = "Current Blender Render"
) -> str:
    """Generates a side-by-side (SxS) comparison image with standardized typography."""
    if not os.path.exists(ref_image_path):
        raise FileNotFoundError(f"Reference image not found: {ref_image_path}")
    if not os.path.exists(capture_image_path):
        raise FileNotFoundError(f"Capture image not found: {capture_image_path}")

    ref_img = Image.open(ref_image_path).convert("RGB")
    cap_img = Image.open(capture_image_path).convert("RGB")

    target_height = 600
    # Scale ref image to target height
    ref_scale = target_height / ref_img.height
    ref_w = int(ref_img.width * ref_scale)
    ref_resized = ref_img.resize((ref_w, target_height), Image.Resampling.LANCZOS)

    # Scale capture image to target height
    cap_scale = target_height / cap_img.height
    cap_w = int(cap_img.width * cap_scale)
    cap_resized = cap_img.resize((cap_w, target_height), Image.Resampling.LANCZOS)

    header_height = 60
    border_width = 4
    total_width = ref_w + cap_w + border_width
    total_height = target_height + header_height

    composite = Image.new("RGB", (total_width, total_height), color=(20, 24, 30))
    draw = ImageDraw.Draw(composite)

    # Paste images
    composite.paste(ref_resized, (0, header_height))
    composite.paste(cap_resized, (ref_w + border_width, header_height))

    # Divider bar
    draw.rectangle(
        [(ref_w, 0), (ref_w + border_width, total_height)],
        fill=(70, 80, 95)
    )

    # Text headers
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Header backgrounds
    draw.rectangle([(0, 0), (ref_w, header_height)], fill=(28, 34, 44))
    draw.rectangle([(ref_w + border_width, 0), (total_width, header_height)], fill=(34, 40, 52))

    # Text drawing
    draw.text((20, 20), f"[REF] {ref_label}", fill=(100, 220, 140), font=font)
    draw.text((ref_w + border_width + 20, 20), f"[3D] {capture_label}", fill=(100, 180, 255), font=font)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    composite.save(output_path, "PNG")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch Visual References & Compose Side-by-Side (SxS) Parity Comparisons"
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # 1. search subcommand
    p_search = subparsers.add_parser("search", help="Search and download reference images")
    p_search.add_argument("--description", required=True, help="Plain English description of asset")
    p_search.add_argument("--asset-name", required=True, help="Canonical slug/name for the asset")
    p_search.add_argument("--output-dir", default="captures/refs", help="Directory to save images")
    p_search.add_argument("--limit", type=int, default=2, help="Max images to download (default: 2)")

    # 2. composite subcommand
    p_comp = subparsers.add_parser("composite", help="Build SxS comparison composite")
    p_comp.add_argument("--ref", required=True, help="Path to reference image")
    p_comp.add_argument("--capture", required=True, help="Path to Blender capture image")
    p_comp.add_argument("--output", required=True, help="Path to save composite PNG")
    p_comp.add_argument("--ref-label", default="Ground Truth Reference", help="Label for reference")
    p_comp.add_argument("--cap-label", default="Current Blender Render", help="Label for capture")

    # 3. pipeline subcommand
    p_pipe = subparsers.add_parser("pipeline", help="Fetch reference and immediately compose with capture")
    p_pipe.add_argument("--description", required=True, help="Plain English description")
    p_pipe.add_argument("--asset-name", required=True, help="Asset identifier slug")
    p_pipe.add_argument("--capture", required=True, help="Path to Blender capture")
    p_pipe.add_argument("--output", required=True, help="Output path for SxS composite")

    args = parser.parse_args()

    if args.subcommand == "search":
        downloaded = download_reference_images(
            description=args.description,
            asset_name=args.asset_name,
            output_dir=args.output_dir,
            limit=args.limit
        )
        print(json.dumps({
            "status": "PASS" if downloaded else "EMPTY",
            "asset_name": args.asset_name,
            "downloaded_count": len(downloaded),
            "files": downloaded
        }, indent=2))
        return 0

    elif args.subcommand == "composite":
        out = build_sxs_composite(
            ref_image_path=args.ref,
            capture_image_path=args.capture,
            output_path=args.output,
            ref_label=args.ref_label,
            capture_label=args.cap_label
        )
        print(json.dumps({"status": "PASS", "composite_path": out}, indent=2))
        return 0

    elif args.subcommand == "pipeline":
        downloaded = download_reference_images(
            description=args.description,
            asset_name=args.asset_name,
            limit=1
        )
        if not downloaded:
            print(json.dumps({"status": "FAIL", "error": "No reference images found."}))
            return 1
        out = build_sxs_composite(
            ref_image_path=downloaded[0],
            capture_image_path=args.capture,
            output_path=args.output,
            ref_label=f"Reference: {clean_query_keywords(args.description)}",
            capture_label=f"Blender: {args.asset_name}"
        )
        print(json.dumps({
            "status": "PASS",
            "reference_image": downloaded[0],
            "composite_path": out
        }, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
