#!/usr/bin/env python3
"""
scripts/gameplay_atlas.py - High-performance CLI query lever for Gameplay Atlas.

Provides instant offline search, mechanic inspection, combination analysis,
game cases lookup, and rapid prototyping recipes for Game Forge and agents.
"""

from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure UTF-8 output across Windows and POSIX shells
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "gameplay_atlas.db"


def get_db_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    if not db_path.exists():
        sys.stderr.write(f"Error: Database file missing at {db_path}.\nRun 'python scripts/sync_gameplay_atlas.py' to generate it.\n")
        sys.exit(1)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def cmd_search(args: argparse.Namespace) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    query = args.query.strip()
    system_filter = getattr(args, "system", None)
    tag_filter = getattr(args, "tag", None)
    scope_filter = getattr(args, "scope", None)
    limit = getattr(args, "limit", 10)
    as_json = getattr(args, "json", False)

    conditions = []
    params = []

    if query:
        # Clean query for FTS5 syntax
        clean_q = ' '.join(f'"{part}"' for part in query.replace('"', ' ').split() if part)
        conditions.append("m.id IN (SELECT id FROM mechanics_fts WHERE mechanics_fts MATCH ?)")
        params.append(clean_q)

    if system_filter:
        conditions.append("m.system = ?")
        params.append(system_filter.lower())

    if tag_filter:
        conditions.append("m.id IN (SELECT mechanic_id FROM mechanic_tags WHERE tag = ?)")
        params.append(tag_filter.lower())

    if scope_filter:
        conditions.append("m.prototype_scope = ?")
        params.append(scope_filter.lower())

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"""
        SELECT m.id, m.name_en, m.system, m.summary_en, m.prototype_scope,
               GROUP_CONCAT(DISTINCT t.tag) AS tags
        FROM mechanics m
        LEFT JOIN mechanic_tags t ON m.id = t.mechanic_id
        {where_clause}
        GROUP BY m.id
        ORDER BY m.system, m.name_en
        LIMIT ?
    """
    params.append(limit)

    cur.execute(sql, params)
    rows = cur.fetchall()

    if as_json:
        results = [
            {
                "id": r["id"],
                "name": r["name_en"],
                "system": r["system"],
                "summary": r["summary_en"],
                "scope": r["prototype_scope"],
                "tags": (r["tags"] or "").split(",") if r["tags"] else [],
            }
            for r in rows
        ]
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print(f"\n[Gameplay Atlas Search] Found {len(rows)} matching mechanics:")
    print("=" * 80)
    if not rows:
        print("  No mechanics found matching criteria.")
        return

    for r in rows:
        tags_str = f" [{r['tags']}]" if r["tags"] else ""
        print(f"• {r['name_en']} (`{r['id']}`) - System: {r['system']}{tags_str}")
        print(f"  Summary: {r['summary_en']}")
        print(f"  Prototype Scope: {r['prototype_scope'] or 'unspecified'}")
        print("-" * 80)


