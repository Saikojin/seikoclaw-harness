import os
import sys
import unittest
import tempfile
import shutil
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openbrain.memory_engine import MemoryEngine
from openbrain.context_engine import ContextEngine
from openbrain.llm_provider import BaseLLMProvider, HeuristicFallbackProvider

class MockNeuralLLMProvider(BaseLLMProvider):
    name = "Mock Neural LLM"

    @property
    def is_neural(self) -> bool:
        return True

    @property
    def is_heuristic(self) -> bool:
        return False

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        return "Consolidated Midterm Record: 10 steps executed successfully with zero regressions."

class TestMemoryCompression(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_memory.db")
        self.chroma_path = os.path.join(self.temp_dir, "test_chroma")
        self.memory = MemoryEngine(db_path=self.db_path, chroma_path=self.chroma_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_heuristic_fallback_does_not_delete_memories(self):
        # By default in test environment without neural backend, heuristic provider is active
        self.memory.context_engine.llm = HeuristicFallbackProvider()

        # Save 12 short term memories
        for i in range(12):
            self.memory.save_memory(f"Step {i}: executed action {i}", tier="Shortterm", source="test")

        # Verify all 12 memories still exist in SQLite as Shortterm
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM memories WHERE tier = 'Shortterm'")
        count = cur.fetchone()[0]
        conn.close()

        self.assertEqual(count, 12, "Heuristic fallback must never delete or corrupt short-term memories!")

    def test_neural_llm_soft_archives_memories(self):
        # Inject mock neural provider
        self.memory.context_engine.llm = MockNeuralLLMProvider()

        # Save 10 short term memories
        ids = []
        for i in range(10):
            mid = self.memory.save_memory(f"Action {i}: verified result {i}", tier="Shortterm", source="test")
            ids.append(mid)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Verify Midterm memory was created
        cur.execute("SELECT id, content FROM memories WHERE tier = 'Midterm'")
        midterm_rows = cur.fetchall()
        self.assertEqual(len(midterm_rows), 1)
        midterm_id = midterm_rows[0][0]
        self.assertIn("Consolidated Midterm Record", midterm_rows[0][1])

        # Verify all 10 raw memories were soft-archived with compressed_into linkage
        cur.execute("SELECT id, tier, compressed_into, archived_at FROM memories WHERE tier = 'Archived'")
        archived_rows = cur.fetchall()
        self.assertEqual(len(archived_rows), 10)
        for row in archived_rows:
            self.assertEqual(row[1], "Archived")
            self.assertEqual(row[2], midterm_id)
            self.assertIsNotNone(row[3])

        conn.close()

    def test_retrieve_similar_filters_archived(self):
        # Save a short-term memory and archive it
        mid = self.memory.save_memory("Critical secret deployment token ABCXYZ", tier="Shortterm", source="test")
        self.memory.promote_memory(mid, "Archived")

        # Save active memory
        self.memory.save_memory("Active deployment note 123", tier="Shortterm", source="test")

        # Search should not surface Archived memory by default in SQLite fallback
        results = self.memory.retrieve_similar("deployment token")
        matching_ids = [r["id"] for r in results]
        self.assertNotIn(mid, matching_ids)

if __name__ == "__main__":
    unittest.main()
