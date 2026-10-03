"""
Cross-Harness Skill Exporter for SeikoClaw.
Exports and symlinks canonical SeikoClaw skills to Claude Code, Codex, Pi, Antigravity, or custom directories.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

HARNESS_MAP = {
    "claude": os.path.expanduser("~/.claude/skills"),
    "codex": os.path.expanduser("~/.codex/skills"),
    "pi": os.path.expanduser("~/.pi/skills"),
    "antigravity": os.path.expanduser("~/.gemini/skills"),
    "agents": os.path.expanduser("~/.agents/skills")
}


def export_skills(source_dir: str, target_dir: str, use_symlinks: bool = False, overwrite: bool = False) -> int:
    """Exports all skills from source_dir to target_dir."""
    source_path = Path(source_dir).resolve()
    target_path = Path(target_dir).resolve()

    if not source_path.exists():
        print(f"[ERROR] Source skills directory does not exist: {source_path}")
        return 0

    target_path.mkdir(parents=True, exist_ok=True)
    exported_count = 0

    for item in source_path.iterdir():
        if not item.is_dir() or item.name.startswith("."):
            continue

        dest_item = target_path / item.name
        if dest_item.exists() or dest_item.is_symlink():
            if not overwrite:
                continue
            if dest_item.is_dir() and not dest_item.is_symlink():
                shutil.rmtree(dest_item)
            else:
                dest_item.unlink()

        if use_symlinks:
            try:
                dest_item.symlink_to(item, target_is_directory=True)
                exported_count += 1
            except OSError as e:
                # Fallback to copy if symlink privileges are restricted on Windows
                shutil.copytree(item, dest_item)
                exported_count += 1
        else:
            shutil.copytree(item, dest_item)
            exported_count += 1

    return exported_count


def main():
    parser = argparse.ArgumentParser(description="Export SeikoClaw skills across agent harnesses")
    parser.add_argument("--harness", choices=list(HARNESS_MAP.keys()) + ["all", "custom"], default="agents", help="Target harness")
    parser.add_argument("--target", type=str, help="Custom target directory (when harness=custom)")
    parser.add_argument("--symlink", action="store_true", help="Use symlinks instead of copying")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing destination skills")
    parser.add_argument("--source", type=str, default=None, help="Source skills directory (default: .agents/skills)")

    args = parser.parse_args()
    base_dir = Path(__file__).resolve().parent.parent
    source_dir = args.source or str(base_dir / ".agents" / "skills")

    if args.harness == "all":
        targets = list(HARNESS_MAP.values())
    elif args.harness == "custom":
        if not args.target:
            print("[ERROR] --target <path> is required when --harness custom is selected.")
            sys.exit(1)
        targets = [args.target]
    else:
        targets = [HARNESS_MAP[args.harness]]

    for t in targets:
        count = export_skills(source_dir, t, use_symlinks=args.symlink, overwrite=args.overwrite)
        print(f"[EXPORT SUCCESS] Exported {count} skills to {t} (symlink={args.symlink})")


if __name__ == "__main__":
    main()