def cmd_get(args: argparse.Namespace) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT raw_json FROM mechanics WHERE id = ?", (args.id.strip(),))
    row = cur.fetchone()
    if not row:
        # Fallback to search if exact ID didn't match
        cur.execute("SELECT id FROM mechanics WHERE id LIKE ? LIMIT 1", (f"%{args.id.strip()}%",))
        fallback = cur.fetchone()
        if fallback:
            cur.execute("SELECT raw_json FROM mechanics WHERE id = ?", (fallback["id"],))
            row = cur.fetchone()

    if not row:
        sys.stderr.write(f"Error: Mechanic '{args.id}' not found in Gameplay Atlas.\n")
        sys.exit(1)

    data = json.loads(row["raw_json"])
    if getattr(args, "json", False):
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    name = data.get("name", {}).get("en", data.get("id"))
    summary = data.get("summary", {}).get("en", "")
    system = data.get("system", "")
    tags = ", ".join(data.get("tags", []))
    rules = data.get("rules", {}).get("en", "")

    print(f"\n{'=' * 80}")
    print(f"📖 {name} (`{data.get('id')}`)")
    print(f"System: {system.upper()} | Tags: {tags} | Prototype Scope: {data.get('prototype', {}).get('scope', 'small')}")
    print(f"{'=' * 80}\n")
    print(f"💡 SUMMARY:\n  {summary}\n")
    print(f"⚙️ RULES & DYNAMICS:\n  {rules}\n")

    loop = data.get("loop", [])
    if loop:
        print("🔁 THE 4-STAGE CORE LOOP:")
        for idx, step in enumerate(loop, 1):
            step_text = step.get("en", str(step))
            print(f"  {idx}. {step_text}")
        print()

    decisions = data.get("decisions", [])
    if decisions:
        print("⚖️ PLAYER DILEMMAS & TRADE-OFFS:")
        for dec in decisions:
            print(f"  • {dec.get('en', str(dec))}")
        print()

    params = data.get("parameters", [])
    if params:
        print("🎛️ TUNABLE PARAMETERS & PSYCHOLOGICAL EFFECTS:")
        for p in params:
            p_name = p.get("name", {}).get("en", "Param")
            p_eff = p.get("effect", {}).get("en", "")
            print(f"  • {p_name}: {p_eff}")
        print()

    cases = data.get("cases", [])
    if cases:
        print("🎮 REAL SHIPPED GAME CASES:")
        for c in cases:
            game = c.get("game", "")
            impl = c.get("implementation", {}).get("en", "")
            src = c.get("source", "")
            img = c.get("image", "")
            print(f"  • {game}: {impl}")
            if src:
                print(f"    Source: {src}")
            if img:
                print(f"    Reference Image: {img}")
        print()

    proto = data.get("prototype", {})
    if proto:
        print("🛠️ RAPID PROTOTYPING RECIPE (Stage B Grounding):")
        print(f"  • First Step: {proto.get('firstStep', {}).get('en', 'N/A')}")
        print(f"  • Pitfall:    {proto.get('pitfall', {}).get('en', 'N/A')}")
        print(f"  • Test:       {proto.get('test', {}).get('en', 'N/A')}")
        print()

    combo = data.get("combination", {}).get("en", "")
    combines_with = ", ".join(data.get("combinesWith", []))
    if combo or combines_with:
        print(f"✨ COMBINATION OPPORTUNITY (combines with: {combines_with}):")
        if combo:
            print(f"  {combo}\n")


def cmd_systems(args: argparse.Namespace) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT system, COUNT(*) as count
        FROM mechanics
        GROUP BY system
        ORDER BY count DESC, system ASC
    """)
    rows = cur.fetchall()

    if getattr(args, "json", False):
        print(json.dumps([{"system": r["system"], "count": r["count"]} for r in rows], indent=2))
        return

    print("\n[Gameplay Atlas Systems] 28 Gameplay Systems:")
    print("=" * 60)
    for r in rows:
        print(f"• {r['system']:<18} ({r['count']} mechanics)")
    print("=" * 60)


def cmd_tags(args: argparse.Namespace) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT tag, COUNT(*) as count
        FROM mechanic_tags
        GROUP BY tag
        ORDER BY count DESC, tag ASC
    """)
    rows = cur.fetchall()

    if getattr(args, "json", False):
        print(json.dumps([{"tag": r["tag"], "count": r["count"]} for r in rows], indent=2))
        return

    print("\n[Gameplay Atlas Tags] 16 Gameplay Tags:")
    print("=" * 60)
    for r in rows:
        print(f"• {r['tag']:<18} ({r['count']} mechanics)")
    print("=" * 60)


