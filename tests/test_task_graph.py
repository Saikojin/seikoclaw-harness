import unittest
import os
import tempfile
import shutil
from openbrain.task_graph import TaskGraph

class TestTaskGraph(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_openbrain.db")
        self.graph = TaskGraph(self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_task_and_generate_hash_id(self):
        tid1 = self.graph.create_task("Design Database Schema", priority=1)
        self.assertTrue(tid1.startswith("sc-"))
        task = self.graph.get_task(tid1)
        self.assertIsNotNone(task)
        self.assertEqual(task["title"], "Design Database Schema")
        self.assertEqual(task["status"], "open")
        self.assertEqual(task["priority"], 1)

    def test_hierarchical_subtask_id(self):
        parent_id = self.graph.create_task("Core Architecture Epic", priority=0, task_type="epic")
        child_id1 = self.graph.create_task("Implement Task DAG", parent_id=parent_id)
        child_id2 = self.graph.create_task("Implement Watchdog", parent_id=parent_id)

        self.assertEqual(child_id1, f"{parent_id}.1")
        self.assertEqual(child_id2, f"{parent_id}.2")

    def test_dependencies_and_cycle_prevention(self):
        t1 = self.graph.create_task("Task 1")
        t2 = self.graph.create_task("Task 2")
        t3 = self.graph.create_task("Task 3")

        # t1 blocks t2, t2 blocks t3
        self.graph.add_dependency(t1, t2, edge_type="blocks")
        self.graph.add_dependency(t2, t3, edge_type="blocks")

        # Cycle test: t3 cannot block t1
        with self.assertRaises(ValueError):
            self.graph.add_dependency(t3, t1, edge_type="blocks")

    def test_ready_frontier_computation(self):
        t1 = self.graph.create_task("Task 1 (Prerequisite)", priority=0)
        t2 = self.graph.create_task("Task 2 (Dependent)", priority=1)
        t3 = self.graph.create_task("Task 3 (Independent)", priority=2)

        self.graph.add_dependency(t1, t2, edge_type="blocks")

        # Initially, only t1 and t3 are ready
        frontier = self.graph.get_ready_frontier()
        frontier_ids = [t["id"] for t in frontier]
        self.assertIn(t1, frontier_ids)
        self.assertIn(t3, frontier_ids)
        self.assertNotIn(t2, frontier_ids)

        # Complete t1
        self.graph.close_task(t1)

        # Now t2 should be on the ready frontier
        frontier_after = self.graph.get_ready_frontier()
        frontier_ids_after = [t["id"] for t in frontier_after]
        self.assertIn(t2, frontier_ids_after)
        self.assertIn(t3, frontier_ids_after)

    def test_atomic_claim(self):
        t1 = self.graph.create_task("Task 1")
        claimed = self.graph.claim_task(t1, worker_id="agent-alpha")
        self.assertTrue(claimed)

        task = self.graph.get_task(t1)
        self.assertEqual(task["status"], "in_progress")
        self.assertEqual(task["claimed_by"], "agent-alpha")

        # Second claim should fail because task is no longer 'open'
        claimed_again = self.graph.claim_task(t1, worker_id="agent-beta")
        self.assertFalse(claimed_again)

    def test_wisps_and_purge(self):
        wisp_id = self.graph.create_wisp("Temporary Diagnostics")
        task = self.graph.get_task(wisp_id)
        self.assertEqual(task["is_ephemeral"], 1)

        self.graph.close_task(wisp_id)
        purged_count = self.graph.purge_wisps()
        self.assertEqual(purged_count, 1)
        self.assertIsNone(self.graph.get_task(wisp_id))

    def test_markdown_sync(self):
        t1 = self.graph.create_task("Setup Harness")
        md_file = os.path.join(self.test_dir, "task_test.md")
        self.graph.sync_to_file(md_file)

        self.assertTrue(os.path.exists(md_file))
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(t1, content)
        self.assertIn("Setup Harness", content)

if __name__ == "__main__":
    unittest.main()
