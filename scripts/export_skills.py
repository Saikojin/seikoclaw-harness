"""
Cross-Harness Skill Exporter & External Importer for SeikoClaw.
Exports/symlinks canonical SeikoClaw skills to Claude Code, Codex, Pi, Antigravity, or custom directories,
and imports external skill repositories with namespace isolation to prevent catalog collisions.
"""

import os
import sys
import re
import shutil
import argparse
from pathlib import Path
from typing import Optional

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
            except OSError:
                # Fallback to copy if symlink privileges are restricted on Windows
                shutil.copytree(item, dest_item)
                exported_count += 1
        else:
            shutil.copytree(item, dest_item)
            exported_count += 1

    return exported_count


def import_skills(source_dir: str, target_dir: str, namespace: Optional[str] = None, overwrite: bool = False) -> int:
    """
    Imports skills from an external repository or directory into target_dir.
    If namespace is provided, the imported skill directory is prefixed with '<namespace>-'
    and its frontmatter name is aligned to prevent collisions with canonical skills.
    """
    source_path = Path(source_dir).resolve()
    target_path = Path(target_dir).resolve()

    if not source_path.exists():
        print(f"[ERROR] Source directory does not exist: {source_path}")
        return 0

    target_path.mkdir(parents=True, exist_ok=True)
    imported_count = 0

    # Scan both root and root/skills (common in agent packs)
    candidate_roots = [source_path]
    if (source_path / "skills").is_dir():
        candidate_roots.append(source_path / "skills")

    seen_skills = set()

    for root in candidate_roots:
        for item in root.iterdir():
            if not item.is_dir() or item.name.startswith("."):
                continue
            skill_md = item / "SKILL.md"
            if not skill_md.exists():
                continue

            orig_name = item.name
            dest_name = f"{namespace}-{orig_name}" if namespace else orig_name

            if dest_name in seen_skills:
                continue
            seen_skills.add(dest_name)

            dest_item = target_path / dest_name
            if dest_item.exists():
                if not overwrite:
                    print(f"[SKIP] Skill '{dest_name}' already exists in target directory.")
                    continue
                shutil.rmtree(dest_item)

            shutil.copytree(item, dest_item)

            # If namespaced, update the frontmatter name inside dest_item / SKILL.md
            if namespace:
                dest_skill_md = dest_item / "SKILL.md"
                if dest_skill_md.exists():
                    try:
                        content = dest_skill_md.read_text(encoding="utf-8-sig")
                        # Replace name: <orig_name> with name: <dest_name>
                        updated_content = re.sub(
                            r"^name:\s*[\'\"]?([a-zA-Z0-9_\-]+)[\'\"]?",
                            f"name: {dest_name}",
                            content,
                            flags=re.MULTILINE
                        )
                        dest_skill_md.write_text(updated_content, encoding="utf-8")
                    except Exception as e:
                        print(f"[WARN] Failed to update frontmatter name for {dest_name}: {e}")

            imported_count += 1

    return imported_count


def main():
    parser = argparse.ArgumentParser(description="Export or import SeikoClaw skills across agent harnesses")
    parser.add_argument("--action", choices=["export", "import"], default="export", help="Action to perform")
    parser.add_argument("--harness", choices=list(HARNESS_MAP.keys()) + ["all", "custom"], default="agents", help="Target harness (for export)")
    parser.add_argument("--target", type=str, help="Custom target directory")
    parser.add_argument("--source", type=str, help="Source skills directory")
    parser.add_argument("--namespace", type=str, help="Namespace prefix for imported skills (e.g. 'addy')")
    parser.add_argument("--symlink", action="store_true", help="Use symlinks instead of copying (export only)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing destination skills")

    args = parser.parse_args()
    base_dir = Path(__file__).resolve().parent.parent

    if args.action == "import":
        source_dir = args.source
        if not source_dir:
            print("[ERROR] --source <path> is required for import action.")
            sys.exit(1)
        target_dir = args.target or str(base_dir / ".agents" / "skills")
        count = import_skills(source_dir, target_dir, namespace=args.namespace, overwrite=args.overwrite)
        print(f"[IMPORT SUCCESS] Imported {count} skills into {target_dir} (namespace={args.namespace or 'none'})")
    else:
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
