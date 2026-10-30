#!/usr/bin/env python3
"""
scripts/sync_gameplay_atlas.py - Synchronize Gameplay Atlas catalog and details into SQLite & local cache.

Discovers the active asset bundle hash from https://gameplayatlas.loopyhop.com/,
fetches all 280 mechanics concurrently, creates data/gameplay_atlas/raw/*.json,
and builds data/gameplay_atlas.db with normalized relational schema and SQLite FTS5 search index.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import os
import re
import sqlite3
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("sync_gameplay_atlas")

BASE_URL = "https://gameplayatlas.loopyhop.com"
DEFAULT_HASH = "fe93b4be8ae4079e"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS mechanics (
    id TEXT PRIMARY KEY,
    system TEXT NOT NULL,
    name_en TEXT NOT NULL,
    name_zh TEXT,
    summary_en TEXT NOT NULL,
    summary_zh TEXT,
    rules_en TEXT,
    rules_zh TEXT,
    contrast_en TEXT,
    contrast_zh TEXT,
    combination_prompt_en TEXT,
    combination_prompt_zh TEXT,
    prototype_scope TEXT,
    prototype_interaction TEXT,
    prototype_first_step_en TEXT,
    prototype_first_step_zh TEXT,
    prototype_pitfall_en TEXT,
    prototype_pitfall_zh TEXT,
    prototype_test_en TEXT,
    prototype_test_zh TEXT,
    walkthrough_setup_en TEXT,
    walkthrough_action_en TEXT,
    walkthrough_result_en TEXT,
    walkthrough_next_en TEXT,
    edition INTEGER,
    raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mechanic_tags (
    mechanic_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (mechanic_id, tag),
    FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mechanic_loops (
    mechanic_id TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    step_en TEXT NOT NULL,
    step_zh TEXT,
    PRIMARY KEY (mechanic_id, step_index),
    FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mechanic_decisions (
    mechanic_id TEXT NOT NULL,
    decision_index INTEGER NOT NULL,
    decision_en TEXT NOT NULL,
    decision_zh TEXT,
    PRIMARY KEY (mechanic_id, decision_index),
    FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mechanic_parameters (
    mechanic_id TEXT NOT NULL,
    param_index INTEGER NOT NULL,
    name_en TEXT NOT NULL,
    name_zh TEXT,
    effect_en TEXT,
    effect_zh TEXT,
    PRIMARY KEY (mechanic_id, param_index),
    FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mechanic_cases (
    mechanic_id TEXT NOT NULL,
    case_index INTEGER NOT NULL,
    game TEXT NOT NULL,
    game_zh TEXT,
    implementation_en TEXT,
    implementation_zh TEXT,
    source TEXT,
    source_label TEXT,
    image TEXT,
    image_kind TEXT,
    observation_en TEXT,
    rights TEXT,
    verified TEXT,
    original_image TEXT,
    PRIMARY KEY (mechanic_id, case_index),
    FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mechanic_combines_with (
    mechanic_id TEXT NOT NULL,
    target_system TEXT NOT NULL,
    PRIMARY KEY (mechanic_id, target_system),
    FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mechanic_combination_ids (
    mechanic_id TEXT NOT NULL,
    target_mechanic_id TEXT NOT NULL,
    PRIMARY KEY (mechanic_id, target_mechanic_id),
    FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mechanic_related (
    mechanic_id TEXT NOT NULL,
    related_mechanic_id TEXT NOT NULL,
    PRIMARY KEY (mechanic_id, related_mechanic_id),
    FOREIGN KEY (mechanic_id) REFERENCES mechanics(id) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE IF NOT EXISTS mechanics_fts USING fts5(
    id UNINDEXED,
    name_en,
    summary_en,
    rules_en,
    system,
    tags,
    cases,
    loop_text,
    decisions_text,
    parameters_text,
    prototype_text,
    tokenize = 'porter unicode61'
);

CREATE INDEX IF NOT EXISTS idx_mechanics_system ON mechanics(system);
CREATE INDEX IF NOT EXISTS idx_mechanic_tags_tag ON mechanic_tags(tag);
CREATE INDEX IF NOT EXISTS idx_mechanic_cases_game ON mechanic_cases(game);
"""


