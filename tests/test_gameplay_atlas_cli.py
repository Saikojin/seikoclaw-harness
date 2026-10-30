#!/usr/bin/env python3
"""
tests/test_gameplay_atlas_cli.py - Verification suite for scripts/gameplay_atlas.py CLI
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

CLI_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "gameplay_atlas.py"


class TestGameplayAtlasCLI(unittest.TestCase):
    def run_cli(self, *args) -> str:
        cmd = [sys.executable, str(CLI_SCRIPT)] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, f"Command failed: {cmd}\nStderr: {result.stderr}")
        return result.stdout

    def test_search_json(self):
        out = self.run_cli("search", "stamina", "--json")
        data = json.loads(out)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertTrue(any("stamina" in item["id"] or "combat" in item["system"] for item in data))

    def test_get_json(self):
        out = self.run_cli("get", "combat-stamina-budget", "--json")
        data = json.loads(out)
        self.assertEqual(data["id"], "combat-stamina-budget")
        self.assertEqual(data["system"], "combat")
        self.assertIn("loop", data)
        self.assertIn("parameters", data)
        self.assertIn("cases", data)

    def test_systems_json(self):
        out = self.run_cli("systems", "--json")
        data = json.loads(out)
        self.assertEqual(len(data), 28)
        systems = [s["system"] for s in data]
        self.assertIn("combat", systems)
        self.assertIn("automation", systems)
        self.assertIn("movement", systems)

    def test_tags_json(self):
        out = self.run_cli("tags", "--json")
        data = json.loads(out)
        self.assertEqual(len(data), 16)
        tags = [t["tag"] for t in data]
        self.assertIn("planning", tags)
        self.assertIn("spatial", tags)

    def test_combine_json(self):
        out = self.run_cli("combine", "combat", "inventory", "--json")
        data = json.loads(out)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_prototype_recipe_json(self):
        out = self.run_cli("prototype-recipe", "automation-belt-routing", "--json")
        data = json.loads(out)
        self.assertEqual(data["id"], "automation-belt-routing")
        self.assertIn("first_step", data)
        self.assertIn("pitfall", data)
        self.assertIn("test", data)
        self.assertIn("walkthrough", data)

    def test_cases_json(self):
        out = self.run_cli("cases", "Factorio", "--json")
        data = json.loads(out)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertTrue(any(c["game"] == "Factorio" for c in data))

    def test_random_mechanic(self):
        out = self.run_cli("random", "--system", "movement", "--json")
        data = json.loads(out)
        self.assertEqual(data["system"], "movement")
        self.assertIn("name", data)


if __name__ == "__main__":
    unittest.main()