def cmd_combine(args: argparse.Namespace) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    sys1 = args.system1.lower().strip()
    sys2 = (args.system2 or "").lower().strip()

    if sys2:
        # Cross-reference mechanics in sys1 that combine with sys2 (or vice versa)
        cur.execute("""
            SELECT m.id, m.name_en, m.system, m.combination_prompt_en,
                   cw.target_system
            FROM mechanics m
            JOIN mechanic_combines_with cw ON m.id = cw.mechanic_id
            WHERE (m.system = ? AND cw.target_system = ?)
               OR (m.system = ? AND cw.target_system = ?)
            ORDER BY m.system, m.name_en
        """, (sys1, sys2, sys2, sys1))
    else:
        # All combinations involving sys1
        cur.execute("""
            SELECT m.id, m.name_en, m.system, m.combination_prompt_en,
                   cw.target_system
            FROM mechanics m
            JOIN mechanic_combines_with cw ON m.id = cw.mechanic_id
            WHERE m.system = ? OR cw.target_system = ?
            ORDER BY cw.target_system, m.name_en
        """, (sys1, sys1))

    rows = cur.fetchall()

    if getattr(args, "json", False):
        results = [
            {
                "id": r["id"],
                "name": r["name_en"],
                "origin_system": r["system"],
                "combines_with": r["target_system"],
                "combination_prompt": r["combination_prompt_en"],
            }
            for r in rows
        ]
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    header = f"Cross-System Combinations: {sys1.upper()}" + (f" + {sys2.upper()}" if sys2 else "")
    print(f"\n[{header}] ({len(rows)} design synergies found):")
    print("=" * 80)
    if not rows:
        print("  No explicit pairing recorded in the catalog. Consider manual fusion using 'prototype-recipe'.")
        return

    for r in rows:
        print(f"• {r['name_en']} (`{r['id']}`) [{r['system']} ──► {r['target_system']}]")
        if r["combination_prompt_en"]:
            print(f"  Idea: {r['combination_prompt_en']}")
        print("-" * 80)