def fetch_url(url: str, retries: int = 3, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except Exception as e:
            last_err = e
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts: {last_err}")


def discover_asset_hash() -> str:
    """Fetch root page and extract active asset directory hash."""
    logger.info("Discovering asset hash from %s...", BASE_URL)
    try:
        html = fetch_url(BASE_URL).decode("utf-8", errors="ignore")
        match = re.search(r'href=["\']/assets/([a-zA-Z0-9]+)/index\.json["\']', html)
        if match:
            asset_hash = match.group(1)
            logger.info("Discovered asset hash: %s", asset_hash)
            return asset_hash
        match = re.search(r'src=["\']/assets/([a-zA-Z0-9]+)/app\.js["\']', html)
        if match:
            asset_hash = match.group(1)
            logger.info("Discovered asset hash from app.js: %s", asset_hash)
            return asset_hash
    except Exception as e:
        logger.warning("Could not probe live homepage (%s), falling back to %s", e, DEFAULT_HASH)
    return DEFAULT_HASH


def fetch_mechanic_detail(asset_hash: str, mechanic_id: str, raw_dir: Path) -> Dict[str, Any]:
    """Fetch individual mechanic JSON payload and save locally."""
    dest_path = raw_dir / f"{mechanic_id}.json"
    url = f"{BASE_URL}/assets/{asset_hash}/mechanics/{mechanic_id}.json"
    data_bytes = fetch_url(url)
    data = json.loads(data_bytes.decode("utf-8"))
    dest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data


def init_database(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def insert_mechanic_into_db(conn: sqlite3.Connection, m: Dict[str, Any]) -> None:
    cur = conn.cursor()
    m_id = m["id"]
    system = m.get("system", "")

    # Localized text extraction helpers
    def en(field: Any) -> str:
        if isinstance(field, dict):
            return field.get("en", "") or ""
        return str(field or "")

    def zh(field: Any) -> str:
        if isinstance(field, dict):
            return field.get("zh", "") or ""
        return ""

    proto = m.get("prototype") or {}
    walkthrough = m.get("walkthrough") or {}

    cur.execute(
        """
        INSERT OR REPLACE INTO mechanics (
            id, system, name_en, name_zh, summary_en, summary_zh,
            rules_en, rules_zh, contrast_en, contrast_zh,
            combination_prompt_en, combination_prompt_zh,
            prototype_scope, prototype_interaction,
            prototype_first_step_en, prototype_first_step_zh,
            prototype_pitfall_en, prototype_pitfall_zh,
            prototype_test_en, prototype_test_zh,
            walkthrough_setup_en, walkthrough_action_en, walkthrough_result_en, walkthrough_next_en,
            edition, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            m_id,
            system,
            en(m.get("name")),
            zh(m.get("name")),
            en(m.get("summary")),
            zh(m.get("summary")),
            en(m.get("rules")),
            zh(m.get("rules")),
            en(m.get("contrast")),
            zh(m.get("contrast")),
            en(m.get("combination")),
            zh(m.get("combination")),
            proto.get("scope", ""),
            proto.get("interaction", ""),
            en(proto.get("firstStep")),
            zh(proto.get("firstStep")),
            en(proto.get("pitfall")),
            zh(proto.get("pitfall")),
            en(proto.get("test")),
            zh(proto.get("test")),
            en(walkthrough.get("setup")),
            en(walkthrough.get("action")),
            en(walkthrough.get("result")),
            en(walkthrough.get("next")),
            m.get("edition", 1),
            json.dumps(m, ensure_ascii=False),
        ),
    )

    # Delete existing relations for clean idempotency
    cur.execute("DELETE FROM mechanic_tags WHERE mechanic_id = ?", (m_id,))
    cur.execute("DELETE FROM mechanic_loops WHERE mechanic_id = ?", (m_id,))
    cur.execute("DELETE FROM mechanic_decisions WHERE mechanic_id = ?", (m_id,))
    cur.execute("DELETE FROM mechanic_parameters WHERE mechanic_id = ?", (m_id,))
    cur.execute("DELETE FROM mechanic_cases WHERE mechanic_id = ?", (m_id,))
    cur.execute("DELETE FROM mechanic_combines_with WHERE mechanic_id = ?", (m_id,))
    cur.execute("DELETE FROM mechanic_combination_ids WHERE mechanic_id = ?", (m_id,))
    cur.execute("DELETE FROM mechanic_related WHERE mechanic_id = ?", (m_id,))

    # Tags
    tags_list = m.get("tags") or []
    for tag in tags_list:
        cur.execute("INSERT OR IGNORE INTO mechanic_tags (mechanic_id, tag) VALUES (?, ?)", (m_id, tag))

    # Loops
    loops_list = m.get("loop") or []
    loop_text_parts = []
    for idx, step in enumerate(loops_list):
        step_en = en(step)
        loop_text_parts.append(step_en)
        cur.execute(
            "INSERT INTO mechanic_loops (mechanic_id, step_index, step_en, step_zh) VALUES (?, ?, ?, ?)",
            (m_id, idx, step_en, zh(step)),
        )

    # Decisions
    decisions_list = m.get("decisions") or []
    decisions_text_parts = []
    for idx, dec in enumerate(decisions_list):
        dec_en = en(dec)
        decisions_text_parts.append(dec_en)
        cur.execute(
            "INSERT INTO mechanic_decisions (mechanic_id, decision_index, decision_en, decision_zh) VALUES (?, ?, ?, ?)",
            (m_id, idx, dec_en, zh(dec)),
        )

    # Parameters
    params_list = m.get("parameters") or []
    param_text_parts = []
    for idx, p in enumerate(params_list):
        p_name_en = en(p.get("name"))
        p_eff_en = en(p.get("effect"))
        param_text_parts.append(f"{p_name_en}: {p_eff_en}")
        cur.execute(
            "INSERT INTO mechanic_parameters (mechanic_id, param_index, name_en, name_zh, effect_en, effect_zh) VALUES (?, ?, ?, ?, ?, ?)",
            (m_id, idx, p_name_en, zh(p.get("name")), p_eff_en, zh(p.get("effect"))),
        )

    # Cases (shipped games)
    cases_list = m.get("cases") or []
    case_text_parts = []
    for idx, c in enumerate(cases_list):
        game_title = c.get("game", "")
        impl_en = en(c.get("implementation"))
        case_text_parts.append(f"{game_title} ({impl_en})")
        cur.execute(
            """
            INSERT INTO mechanic_cases (
                mechanic_id, case_index, game, game_zh, implementation_en, implementation_zh,
                source, source_label, image, image_kind, observation_en, rights, verified, original_image
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                m_id,
                idx,
                game_title,
                c.get("gameZh", ""),
                impl_en,
                zh(c.get("implementation")),
                c.get("source", ""),
                c.get("sourceLabel", ""),
                c.get("image", ""),
                c.get("imageKind", ""),
                en(c.get("observation")),
                c.get("rights", ""),
                c.get("verified", ""),
                c.get("originalImage", ""),
            ),
        )

    # Combines With & Combinations
    for sys_target in m.get("combinesWith") or []:
        cur.execute("INSERT OR IGNORE INTO mechanic_combines_with (mechanic_id, target_system) VALUES (?, ?)", (m_id, sys_target))

    for combo_id in m.get("combinationIds") or []:
        cur.execute("INSERT OR IGNORE INTO mechanic_combination_ids (mechanic_id, target_mechanic_id) VALUES (?, ?)", (m_id, combo_id))

    for rel_id in m.get("related") or []:
        cur.execute("INSERT OR IGNORE INTO mechanic_related (mechanic_id, related_mechanic_id) VALUES (?, ?)", (m_id, rel_id))

    # FTS5 Indexing
    prototype_text = " ".join(
        filter(
            None,
            [
                proto.get("scope", ""),
                proto.get("interaction", ""),
                en(proto.get("firstStep")),
                en(proto.get("pitfall")),
                en(proto.get("test")),
            ],
        )
    )

    cur.execute("DELETE FROM mechanics_fts WHERE id = ?", (m_id,))
    cur.execute(
        """
        INSERT INTO mechanics_fts (
            id, name_en, summary_en, rules_en, system, tags, cases,
            loop_text, decisions_text, parameters_text, prototype_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            m_id,
            en(m.get("name")),
            en(m.get("summary")),
            en(m.get("rules")),
            system,
            " ".join(tags_list),
            " ".join(case_text_parts),
            " ".join(loop_text_parts),
            " ".join(decisions_text_parts),
            " ".join(param_text_parts),
            prototype_text,
        ),
    )


def sync(workspace_dir: Path, workers: int = 12) -> Tuple[int, int]:
    """Execute complete sync pipeline."""
    data_dir = workspace_dir / "data" / "gameplay_atlas"
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    db_path = workspace_dir / "data" / "gameplay_atlas.db"

    asset_hash = discover_asset_hash()
    index_url = f"{BASE_URL}/assets/{asset_hash}/index.json"

    logger.info("Fetching index catalog from %s...", index_url)
    index_bytes = fetch_url(index_url)
    catalog = json.loads(index_bytes.decode("utf-8"))
    (raw_dir / "index.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")

    total_mechanics = len(catalog)
    logger.info("Found %d mechanics in catalog. Beginning concurrent detail downloads (workers=%d)...", total_mechanics, workers)

    mechanics_data: List[Dict[str, Any]] = []
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_id = {
            executor.submit(fetch_mechanic_detail, asset_hash, item["id"], raw_dir): item["id"]
            for item in catalog
        }
        completed = 0
        for future in concurrent.futures.as_completed(future_to_id):
            item_id = future_to_id[future]
            try:
                detail = future.result()
                mechanics_data.append(detail)
                completed += 1
                if completed % 50 == 0 or completed == total_mechanics:
                    logger.info("Progress: %d / %d mechanics downloaded (%.1fs)", completed, total_mechanics, time.time() - start_time)
            except Exception as e:
                logger.error("Failed to download mechanic %s: %s", item_id, e)
                raise

    logger.info("All %d mechanics fetched. Building SQLite database at %s...", len(mechanics_data), db_path)
    conn = init_database(db_path)
    with conn:
        for m in mechanics_data:
            insert_mechanic_into_db(conn, m)
        conn.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('asset_hash', ?)", (asset_hash,))
        conn.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('last_synced_at', ?)", (time.strftime("%Y-%m-%dT%H:%M:%SZ"),))
        conn.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('total_mechanics', ?)", (str(len(mechanics_data)),))

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM mechanics")
    row_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT system) FROM mechanics")
    sys_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM mechanic_parameters")
    param_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM mechanic_cases")
    cases_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM mechanics_fts")
    fts_count = cur.fetchone()[0]
    conn.close()

    elapsed = time.time() - start_time
    logger.info("Sync complete in %.2fs!", elapsed)
    logger.info("Database verification: %d mechanics across %d systems, %d parameters, %d game cases, %d FTS indexed rows.",
                row_count, sys_count, param_count, cases_count, fts_count)

    return row_count, sys_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronize Gameplay Atlas catalog into SQLite and JSON cache.")
    parser.add_argument("--workers", type=int, default=12, help="Number of concurrent download threads")
    parser.add_argument("--workspace", type=str, default=".", help="Root workspace directory")
    args = parser.parse_args()

    workspace_dir = Path(args.workspace).resolve()
    try:
        count, systems = sync(workspace_dir, workers=args.workers)
        print(f"\n[SUCCESS] Successfully synced {count} mechanics across {systems} systems into {workspace_dir / 'data' / 'gameplay_atlas.db'}")
    except Exception as e:
        logger.exception("Synchronization failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
