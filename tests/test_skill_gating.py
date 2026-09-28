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

    def test_disk_aware_regression_protection(self):
        skills_dir = os.path.join(self.temp_dir, "skills")
        tdd_dir = os.path.join(skills_dir, "tdd")
        os.makedirs(tdd_dir, exist_ok=True)
        
        # Write hand-written skill on disk (NOT in DB)
        disk_skill = """---
name: tdd
description: Test Driven Development
---
# RULES
Write tests before code.
# BOUNDARIES
Never bypass test assertions. Never commit failing tests.
"""
        with open(os.path.join(tdd_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(disk_skill)

        # Candidate skill that discards "Never bypass test assertions"
        candidate_bad = """---
name: tdd
description: Test Driven Development
---
# RULES
Just write code and tests.
# BOUNDARIES
Do NOT leave untracked changes.
"""
        passed, msg = self.gater.gate_and_save(
            skill_text=candidate_bad,
            skill_name="tdd",
            memory_engine=self.memory,
            target_dir=skills_dir
        )
        self.assertFalse(passed)
        self.assertIn("Regression Error", msg)

    def test_candidate_staging_and_promotion(self):
        skills_dir = os.path.join(self.temp_dir, "skills")
        skill_text = """---
name: api-tester
description: API testing workflow
---
# RULES
Always validate status codes.
# BOUNDARIES
Never log authentication tokens.
"""
        # 1. Save as staged candidate
        passed, msg = self.gater.gate_and_save(
            skill_text=skill_text,
            skill_name="api-tester",
            memory_engine=self.memory,
            target_dir=skills_dir,
            staging=True
        )
        self.assertTrue(passed)
        self.assertTrue(os.path.exists(os.path.join(skills_dir, ".candidates", "api-tester", "SKILL.md")))
        self.assertFalse(os.path.exists(os.path.join(skills_dir, "api-tester", "SKILL.md")))

        # 2. List candidates
        cands = self.gater.list_candidates(target_dir=skills_dir)
        self.assertEqual(len(cands), 1)
        self.assertEqual(cands[0]["name"], "api-tester")

        # 3. Diff candidate
        diff = self.gater.diff_candidate("api-tester", target_dir=skills_dir)
        self.assertIn("api-tester", diff)

        # 4. Promote candidate
        ok, pmsg = self.gater.promote_candidate("api-tester", target_dir=skills_dir, memory_engine=self.memory)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(os.path.join(skills_dir, "api-tester", "SKILL.md")))
        self.assertFalse(os.path.exists(os.path.join(skills_dir, ".candidates", "api-tester", "SKILL.md")))

    def test_heuristic_fallback_safety(self):
        from openbrain.llm_provider import HeuristicFallbackProvider
        provider = HeuristicFallbackProvider()
        self.assertTrue(provider.is_heuristic)
        self.assertFalse(provider.is_neural)

        # Skill synthesis prompt returns empty string (refuses to clobber)
        synth_res = provider.generate('Synthesize or Evolve a "Skill" from TRAJECTORY: ...')
        self.assertEqual(synth_res, "")

        # Caveman prompt returns empty string (refuses to delete memories)
        cave_res = provider.generate('Summarize into Midterm memory. Use Smart Caveman logic: ...')
        self.assertEqual(cave_res, "")

if __name__ == "__main__":
    unittest.main()
