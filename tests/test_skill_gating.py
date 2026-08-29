import os
import sys
import unittest
import tempfile
import shutil

# Ensure openbrain is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openbrain.skill_gating import SkillGater
from openbrain.memory_engine import MemoryEngine

class TestSkillGater(unittest.TestCase):
    def setUp(self):
        self.gater = SkillGater()
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_openbrain.db")
        self.chroma_path = os.path.join(self.temp_dir, "test_chroma")
        self.memory = MemoryEngine(db_path=self.db_path, chroma_path=self.chroma_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_valid_skill(self):
        skill_text = """---
name: test-skill
evolution: Lite
version: 1.0.0
---
# RULES
When running tests, use pytest.
# BOUNDARIES
Never execute unvetted rm commands.
"""
        success, meta, body, err = self.gater.parse_skill_text(skill_text)
        self.assertTrue(success)
        self.assertEqual(meta.get("name"), "test-skill")
        self.assertIn("# RULES", body)
        self.assertIn("# BOUNDARIES", body)

    def test_reject_missing_frontmatter(self):
        skill_text = "# RULES\nSome rules without frontmatter."
        is_valid, msg, _ = self.gater.validate_schema(skill_text)
        self.assertFalse(is_valid)
        self.assertIn("Missing valid YAML frontmatter", msg)

    def test_reject_disallowed_placeholders(self):
        skill_text = """---
name: mock-skill
---
# RULES
Do something [Mock Response] here.
# BOUNDARIES
Avoid doing bad things.
"""
        is_valid, msg, _ = self.gater.validate_schema(skill_text)
        self.assertFalse(is_valid)
        self.assertIn("disallowed placeholder", msg)

    def test_reject_missing_boundaries(self):
        skill_text = """---
name: no-boundary-skill
---
# RULES
Always run the test command after editing.
"""
        is_valid, msg, _ = self.gater.validate_schema(skill_text)
        self.assertFalse(is_valid)
        self.assertIn("Missing '# BOUNDARIES'", msg)

    def test_gate_and_save_success(self):
        skill_text = """---
name: auto-refactor
description: Automated refactoring skill
---
# RULES
1. Run lint check before refactoring.
2. Verify all unit tests pass.
# BOUNDARIES
Never commit code with failing tests or unformatted blocks.
"""
        skills_dir = os.path.join(self.temp_dir, "skills")
        passed, msg = self.gater.gate_and_save(
            skill_text=skill_text,
            skill_name="auto-refactor",
            memory_engine=self.memory,
            target_dir=skills_dir
        )
        self.assertTrue(passed)
        self.assertTrue(os.path.exists(os.path.join(skills_dir, "auto-refactor", "SKILL.md")))
        
        # Verify Openbrain persistent storage
        skill_db = self.memory.get_skill("auto-refactor")
        self.assertIsNotNone(skill_db)
        self.assertEqual(skill_db["name"], "auto-refactor")

    def test_mistake_tracker(self):
        mem_id = self.memory.save_mistake(
            task_id="AUTH-002",
            error_trace="TypeError: NoneType object has no attribute 'token'",
            context="Testing JWT token refresh handler",
            hypothesis="Ensure token validator handles expired refresh tokens gracefully."
        )
        self.assertIsNotNone(mem_id)
        
        mistakes = self.memory.get_mistakes("JWT token refresh")
        self.assertTrue(len(mistakes) > 0)
        self.assertIn("AUTH-002", mistakes[0]["content"])

if __name__ == "__main__":
    unittest.main()
