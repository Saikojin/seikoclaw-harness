#!/usr/bin/env python3
"""
tests/test_gameplay_atlas_db.py - Unit and verification tests for data/gameplay_atlas.db
"""

import sqlite3
import unittest
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "gameplay_atlas.db"


class TestGameplayAtlasDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assertTrue(DB_PATH.exists(), f"Database file missing at {DB_PATH}")
        cls.conn = sqlite3.connect(str(DB_PATH))
        cls.conn.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_total_mechanics_count(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM mechanics")
        count = cur.fetchone()[0]
        self.assertEqual(count, 280, f"Expected 280 mechanics, got {count}")

    def test_systems_count(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT system) FROM mechanics")
        count = cur.fetchone()[0]
        self.assertEqual(count, 28, f"Expected 28 systems, got {count}")

    def test_fts5_virtual_table(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM mechanics_fts")
        count = cur.fetchone()[0]
        self.assertEqual(count, 280, f"Expected 280 indexed FTS rows, got {count}")

    def test_fts5_search_query(self):
        cur = self.conn.cursor()
        # Search for parry mechanics
        cur.execute("""
            SELECT m.id, m.name_en, m.system
            FROM mechanics_fts f
            JOIN mechanics m ON f.id = m.id
            WHERE mechanics_fts MATCH 'parry'
        """)
        rows = cur.fetchall()
        self.assertGreaterEqual(len(rows), 1, "Expected at least 1 mechanic matching 'parry'")
        matched_ids = [r["id"] for r in rows]
        self.assertTrue(any("parry" in m_id or "combat" in m_id for m_id in matched_ids))

    def test_mechanic_relational_integrity(self):
        cur = self.conn.cursor()
        # Check automation-belt-routing
        cur.execute("SELECT * FROM mechanics WHERE id = 'automation-belt-routing'")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["name_en"], "Conveyor routing")
        self.assertEqual(row["system"], "automation")
        self.assertIn("Route materials around obstacles", row["summary_en"])

        # Check loops
        cur.execute("SELECT step_index, step_en FROM mechanic_loops WHERE mechanic_id = 'automation-belt-routing' ORDER BY step_index")
        loops = cur.fetchall()
        self.assertEqual(len(loops), 4)
        self.assertEqual(loops[0]["step_en"], "Identify endpoints")

        # Check parameters
        cur.execute("SELECT name_en, effect_en FROM mechanic_parameters WHERE mechanic_id = 'automation-belt-routing'")
        params = cur.fetchall()
        self.assertGreaterEqual(len(params), 2)

        # Check cases
        cur.execute("SELECT game, implementation_en FROM mechanic_cases WHERE mechanic_id = 'automation-belt-routing'")
        cases = cur.fetchall()
        self.assertGreaterEqual(len(cases), 2)
        games = [c["game"] for c in cases]
        self.assertIn("Factorio", games)
        self.assertIn("Satisfactory", games)

    def test_prototype_recipes(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, prototype_first_step_en, prototype_pitfall_en, prototype_test_en
            FROM mechanics
            WHERE prototype_first_step_en IS NOT NULL AND prototype_first_step_en != ''
        """)
        rows = cur.fetchall()
        # All 280 mechanics should have prototype firstStep guidance
        self.assertEqual(len(rows), 280, f"Expected all 280 mechanics to have prototype guidance, got {len(rows)}")


if __name__ == "__main__":
    unittest.main()