def cmd_prototype_recipe(args: argparse.Namespace) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name_en, system, prototype_scope, prototype_interaction,
               prototype_first_step_en, prototype_pitfall_en, prototype_test_en,
               walkthrough_setup_en, walkthrough_action_en, walkthrough_result_en, walkthrough_next_en
        FROM mechanics
        WHERE id = ? OR id LIKE ?
        LIMIT 1
    """, (args.id.strip(), f"%{args.id.strip()}%"))

    r = cur.fetchone()
    if not r:
        sys.stderr.write(f"Error: Mechanic '{args.id}' not found.\n")
        sys.exit(1)

    if getattr(args, "json", False):
        data = {
            "id": r["id"],
            "name": r["name_en"],
            "system": r["system"],
            "scope": r["prototype_scope"],
            "interaction": r["prototype_interaction"],
            "first_step": r["prototype_first_step_en"],
            "pitfall": r["prototype_pitfall_en"],
            "test": r["prototype_test_en"],
            "walkthrough": {
                "setup": r["walkthrough_setup_en"],
                "action": r["walkthrough_action_en"],
                "result": r["walkthrough_result_en"],
                "next": r["walkthrough_next_en"],
            },
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print(f"\n{'=' * 80}")
    print(f"🛠️ RAPID PROTOTYPING SPEC: {r['name_en']} (`{r['id']}`)")
    print(f"System: {r['system'].upper()} | Scope: {r['prototype_scope']} | Interaction: {r['prototype_interaction']}")
    print(f"{'=' * 80}\n")
    print(f"1. MICRO-SLICE FIRST STEP:\n   {r['prototype_first_step_en']}\n")
    print(f"2. CRITICAL PITFALL TO AVOID:\n   {r['prototype_pitfall_en']}\n")
    print(f"3. PLAYTEST VERIFICATION TEST:\n   {r['prototype_test_en']}\n")
    print("4. CONCRETE WALKTHROUGH FLOW:")
    print(f"   • Setup:  {r['walkthrough_setup_en']}")
    print(f"   • Action: {r['walkthrough_action_en']}")
    print(f"   • Result: {r['walkthrough_result_en']}")
    print(f"   • Next:   {r['walkthrough_next_en']}\n")


def cmd_cases(args: argparse.Namespace) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    game_query = args.game.strip()
    cur.execute("""
        SELECT c.game, c.implementation_en, c.source, c.image,
               m.id as mechanic_id, m.name_en, m.system
        FROM mechanic_cases c
        JOIN mechanics m ON c.mechanic_id = m.id
        WHERE c.game LIKE ?
        ORDER BY m.system, m.name_en
    """, (f"%{game_query}%",))

    rows = cur.fetchall()

    if getattr(args, "json", False):
        results = [
            {
                "game": r["game"],
                "mechanic_id": r["mechanic_id"],
                "mechanic_name": r["name_en"],
                "system": r["system"],
                "implementation": r["implementation_en"],
                "source": r["source"],
                "image": r["image"],
            }
            for r in rows
        ]
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print(f"\n[Gameplay Cases for '{game_query}'] Found {len(rows)} mechanics:")
    print("=" * 80)
    if not rows:
        print("  No cases found matching that game title in the atlas.")
        return

    for r in rows:
        print(f"• {r['name_en']} (`{r['mechanic_id']}`) - System: {r['system']}")
        print(f"  Game: {r['game']}")
        print(f"  Implementation: {r['implementation_en']}")
        if r["source"]:
            print(f"  Source: {r['source']}")
        if r["image"]:
            print(f"  Reference Image: {r['image']}")
        print("-" * 80)


def cmd_random(args: argparse.Namespace) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    conditions = []
    params = []
    if args.system:
        conditions.append("system = ?")
        params.append(args.system.lower().strip())
    if args.tag:
        conditions.append("id IN (SELECT mechanic_id FROM mechanic_tags WHERE tag = ?)")
        params.append(args.tag.lower().strip())

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    cur.execute(f"SELECT id FROM mechanics {where_clause} ORDER BY RANDOM() LIMIT 1", params)
    row = cur.fetchone()
    if not row:
        sys.stderr.write("No mechanics match the random filter criteria.\n")
        sys.exit(1)

    args.id = row["id"]
    cmd_get(args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gameplay Atlas CLI - 280 game mechanics field guide query lever.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = subparsers.add_parser("search", help="Full-text search across mechanics.")
    p_search.add_argument("query", type=str, nargs="?", default="", help="Search query (e.g. 'stamina', 'conveyor', 'deck')")
    p_search.add_argument("--system", type=str, help="Filter by gameplay system (e.g. 'combat', 'automation')")
    p_search.add_argument("--tag", type=str, help="Filter by tag (e.g. 'spatial', 'timing', 'optimization')")
    p_search.add_argument("--scope", type=str, help="Filter by prototype scope ('small', 'medium')")
    p_search.add_argument("--limit", type=int, default=10, help="Maximum results to return")
    p_search.add_argument("--json", action="store_true", help="Output raw JSON")
    p_search.set_defaults(func=cmd_search)

    # get
    p_get = subparsers.add_parser("get", help="Inspect a specific mechanic by ID.")
    p_get.add_argument("id", type=str, help="Mechanic identifier (e.g. 'automation-belt-routing')")
    p_get.add_argument("--json", action="store_true", help="Output raw JSON")
    p_get.set_defaults(func=cmd_get)

    # systems
    p_sys = subparsers.add_parser("systems", help="List all 28 gameplay systems.")
    p_sys.add_argument("--json", action="store_true", help="Output raw JSON")
    p_sys.set_defaults(func=cmd_systems)

    # tags
    p_tags = subparsers.add_parser("tags", help="List all 16 gameplay tags.")
    p_tags.add_argument("--json", action="store_true", help="Output raw JSON")
    p_tags.set_defaults(func=cmd_tags)

    # combine
    p_comb = subparsers.add_parser("combine", help="Explore cross-system mechanic combinations.")
    p_comb.add_argument("system1", type=str, help="First system (e.g. 'combat', 'automation')")
    p_comb.add_argument("system2", type=str, nargs="?", default="", help="Second system to pair with (optional)")
    p_comb.add_argument("--json", action="store_true", help="Output raw JSON")
    p_comb.set_defaults(func=cmd_combine)

    # prototype-recipe
    p_proto = subparsers.add_parser("prototype-recipe", help="Extract Stage B rapid prototyping recipe.")
    p_proto.add_argument("id", type=str, help="Mechanic identifier")
    p_proto.add_argument("--json", action="store_true", help="Output raw JSON")
    p_proto.set_defaults(func=cmd_prototype_recipe)

    # cases
    p_cases = subparsers.add_parser("cases", help="Find mechanics implemented by a specific shipped game.")
    p_cases.add_argument("game", type=str, help="Game name (e.g. 'Factorio', 'Celeste', 'Hades')")
    p_cases.add_argument("--json", action="store_true", help="Output raw JSON")
    p_cases.set_defaults(func=cmd_cases)

    # random
    p_rand = subparsers.add_parser("random", help="Serendipitous random mechanic generator.")
    p_rand.add_argument("--system", type=str, help="Filter by system")
    p_rand.add_argument("--tag", type=str, help="Filter by tag")
    p_rand.add_argument("--json", action="store_true", help="Output raw JSON")
    p_rand.set_defaults(func=cmd_random)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
